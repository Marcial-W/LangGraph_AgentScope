from typing import Any, Dict

from llm.client import LLMClient


class CriticAgent:
    def __init__(self) -> None:
        self.client = LLMClient()

    async def refine(self, task: Dict[str, Any], draft: Dict[str, Any]) -> Dict[str, Any]:
        payload = task.get("payload", {})
        messages = [
            {"role": "system", "content": "You are CriticAgent. Proofread and improve tone/style."},
            {"role": "user", "content": f"Refine the content for platform={payload.get('platform')}"},
            {"role": "user", "content": f"Draft: {draft.get('body', '')}"},
        ]
        res = await self.client.chat(messages)
        return {
            "title": draft.get("title", "Refined"),
            "body": res["content"],
            "tags": draft.get("tags", []),
            "schema": "content.refined.v1",
        }


