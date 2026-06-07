# Celery 异步任务使用指南

## 📋 概述

本项目已集成 Celery 异步任务队列，用于处理耗时的 AI 推理、文件处理和数据处理任务，显著提升系统的并发能力和响应速度。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install celery==5.3.6 flower==2.0.1
```

### 2. 启动 Celery Workers

#### Windows 系统
```bash
# 方式一：使用批处理脚本（推荐）
start_celery_workers.bat

# 方式二：手动启动各个 Worker
# AI 推理队列
celery -A celery_worker:celery_app worker --loglevel=info --queues=ai_queue --concurrency=2

# 文件处理队列
celery -A celery_worker:celery_app worker --loglevel=info --queues=file_queue --concurrency=2

# 数据处理队列
celery -A celery_worker:celery_app worker --loglevel=info --queues=data_queue --concurrency=1
```

#### Linux/Mac 系统
```bash
# AI 推理队列
celery -A celery_worker:celery_app worker --loglevel=info --queues=ai_queue --concurrency=2 &

# 文件处理队列
celery -A celery_worker:celery_app worker --loglevel=info --queues=file_queue --concurrency=2 &

# 数据处理队列
celery -A celery_worker:celery_app worker --loglevel=info --queues=data_queue --concurrency=1 &
```

### 3. 启动 Flower 监控面板（可选）

```bash
celery -A celery_worker:celery_app flower --port=5555
```

访问 http://localhost:5555 查看任务执行情况。

### 4. 启动 FastAPI 服务

```bash
python main.py
```

## 💡 使用示例

### 示例 1：异步问答

```python
import requests

# 1. 提交异步任务
response = requests.post(
    "http://localhost:8000/query/async/",
    json={
        "question": "头痛怎么办？",
        "session_id": "user_123",
        "context_messages": []
    }
)

task_id = response.json()["task_id"]
print(f"任务 ID: {task_id}")

# 2. 查询任务状态
import time
while True:
    status_response = requests.get(f"http://localhost:8000/query/async/status/{task_id}")
    status = status_response.json()
    
    if status["status"] == "completed":
        print("回答:", status["result"]["answer"])
        break
    elif status["status"] == "failed":
        print("失败:", status["error"])
        break
    
    time.sleep(1)
```

### 示例 2：在代码中直接调用 Celery 任务

```python
from tasks.ai_tasks import generate_llm_response, extract_image_features
from tasks.file_tasks import process_document, upload_to_minio

# 异步生成 LLM 回答
task = generate_llm_response.delay(
    question="头痛怎么办？",
    context_messages=[]
)

# 获取结果（阻塞）
result = task.get(timeout=60)
print(result["answer"])

# 或者非阻塞检查
if task.ready():
    result = task.get()
else:
    print("任务还在执行中...")
```

### 示例 3：批量处理任务

```python
from celery import group
from tasks.file_tasks import process_document

# 批量处理多个文档
documents = [
    {"data": doc1_data, "filename": "doc1.pdf", "type": "pdf"},
    {"data": doc2_data, "filename": "doc2.docx", "type": "docx"},
]

# 创建任务组
task_group = group(
    process_document.s(doc["data"], doc["filename"], doc["type"])
    for doc in documents
)

# 并行执行
result = task_group.apply_async()

# 获取所有结果
results = result.get(timeout=300)
```

## 📊 任务队列说明

### AI 队列 (ai_queue)
- **用途**：处理 AI 推理相关任务
- **并发数**：2
- **任务类型**：
  - `generate_llm_response` - LLM 对话生成
  - `extract_image_features` - 图片特征提取
  - `vector_search_images` - 图片向量检索
  - `vector_search_documents` - 文档混合检索
  - `generate_text_embedding` - 文本 Embedding 生成

### 文件队列 (file_queue)
- **用途**：处理文件上传和处理任务
- **并发数**：2
- **任务类型**：
  - `process_document` - 文档解析和分块
  - `upload_to_minio` - 文件上传到 MinIO
  - `process_image` - 图片预处理
  - `batch_upload_images` - 批量图片上传

### 数据队列 (data_queue)
- **用途**：处理数据存储和缓存任务
- **并发数**：1
- **任务类型**：
  - `save_session_message` - 会话消息存储
  - `update_session_cache` - 会话缓存更新
  - `sync_session_to_db` - 会话批量同步
  - `cleanup_expired_sessions` - 过期会话清理
  - `log_operation` - 操作日志记录

## 🔧 配置说明

### Celery 配置 (core/celery_config.py)

```python
# 并发配置
worker_concurrency=4  # 每个 worker 的并发进程数
worker_prefetch_multiplier=1  # 每次预取任务数

# 超时配置
task_soft_time_limit=300  # 软超时 5 分钟
task_time_limit=600  # 硬超时 10 分钟

# 重试配置
task_acks_late=True  # 任务完成后确认
task_reject_on_worker_lost=True  # worker 丢失时拒绝

# 速率限制
task_annotations={
    'ai_tasks.generate_llm_response': {'rate_limit': '10/m'},
}
```

### Redis 配置
Celery 使用 Redis 作为消息代理和结果后端：
- **Broker**: `redis://localhost:6379/1`
- **Backend**: `redis://localhost:6379/2`

## 📈 性能优化建议

### 1. 调整并发数
根据服务器资源配置并发数：
```bash
# CPU 密集型任务（AI 推理）：并发数 = CPU 核心数
celery worker --concurrency=4

# I/O 密集型任务（文件处理）：并发数 = CPU 核心数 * 2
celery worker --concurrency=8
```

### 2. 任务优先级
```python
# 高优先级任务
task.apply_async(priority=9)

# 低优先级任务
task.apply_async(priority=1)
```

### 3. 任务分组
对于批量任务，使用 group 并行执行：
```python
from celery import group
tasks = group(my_task.s(item) for item in items)
result = tasks.apply_async()
```

### 4. 结果缓存
对于重复计算的任务，启用结果缓存：
```python
@celery_app.task(bind=True, cache=True)
def cached_task(self, arg):
    # 自动缓存结果
    pass
```

## 🔍 监控和调试

### 1. 查看 Worker 状态
```bash
celery -A celery_worker:celery_app inspect active
celery -A celery_worker:celery_app inspect stats
```

### 2. 查看任务队列长度
```bash
celery -A celery_worker:celery_app inspect reserved
```

### 3. 使用 Flower 监控
访问 http://localhost:5555 查看：
- 实时任务执行情况
- Worker 状态
- 任务历史记录
- 性能指标

### 4. 日志查看
```bash
# 查看 Worker 日志
tail -f celery_worker.log

# 查看特定队列的日志
grep "ai_queue" celery_worker.log
```

## ⚠️ 注意事项

### 1. 任务序列化
- 所有任务参数和返回值必须是 JSON 可序列化的
- 对于 bytes 数据，使用 hex 编码：`data.hex()`
- 对于 numpy 数组，转换为 list：`array.tolist()`

### 2. 错误处理
- 所有任务都包含重试逻辑
- 使用 `bind=True` 和 `max_retries` 配置重试
- 记录详细的错误日志

### 3. 资源管理
- 避免在任务中创建大量临时对象
- 及时释放数据库连接
- 监控内存使用情况

### 4. 任务幂等性
- 确保任务可以安全重试
- 使用唯一 ID 避免重复处理
- 检查任务是否已执行

## 🐛 常见问题

### Q1: Worker 无法连接到 Redis
**解决方案**：
```bash
# 检查 Redis 是否运行
redis-cli ping

# 检查 Redis 配置
redis-cli CONFIG GET bind
```

### Q2: 任务执行超时
**解决方案**：
```python
# 增加超时时间
@celery_app.task(time_limit=600, soft_time_limit=500)
def my_task():
    pass
```

### Q3: 任务堆积过多
**解决方案**：
```bash
# 增加 Worker 数量
celery worker --concurrency=8

# 添加更多 Worker 实例
celery worker --queues=ai_queue --hostname=worker2@%h
```

### Q4: 内存泄漏
**解决方案**：
```bash
# 定期重启 Worker
celery worker --max-tasks-per-child=100

# 监控内存使用
celery -A celery_worker:celery_app inspect memdump
```

## 📚 参考资料

- [Celery 官方文档](https://docs.celeryq.dev/)
- [FastAPI + Celery 集成指南](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Redis 作为 Celery Broker](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html)

## 🎯 下一步优化

1. **实现 WebSocket 实时推送**：将 Celery 任务进度推送到前端
2. **添加任务优先级队列**：区分 VIP 用户和普通用户
3. **实现定时任务**：定期清理过期数据
4. **添加任务限流**：防止系统过载
5. **集成分布式追踪**：使用 Jaeger 或 Zipkin
