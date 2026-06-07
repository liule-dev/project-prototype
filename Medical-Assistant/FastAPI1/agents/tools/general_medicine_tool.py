"""
外科文档检索工具
"""
from langchain_core.tools import tool
from agents.tools.document_tool import document_search_tool
import logging

logger = logging.getLogger(__name__)


@tool
def general_medicine_tool(query: str) -> dict:
    """
    检索外科相关医学文档
    
    参数:
        query: 用户查询文本
    
    返回:
        包含外科文档检索结果的字典
    """
    try:
        logger.info(f"🔪 外科文档检索：{query[:50]}")
        
        # 调用通用文档检索工具，指定外科领域
        result = document_search_tool.invoke({
            "query": query,
            "top_k": 3,
            "domain": "外科"
        })
        
        return result
        
    except Exception as e:
        logger.error(f"外科文档检索失败：{e}")
        return {
            "documents": [],
            "total_count": 0,
            "error": str(e)
        }
