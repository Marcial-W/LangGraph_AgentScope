import os
import time
from typing import Any, Dict, List, Tuple

from prometheus_client import Counter, Gauge, start_http_server

_started_servers: set[Tuple[str, int]] = set()
_STATUS_TO_VALUE = {"pending": 0, "running": 1, "success": 2, "human_required": 0.5, "error": -1}

EVENT_COUNTER = Counter("agent_events_total", "Total number of workflow events", ["event_type"])
EVENT_TS = Gauge("agent_event_timestamp", "Unix timestamp of last event by type", ["event_type"])
TASK_LAST_EVENT = Gauge("agent_task_last_event_timestamp", "Unix timestamp of last event per task", ["task_id"])
TASK_STATUS = Gauge(
    "agent_task_status_value",
    "Task status indicator (-1 error,0 pending,0.5 human_required,1 running,2 success)",
    ["task_id"],
)


def _ensure_server() -> None:
    host = os.getenv("PROMETHEUS_HOST", "0.0.0.0")
    port = int(os.getenv("PROMETHEUS_PORT", "9000"))
    key = (host, port)
    if key in _started_servers:
        return
    start_http_server(port, addr=host)
    _started_servers.add(key)


class Metrics:
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []
        _ensure_server()

    async def handle_event(self, event: Dict[str, Any]) -> None:
        self._events.append(event)
        event_type = event.get("type", "unknown")
        task_id = event.get("task_id")
        now = time.time()
        EVENT_COUNTER.labels(event_type).inc()
        EVENT_TS.labels(event_type).set(now)
        if task_id:
            TASK_LAST_EVENT.labels(task_id).set(now)
            status = event.get("status")
            if not status and isinstance(event.get("meta"), dict):
                status = event["meta"].get("status")
            if not status and isinstance(event.get("result"), dict):
                status = event["result"].get("status")
            if status:
                value = _STATUS_TO_VALUE.get(status, 0)
                TASK_STATUS.labels(task_id).set(value)

    def all(self) -> List[Dict[str, Any]]:
        return list(self._events)

