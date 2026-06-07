"""
LLM 大模型调用服务层
提供统一的 LLM 调用接口，支持流式输出
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from core import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 调用服务"""
    
    def __init__(self):
        """初始化 LLM 客户端"""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            streaming=True
        )
        logger.info(f"✅ LLM 初始化完成：{settings.LLM_MODEL_NAME}")
    
    def chat(self, messages: list, system_prompt: str = None) -> str:
        """
        简单对话
        
        Args:
            messages: 对话历史列表
            system_prompt: 系统提示词（可选）
            
        Returns:
            LLM 回答
        """
        try:
            # 构建消息列表
            chat_messages = []
            
            # 添加系统提示
            if system_prompt:
                chat_messages.append(SystemMessage(content=system_prompt))
            
            # 添加历史消息
            for msg in messages:
                if isinstance(msg, dict):
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        chat_messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        chat_messages.append(AIMessage(content=content))
                else:
                    chat_messages.append(msg)
            
            # 调用 LLM
            response = self.llm.invoke(chat_messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM 对话失败：{e}")
            raise
    
    def chat_stream(self, messages: list, system_prompt: str = None):
        """
        流式对话（生成器）
        
        Args:
            messages: 对话历史列表
            system_prompt: 系统提示词
            
        Yields:
            LLM 回答的文本片段
        """
        try:
            # 构建消息列表
            chat_messages = []
            
            if system_prompt:
                chat_messages.append(SystemMessage(content=system_prompt))
            
            for msg in messages:
                if isinstance(msg, dict):
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        chat_messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        chat_messages.append(AIMessage(content=content))
                else:
                    chat_messages.append(msg)
            
            # 流式调用 LLM
            for chunk in self.llm.stream(chat_messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f"LLM 流式对话失败：{e}")
            yield f"错误：{str(e)}"
    
    def extract_json(self, prompt: str, schema: dict = None) -> dict:
        """
        提取结构化 JSON 数据
        
        Args:
            prompt: 提示词
            schema: JSON Schema（可选）
            
        Returns:
            解析后的 JSON 数据
        """
        try:
            system_prompt = "请返回 JSON 格式的回答，不要包含其他内容"
            if schema:
                system_prompt += f"\nJSON Schema: {schema}"
            
            response = self.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=system_prompt
            )
            
            # 尝试解析 JSON
            import json
            try:
                # 清理响应文本
                response = response.strip()
                if response.startswith("```json"):
                    response = response.replace("```json", "").replace("```", "").strip()
                return json.loads(response)
            except Exception as parse_err:
                logger.error(f"JSON 解析失败：{parse_err}")
                return {}
        except Exception as e:
            logger.error(f"提取 JSON 失败：{e}")
            return {}


# 全局 LLM 服务实例
llm_service = LLMService()
