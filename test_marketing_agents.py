# -*- coding: utf-8 -*-
"""测试营销智能体系统 - 在项目根目录运行"""

import sys
import os
import asyncio

# 添加 agentscope 源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agentscope", "src"))

# 添加自定义智能体路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agentscope"))

from agentscope.message import Msg
from agent_all import StrategyAgent, ContentAgent, ExecutionAgent, InteractionAgent

async def test_all_agents():
    """测试所有营销智能体"""
    print("=== 营销智能体系统测试 ===\n")
    
    # 1. 策略生成智能体
    print("【1. 策略生成智能体】")
    strategy_agent = StrategyAgent(name="营销策略师")
    msg = Msg("user", "请分析AI产品的热点趋势和目标受众", "user")
    response = await strategy_agent.reply(msg)
    print(response.content)
    print("\n" + "="*60 + "\n")
    
    # 2. 内容生成智能体
    print("【2. 内容生成智能体】")
    content_agent = ContentAgent(name="内容创作者")
    msg = Msg("user", "为小红书生成AI产品推广图文", "user")
    response = await content_agent.reply(msg)
    print(response.content)
    print("\n" + "="*60 + "\n")
    
    # 3. 调度执行智能体
    print("【3. 调度执行智能体】")
    execution_agent = ExecutionAgent(name="执行调度员")
    msg = Msg("user", "请分配任务并监控执行进度", "user")
    response = await execution_agent.reply(msg)
    print(response.content)
    print("\n" + "="*60 + "\n")
    
    # 4. 互动智能体
    print("【4. 互动智能体】")
    interaction_agent = InteractionAgent(name="社区运营官")
    msg = Msg("user", "用户评论'产品很棒'，请生成合适的互动评论", "user")
    response = await interaction_agent.reply(msg)
    print(response.content)
    
    print("\n=== 测试完成！所有智能体运行正常 ===")

if __name__ == "__main__":
    try:
        asyncio.run(test_all_agents())
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        import traceback
        traceback.print_exc()
