import json
from typing import Any, Dict, Optional

from storage.postgres import PostgresClient


class TaskStore:
    def __init__(self, dsn: str | None = None) -> None:
        self.client = PostgresClient(dsn=dsn)

    async def upsert(self, task: Dict[str, Any]) -> None:
        task_id = task["task_id"]
        payload = task.get("payload", {})
        meta = task.get("meta", {})
        status = meta.get("status", "pending")
        query = """
            INSERT INTO task_state (task_id, task_type, payload, meta, status)
            VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
            ON CONFLICT (task_id) DO UPDATE
            SET task_type = EXCLUDED.task_type,
                payload = EXCLUDED.payload,
                meta = EXCLUDED.meta,
                status = EXCLUDED.status,
                updated_at = NOW();
        """
        await self.client.execute(
            query,
            (task_id, task.get("type"), json.dumps(payload), json.dumps(meta), status),
        )

    async def set_status(self, task_id: str, status: str) -> None:
        existing = await self.get(task_id) or {"task_id": task_id, "type": None, "payload": {}, "meta": {}}
        meta = dict(existing.get("meta") or {})
        meta["status"] = status
        updated_task = {
            "task_id": task_id,
            "type": existing.get("type") or "unknown",
            "payload": existing.get("payload") or {},
            "meta": meta,
        }
        await self.upsert(updated_task)

    async def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT task_id, task_type, payload, meta, status
            FROM task_state WHERE task_id = %s
        """
        rows = await self.client.fetch(query, (task_id,))
        if not rows:
            return None
        row = rows[0]
        meta = row.get("meta") or {}
        meta["status"] = row.get("status")
        return {
            "task_id": row["task_id"],
            "type": row.get("task_type"),
            "payload": row.get("payload") or {},
            "meta": meta,
        }

