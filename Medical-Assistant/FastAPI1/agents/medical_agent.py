"""
医疗助手多智能体系统 - 基于 LangGraph 实现
使用状态机和工作流管理多个专科智能体的协作
包含校验智能体：相关性判断、置信度评估、重试控制、流式输出
"""
from typing import TypedDict, List, Annotated, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from core import settings
from agents.tools.internal_medicine_tool import internal_medicine_tool
from agents.tools.general_medicine_tool import general_medicine_tool
from agents.tools.image_tool import image_search_tool
import logging
import re

from services.llmlingua_service import get_llmlingua_compressor

logger = logging.getLogger(__name__)


# ============================================================================
# 状态定义
# ============================================================================

class AgentState(TypedDict):
    """智能体状态"""
    messages: List[BaseMessage]
    question: str
    specialty: str
    answer: str
    images: list
    context: dict
    # 校验相关字段
    confidence: float
    retry_count: int
    is_relevant: bool
    is_validated: bool


# ============================================================================
# 专科智能体节点
# ============================================================================

class InternalMedicineNode:
    """内科智能体节点"""

    def __init__(self):
        logger.info("⏳ 正在加载 LLM 模型...")
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            streaming=True
        )
        logger.info("✅ LLM 模型加载完成")

        self.system_prompt = """你是内科专家。基于检索结果给出200字专业回答,明确药物/治疗方案。
声明:建议仅供参考,请遵医嘱。无关问题礼貌引导,无结果告知未发现。
最后追问1-2个具体症状。"""

        logger.info("✅ 内科智能体节点初始化完成")

    def process(self, state: AgentState) -> AgentState:
        """处理内科问题"""
        question = state["question"]
        messages = state["messages"]

        # 构建提示
        system_msg = HumanMessage(content=self.system_prompt)
        user_msg = HumanMessage(content=f"问题：{question}")

        # 调用工具获取信息
        tool_result = internal_medicine_tool.invoke({"query": question})

        # 判断检索结果是否为空
        documents = tool_result.get("documents", [])
        if not documents:
            return {
                "answer": "⚠️ 暂未检索到相关知识库文档，无法为您提供准确建议。建议您咨询专业医生或补充相关资料后再次提问。",
                "specialty": "internal_medicine",
                "messages": state["messages"] + [user_msg]
            }

        # 提取文档内容并始终压缩（移除条件判断）
        doc_contents = [doc.get("content_snippet", "") for doc in documents]
        compressor = get_llmlingua_compressor()
        compressed_docs = compressor.compress_for_retrieval(question, doc_contents, target_token=300)

        # LLM 总结（包含历史上下文）
        llm_messages = [system_msg] + messages + [user_msg, AIMessage(content=f"检索结果（已压缩）：{compressed_docs}"),
                                                  HumanMessage(content="请根据以上检索到的文档内容给出专业回答")]
        response = self.llm.invoke(llm_messages)
        return {
            "answer": response.content,
            "specialty": "internal_medicine",
            "messages": state["messages"] + [user_msg, response]
        }


class GeneralMedicineNode:
    """外科智能体节点"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            streaming=True
        )

        self.system_prompt = """你是外科专家。基于检索结果给出200字专业回答,明确手术方式/处置措施。
        声明:建议仅供参考,请遵医嘱。无关问题礼貌引导,无结果告知未发现。
        最后追问1-2个具体细节(如受伤时间、疼痛程度)。"""

    logger.info("✅ 外科智能体节点初始化完成")

    def process(self, state: AgentState) -> AgentState:
        """处理外科问题"""
        question = state["question"]
        messages = state["messages"]

        system_msg = HumanMessage(content=self.system_prompt)
        user_msg = HumanMessage(content=f"问题：{question}")

        tool_result = general_medicine_tool.invoke({"query": question})

        documents = tool_result.get("documents", [])
        if not documents:
            return {
                "answer": "⚠️ 暂未检索到相关知识库文档，无法为您提供准确建议。建议您咨询专业医生或补充相关资料后再次提问。",
                "specialty": "general_medicine",
                "messages": state["messages"] + [user_msg]
            }

        # 提取文档内容并压缩
        doc_contents = [doc.get("content_snippet", "") for doc in documents]
        compressor = get_llmlingua_compressor()
        compressed_docs = compressor.compress_for_retrieval(question, doc_contents, target_token=300)

        # LLM 总结（包含历史上下文）
        llm_messages = [system_msg] + messages + [user_msg, AIMessage(content=f"检索结果（已压缩）：{compressed_docs}"),
                                                  HumanMessage(content="请根据以上检索到的文档内容给出专业回答")]
        response = self.llm.invoke(llm_messages)

        return {
            "answer": response.content,
            "specialty": "general_medicine",
            "messages": state["messages"] + [user_msg, response]
        }


class ImagingNode:
    """医学影像智能体节点"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            streaming=True
        )

        self.system_prompt = """你是影像专家。基于检索结果给出200字影像学分析意见,明确诊断倾向。
        声明:建议仅供参考,请遵医嘱。无关问题礼貌引导,无结果告知未发现。
        最后追问1-2个临床信息(如检查目的、既往病史)。"""
        logger.info("✅ 医学影像智能体节点初始化完成")

    def process(self, state: AgentState) -> AgentState:
        """处理医学影像问题"""
        question = state["question"]
        messages = state["messages"]

        system_msg = HumanMessage(content=self.system_prompt)
        user_msg = HumanMessage(content=f"问题：{question}")

        # 调用影像检索工具（带日志）
        logger.info(f"🔍 开始检索影像：{question[:30]}...")
        tool_result = image_search_tool.invoke({"query_text": question})
        logger.info(f"✅ 影像检索完成")
        
        # 判断检索结果是否为空
        if isinstance(tool_result, dict) and 'images' in tool_result:
            images = tool_result.get('images', [])
        if not images:
            return {
                "answer": "⚠️ 暂未检索到相关知识库文档，无法为您提供准确建议。建议您咨询专业医生或补充相关资料后再次提问。",
                "specialty": "imaging",
                "images": [],
                "messages": state["messages"] + [user_msg]
            }
        # 提取并压缩检索到的内容
        if isinstance(tool_result, dict) and 'images' in tool_result:
            doc_contents = [img.get("url", "") + (img.get("filename", "")) for img in images]
            compressor = get_llmlingua_compressor()
            compressed_content = compressor.compress_for_retrieval(question, doc_contents,
                                                                                 target_token=300)
        else:
            compressed_content = str(images)

        # LLM 总结（包含历史上下文）
        llm_messages = [system_msg] + messages + [user_msg,
                                                    AIMessage(content=f"检索结果（已压缩）：{compressed_content}"),
                                                    HumanMessage(content="请根据以上检索到的文档内容给出专业回答")]
        response = self.llm.invoke(llm_messages)

        return {
            "answer": response.content,
            "specialty": "imaging",
            "images": images,
            "messages": state["messages"] + [user_msg, response]
        }



# ============================================================================
# 校验智能体节点
# ============================================================================

class ValidatorNode:
    """校验智能体节点 - 负责相关性判断、置信度评估、重试控制"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=0.1,  # 低温度保证评估稳定性
            streaming=False
        )
        logger.info("✅ 校验智能体节点初始化完成")

    def check_relevance(self, state: AgentState) -> AgentState:
        """检查问题是否与医疗健康相关"""
        question = state["question"]
        
        prompt = f"""请判断以下问题是否与医疗健康相关，只返回 JSON 格式：
        问题：{question}
        要求：
        - 如果与医疗健康相关，返回：{{"is_relevant": true}}
        - 如果不相关（如闲聊、技术问题、商业问题等），返回：{{"is_relevant": false}}
        
        示例：
        - "我最近头痛" → {{"is_relevant": true}}
        - "今天天气怎么样" → {{"is_relevant": false}}
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            is_relevant = "true" in response.content.lower()
            if not is_relevant:
                return {
                    "answer": f"抱歉，您的问题与医疗健康无关。作为医疗助手，我只能回答与医疗健康相关的问题。如果您有健康方面的疑问，我很乐意为您提供专业建议。",
                    "is_relevant": False,
                    "is_validated": True,
                    "confidence": 1.0,
                    "retry_count": 0
                }
        except:
            is_relevant = True
        
        return {
            "is_relevant": is_relevant,
            "retry_count": 0
        }

    def evaluate_and_validate(self, state: AgentState) -> AgentState:
        """评估回答置信度并决定是否通过"""
        answer = state.get("answer", "")
        question = state["question"]
        retry_count = state.get("retry_count", 0)
        
        MAX_RETRIES = 3
        CONFIDENCE_THRESHOLD = 0.8
        
        # 评估置信度
        prompt = f"""请评估以下回答的质量和置信度，只返回一个 0-1 之间的小数：

        问题：{question}
        回答：{answer[:500]}
        
        评估标准：
        - 0.0-0.5：回答与问题无关、未回答、或质量极差
        - 0.5-0.7：部分相关，但信息不完整或不够准确
        - 0.7-0.8：基本回答正确，但有少量遗漏
        - 0.8-1.0：回答准确、完整、专业
        
        只返回一个数字（如 0.85），不要其他内容。
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            numbers = re.findall(r'\d+\.\d+', response.content)
            if numbers:
                confidence = float(numbers[0])
                confidence = min(max(confidence, 0.0), 1.0)
            else:
                confidence = 0.5
        except:
            confidence = 0.5
        
        logger.info(f"📊 置信度评估：{confidence:.2f} (阈值: {CONFIDENCE_THRESHOLD}, 重试次数: {retry_count})")
        
        # 判断是否满足要求
        if confidence >= CONFIDENCE_THRESHOLD or retry_count >= MAX_RETRIES:
            # 通过校验
            return {
                "confidence": confidence,
                "is_validated": True,
                "retry_count": retry_count
            }
        else:
            # 需要重新检索
            return {
                "confidence": confidence,
                "is_validated": False,
                "retry_count": retry_count + 1
            }


# ============================================================================
# 分类器节点
# ============================================================================

class ClassifierNode:
    """问题分类器节点 - 判断问题属于哪个科室"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=0.1,  # 低温保证分类稳定性
            streaming=False
        )

        logger.info("✅ 分类器节点初始化完成")

    def classify(self, state: AgentState) -> AgentState:
        """分类问题到对应科室"""
        question = state["question"]

        classification_prompt = f"""
请判断以下医疗问题属于哪个科室，只返回一个关键词：
- 如果是内科：主要通过药物、生活方式干预等非侵入性手段治疗，示例：高血压吃药、糖尿病打胰岛素、感冒发烧、胃痛咳嗽、心脏病调理等，返回：internal
- 如果是外科：主要通过手术、缝合、复位等侵入性或操作性手段治疗，示例：骨折打石膏/开刀、阑尾炎切除、外伤缝合、肿瘤摘除、烧伤处理、急腹症等，返回：general
- 如果涉及影像科：涉及对 CT、X 光、MRI 等医学影像文件的分析和解读，返回：imaging

问题：{question}
科室：
"""
        response = self.llm.invoke([HumanMessage(content=classification_prompt)])
        specialty = response.content.strip().lower()

        # 默认返回内科
        if specialty not in ['internal', 'general', 'imaging']:
            specialty = 'internal'

        logger.info(f"问题分类：{specialty} | 问题：{question[:50]}...")

        return {"specialty": specialty}


# ============================================================================
# 路由函数
# ============================================================================

def route_after_relevance(state: AgentState) -> Literal["relevant", "irrelevant"]:
    """根据相关性判断路由"""
    if state.get("is_relevant") == False:
        return "irrelevant"
    return "relevant"

def route_after_specialty(state: AgentState) -> Literal["internal", "general", "imaging"]:
    """根据分类结果路由到对应节点"""
    specialty = state["specialty"]

    if specialty == 'general':
        return "general"
    elif specialty == 'imaging':
        return "imaging"
    else:
        return "internal"

def route_after_validation(state: AgentState) -> Literal["validated", "retry", "end"]:
    """根据校验结果路由"""
    if state.get("is_validated"):
        return "end"
    elif state.get("retry_count", 0) >= 3:
        return "end"
    else:
        return "retry"


# ============================================================================
# 协调器（使用 LangGraph）
# ============================================================================

class MedicalAgentCoordinator:
    """医疗多智能体协调器 - 基于 LangGraph 工作流"""

    def __init__(self):
        """初始化工作流"""
        logger.info("🚀 开始初始化多智能体工作流...")
        # 初始化各节点
        self.validator = ValidatorNode()
        self.classifier = ClassifierNode()
        self.internal_agent = InternalMedicineNode()
        self.general_agent = GeneralMedicineNode()
        self.imaging_agent = ImagingNode()

        # 构建状态图
        self._build_graph()

        logger.info("✅ LangGraph 多智能体工作流初始化完成")

    def _build_graph(self):
        """构建 LangGraph 工作流"""
        # 创建状态图
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("validator_relevance", self.validator.check_relevance)
        workflow.add_node("classifier", self.classifier.classify)
        workflow.add_node("internal", self.internal_agent.process)
        workflow.add_node("general", self.general_agent.process)
        workflow.add_node("imaging", self.imaging_agent.process)
        workflow.add_node("validator_confidence", self.validator.evaluate_and_validate)

        # 设置入口点
        workflow.set_entry_point("validator_relevance")

        # 相关性判断后的路由
        workflow.add_conditional_edges(
            "validator_relevance",
            route_after_relevance,
            {
                "irrelevant": END,  # 不相关直接结束
                "relevant": "classifier"
            }
        )

        # 分类后的路由
        workflow.add_conditional_edges(
            "classifier",
            route_after_specialty,
            {
                "internal": "internal",
                "general": "general",
                "imaging": "imaging"
            }
        )

        # 专科节点完成后进入置信度评估
        workflow.add_edge("internal", "validator_confidence")
        workflow.add_edge("general", "validator_confidence")
        workflow.add_edge("imaging", "validator_confidence")

        # 置信度评估后的路由
        workflow.add_conditional_edges(
            "validator_confidence",
            route_after_validation,
            {
                "validated": END,  # 通过校验，结束
                "retry": "classifier",  # 重新检索
                "end": END  # 达到最大重试次数
            }
        )

        # 编译工作流
        self.app = workflow.compile()

    def query_with_context(self, question: str, context_messages: list = None, image_data: str = None, context: dict = None) -> dict:
        """
        带上下文的查询接口

        Args:
            question: 用户问题
            context_messages: 历史对话上下文
            image_data: 可选的图片数据
            context: 上下文信息

        Returns:
            智能体响应
        """
        try:
            # 1. 限制最大消息条数（例如：最多保留最近 10 条）
            MAX_HISTORY_MESSAGES = 16
            if context_messages and len(context_messages) > MAX_HISTORY_MESSAGES:
                logger.info(f"✂️ 历史消息过多，截断保留最近 {MAX_HISTORY_MESSAGES} 条")
                context_messages = context_messages[-MAX_HISTORY_MESSAGES:]

            # 2. 压缩历史对话上下文（如果存在且超过 4 条）
            compressed_messages = context_messages or []
            if context_messages and len(context_messages) > 4:
                logger.info(f"🗜️ 开始压缩对话历史：{len(context_messages)} 条消息")
                compressor = get_llmlingua_compressor()
                compressed_messages = compressor.compress_messages(
                    context_messages,
                    target_token=500
                )
                logger.info(f"✅ 对话历史压缩完成：{len(context_messages)} → {len(compressed_messages)} 条")

            # 初始状态，使用压缩后的历史消息
            initial_state = {
                "messages": compressed_messages,
                "question": question,
                "specialty": "",
                "answer": "",
                "images": [],
                "context": context or {},
                "confidence": 0.0,
                "retry_count": 0,
                "is_relevant": True,
                "is_validated": False
            }

            # 运行工作流
            result = self.app.invoke(initial_state)

            return {
                "answer": result["answer"],
                "specialty": result.get("specialty", "unknown"),
                "images": result.get("images", []),
                "messages": result["messages"],
                "confidence": result.get("confidence", 0.0),
                "retry_count": result.get("retry_count", 0),
                "is_relevant": result.get("is_relevant", True)
            }

        except Exception as e:
            logger.error(f"工作流执行失败：{e}")
            return {
                "answer": f"抱歉，处理您的问题时出现错误：{str(e)}",
                "specialty": "error",
                "error": str(e),
                "messages": []
            }

    def query(self, question: str, image_data: str = None, context: dict = None) -> dict:
        """
        统一查询接口

        Args:
            question: 用户问题
            image_data: 可选的图片数据
            context: 上下文信息

        Returns:
            智能体响应
        """
        return self.query_with_context(question, context_messages=None, image_data=image_data, context=context)

    def chat_stream(self, question: str, context_messages: list = None):
        """
        流式对话接口

        Args:
            question: 用户问题
            context_messages: 历史对话上下文

        Yields:
            文本片段
        """
        try:
            raw_context_messages = context_messages or []
            context_messages = []
            for msg in raw_context_messages:
                if isinstance(msg, BaseMessage):
                    context_messages.append(msg)
                    continue
                role = msg.get("role", "user") if isinstance(msg, dict) else "user"
                content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
                if isinstance(content, list) and content:
                    content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
                if role == "assistant":
                    context_messages.append(AIMessage(content=str(content)))
                else:
                    context_messages.append(HumanMessage(content=str(content)))

            initial_state = {
                "messages": context_messages,
                "question": question,
                "specialty": "",
                "answer": "",
                "images": [],
                "context": {},
                "confidence": 0.0,
                "retry_count": 0,
                "is_relevant": True,
                "is_validated": False
            }

            relevance = self.validator.check_relevance(initial_state)
            if relevance.get("is_relevant") is False:
                yield relevance.get("answer", "抱歉，您的问题与医疗健康无关。")
                return

            classifier_result = self.classifier.classify(initial_state)
            specialty = classifier_result["specialty"]
            user_msg = HumanMessage(content=f"问题：{question}")

            if specialty == 'general':
                node = self.general_agent
                tool_result = general_medicine_tool.invoke({"query": question})
                documents = tool_result.get("documents", [])
            elif specialty == 'imaging':
                node = self.imaging_agent
                tool_result = image_search_tool.invoke({"query_text": question})
                documents = tool_result.get("images", []) if isinstance(tool_result, dict) else []
            else:
                node = self.internal_agent
                tool_result = internal_medicine_tool.invoke({"query": question})
                documents = tool_result.get("documents", [])

            if not documents:
                yield "⚠️ 暂未检索到相关知识库文档，无法为您提供准确建议。建议您咨询专业医生或补充相关资料后再次提问。"
                return

            if specialty == 'imaging':
                doc_contents = [img.get("url", "") + img.get("filename", "") for img in documents]
            else:
                doc_contents = [doc.get("content_snippet", "") for doc in documents]

            compressor = get_llmlingua_compressor()
            compressed_docs = compressor.compress_for_retrieval(question, doc_contents, target_token=300)
            llm_messages = [
                HumanMessage(content=node.system_prompt),
                *context_messages,
                user_msg,
                AIMessage(content=f"检索结果（已压缩）：{compressed_docs}"),
                HumanMessage(content="请根据以上检索到的文档内容给出专业回答")
            ]

            for chunk in node.llm.stream(llm_messages):
                content = getattr(chunk, "content", "")
                if content:
                    yield content

        except Exception as e:
            logger.error(f"流式对话失败：{e}")
            yield f"错误：{str(e)}"


# ============================================================================
# 全局实例（单例模式）
# ============================================================================

coordinator = None

def get_coordinator() -> MedicalAgentCoordinator:
    """获取多智能体协调器实例（单例模式）"""
    global coordinator
    if coordinator is None:
        coordinator = MedicalAgentCoordinator()
    return coordinator


def get_medical_agent() -> MedicalAgentCoordinator:
    """获取智能体实例（兼容旧代码）"""
    return get_coordinator()
