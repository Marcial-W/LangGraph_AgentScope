import asyncio
import uuid

from orchestrator.content_marketing_flow import ContentMarketingFlow
from storage.state import TaskStore
from mq.queue import InMemoryEventBus
from monitoring.metrics import Metrics


async def main() -> None:
    store = TaskStore()
    bus = InMemoryEventBus()
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


