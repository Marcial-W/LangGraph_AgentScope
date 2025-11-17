# -*- coding: utf-8 -*-
"""
策略生成智能体 (Strategy Agent)
负责制定话题、传播节奏、账号矩阵角色分配、目标指标设定等
"""

from agentscope.agent import AgentBase
from agentscope.message import Msg
from typing import Dict, List, Any
import json


class StrategyAgent(AgentBase):
    """策略生成智能体 - 担任策划组的角色"""
    
    def __init__(self, name: str = "strategy_agent"):
        super().__init__()
        self.name = name
        self.strategies = []
        
    async def reply(self, message: Msg) -> Msg:
        """处理策略生成请求"""
        content = message.content if isinstance(message.content, str) else str(message.content)
        
        # 分析请求类型
        if "热点" in content or "趋势" in content:
            response = self._analyze_trends(content)
        elif "目标受众" in content or "用户画像" in content:
            response = self._identify_target_audience(content)
        elif "任务包" in content or "任务分配" in content:
            response = self._generate_task_packages(content)
        else:
            response = self._generate_strategy(content)
            
        return Msg(
            role="assistant",
            name=self.name,
            content=response
        )
    
    def _analyze_trends(self, content: str) -> str:
        """热点趋势预测"""
        # 模拟趋势分析
        trends = {
            "当前热点": ["AI技术", "绿色生活", "健康养生"],
            "预测趋势": ["智能家居", "虚拟现实", "可持续发展"],
            "建议切入点": "结合品牌特色与AI技术热点，打造科技感内容"
        }
        return f"📊 趋势分析结果：\n{json.dumps(trends, ensure_ascii=False, indent=2)}"
    
    def _identify_target_audience(self, content: str) -> str:
        """目标受众识别"""
        audience_profile = {
            "主要群体": "25-35岁都市白领",
            "兴趣标签": ["科技", "生活品质", "自我提升"],
            "活跃平台": ["微博", "小红书", "抖音"],
            "内容偏好": "实用性强、视觉效果好的短视频"
        }
        return f"🎯 目标受众画像：\n{json.dumps(audience_profile, ensure_ascii=False, indent=2)}"
    
    def _generate_task_packages(self, content: str) -> str:
        """任务包生成"""
        tasks = [
            {
                "任务ID": "TASK001",
                "任务类型": "热点话题引导",
                "执行账号": ["主账号A", "矩阵账号B"],
                "发布时间": "20:00-21:00黄金时段",
                "内容要求": "围绕AI应用场景，展示产品优势"
            },
            {
                "任务ID": "TASK002", 
                "任务类型": "互动引流",
                "执行账号": ["互动账号C", "互动账号D"],
                "执行动作": "评论区互动、转发扩散",
                "KPI指标": "互动率>5%，转发量>100"
            }
        ]
        return f"📋 任务包已生成：\n{json.dumps(tasks, ensure_ascii=False, indent=2)}"
    
    def _generate_strategy(self, content: str) -> str:
        """生成综合策略"""
        strategy = {
            "策略主题": "AI赋能美好生活",
            "传播节奏": {
                "预热期": "3天软性内容铺垫",
                "引爆期": "2天集中发布核心内容", 
                "维护期": "5天持续互动维护热度"
            },
            "账号矩阵": {
                "主账号": "品牌官方发声，权威内容",
                "KOL账号": "专业解读，深度分析",
                "素人账号": "真实体验，用户视角"
            },
            "预期指标": {
                "曝光量": "100万+",
                "互动率": "8%",
                "转化率": "2%"
            }
        }
        
        self.strategies.append(strategy)
        return f"🎯 营销策略方案：\n{json.dumps(strategy, ensure_ascii=False, indent=2)}"
