import asyncio
import os
import sys
import uuid

from orchestrator.content_marketing_flow import ContentMarketingFlow
from storage.audit import AuditLog
from storage.postgres import run_migrations
from storage.state import TaskStore
from mq.queue import InMemoryEventBus, RedisEventBus
from monitoring.metrics import Metrics

# Windows 事件循环兼容性修复
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def _make_event_bus():
    bus_type = os.getenv("EVENT_BUS", "memory").lower()
    if bus_type == "redis":
        return RedisEventBus(url=os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    return InMemoryEventBus()


async def main() -> None:
    await run_migrations()
    store = TaskStore()
    bus = _make_event_bus()
    metrics = Metrics()
    audit = AuditLog()
    bus.subscribe(metrics.handle_event)
    bus.subscribe(audit.record_event)

    flow = ContentMarketingFlow(store, bus)
    task = {
        "task_id": str(uuid.uuid4()),
        "type": "content.generate",
        "payload": {"topic": "AI在营销中的应用", "style": "科普风格", "platform": "twitter"},
        "meta": {"retries": 0, "status": "pending"},
    }
    await store.upsert(task)

    result = await flow.run(task, human_auto_approve=True)
    print({"result": result})


if __name__ == "__main__":
    asyncio.run(main())
