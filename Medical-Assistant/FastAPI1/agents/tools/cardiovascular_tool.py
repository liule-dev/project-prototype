"""
心血管文档检索工具
"""
from langchain_core.tools import tool
from agents.tools.document_tool import document_search_tool
import logging

logger = logging.getLogger(__name__)


@tool
def cardiovascular_tool(query: str) -> dict:
    """
    检索心血管相关医学文档
    
    参数:
        query: 用户查询文本
    
    返回:
        包含心血管文档检索结果的字典
    """
    try:
        logger.info(f"❤️ 心血管文档检索：{query[:50]}")
        
        # 调用通用文档检索工具，指定心血管领域
        result = document_search_tool.invoke({
            "query": query,
            "top_k": 3,
            "domain": "心血管"
        })
        
        return result
        
    except Exception as e:
        logger.error(f"心血管文档检索失败：{e}")
        return {
            "documents": [],
            "total_count": 0,
            "error": str(e)
        }
