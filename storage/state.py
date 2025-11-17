import asyncio
from typing import Any, Dict, Optional


class TaskStore:
    def __init__(self) -> None:
        self._tasks: Dict[str, Dict[str, Any]] = {}

    async def upsert(self, task: Dict[str, Any]) -> None:
        self._tasks[task["task_id"]] = task

    async def set_status(self, task_id: str, status: str) -> None:
        if task_id not in self._tasks:
            self._tasks[task_id] = {"task_id": task_id, "meta": {}}
        self._tasks[task_id].setdefault("meta", {})["status"] = status

    async def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        await asyncio.sleep(0)  # keep async signature
        return self._tasks.get(task_id)


