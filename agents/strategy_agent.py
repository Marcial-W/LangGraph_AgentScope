import uuid
from typing import Any, Dict

from llm.client import LLMClient


class StrategyAgent:
    def __init__(self) -> None:
        self.client = LLMClient()

    async def plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        payload = task.get("payload", {})
        messages = [
            {"role": "system", "content": "You are StrategyAgent. Plan → Act → Critic → Fix → Output."},
            {"role": "user", "content": f"Create a concise content plan. Topic={payload.get('topic')}, style={payload.get('style')}."},
        ]
        res = await self.client.chat(messages)
        return {
            "plan_id": str(uuid.uuid4()),
            "steps": ["outline", "write", "critique", "revise", "publish"],
            "summary": res["content"],
            "schema": "strategy.plan.v1",
        }


