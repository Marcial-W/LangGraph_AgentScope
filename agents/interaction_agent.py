from typing import Any, Dict


class InteractionAgent:
    async def analyze(self, task: Dict[str, Any], publish_result: Dict[str, Any]) -> Dict[str, Any]:
        platform = publish_result.get("platform", "mock")
        post_id = publish_result.get("post_id", "mock-0")
        # Simulate analytics
        return {
            "platform": platform,
            "post_id": post_id,
            "metrics": {"views": 123, "likes": 12, "comments": 3, "shares": 1},
            "schema": "monitor.analytics.v1",
        }


