import os
from typing import Any, Dict, List


class LLMClient:
    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Minimal async chat client.
        If QWEN_API_KEY exists, this is where real API integration should go.
        For MVP, we return a deterministic composed response for reproducibility.
        """
        api_key = os.getenv("QWEN_API_KEY", "")
        # Placeholder for real provider call
        user_parts = [m["content"] for m in messages if m.get("role") in ("user", "system")]
        content = " ".join(user_parts).strip()
        # Lightweight stylistic transformation to mimic LLM behavior
        content = f"[LLM:{'qwen' if api_key else 'local'}] {content}"
        return {
            "role": "assistant",
            "content": content,
            "usage": {"prompt_tokens": len(content.split()), "completion_tokens": 12},
            "provider": "qwen" if api_key else "local",
        }


