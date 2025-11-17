from typing import Any, Dict, List


class Metrics:
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []

    async def handle_event(self, event: Dict[str, Any]) -> None:
        self._events.append(event)

    def all(self) -> List[Dict[str, Any]]:
        return list(self._events)


