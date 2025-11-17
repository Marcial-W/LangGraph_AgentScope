# -*- coding: utf-8 -*-
"""
营销智能体的 LangGraph 工作流示例
"""

import sys
import os
import asyncio

# 添加必要的路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agentscope", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agentscope"))

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from agentscope.message import Msg
from agent_all import StrategyAgent, ContentAgent, ExecutionAgent, InteractionAgent


class MarketingState(TypedDict):
    """营销工作流的状态定义"""
    task: str  # 用户任务描述
    strategy: Dict[str, Any]  # 策略分析结果
    content: List[Dict[str, str]]  # 生成的内容列表
    execution_plan: Dict[str, Any]  # 执行计划
    interaction_plan: Dict[str, Any]  # 互动方案
    final_output: str  # 最终输出


def build_marketing_workflow():
    """构建营销智能体协作工作流"""
    
    # 创建智能体实例
    strategy_agent = StrategyAgent(name="策略师")
    content_agent = ContentAgent(name="创作者")
    execution_agent = ExecutionAgent(name="调度员")
    interaction_agent = InteractionAgent(name="运营官")
    
    # 定义节点函数
    async def analyze_strategy(state: MarketingState) -> MarketingState:
        """策略分析节点"""
        msg = Msg("user", f"请为以下任务制定营销策略：{state['task']}", "user")
        response = await strategy_agent.reply(msg)
        state["strategy"] = {"result": response.content}
        return state
    
    async def generate_content(state: MarketingState) -> MarketingState:
        """内容生成节点"""
        msg = Msg("user", f"基于策略：{state['strategy']['result'][:100]}...，请生成营销内容", "user")
        response = await content_agent.reply(msg)
        state["content"] = [{"platform": "multi", "content": response.content}]
        return state
    
    async def plan_execution(state: MarketingState) -> MarketingState:
        """执行计划节点"""
        msg = Msg("user", "请为生成的内容制定发布执行计划", "user")
        response = await execution_agent.reply(msg)
        state["execution_plan"] = {"plan": response.content}
        return state
    
    async def design_interaction(state: MarketingState) -> MarketingState:
        """互动方案节点"""
        msg = Msg("user", "请制定内容发布后的互动运营方案", "user")
        response = await interaction_agent.reply(msg)
        state["interaction_plan"] = {"plan": response.content}
        return state
    
    def summarize_output(state: MarketingState) -> MarketingState:
        """汇总输出节点"""
        summary = f"""
🎯 营销方案汇总：

一、策略分析
{state['strategy']['result'][:200]}...

二、内容创作
{state['content'][0]['content'][:200]}...

三、执行计划
{state['execution_plan']['plan'][:200]}...

四、互动运营
{state['interaction_plan']['plan'][:200]}...

✅ 方案制定完成，可以开始执行！
        """
        state["final_output"] = summary
        return state
    
    # 构建工作流
    workflow = StateGraph(MarketingState)
    
    # 添加节点
    workflow.add_node("strategy", analyze_strategy)
    workflow.add_node("content", generate_content)
    workflow.add_node("execution", plan_execution)
    workflow.add_node("interaction", design_interaction)
    workflow.add_node("summarize", summarize_output)
    
    # 定义流程
    workflow.set_entry_point("strategy")
    workflow.add_edge("strategy", "content")
    workflow.add_edge("content", "execution")
    workflow.add_edge("execution", "interaction")
    workflow.add_edge("interaction", "summarize")
    workflow.add_edge("summarize", END)
    
    return workflow.compile()


async def run_marketing_campaign(task: str):
    """运行营销活动"""
    workflow = build_marketing_workflow()
    
    # 初始状态
    initial_state = {
        "task": task,
        "strategy": {},
        "content": [],
        "execution_plan": {},
        "interaction_plan": {},
        "final_output": ""
    }
    
    # 执行工作流
    result = await workflow.ainvoke(initial_state)
    
    return result["final_output"]


if __name__ == "__main__":
    # 测试工作流
    task = "为新上线的AI助手产品策划一次社交媒体营销活动"
    
    print(f"📢 营销任务：{task}\n")
    print("🚀 启动智能体工作流...\n")
    
    try:
        output = asyncio.run(run_marketing_campaign(task))
        print(output)
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        import traceback
        traceback.print_exc()
