"""
通用搜索工具
提供综合搜索能力（文档 + 图片）
"""
from langchain_core.tools import tool
from agents.tools.document_tool import document_search_tool
from agents.tools.image_tool import image_search_tool
import logging

logger = logging.getLogger(__name__)


@tool
def search_tool(query: str, search_type: str = "all", top_k: int = 3) -> dict:
    """
    综合搜索工具（文档 + 图片）
    
    参数:
        query: 用户查询文本
        search_type: 搜索类型 ("all" | "document" | "image")
        top_k: 每种类型返回数量
    
    返回:
        包含文档和图片检索结果的字典
    """
    try:
        logger.info(f"🔍 开始综合搜索：{query[:50]}, 类型：{search_type}")
        
        result = {
            "query": query,
            "search_type": search_type
        }
        
        # 文档搜索
        if search_type in ["all", "document"]:
            doc_result = document_search_tool.invoke({
                "query": query,
                "top_k": top_k
            })
            result["documents"] = doc_result.get("documents", [])
            result["document_count"] = doc_result.get("total_count", 0)
        
        # 图片搜索
        if search_type in ["all", "image"]:
            img_result = image_search_tool.invoke({
                "query_text": query,
                "top_k": top_k
            })
            result["images"] = img_result.get("images", [])
            result["image_count"] = img_result.get("total_count", 0)
        
        logger.info(f"✅ 综合搜索完成")
        
        return result
        
    except Exception as e:
        logger.error(f"综合搜索失败：{e}")
        return {
            "query": query,
            "error": str(e),
            "documents": [],
            "images": []
        }
