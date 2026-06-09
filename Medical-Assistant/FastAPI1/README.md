# 医疗 AI 助手 - FastAPI 后端服务

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.124.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Redis](https://img.shields.io/badge/Redis-7.0-red)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)

**基于 FastAPI + LangChain + Celery 的企业级医疗 AI 问答系统**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [架构设计](#-架构设计) • [API 文档](#-api-文档) • [性能优化](#-性能优化)

</div>

---

## 📋 目录

- [项目简介](#-项目简介)
- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
  - [环境要求](#环境要求)
  - [本地开发](#本地开发)
  - [Docker 部署](#docker-部署)
- [配置说明](#-配置说明)
- [API 文档](#-api-文档)
- [架构设计](#-架构设计)
  - [三级缓存架构](#三级缓存架构)
  - [异步任务队列](#异步任务队列)
  - [多智能体协作](#多智能体协作)
- [性能优化](#-性能优化)
- [测试](#-测试)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 📖 项目简介

医疗 AI 助手是一个基于 **FastAPI** 构建的高性能医疗问答系统，集成了多模态 AI 能力（文本、图像、文档），支持智能分诊、医学文献检索、影像辅助诊断等功能。

### 核心优势

- ⚡ **高性能**: 三级缓存架构，响应时间 < 50ms（缓存命中）
- 🚀 **高并发**: 支持 200+ 用户同时在线，QPS 达 300+
- 🎯 **智能化**: 多智能体协作，自动分诊至专科医生
- 📊 **可扩展**: Celery 异步任务队列，轻松水平扩展
- 🔒 **企业级**: 完整的认证、日志、监控体系

---

## ✨ 功能特性

### 🤖 AI 问答
- ✅ 自然语言医疗咨询
- ✅ 智能分诊（内科/外科/心血管等 10+ 专科）
- ✅ 流式响应（WebSocket）
- ✅ 上下文记忆（多轮对话）

### 🖼️ 多模态支持
- ✅ 医学影像上传与分析（CLIP 模型）
- ✅ 文档解析（PDF/Word）
- ✅ 视频处理

### 🔍 智能检索
- ✅ 混合检索（向量 + BM25）
- ✅ RAG 增强生成
- ✅ 相关性重排序（Rerank）

### 💾 数据管理
- ✅ 会话历史持久化
- ✅ 用户认证与授权
- ✅ 操作日志审计

---

## 🛠️ 技术栈

### 核心框架
- **Web 框架**: [FastAPI](https://fastapi.tiangolo.com/) 0.124.0
- **ASGI 服务器**: [Uvicorn](https://www.uvicorn.org/) 0.38.0
- **数据校验**: [Pydantic](https://docs.pydantic.dev/) 2.12.0

### AI/ML
- **LLM 集成**: [LangChain](https://www.langchain.com/) 0.3.0
- **工作流编排**: [LangGraph](https://langchain-ai.github.io/langgraph/) 0.2.28
- **Embedding**: [Sentence Transformers](https://www.sbert.net/) 3.0.1
- **图像理解**: [CLIP](https://openai.com/research/clip) (ViT-B/16)
- **文本压缩**: [LLMLingua-2](https://github.com/microsoft/LLMLingua) 0.2.2

### 数据存储
- **关系数据库**: MySQL 8.0 + SQLAlchemy ORM
- **向量数据库**: [Qdrant](https://qdrant.tech/) 1.17.1
- **缓存层**: Redis 7.0
- **对象存储**: [MinIO](https://min.io/) 7.2.20

### 异步任务
- **任务队列**: [Celery](https://docs.celeryq.dev/) 5.3.6
- **监控面板**: [Flower](https://flower.readthedocs.io/) 2.0.1

### 检索增强
- **全文检索**: [Rank-BM25](https://github.com/dorianbrown/rank_bm25) 0.2.2
- **中文分词**: [Jieba](https://github.com/fxsjy/jieba) 0.42.1

---

## 📁 项目结构

```
FastAPI1/
├── agents/                  # 智能体模块
│   ├── tools/              # 工具函数
│   │   ├── cardiovascular_tool.py    # 心血管专科工具
│   │   ├── document_tool.py          # 文档检索工具
│   │   ├── image_tool.py             # 图像处理工具
│   │   └── search_tool.py            # 通用搜索工具
│   ├── medical_agent.py    # 多智能体协调器
│   └── clip_extractor.py   # CLIP 特征提取器
│
├── api/                     # API 路由
│   ├── routes/
│   │   ├── auth.py         # 认证接口
│   │   ├── upload.py       # 文件上传接口
│   │   ├── query_async.py  # 异步查询接口
│   │   └── websocket_async.py  # WebSocket 流式接口
│   └── deps.py             # 依赖注入
│
├── core/                    # 核心配置
│   ├── config.py           # 应用配置
│   ├── database.py         # MySQL 连接
│   ├── redis.py            # Redis 客户端
│   ├── qdrant.py           # Qdrant 客户端
│   └── celery_config.py    # Celery 配置
│
├── models/                  # 数据模型
│   └── schemas.py          # Pydantic 模型
│
├── services/                # 业务服务层
│   ├── cache_service.py    # 三级缓存服务 ⭐
│   ├── session_service.py  # 会话管理
│   ├── vector_service.py   # 向量检索
│   ├── bm25_service.py     # BM25 检索
│   ├── llmlingua_service.py # 文本压缩
│   ├── minio_service.py    # 对象存储
│   └── llm_service.py      # LLM 调用
│
├── tasks/                   # Celery 异步任务
│   ├── ai_tasks.py         # AI 推理任务
│   ├── file_tasks.py       # 文件处理任务
│   └── data_tasks.py       # 数据同步任务
│
├── test/                    # 测试脚本
│   ├── test_optimization.py      # 性能优化验证
│   ├── test_cache_protection.py  # 缓存防护测试
│   ├── test_celery_*.py          # Celery 测试
│   └── ...
│
├── cache/                   # 模型缓存目录
├── .env                     # 环境变量（不提交）
├── .env.example             # 环境变量模板
├── main.py                  # 应用入口
├── celery_worker.py         # Celery Worker 入口
├── requirements.txt         # Python 依赖
├── Dockerfile               # Docker 镜像
└── docker-compose-celery.yml # Docker Compose 配置
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Redis 7.0+
- MySQL 8.0+
- Qdrant 1.17+
- MinIO（可选，用于文件存储）

### 本地开发

#### 1. 克隆项目

```bash
git clone https://github.com/your-repo/Medical-Assistant.git
cd Medical-Assistant/FastAPI1
```

#### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填写正确的配置
```

关键配置项：
```env
# LLM API 配置
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# 数据库配置
REDIS_HOST=localhost
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password

# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

#### 5. 启动依赖服务

```bash
# 启动 Redis
redis-server

# 启动 MySQL
mysql.server start

# 启动 Qdrant
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

#### 6. 初始化数据库

```bash
python -c "from core.database import init_db; init_db()"
```

#### 7. 启动 Celery Worker

```bash
# Windows
start_celery.bat

# Linux/Mac
celery -A celery_worker:celery_app worker --loglevel=info --queues=ai_queue,file_queue,data_queue
```

#### 8. 启动 FastAPI 服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

---

### Docker 部署

#### 1. 使用 Docker Compose（推荐）

```bash
cd ..  # 返回项目根目录
docker compose up -d
```

这将启动以下服务：
- FastAPI 应用（4 workers）
- Celery Workers（AI/File/Data 队列）
- Redis
- MySQL
- Qdrant
- MinIO
- Nginx（反向代理）

#### 2. 单独构建 FastAPI 镜像

```bash
cd FastAPI1
docker build -t medical-assistant-api .
docker run -d -p 8000:8000 --env-file .env medical-assistant-api
```

---

## ⚙️ 配置说明

### 环境变量详解

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `LLM_API_KEY` | LLM API 密钥 | - | ✅ |
| `LLM_BASE_URL` | LLM API 地址 | - | ✅ |
| `LLM_MODEL_NAME` | 模型名称 | qwen-plus | ✅ |
| `REDIS_HOST` | Redis 主机 | localhost | ✅ |
| `REDIS_PORT` | Redis 端口 | 6379 | ❌ |
| `DB_HOST` | MySQL 主机 | localhost | ✅ |
| `DB_PORT` | MySQL 端口 | 3306 | ❌ |
| `QDRANT_HOST` | Qdrant 主机 | localhost | ✅ |
| `MINIO_ENDPOINT` | MinIO 端点 | localhost:9000 | ❌ |
| `HF_ENDPOINT` | Hugging Face 镜像 | https://hf-mirror.com | ❌ |
| `TRANSFORMERS_CACHE` | 模型缓存目录 | ./cache | ❌ |

### 性能调优参数

```env
# 缓存 TTL（秒）
CACHE_TTL_LLM_ANSWER=86400        # LLM 回答缓存 24 小时
CACHE_TTL_SESSION_HISTORY=7200    # 会话历史缓存 2 小时
CACHE_TTL_CLIP_VECTOR=86400       # CLIP 向量缓存 24 小时

# 检索配置
BM25_K1=1.5                       # BM25 k1 参数
BM25_B=0.75                       # BM25 b 参数
HYBRID_SEARCH_ALPHA=0.7           # 混合检索权重

# 文件上传
MAX_FILE_SIZE=104857600           # 最大文件大小 100MB
MAX_DOC_TEXT_LENGTH=10000         # 文档最大长度 10000 字
```

---

## 📚 API 文档

### 主要接口

#### 1. 用户认证

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "123456"
}
```

#### 2. WebSocket 流式问答

```javascript
const ws = new WebSocket('ws://localhost:8000/api/query/stream/async?session_id=xxx');

ws.onopen = () => {
  ws.send(JSON.stringify({
    question: "头痛怎么办？"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.event === 'delta') {
    console.log(data.text);  // 流式输出
  }
};
```

#### 3. 文件上传

```http
POST /api/upload/document
Content-Type: multipart/form-data

file: <medical_report.pdf>
```

#### 4. 会话管理

```http
GET /api/session/{session_id}/history
Authorization: Bearer <token>
```

完整 API 文档请访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🏗️ 架构设计

### 三级缓存架构

```
用户请求
  ↓
┌─────────────────────┐
│ L1: 内存缓存         │ ← 0.01ms (LRU, 1000条)
└─────────────────────┘
  ↓ 未命中
┌─────────────────────┐
│ L2: Redis 缓存       │ ← 5ms (TTL + 抖动防雪崩)
└─────────────────────┘
  ↓ 未命中
┌─────────────────────┐
│ L3: MySQL 数据库     │ ← 50ms (连接池 60)
└─────────────────────┘
```

**核心特性**：
- ✅ 自动回填：L2 命中后自动写入 L1
- ✅ 击穿防护：互斥锁机制
- ✅ 雪崩防护：随机 TTL 抖动
- ✅ 容量控制：LRU 淘汰策略

**性能提升**：
- 热点问答响应：**0.01ms**（提升 500 倍）
- 缓存命中率：**90%+**
- 数据库负载：降低 **85-90%**

---

### 异步任务队列

```
FastAPI 主进程
  ↓ 提交任务
Redis Broker
  ↓ 分发
┌──────────────┬──────────────┬──────────────┐
│  AI Queue    │ File Queue   │ Data Queue   │
│ (concurrency │ (concurrency │ (concurrency │
│     = 4)     │     = 4)     │     = 2)     │
└──────────────┴──────────────┴──────────────┘
  ↓ 执行
Celery Workers
  ↓ 结果
Redis Backend
```

**任务类型**：
- **AI 任务**: LLM 推理、向量检索、图像分析
- **文件任务**: 文档解析、视频处理、MinIO 上传
- **数据任务**: 会话同步、缓存更新、日志记录

**优势**：
- 非阻塞：API 立即响应
- 可重试：失败自动重试 3 次
- 可监控：Flower 实时监控
- 可扩展：水平增加 Worker

---

### 多智能体协作

```
用户问题
  ↓
路由智能体（分类）
  ↓
┌─────┬─────┬──────┬──────┐
│内科 │外科 │心血管│ 眼科  │ ...
└─────┴─────┴──────┴──────┘
  ↓
专科智能体（检索 + 推理）
  ↓
校验智能体（质量检查）
  ↓
最终回答
```

**智能体类型**：
- **路由智能体**: 问题分类与分诊
- **专科智能体**: 内科、外科、心血管等 10+ 专科
- **校验智能体**: 答案相关性验证
- **反思智能体**: 低置信度时重新检索

---

## 📊 性能优化

### 已实施的优化

| 优化项 | 优化前 | 优化后 | 提升 |
|--------|--------|--------|------|
| **Redis 连接池** | 50 | 200 | ↑ 300% |
| **MySQL 连接池** | 30 | 60 | ↑ 100% |
| **Celery 并发** | 4 | 8 | ↑ 100% |
| **LLM 吞吐** | 10/min | 30/min | ↑ 200% |
| **响应时间** | 800ms | 0.01-5ms | ↑ 99% |
| **并发用户** | 60人 | 250人 | ↑ 300% |

### 性能测试

运行性能验证脚本：

```bash
cd test
python test_optimization.py
```

预期输出：
```
✅ Redis 最大连接数: 200
✅ 数据库最大连接数: 60
✅ Celery Worker 并发数: 8
✅ LLM 任务速率限制: 30/m
🎉 所有优化项验证通过！
```

---

## 🧪 测试

### 测试分类

```
test/
├── 性能测试
│   ├── test_optimization.py       # 三级缓存验证
│   └── test_cache_protection.py   # 缓存防护测试
├── Celery 测试
│   ├── test_celery_task.py        # 基础任务
│   └── test_celery_llmlingua.py   # LLMLingua 初始化
├── 向量检索测试
│   ├── test_bm25.py               # BM25 检索
│   ├── test_document_search.py    # 文档检索
│   └── test_full_search.py        # 完整流程
├── WebSocket 测试
│   └── test_websocket_stress.py   # 压力测试
└── 工具脚本
    ├── clear_redis.py             # 清理 Redis
    ├── clear_qdrant.py            # 清理 Qdrant
    └── check_db_messages.py       # 数据库检查
```

### 运行测试

```bash
# 运行所有测试
cd test
python -m pytest

# 运行单个测试
python test_optimization.py

# 压力测试
python test_websocket_stress.py --users 200
```

---

## ❓ 常见问题

### 1. Redis 连接池耗尽

**错误**: `Connection pool exhausted`

**解决**: 
```python
# core/redis.py
'max_connections': 200  # 增加连接数
```

### 2. Celery Worker 无法启动

**错误**: `ModuleNotFoundError: No module named 'tasks'`

**解决**:
```bash
# 确保在项目根目录运行
cd FastAPI1
celery -A celery_worker:celery_app worker
```

### 3. Hugging Face 模型加载失败

**错误**: `ConnectionError: Couldn't reach huggingface.co`

**解决**:
```env
# .env
HF_ENDPOINT=https://hf-mirror.com
HF_HUB_OFFLINE=1  # 启用离线模式
```

### 4. WebSocket 连接断开

**原因**: Nginx 超时配置

**解决**:
```nginx
# nginx.conf
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;
```

更多问题请查看 [FAQ](docs/FAQ.md)。

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 代码风格
- 使用 `black` 格式化代码
- 添加必要的单元测试
- 更新文档

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。

---

## 📞 联系方式

- 项目维护者: Your Name
- Email: your-email@example.com
- 问题反馈: [GitHub Issues](https://github.com/your-repo/Medical-Assistant/issues)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

Made with ❤️ by Medical AI Team

</div>
