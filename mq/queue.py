import asyncio
import contextlib
import json
import os
from typing import Any, Awaitable, Callable, Dict, List, Optional

try:  # Optional dependency：redis.asyncio
    import redis.asyncio as redis_async  # type: ignore
except Exception:  # pragma: no cover - redis 依赖可选
    redis_async = None


class InMemoryEventBus:
    def __init__(self) -> None:
        self._subscribers: List[Callable[[Dict[str, Any]], Awaitable[None]]] = []

    def subscribe(self, cb: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        self._subscribers.append(cb)

    async def emit(self, event: Dict[str, Any]) -> None:
        await asyncio.gather(*(cb(event) for cb in self._subscribers))


class RedisEventBus:
    """
    使用 Redis Pub/Sub 的事件总线。若未安装 redis.asyncio，将在初始化时抛错。
    """

    def __init__(
        self,
        url: str | None = None,
        channel: str = "agent-events",
        auto_listen: bool = True,
    ) -> None:
        if redis_async is None:
            raise RuntimeError("请先安装 `redis` 依赖以启用 RedisEventBus。")
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.channel = channel
        self._redis = redis_async.from_url(self.url, decode_responses=True)
        self._subscribers: List[Callable[[Dict[str, Any]], Awaitable[None]]] = []
        self._listener_task: Optional[asyncio.Task[None]] = None
        self._auto_listen = auto_listen

    def subscribe(self, cb: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        self._subscribers.append(cb)
        if self._auto_listen and self._listener_task is None:
            self._listener_task = asyncio.create_task(self._listen_loop())

    async def emit(self, event: Dict[str, Any]) -> None:
        payload = json.dumps(event, ensure_ascii=False)
        await self._redis.publish(self.channel, payload)

    async def close(self) -> None:
        if self._listener_task:
            self._listener_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._listener_task
        await self._redis.close()

    async def _listen_loop(self) -> None:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self.channel)
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                data = json.loads(message["data"])
                await asyncio.gather(*(cb(data) for cb in self._subscribers))
        finally:
            await pubsub.unsubscribe(self.channel)
            await pubsub.close()

