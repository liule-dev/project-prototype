# exam/ai_service.py
import requests
import json
import os
from django.conf import settings


class QwenAIService:
    def __init__(self):
        # 从环境变量或settings获取API密钥
        self.api_key = getattr(settings, 'QWEN_API_KEY', None) or os.environ.get('QWEN_API_KEY')
        if not self.api_key:
            raise ValueError("未找到通义千问API密钥，请在环境变量或settings.py中配置QWEN_API_KEY")
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def generate_exam_questions(self, subject, knowledge_points, difficulty_distribution, count):
        """
        使用通义千问生成考试题目
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # 构建提示词
        prompt = f"""
        请为{subject}科目生成{count}道题目用于考试组卷。
        知识点要求：{', '.join(knowledge_points) if isinstance(knowledge_points, list) else knowledge_points}
        难度分布要求：{difficulty_distribution}

        要求：
        1. 题目类型包括单选题和多选题
        2. 每道题提供标准答案
        3. 每道题附带解析说明
        4. 标注题目难度（简单/中等/困难）
        5. 以JSON格式返回结果

        返回格式示例：
        {{
            "questions": [
                {{
                    "content": "题目内容",
                    "type": "single_choice",  // single_choice 或 multiple_choice
                    "options": {{
                        "A": "选项A内容",
                        "B": "选项B内容",
                        "C": "选项C内容",
                        "D": "选项D内容"
                    }},
                    "answer": "A",  // 单选题为单个字母，多选题为字母组合如"AB"
                    "difficulty": "中等",
                    "analysis": "题目解析",
                    "knowledge_point": "相关知识点"
                }}
            ]
        }}
        """

        data = {
            "model": "qwen-plus",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "result_format": "message"
            }
        }

        try:
            response = requests.post(self.base_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()

            # 解析返回结果
            if 'output' in result and 'choices' in result['output']:
                content = result['output']['choices'][0]['message']['content']
                # 这里需要解析AI返回的JSON内容
                # 实际实现中可能需要更复杂的解析逻辑
                return content
            else:
                raise Exception("API返回格式不正确")
        except Exception as e:
            raise Exception(f"调用通义千问API失败: {str(e)}")
