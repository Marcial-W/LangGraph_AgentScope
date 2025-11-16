# -*- coding: utf-8 -*-
"""
互动智能体 (Interaction Agent)
专注于社区互动、评论、点赞、转发、私信等操作
"""

from agentscope.agent import Agent
from agentscope.message import Message
from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime


class InteractionAgent(Agent):
    """互动智能体 - 专注社区互动操作"""
    
    def __init__(self, name: str = "interaction_agent", **kwargs):
        super().__init__(name=name, **kwargs)
        self.interaction_templates = self._load_interaction_templates()
        self.emotion_keywords = {
            "positive": ["喜欢", "赞", "棒", "支持", "期待", "真好", "优秀"],
            "negative": ["差", "不好", "失望", "问题", "bug", "退货"],
            "neutral": ["怎么", "如何", "多少", "什么", "哪里", "咨询"]
        }
        self.interaction_history = []
        
    def reply(self, message: Message) -> Message:
        """处理互动请求"""
        content = message.content if isinstance(message.content, str) else str(message.content)
        
        # 解析互动需求
        if "评论" in content:
            response = self._handle_comment(content)
        elif "点赞" in content:
            response = self._handle_like(content)
        elif "转发" in content:
            response = self._handle_repost(content)
        elif "私信" in content:
            response = self._handle_dm(content)
        elif "情绪" in content or "情感" in content:
            response = self._analyze_emotion(content)
        else:
            response = self._auto_interact(content)
            
        return Message(
            role="assistant",
            name=self.name,
            content=response
        )
    
    def _load_interaction_templates(self) -> Dict[str, List[str]]:
        """加载互动模板库"""
        return {
            "positive_comments": [
                "太赞了！正是我需要的～",
                "感谢分享，已经收藏啦！❤️",
                "这个功能真的很实用，期待更多更新！",
                "用了一段时间，体验真的很棒👍",
                "终于找到了合适的解决方案，感谢！"
            ],
            "question_comments": [
                "请问这个支持XX功能吗？",
                "想了解一下具体的使用场景～",
                "有没有详细的教程呢？",
                "小白能上手吗？求指导！",
                "和其他产品相比有什么优势呢？"
            ],
            "repost_texts": [
                "这个真的很实用，分享给需要的朋友们～",
                "马住！有时间仔细研究一下",
                "转发收藏，说不定以后用得上",
                "好东西要分享，推荐给大家！",
                "Get到新技能，转发mark一下"
            ],
            "dm_templates": [
                "您好！看到您的分享很感兴趣，想了解更多细节～",
                "Hi～刚看到你的帖子，有几个问题想请教一下",
                "你好呀！产品看起来很不错，能详细介绍一下吗？"
            ]
        }
    
    def _handle_comment(self, request: str) -> str:
        """处理评论生成"""
        # 分析评论上下文
        context_emotion = self._detect_emotion(request)
        
        comment_strategy = {
            "目标帖子": "AI产品测评帖",
            "情感判断": context_emotion,
            "评论策略": "真实、有价值、引导正向讨论"
        }
        
        # 根据情感选择合适的评论
        if context_emotion == "positive":
            comments = random.sample(self.interaction_templates["positive_comments"], 3)
        elif context_emotion == "negative":
            comments = [
                "理解您的困扰，我们会认真改进的～",
                "感谢您的反馈！能具体说说遇到的问题吗？",
                "抱歉给您带来不好的体验，我们马上核查处理！"
            ]
        else:
            comments = random.sample(self.interaction_templates["question_comments"], 3)
            
        result = {
            "评论方案": comment_strategy,
            "推荐评论": comments,
            "发布建议": "间隔10-30分钟发布，避免刷屏"
        }
        
        self.interaction_history.append({
            "type": "comment",
            "time": datetime.now(),
            "content": comments[0]
        })
        
        return f"💬 评论互动方案：\n{json.dumps(result, ensure_ascii=False, indent=2)}"
    
    def _handle_like(self, request: str) -> str:
        """处理点赞策略"""
        like_strategy = {
            "点赞目标": {
                "优先级1": "品牌相关正面内容",
                "优先级2": "目标用户群体的优质内容",
                "优先级3": "行业KOL的专业分享"
            },
            "点赞节奏": {
                "日均点赞": "30-50个",
                "时间分布": "分散在活跃时段",
                "账号分配": "多账号轮流执行"
            },
            "注意事项": [
                "避免短时间大量点赞",
                "选择真实有价值的内容",
                "配合适当的评论互动"
            ]
        }
        
        return f"👍 点赞策略：\n{json.dumps(like_strategy, ensure_ascii=False, indent=2)}"
    
    def _handle_repost(self, request: str) -> str:
        """处理转发策略"""
        repost_plan = {
            "转发内容筛选": {
                "必转": "品牌官方重要发布",
                "优先转": "正面用户反馈、专业测评",
                "选择转": "行业趋势、相关热点"
            },
            "转发文案": random.sample(self.interaction_templates["repost_texts"], 3),
            "执行要点": {
                "添加个人观点": "让转发更真实",
                "适当@好友": "扩大传播范围",
                "配合话题标签": "增加曝光机会"
            }
        }
        
        return f"🔄 转发方案：\n{json.dumps(repost_plan, ensure_ascii=False, indent=2)}"
    
    def _handle_dm(self, request: str) -> str:
        """处理私信互动"""
        dm_strategy = {
            "私信场景": [
                "潜在客户咨询",
                "售后问题处理",
                "KOL合作洽谈"
            ],
            "回复模板": {
                "咨询类": "您好！感谢关注～针对您的问题...",
                "合作类": "Hi！看到您的私信了，关于合作...",
                "投诉类": "非常抱歉给您带来困扰，我们马上..."
            },
            "回复原则": [
                "2小时内响应",
                "保持专业友好",
                "及时转人工处理复杂问题"
            ]
        }
        
        return f"✉️ 私信互动方案：\n{json.dumps(dm_strategy, ensure_ascii=False, indent=2)}"
    
    def _analyze_emotion(self, content: str) -> str:
        """情绪分析和回复建议"""
        emotion = self._detect_emotion(content)
        
        emotion_response = {
            "情绪识别": emotion,
            "回复策略": {
                "positive": {
                    "基调": "感谢、鼓励、引导深入",
                    "示例": "太开心看到您的认可！期待您的更多分享～"
                },
                "negative": {
                    "基调": "理解、解决、挽回",
                    "示例": "非常理解您的心情，我们这就为您解决！"
                },
                "neutral": {
                    "基调": "专业、详细、引导",
                    "示例": "感谢您的提问！具体来说..."
                }
            }[emotion],
            "风险提示": "负面情绪需要及时人工介入"
        }
        
        return f"😊 情绪分析结果：\n{json.dumps(emotion_response, ensure_ascii=False, indent=2)}"
    
    def _auto_interact(self, request: str) -> str:
        """自动互动综合方案"""
        auto_plan = {
            "互动目标": "提升品牌活跃度和用户粘性",
            "日常任务": {
                "浏览点赞": "每日30-50个相关内容",
                "评论互动": "10-20条有价值评论",
                "转发分享": "3-5条优质内容",
                "私信回复": "及时响应所有咨询"
            },
            "智能特性": {
                "行为模拟": "模仿真实用户互动习惯",
                "时间随机": "避免机械化操作",
                "内容个性化": "根据账号人设调整语气"
            },
            "效果预期": {
                "互动率提升": "20-30%",
                "用户好感度": "显著提升",
                "转化效果": "间接促进10%"
            }
        }
        
        return f"🤖 自动互动方案：\n{json.dumps(auto_plan, ensure_ascii=False, indent=2)}"
    
    def _detect_emotion(self, content: str) -> str:
        """检测内容情绪"""
        content_lower = content.lower()
        
        positive_count = sum(1 for word in self.emotion_keywords["positive"] if word in content)
        negative_count = sum(1 for word in self.emotion_keywords["negative"] if word in content)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
