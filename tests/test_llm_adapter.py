import asyncio
from llm.client import LLMClient


def test_llm_client_chat_returns_dict():
    async def run():
        client = LLMClient()
        res = await client.chat([{"role": "user", "content": "hello world"}])
        assert isinstance(res, dict)
        assert res["role"] == "assistant"
        assert "content" in res

    asyncio.run(run())


