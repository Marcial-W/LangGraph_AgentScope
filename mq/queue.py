import asyncio
from typing import Any, Awaitable, Callable, Dict, List


class InMemoryEventBus:
    def __init__(self) -> None:
        self._subscribers: List[Callable[[Dict[str, Any]], Awaitable[None]]] = []

    def subscribe(self, cb: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        self._subscribers.append(cb)

    async def emit(self, event: Dict[str, Any]) -> None:
        await asyncio.gather(*(cb(event) for cb in self._subscribers))


