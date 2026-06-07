# ai_service.py
import dashscope
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def _get_api_key():
    """动态获取API密钥"""
    return getattr(settings, 'TONGYI_API_KEY', '').strip()

def generate_study_plan(subjects, time_frame, goals):
    """生成学习计划"""
    # 确保每次调用时都使用最新的API密钥
    dashscope.api_key = _get_api_key()

    if not dashscope.api_key:
        raise ValueError("TONGYI_API_KEY 未正确配置")

    prompt = f"""
    先说明今天的日期。
    请为以下学习需求生成详细的学习计划：
    科目：{subjects}
    时间安排：{time_frame}
    学习目标：{goals}

    要求：
    1. 按周/天分解学习任务
    2. 包含具体的学习内容和时间分配
    3. 提供学习建议和重点难点提示
    4. 计划生成后，请讲个笑话，增加趣味性。
    """

    try:
        response = dashscope.Generation.call(
            model='qwen-plus',
            prompt=prompt,
            max_tokens=2000
        )

        # 添加响应检查
        if hasattr(response, 'output') and hasattr(response.output, 'text'):
            return response.output.text
        else:
            return "AI服务响应异常，请稍后重试"

    except Exception as e:
        print(f"AI服务调用错误: {e}")
        return f"AI服务调用失败: {str(e)}"


def analyze_wrong_topics(wrong_topics_data):
    """分析错题本数据"""
    prompt = f"""
    先讲个笑话
    请分析以下错题数据并提供学习建议：
    错题信息：{wrong_topics_data}
    如果错题信息为空，请说明今天的日期，并提醒用户及时添加错题。

    要求：
    1. 统计错误知识点分布
    2. 识别薄弱环节
    3. 提供针对性学习建议
    4. 制定复习策略
    """

    response = dashscope.Generation.call(
        model='qwen-plus',
        prompt=prompt,
        max_tokens=1500
    )
    return response.output.text

