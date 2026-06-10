"""
统一 AI 服务模块
提供通义千问大模型的统一调用接口
"""
from .base import QwenAIService
from .grading import GradingService
from .study_assistant import StudyAssistantService

__all__ = ['QwenAIService', 'GradingService', 'StudyAssistantService']
