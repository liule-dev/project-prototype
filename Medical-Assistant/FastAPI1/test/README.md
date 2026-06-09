# 测试与工具脚本文件夹

本文件夹包含所有测试、清理和维护脚本。

## 📁 文件分类

### 🔧 性能优化工具

| 文件名 | 说明 | 使用方式 |
|--------|------|----------|
| `test_optimization.py` | **三级缓存性能验证**（L1内存+L2 Redis+L3 MySQL） | `python test_optimization.py` |

### 🧹 清理工具（生产环境使用）

| 文件名 | 说明 | 使用方式 |
|--------|------|----------|
| `run_cleanup.bat` | Windows 启动脚本（一键运行） | 双击运行 |
| `run_redis_cleanup.bat` | Redis 清理 Windows 启动脚本 | 双击运行 |
| `scheduler_cleanup.py` | 定时清理调度器 | `python scheduler_cleanup.py` |
| `cleanup_orphan_vectors.py` | 孤立向量清理核心脚本 | `python cleanup_orphan_vectors.py` |
| `clear_qdrant.py` | Qdrant 数据清空工具 | `python clear_qdrant.py all` |
| `clear_redis.py` | Redis 缓存清理工具 | `python clear_redis.py` |
| `README_CLEANUP.md` | 清理工具详细说明 | 查看文档 |

### 🧪 测试脚本（开发调试使用）

#### **缓存与性能测试**
| 文件名 | 说明 |
|--------|------|
| `test_cache_protection.py` | 缓存击穿/雪崩防护测试 |
| `test_optimization.py` | 三级缓存架构性能验证 |

#### **Celery 异步任务测试**
| 文件名 | 说明 |
|--------|------|
| `test_celery_task.py` | Celery 基础任务测试 |
| `test_celery_llmlingua.py` | Celery Worker 中 LLMLingua 初始化测试 |

#### **LLMLingua 压缩测试**
| 文件名 | 说明 |
|--------|------|
| `test_llmlingua_init.py` | LLMLingua 模型初始化诊断 |
| `test_llmlingua_model.py` | LLMLingua 压缩功能测试 |

#### **认证与安全测试**
| 文件名 | 说明 |
|--------|------|
| `test_auth.py` | JWT 认证接口测试 |
| `init_test_user.py` | 初始化测试用户 |

#### **向量检索测试**
| 文件名 | 说明 |
|--------|------|
| `test_qdrant_data.py` | 检查 Qdrant 数据库中的数据 |
| `check_payload.py` | 检查 payload 结构 |
| `test_document_search.py` | 测试文档检索功能 |
| `test_filter.py` | 测试过滤器语法 |
| `test_full_search.py` | 完整检索流程测试 |
| `test_real_search.py` | 实际场景检索测试 |
| `bm25.py` | BM25 索引初始化工具 |
| `test_bm25.py` | BM25 混合检索测试 |

#### **WebSocket 压力测试**
| 文件名 | 说明 |
|--------|------|
| `test_websocket_stress.py` | WebSocket 并发压力测试 |

#### **数据库检查工具**
| 文件名 | 说明 |
|--------|------|
| `check_db_messages.py` | 检查数据库会话消息 |
| `check_redis_queues.py` | 检查 Redis 队列状态 |

---

## 🚀 快速开始

### 清理孤立的向量化数据

**最简单的方式**：双击 `run_cleanup.bat`

```bash
# 或者命令行运行
python cleanup_orphan_vectors.py          # 手动清理一次
python scheduler_cleanup.py               # 启动定时服务
```

### 清空 Qdrant 数据库

```bash
python clear_qdrant.py all                # 清空所有集合
python clear_qdrant.py medical_documents  # 清空指定集合
```

---

## 📝 详细说明

### 清理工具工作原理

1. **扫描 Qdrant** - 获取所有文档的元数据
2. **检查 MinIO** - 验证文档是否仍然存在
3. **删除孤立向量** - 如果 MinIO 中不存在，则从 Qdrant 删除
4. **记录日志** - 保存到 `cleanup_orphan_vectors.log`

### 定时任务配置

- **默认时间**：每天凌晨 2:00
- **修改方法**：编辑 `scheduler_cleanup.py` 第 54 行
- **日志位置**：同目录下的 `.log` 文件

---

## ⚠️ 注意事项

1. **测试脚本** 仅用于开发调试，生产环境不要运行
2. **清理工具** 会实际删除数据，请谨慎使用
3. **定时服务** 需要保持终端开启或使用 Windows 任务计划程序
4. **首次运行前** 确保 Qdrant 和 MinIO 服务正常

---

## 📖 完整文档

详细使用说明请查看 [`README_CLEANUP.md`](./README_CLEANUP.md)
