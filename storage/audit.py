import json
from typing import Any, Dict, List, Optional

from storage.postgres import PostgresClient


class AuditLog:
    def __init__(self, dsn: str | None = None) -> None:
        self.client = PostgresClient(dsn=dsn)

    async def record_event(self, event: Dict[str, Any]) -> None:
        query = """
            INSERT INTO task_events (task_id, event_type, payload)
            VALUES (%s, %s, %s::jsonb)
        """
        await self.client.execute(
            query,
            (
                event.get("task_id"),
                event.get("type", "unknown"),
                json.dumps(event, ensure_ascii=False),
            ),
        )

    async def list_events(self, task_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        base = "SELECT task_id, event_type, payload, created_at FROM task_events"
        params: List[Any] = []
        if task_id:
            base += " WHERE task_id = %s"
            params.append(task_id)
        base += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        rows = await self.client.fetch(base, params)
        return rows

