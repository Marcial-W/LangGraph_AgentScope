import asyncio
import uuid

from agents.strategy_agent import StrategyAgent
from agents.content_agent import ContentAgent
from agents.critic_agent import CriticAgent


def test_agent_output_has_schema_fields():
    async def run():
        task = {
            "task_id": str(uuid.uuid4()),
            "payload": {"topic": "Test", "style": "casual", "platform": "twitter"},
        }
        plan = await StrategyAgent().plan(task)
        assert plan["schema"] == "strategy.plan.v1"

        draft = await ContentAgent().generate(task, plan)
        assert draft["schema"] == "content.draft.v1"

        refined = await CriticAgent().refine(task, draft)
        assert refined["schema"] == "content.refined.v1"

    asyncio.run(run())


