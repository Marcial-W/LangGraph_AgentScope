import asyncio
import os
import uuid

import psycopg
import pytest

from orchestrator.content_marketing_flow import ContentMarketingFlow
from storage.postgres import run_migrations
from storage.state import TaskStore
from mq.queue import InMemoryEventBus


def _postgres_available() -> bool:
    dsn = os.getenv("POSTGRES_DSN", "postgresql://app:app@localhost:5432/appdb")
    try:
        with psycopg.connect(dsn, connect_timeout=1):
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _postgres_available(), reason="Postgres not available for workflow test"
)


def test_workflow_end_to_end_success():
    async def run():
        await run_migrations()
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


