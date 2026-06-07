# 🚀 Celery 异步化 - 5 分钟快速启动

## 前置条件

确保已安装：
- Python 3.10+
- Redis（运行在 localhost:6379）
- MySQL（运行在 localhost:3310）
- MinIO（运行在 localhost:9000）

## 快速启动步骤

### 第 1 步：安装依赖

```bash
cd FastAPI1
pip install -r requirements.txt
```

### 第 2 步：启动 Redis

如果 Redis 未运行，先启动它：

```bash
# Windows: 下载 Redis for Windows 并运行
# Linux: sudo systemctl start redis
# Docker: docker run -d -p 6379:6379 redis:7-alpine
```

验证 Redis 是否运行：
```bash
redis-cli ping
# 应该返回 PONG
```

### 第 3 步：启动 Celery Workers

#### Windows 用户（推荐）
```bash
start_celery_workers.bat
```

这会打开 3 个窗口，分别运行：
- AI Queue Worker（并发数 2）
- File Queue Worker（并发数 2）
- Data Queue Worker（并发数 1）

#### Linux/Mac 用户
```bash
# 终端 1 - AI Queue
celery -A celery_worker:celery_app worker --loglevel=info --queues=ai_queue --concurrency=2

# 终端 2 - File Queue
celery -A celery_worker:celery_app worker --loglevel=info --queues=file_queue --concurrency=2

# 终端 3 - Data Queue
celery -A celery_worker:celery_app worker --loglevel=info --queues=data_queue --concurrency=1
```

### 第 4 步：启动 FastAPI

在新的终端中：
```bash
python main.py
```

服务将在 http://localhost:8000 启动

### 第 5 步：（可选）启动 Flower 监控

```bash
celery -A celery_worker:celery_app flower --port=5555
```

访问 http://localhost:5555 查看任务执行情况
- 用户名：admin
- 密码：admin123

## ✅ 验证是否成功

### 测试 1：检查 Worker 状态

```bash
celery -A celery_worker:celery_app inspect ping
```

应该看到所有 Worker 的响应。

### 测试 2：提交异步任务

```python
import requests

# 提交任务
response = requests.post(
    "http://localhost:8000/query/async/",
    json={"question": "头痛怎么办？"}
)

print(response.json())
# 应该返回: {"task_id": "...", "status": "processing"}
```

### 测试 3：查询任务状态

```python
import time

task_id = response.json()["task_id"]

# 轮询任务状态
while True:
    status = requests.get(f"http://localhost:8000/query/async/status/{task_id}")
    print(status.json())
    
    if status.json()["status"] == "completed":
        break
    
    time.sleep(1)
```

## 🎯 使用示例

### 示例 1：REST API 异步问答

```python
import requests
import time

# 1. 提交任务
resp = requests.post("http://localhost:8000/query/async/", json={
    "question": "感冒发烧怎么办？",
    "session_id": "user_123"
})

task_id = resp.json()["task_id"]
print(f"任务 ID: {task_id}")

# 2. 等待结果
while True:
    status = requests.get(f"http://localhost:8000/query/async/status/{task_id}")
    data = status.json()
    
    if data["status"] == "completed":
        print("回答:", data["result"]["answer"])
        break
    elif data["status"] == "failed":
        print("失败:", data["error"])
        break
    
    time.sleep(1)
```

### 示例 2：WebSocket 实时问答

```javascript
// 前端 JavaScript
const ws = new WebSocket('ws://localhost:8000/query/stream/async?user_id=1&session_id=test_session');

ws.onopen = () => {
    console.log('连接建立');
    
    // 发送问题
    ws.send(JSON.stringify({
        question: '头痛怎么办？'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.event === 'delta') {
        // 接收流式文本
        console.log('收到片段:', data.text);
    } else if (data.event === 'end') {
        // 回答完成
        console.log('完整回答结束');
        if (data.images) {
            console.log('相关图片:', data.images);
        }
    } else if (data.event === 'error') {
        console.error('错误:', data.message);
    }
};
```

### 示例 3：直接在代码中调用任务

```python
from tasks.ai_tasks import generate_llm_response

# 提交任务
task = generate_llm_response.delay(
    question="高血压如何控制？",
    context_messages=[]
)

# 获取结果（阻塞）
result = task.get(timeout=60)
print(result["answer"])
```

## 🔍 故障排查

### 问题 1：Worker 无法启动

**症状**：`ModuleNotFoundError: No module named 'tasks'`

**解决方案**：
```bash
# 确保在正确的目录
cd FastAPI1

# 设置 PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%      # Windows
```

### 问题 2：Redis 连接失败

**症状**：`ConnectionError: Error connecting to Redis`

**解决方案**：
```bash
# 检查 Redis 是否运行
redis-cli ping

# 检查 Redis 配置
redis-cli CONFIG GET bind

# 如果需要，修改 core/celery_config.py 中的 Redis 地址
```

### 问题 3：任务一直显示 "pending"

**症状**：任务提交后状态一直是 "pending"

**解决方案**：
```bash
# 检查 Worker 是否在运行
celery -A celery_worker:celery_app inspect active

# 检查队列中是否有任务
celery -A celery_worker:celery_app inspect reserved

# 查看 Worker 日志
tail -f celery_worker.log
```

### 问题 4：任务执行失败

**症状**：任务状态变为 "failed"

**解决方案**：
```bash
# 查看详细错误信息
celery -A celery_worker:celery_app loglevel debug

# 检查任务参数是否正确
# 确保所有参数都是 JSON 可序列化的
```

## 📊 监控和管理

### 查看 Worker 状态
```bash
celery -A celery_worker:celery_app inspect stats
```

### 查看活跃任务
```bash
celery -A celery_worker:celery_app inspect active
```

### 查看队列长度
```bash
celery -A celery_worker:celery_app inspect reserved
```

### 重启 Worker
```bash
# Windows: 关闭批处理脚本窗口，重新运行
# Linux/Mac: Ctrl+C 停止，然后重新启动
```

### 清理任务结果
```python
from core.celery_config import celery_app

# 清理过期结果
celery_app.control.purge()
```

## 🎓 下一步

1. **阅读详细文档**：查看 `CELERY_ASYNC_GUIDE.md`
2. **了解架构设计**：查看 `ASYNC_REFACTORING_SUMMARY.md`
3. **调整配置**：根据服务器性能调整并发数
4. **添加监控**：配置告警和日志收集
5. **优化性能**：分析瓶颈并调优

## 💡 提示

- **开发环境**：使用 `--loglevel=debug` 查看详细日志
- **生产环境**：使用 `--loglevel=warning` 减少日志输出
- **性能测试**：使用 `flower` 监控任务执行时间
- **资源限制**：设置 `--max-tasks-per-child` 防止内存泄漏

## 🎉 完成！

现在你的医疗助手系统已经支持多人同时访问，不会再有排队等待的问题了！

享受高性能的异步架构带来的流畅体验吧！🚀
