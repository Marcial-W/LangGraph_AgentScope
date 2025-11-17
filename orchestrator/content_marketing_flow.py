import asyncio
from typing import Any, Dict, Callable, Optional, Tuple

from agents.content_agent import ContentAgent
from agents.critic_agent import CriticAgent
from agents.strategy_agent import StrategyAgent
from agents.execution_agent import ExecutionAgent
from agents.interaction_agent import InteractionAgent
from storage.state import TaskStore
from mq.queue import InMemoryEventBus


class ContentMarketingFlow:
    def __init__(self, store: TaskStore, bus: InMemoryEventBus):
        self.store = store
        self.bus = bus
        self.strategy = StrategyAgent()
        self.writer = ContentAgent()
        self.critic = CriticAgent()
        self.publisher = ExecutionAgent()
        self.monitor = InteractionAgent()

    async def run(self, task: Dict[str, Any], human_auto_approve: bool = True) -> Dict[str, Any]:
        task_id = task["task_id"]
        await self.store.set_status(task_id, "running")

        async def with_retry(
            name: str,
            fn: Callable[[], Any],
            retries: int = 2,
            rollback: Optional[Callable[[], Any]] = None,
        ) -> Tuple[bool, Any]:
            last_err: Optional[Exception] = None
            for attempt in range(retries + 1):
                try:
                    result = await fn()
                    return True, result
                except Exception as e:  # noqa: BLE001 - controlled retry wrapper
                    last_err = e
                    if attempt < retries:
                        await asyncio.sleep(0.2 * (attempt + 1))
                        continue
            if rollback is not None:
                try:
                    await rollback()
                except Exception:
                    pass
            return False, {"error": f"{name} failed: {last_err}"}

        # Plan
        ok, plan = await with_retry("strategy", lambda: self.strategy.plan(task))
        if not ok:
            await self.store.set_status(task_id, "error")
            return plan
        await self.bus.emit({"type": "plan.created", "task_id": task_id, "plan": plan})

        # Write
        ok, draft = await with_retry("writer", lambda: self.writer.generate(task, plan))
        if not ok:
            await self.store.set_status(task_id, "error")
            return draft
        await self.bus.emit({"type": "content.draft", "task_id": task_id, "draft": draft})

        # Critic
        ok, improved = await with_retry("critic", lambda: self.critic.refine(task, draft))
        if not ok:
            await self.store.set_status(task_id, "error")
            return improved
        await self.bus.emit({"type": "content.refined", "task_id": task_id, "content": improved})

        # Human review conditional branch
        if not human_auto_approve:
            await self.store.set_status(task_id, "human_required")
            # In real system, wait for external approval event
            # Here we simulate approval
            await self.bus.emit({"type": "human.review.required", "task_id": task_id})
            await asyncio.sleep(0.1)
            await self.store.set_status(task_id, "running")

        # Publish with rollback
        async def publish_action():
            return await self.publisher.publish(task, improved)

        async def publish_rollback():
            await self.publisher.rollback(task)

        ok, publish_res = await with_retry(
            "publisher", publish_action, retries=2, rollback=publish_rollback
        )
        if not ok:
            await self.store.set_status(task_id, "error")
            return publish_res
        await self.bus.emit({"type": "content.published", "task_id": task_id, "result": publish_res})

        # Monitor
        ok, monitor_res = await with_retry(
            "monitor", lambda: self.monitor.analyze(task, publish_res)
        )
        if not ok:
            await self.store.set_status(task_id, "error")
            return monitor_res
        await self.bus.emit({"type": "content.analytics", "task_id": task_id, "data": monitor_res})

        await self.store.set_status(task_id, "success")
        return {
            "task_id": task_id,
            "final": {
                "plan": plan,
                "content": improved,
                "publish": publish_res,
                "monitor": monitor_res,
            },
        }


