import asyncio
import uuid

from orchestrator.content_marketing_flow import ContentMarketingFlow
from storage.state import TaskStore
from mq.queue import InMemoryEventBus


def test_workflow_end_to_end_success():
    async def run():
        store = TaskStore()
        bus = InMemoryEventBus()
        flow = ContentMarketingFlow(store, bus)
        task = {
            "task_id": str(uuid.uuid4()),
            "type": "content.generate",
            "payload": {"topic": "Retry", "style": "short", "platform": "twitter"},
            "meta": {"retries": 0, "status": "pending"},
        }
        await store.upsert(task)
        res = await flow.run(task)
        assert res["task_id"] == task["task_id"]
        final = res["final"]
        assert "plan" in final and "content" in final and "publish" in final and "monitor" in final

    asyncio.run(run())


