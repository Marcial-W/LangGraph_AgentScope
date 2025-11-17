import asyncio
import os
import uuid

from orchestrator.content_marketing_flow import ContentMarketingFlow
from storage.state import TaskStore
from mq.queue import InMemoryEventBus, RedisEventBus
from monitoring.metrics import Metrics


def _make_event_bus():
    bus_type = os.getenv("EVENT_BUS", "memory").lower()
    if bus_type == "redis":
        return RedisEventBus(url=os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    return InMemoryEventBus()


async def main() -> None:
    store = TaskStore()
    bus = _make_event_bus()
    metrics = Metrics()
    bus.subscribe(metrics.handle_event)

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

