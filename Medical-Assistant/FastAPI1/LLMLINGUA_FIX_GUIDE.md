# LLMLingua 初始化问题完整解决方案

## 🔍 问题诊断

### 错误信息
```
We couldn't connect to 'https://hf-mirror.com' to load this file, 
couldn't find it in the cached files and it looks like 
microsoft/llmlingua-2-xlm-roberta-large-meetingbank is not the path 
to a directory containing a file named config.json.
```

### 根本原因

1. **错误的参数使用**：`PromptCompressor` 类**不支持** `local_files_only` 参数
2. **环境变量设置时机错误**：在 Celery Worker 进程中，模块级别的环境变量设置可能丢失
3. **使用了废弃的环境变量**：`TRANSFORMERS_CACHE` 已被废弃，应使用 `HF_HOME`

## ✅ 解决方案

### 1. 修复 llmlingua_service.py

**关键修改点：**

```python
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

from llmlingua import PromptCompressor  # ✅ 现在才导入
```

**初始化时移除不支持的参数：**

```python
def __init__(self):
    """初始化 LLMLingua 压缩器"""
    try:
        # 再次确认环境变量已设置（防止 Celery Worker 中丢失）
        cache_dir = os.environ.get('HF_HOME')
        print(f"🔧 [LLMLingua.__init__] 当前 HF_HOME: {cache_dir}")
        
        # 验证模型文件是否存在
        model_cache_path = os.path.join(
            cache_dir, 
            'models--microsoft--llmlingua-2-xlm-roberta-large-meetingbank'
        )
        if os.path.exists(model_cache_path):
            print(f"✅ [LLMLingua] 找到本地模型缓存: {model_cache_path}")
        
        # ❌ 错误写法：不要使用 local_files_only 参数
        # self.compressor = PromptCompressor(..., local_files_only=True)
        
        # ✅ 正确写法：只使用支持的参数
        self.compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
            use_llmlingua2=True,
            device_map="cpu"  # 只保留支持的参数
        )
        logger.info("✅ LLMLingua 压缩器初始化完成")
    except Exception as e:
        logger.error(f"❌ LLMLingua 初始化失败：{e}")
        raise
```

### 2. 修复 celery_config.py

**在 Celery Worker 启动时强制设置环境变量：**

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ⚠️ 在导入 settings 之前先设置 Hugging Face 环境变量
from core import settings

# ⚠️ 为 Celery Worker 强制设置 Hugging Face 离线模式环境变量
cache_dir = os.path.abspath(settings.TRANSFORMERS_CACHE)
os.environ['HF_HOME'] = cache_dir
os.environ['HUGGINGFACE_HUB_CACHE'] = cache_dir
os.environ['HF_ENDPOINT'] = settings.HF_ENDPOINT
os.environ['HF_HUB_OFFLINE'] = '1'  # ✅ 关键：启用离线模式
os.environ['TRANSFORMERS_OFFLINE'] = '1'

print(f"🔧 [Celery] HF_HOME: {os.environ.get('HF_HOME')}")
print(f"🔧 [Celery] HF_HUB_OFFLINE: {os.environ.get('HF_HUB_OFFLINE')}")

from celery import Celery  # ✅ 现在才导入 Celery
```

## 📋 环境变量说明

| 环境变量 | 值 | 作用 |
|---------|-----|------|
| `HF_HOME` | 缓存目录绝对路径 | ✅ **推荐**：统一的 Hugging Face 缓存根目录 |
| `HUGGINGFACE_HUB_CACHE` | 缓存目录绝对路径 | Hub 模型缓存目录 |
| `HF_ENDPOINT` | `https://hf-mirror.com` | Hugging Face 镜像地址（国内加速） |
| `HF_HUB_OFFLINE` | `'1'` | ✅ **最关键**：启用离线模式，不从网络下载 |
| `TRANSFORMERS_OFFLINE` | `'1'` | Transformers 库离线模式 |

## 🎯 你的模型文件位置

你的 4.2GB 模型文件已经正确下载到：
```
D:\86152\tiku-xiangmu\Medical-Assistant\FastAPI1\cache\models--microsoft--llmlingua-2-xlm-roberta-large-meetingbank\snapshots\ebaba9b0e874dadd3003ffcff828e4397e568089\
```

包含以下文件：
- `model.safetensors` (2132.25 MB) - 主模型文件
- `tokenizer.json` (16.29 MB) - 分词器
- `config.json` - 配置文件
- `tokenizer_config.json` - 分词器配置
- `special_tokens_map.json` - 特殊token映射

## 🧪 测试验证

运行测试脚本验证修复：

```bash
cd D:\86152\tiku-xiangmu\Medical-Assistant\FastAPI1
python test_celery_llmlingua.py
```

预期输出：
```
🔧 [Celery] HF_HOME: D:\...\FastAPI1\cache
🔧 [Celery] HF_HUB_OFFLINE: 1
✅ [LLMLingua] 找到本地模型缓存: D:\...\cache\models--microsoft--llmlingua-2-xlm-roberta-large-meetingbank
✅ LLMLingua 压缩器初始化成功！
所有测试通过！
```

## 🚀 重启 Celery Worker

修复后需要重启 Celery Worker：

```bash
# 停止现有的 Celery Worker（Ctrl+C）

# 重新启动
cd D:\86152\tiku-xiangmu\Medical-Assistant\FastAPI1
celery -A core.celery_config worker --loglevel=info -Q ai_queue
```

## 💡 关键要点总结

1. **不要使用 `local_files_only` 参数**：`PromptCompressor` 不支持此参数
2. **使用 `HF_HOME` 而非 `TRANSFORMERS_CACHE`**：后者已被废弃
3. **必须设置 `HF_HUB_OFFLINE='1'`**：这是启用离线模式的关键
4. **在 Celery Worker 启动时重新设置环境变量**：防止进程间环境变量丢失
5. **使用绝对路径**：避免相对路径在不同工作目录下失效

## 🔧 常见问题

### Q: 为什么我有 4.2GB 的模型文件还是初始化失败？
A: 因为代码中使用了不支持的 `local_files_only` 参数，导致 TypeError。即使模型文件存在，也无法正确加载。

### Q: 为什么设置了环境变量还是尝试连接网络？
A: 可能原因：
1. 使用了废弃的 `TRANSFORMERS_CACHE` 而非 `HF_HOME`
2. 没有设置 `HF_HUB_OFFLINE='1'`
3. Celery Worker 进程中没有正确继承环境变量

### Q: 如何确认离线模式已启用？
A: 查看启动日志中的 `HF_HUB_OFFLINE: 1` 输出，以及确保没有网络连接尝试。
