from typing import Any, Dict

from llm.client import LLMClient


class ContentAgent:
    def __init__(self) -> None:
        self.client = LLMClient()

    async def generate(self, task: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        payload = task.get("payload", {})
        messages = [
            {"role": "system", "content": "You are ContentAgent. Generate article/script/marketing copy."},
            {"role": "user", "content": f"Write content for topic={payload.get('topic')} with style={payload.get('style')}."},
            {"role": "user", "content": f"Plan summary: {plan.get('summary', '')}"},
        ]
        res = await self.client.chat(messages)
        return {
            "title": f"{payload.get('topic', 'Untitled')} - Draft",
            "body": res["content"],
            "tags": [payload.get("platform", "generic")],
            "schema": "content.draft.v1",
        }


