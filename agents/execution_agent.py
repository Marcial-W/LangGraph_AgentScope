from typing import Any, Dict


class ExecutionAgent:
    def __init__(self) -> None:
        self._published = {}

    async def publish(self, task: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
        task_id = task["task_id"]
        result = {
            "platform": task.get("payload", {}).get("platform", "mock"),
            "post_id": f"mock-{task_id}",
            "status": "posted",
            "schema": "publish.result.v1",
        }
        self._published[task_id] = result
        return result

    async def rollback(self, task: Dict[str, Any]) -> None:
        task_id = task["task_id"]
        if task_id in self._published:
            del self._published[task_id]


