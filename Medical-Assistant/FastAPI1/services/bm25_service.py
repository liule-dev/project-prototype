"""
BM25 关键词检索服务
提供基于 BM25 算法的文档关键词检索能力
"""
import jieba
import jieba.analyse
from rank_bm25 import BM25Okapi
from typing import List, Dict, Optional
import hashlib
import logging
import pickle
import os
import tempfile
import threading

logger = logging.getLogger(__name__)

# 索引存储路径配置
INDEX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "indexes")
BM25_INDEX_PATH = os.path.join(INDEX_DIR, "bm25_index.pkl")


class BM25Service:
    """BM25 关键词检索服务"""
    
    def __init__(self):
        # BM25 索引存储
        self.bm25_index: Optional[BM25Okapi] = None
        # 文档ID列表
        self.doc_ids: List[str] = []
        # 文档内容映射 {doc_id: content}
        self.doc_contents: Dict[str, str] = {}
        # 分词后的文档列表
        self.tokenized_docs: List[List[str]] = []
        # 是否已初始化
        self._initialized = False
        # 线程锁，防止并发保存冲突
        self._lock = threading.Lock()
        
        # 启动时自动加载索引
        self.load_index()
    
    def add_document(self, doc_id: str, content: str):
        """
        添加单个文档到 BM25 索引
        
        Args:
            doc_id: 文档唯一标识
            content: 文档文本内容
        """
        try:
            # 中文分词
            tokens = list(jieba.cut_for_search(content))
            tokens = [token.strip() for token in tokens if token.strip() and len(token) > 0]
            
            # 存储文档信息
            if doc_id not in self.doc_ids:
                self.doc_ids.append(doc_id)
                self.doc_contents[doc_id] = content
                self.tokenized_docs.append(tokens)
            
            logger.debug(f"添加文档到 BM25 索引：{doc_id}")
        except Exception as e:
            logger.error(f"添加文档到 BM25 索引失败：{e}")
            raise
    
    def add_documents_batch(self, documents: List[Dict[str, str]]):
        """
        批量添加文档到 BM25 索引
        
        Args:
            documents: 文档列表，每个文档包含 'id' 和 'content' 字段
        """
        try:
            for doc in documents:
                doc_id = doc.get('id')
                content = doc.get('content', '')
                if doc_id and content:
                    self.add_document(doc_id, content)
            
            # 重新构建 BM25 索引
            self._rebuild_index()
            logger.info(f"批量添加 {len(documents)} 个文档到 BM25 索引")
        except Exception as e:
            logger.error(f"批量添加文档失败：{e}")
            raise
    
    def _rebuild_index(self):
        """重建 BM25 索引并持久化"""
        try:
            if self.tokenized_docs:
                self.bm25_index = BM25Okapi(self.tokenized_docs)
                self._initialized = True
                logger.info(f"BM25 索引重建完成，共 {len(self.tokenized_docs)} 个文档")
                # 重建成功后异步保存
                self._save_index_async()
            else:
                logger.warning("没有文档可构建索引")
        except Exception as e:
            logger.error(f"重建 BM25 索引失败：{e}")
            raise
    
    def _save_index_async(self):
        """异步保存索引，避免阻塞主线程"""
        def save_task():
            with self._lock:
                self.save_index()
        thread = threading.Thread(target=save_task, daemon=True)
        thread.start()

    def save_index(self):
        """将索引持久化到磁盘（原子写入）"""
        try:
            os.makedirs(INDEX_DIR, exist_ok=True)
            data = {
                "doc_ids": self.doc_ids,
                "doc_contents": self.doc_contents,
                "tokenized_docs": self.tokenized_docs
            }
            # 先写入临时文件，再替换，防止写入中途崩溃导致文件损坏
            temp_fd, temp_path = tempfile.mkstemp(dir=INDEX_DIR, suffix='.pkl')
            try:
                with os.fdopen(temp_fd, 'wb') as f:
                    pickle.dump(data, f)
                os.replace(temp_path, BM25_INDEX_PATH)
                logger.info(f"💾 BM25 索引已安全保存至 {BM25_INDEX_PATH}")
            except:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise
        except Exception as e:
            logger.error(f"保存 BM25 索引失败：{e}")

    def load_index(self):
        """从磁盘加载索引"""
        try:
            if os.path.exists(BM25_INDEX_PATH):
                with open(BM25_INDEX_PATH, 'rb') as f:
                    data = pickle.load(f)
                self.doc_ids = data.get("doc_ids", [])
                self.doc_contents = data.get("doc_contents", {})
                self.tokenized_docs = data.get("tokenized_docs", [])
                
                if self.tokenized_docs:
                    self.bm25_index = BM25Okapi(self.tokenized_docs)
                    self._initialized = True
                    logger.info(f"📂 成功加载本地 BM25 索引，包含 {len(self.doc_ids)} 个文档")
                else:
                    logger.warning("⚠️ 索引文件存在但内容为空")
            else:
                logger.info("⚠️ 未找到本地 BM25 索引文件，系统将使用空索引等待首次构建")
        except Exception as e:
            logger.error(f"加载 BM25 索引失败（可能文件损坏）：{e}，将重置索引")
            self.clear_index()
    
    def encode_sparse_vector(self, text: str) -> dict:
        """
        将文本转换为 Qdrant 兼容的稀疏向量格式
        返回: {"indices": [词ID列表], "values": [词频/权重列表]}
        """
        tokens = list(jieba.cut_for_search(text))
        # 简单去重和计数
        token_counts = {}
        for token in tokens:
            if token.strip():
                token_counts[token] = token_counts.get(token, 0) + 1
        
        indices = []
        values = []
        for token, count in token_counts.items():
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            indices.append(int(digest[:12], 16) % 1000000)
            values.append(count)
            
        return {"indices": indices, "values": values}
        """
        使用 BM25 算法搜索文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表，包含 doc_id、score、content
        """
        try:
            if not self._initialized or not self.bm25_index:
                logger.warning("BM25 索引未初始化")
                return []
            
            # 对查询进行分词
            query_tokens = list(jieba.cut_for_search(query))
            query_tokens = [token.strip() for token in query_tokens if token.strip() and len(token) > 0]
            
            # 获取 BM25 分数
            scores = self.bm25_index.get_scores(query_tokens)
            
            # 获取 top_k 个最高分数的文档
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            
            results = []
            for idx in top_indices:
                if idx < len(self.doc_ids) and scores[idx] > 0:
                    doc_id = self.doc_ids[idx]
                    results.append({
                        "doc_id": doc_id,
                        "score": float(scores[idx]),
                        "content": self.doc_contents.get(doc_id, ""),
                        "rank": len(results) + 1
                    })
            
            logger.info(f"BM25 搜索完成，找到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"BM25 搜索失败：{e}")
            return []
    
    def remove_document(self, doc_id: str):
        """
        从 BM25 索引中移除文档
        
        Args:
            doc_id: 要移除的文档ID
        """
        try:
            if doc_id in self.doc_ids:
                idx = self.doc_ids.index(doc_id)
                self.doc_ids.pop(idx)
                self.tokenized_docs.pop(idx)
                self.doc_contents.pop(doc_id, None)
                
                # 重新构建索引
                self._rebuild_index()
                logger.info(f"从 BM25 索引移除文档：{doc_id}")
            else:
                logger.warning(f"文档不存在于 BM25 索引：{doc_id}")
        except Exception as e:
            logger.error(f"移除文档失败：{e}")
            raise
    
    def clear_index(self):
        """清空 BM25 索引"""
        try:
            self.bm25_index = None
            self.doc_ids = []
            self.doc_contents = {}
            self.tokenized_docs = []
            self._initialized = False
            logger.info("BM25 索引已清空")
        except Exception as e:
            logger.error(f"清空索引失败：{e}")
            raise
    
    def get_stats(self) -> Dict:
        """获取 BM25 索引统计信息"""
        return {
            "total_documents": len(self.doc_ids),
            "initialized": self._initialized,
            "index_type": "BM25Okapi"
        }


# 全局 BM25 服务实例
bm25_service = BM25Service()
