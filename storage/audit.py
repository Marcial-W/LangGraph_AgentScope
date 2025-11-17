from typing import Any, Dict, List


class AuditLog:
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []

    def append(self, event: Dict[str, Any]) -> None:
        self._events.append(event)

    def all(self) -> List[Dict[str, Any]]:
        return list(self._events)


