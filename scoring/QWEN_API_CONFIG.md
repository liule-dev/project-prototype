# 通义千问API配置说明

## 获取API密钥

1. 访问阿里云官网并登录您的账号
2. 进入[通义千问控制台](https://dashscope.console.aliyun.com/)
3. 创建API密钥（如果还没有的话）
4. 复制您的API密钥

## 配置方法

### 方法一：修改.env文件（推荐）

打开项目根目录下的`.env`文件，将其中的`your_api_key_here`替换为您真实的API密钥：

```
# 通义千问API配置
# 请将your_api_key_here替换为您在阿里云申请的真实API密钥
QWEN_API_KEY=your_real_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/api11/v1
QWEN_MODEL=qwen-plus
```

### 方法二：设置环境变量

您也可以通过设置系统环境变量来配置API密钥：

Windows:
```cmd
set QWEN_API_KEY=your_real_api_key_here
```

Linux/Mac:
```bash
export QWEN_API_KEY=your_real_api_key_here
```

## 可用模型

- `qwen-turbo`: 速度快，成本低
- `qwen-plus`: 平衡速度和效果（默认）
- `qwen-max`: 效果最佳，适合复杂任务

## 测试配置

配置完成后，可以运行以下命令测试连接：

```bash
python test_qwen_api.py
```

如果配置正确，您将看到AI生成的内容；如果配置错误，会显示相应的错误信息。