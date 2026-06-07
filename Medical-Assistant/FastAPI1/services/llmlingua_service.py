"""
LLMLingua 上下文压缩服务 - 基于语义重要性的智能 Prompt 压缩
"""
# ⚠️ 必须在导入任何 transformers/llmlingua 相关库之前设置环境变量
import os
from core import settings

# 获取绝对路径（必须使用绝对路径）
cache_dir = os.path.abspath(settings.TRANSFORMERS_CACHE)

# ⚠️ 强制设置所有相关环境变量（必须在导入 llmlingua 之前）
os.environ['HF_HOME'] = cache_dir  # ✅ 推荐使用 HF_HOME（新版）
os.environ['HUGGINGFACE_HUB_CACHE'] = cache_dir
os.environ['HF_ENDPOINT'] = settings.HF_ENDPOINT
os.environ['HF_HUB_OFFLINE'] = '1'  # ✅ 启用离线模式（最关键）
os.environ['TRANSFORMERS_OFFLINE'] = '1'

# 打印调试信息（在导入前）
print(f"🔧 [LLMLingua] 缓存目录: {cache_dir}")
print(f"🔧 [LLMLingua] HF_HOME: {os.environ.get('HF_HOME')}")
print(f"🔧 [LLMLingua] HF_HUB_OFFLINE: {os.environ.get('HF_HUB_OFFLINE')}")
print(f"🔧 [LLMLingua] TRANSFORMERS_OFFLINE: {os.environ.get('TRANSFORMERS_OFFLINE')}")

from llmlingua import PromptCompressor
import logging

logger = logging.getLogger(__name__)


class LLMLinguaCompressor:
    """LLMLingua 压缩器 - 保留关键信息，删除冗余内容"""

    def __init__(self):
        """初始化 LLMLingua 压缩器"""
        try:
            # 再次确认环境变量已设置（防止 Celery Worker 中丢失）
            cache_dir = os.environ.get('HF_HOME')
            print(f"🔧 [LLMLingua.__init__] 当前 HF_HOME: {cache_dir}")
            print(f"🔧 [LLMLingua.__init__] HF_HUB_OFFLINE: {os.environ.get('HF_HUB_OFFLINE')}")
            
            # 验证模型文件是否存在
            model_cache_path = os.path.join(
                cache_dir, 
                'models--microsoft--llmlingua-2-xlm-roberta-large-meetingbank'
            )
            if os.path.exists(model_cache_path):
                print(f"✅ [LLMLingua] 找到本地模型缓存: {model_cache_path}")
            else:
                print(f"⚠️ [LLMLingua] 未找到模型缓存: {model_cache_path}")
            
            # 注意：PromptCompressor 不支持 local_files_only 参数
            # 离线模式通过环境变量 HF_HUB_OFFLINE=1 控制
            self.compressor = PromptCompressor(
                model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
                use_llmlingua2=True,  # 启用 LLMLingua-2，速度更快
                device_map="cpu"  # 强制使用 CPU
            )
            logger.info("✅ LLMLingua 压缩器初始化完成")
        except Exception as e:
            logger.error(f"❌ LLMLingua 初始化失败：{e}")
            logger.error(f"   缓存目录: {os.environ.get('HF_HOME')}")
            logger.error(f"   HF_HUB_OFFLINE: {os.environ.get('HF_HUB_OFFLINE')}")
            raise

    def compress_messages(
            self,
            messages: list,
            target_token: int = 500,
            rate: float = 0.5,
            force_tokens: list = None
    ) -> list:
        """
        压缩对话历史

        Args:
            messages: 原始消息列表 [{"role": "user/assistant", "content": "..."}]
            target_token: 目标 token 数
            rate: 压缩率（0.5 = 压缩到原来的 50%）
            force_tokens: 强制保留的 tokens（医学术语等）

        Returns:
            压缩后的消息列表
        """
        if not messages or len(messages) <= 4:
            return messages

        # 估算当前 token 数
        total_text = "\n".join([msg.get("content", "") for msg in messages])
        estimated_tokens = len(total_text) // 2  # 粗略估计

        if estimated_tokens <= target_token:
            return messages

        logger.info(f"🗜️ 开始 LLMLingua 压缩：{len(messages)} 条消息，约 {estimated_tokens} tokens")

        try:
            # 构建对话文本（带角色标识）
            conversation_text = ""
            role_map = {"user": "患者", "assistant": "医生", "system": "系统"}

            for msg in messages:
                role = role_map.get(msg.get("role", "user"), "用户")
                content = msg.get("content", "")
                conversation_text += f"{role}：{content}\n\n"

            # 医疗领域强制保留的关键词
            if force_tokens is None:
                force_tokens = [
                    "头痛", "发热", "咳嗽", "疼痛", "恶心", "呕吐",
                    "诊断", "治疗", "药物", "剂量", "症状", "检查",
                    "CT", "MRI", "X光", "血压", "血糖", "心率"
                ]

            # 执行压缩
            compressed_result = self.compressor.compress_prompt(
                context=[conversation_text],
                instruction="",
                question="",
                target_token=target_token,
                rate=rate,
                force_tokens=force_tokens,
                force_reserve_digit=True,  # 保留数字（剂量、时间等）
                drop_consecutive=True,  # 删除连续冗余
            )

            compressed_text = compressed_result["compressed_prompt"]

            # 解析压缩后的文本，还原为消息格式
            compressed_messages = self._parse_compressed_text(compressed_text)

            # 如果压缩后消息太少，保留最近 2 轮完整对话
            if len(compressed_messages) < 2:
                recent_messages = messages[-4:]  # 最近 2 轮
                compressed_messages = [
                                          {"role": "system", "content": f"【历史对话已压缩】\n{compressed_text[:200]}"}
                                      ] + recent_messages

            logger.info(
                f"✅ 压缩完成：{estimated_tokens} → {len(compressed_text) // 2} tokens ({len(messages)} → {len(compressed_messages)} 条)")

            return compressed_messages

        except Exception as e:
            logger.error(f"❌ LLMLingua 压缩失败：{e}，降级使用简单截断")
            # 降级方案：保留最近 6 条
            return messages[-6:]

    def _parse_compressed_text(self, text: str) -> list:
        """
        解析压缩后的文本，还原为消息列表

        Args:
            text: 压缩后的文本

        Returns:
            消息列表
        """
        messages = []
        lines = text.strip().split("\n\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 尝试提取角色和内容
            if line.startswith("患者："):
                messages.append({"role": "user", "content": line[3:].strip()})
            elif line.startswith("医生："):
                messages.append({"role": "assistant", "content": line[3:].strip()})
            elif line.startswith("系统："):
                messages.append({"role": "system", "content": line[3:].strip()})
            else:
                # 无法识别角色，默认为系统消息
                if messages and messages[-1]["role"] == "user":
                    messages.append({"role": "assistant", "content": line})
                else:
                    messages.append({"role": "user", "content": line})

        return messages

    def compress_for_retrieval(
            self,
            query: str,
            documents: list,
            target_token: int = 300
    ) -> str:
        """
        压缩检索到的文档（用于 RAG 场景）

        Args:
            query: 用户查询
            documents: 检索到的文档列表
            target_token: 目标 token 数

        Returns:
            压缩后的文档内容
        """
        if not documents:
            return ""

        # 合并所有文档
        doc_text = "\n\n".join([f"文档{i + 1}：{doc}" for i, doc in enumerate(documents)])

        try:
            compressed = self.compressor.compress_prompt(
                context=[doc_text],
                instruction="",
                question=query,
                target_token=target_token,
                rate=0.5,
                force_reserve_digit=True
            )

            return compressed["compressed_prompt"]

        except Exception as e:
            logger.error(f"❌ 文档压缩失败：{e}")
            # 返回前 500 字
            return doc_text[:500]


# 全局实例（延迟加载）
_llmlingua_instance = None

def get_llmlingua_compressor():
    """
    获取 LLMLingua 压缩器实例（单例模式，延迟加载）
    只在第一次调用时才初始化模型，避免 Celery Worker 启动时内存溢出
    """
    global _llmlingua_instance
    if _llmlingua_instance is None:
        logger.info("🔄 正在初始化 LLMLingua 压缩器...")
        try:
            _llmlingua_instance = LLMLinguaCompressor()
            logger.info("✅ LLMLingua 压缩器初始化完成")
        except Exception as e:
            logger.error(f"❌ LLMLingua 初始化失败：{e}")
            raise
    return _llmlingua_instance
