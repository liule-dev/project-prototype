import requests
import json
import os
import dotenv
from django.conf import settings

class QwenAIService:
    def __init__(self):
        # 从 .env 文件读取配置（与 Agent.py 使用相同的配置源）
        dotenv_path = dotenv.find_dotenv()
        # 尝试读取两种配置格式
        self.api_key = dotenv.get_key(dotenv_path, "api_key") or dotenv.get_key(dotenv_path, "QWEN_API_KEY")
        self.base_url = dotenv.get_key(dotenv_path, "base_url") or dotenv.get_key(dotenv_path, "QWEN_BASE_URL")
        self.model = dotenv.get_key(dotenv_path, "model") or dotenv.get_key(dotenv_path, "QWEN_MODEL") or 'qwen-plus'
        
        # 打印配置用于调试
        print(f"AI服务配置 - api_key: {'已设置' if self.api_key else '未设置'}, base_url: {self.base_url}, model: {self.model}")
        
    def analyze_and_grade_question(self, question_content, standard_answer, student_answer):
        """
        使用通义千问分析题目并批改学生答案
        :param question_content: 题目内容
        :param standard_answer: 标准答案
        :param student_answer: 学生答案
        :return: 包含分析结果和评分的字典
        """
        prompt = f"""
        你是一个专业的教育评分助手，请根据以下信息对学生的答案进行分析和评分：

        题目内容：
        {question_content}

        标准答案：
        {standard_answer}

        学生答案：
        {student_answer}

        请按照以下格式返回结果：
        {{
            "score": 0-100之间的分数,
            "analysis": "对答案的详细分析，包括正确和错误之处",
            "feedback": "给学生的反馈建议"
        }}

        注意：
        1. 分数必须是0-100之间的整数
        2. 分析应该具体指出学生答案中的正确和错误部分
        3. 反馈应该具有建设性，帮助学生改进
        """

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model,
            'input': {
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一个专业的教育评分助手'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            },
            'parameters': {
                'temperature': 0.3,
                'top_p': 0.8,
                'max_tokens': 1500,
                'response_format': 'json_object'
            }
        }

        try:
            response = requests.post(
                f'{self.base_url}/services/aigc/text-generation/generation',
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                output_text = result['output']['text']
                # 解析返回的JSON
                try:
                    return json.loads(output_text)
                except json.JSONDecodeError:
                    # 如果解析失败，返回原始文本
                    return {
                        'score': 0,
                        'analysis': f'AI分析结果: {output_text}',
                        'feedback': '无法解析AI分析结果'
                    }
            else:
                return {
                    'score': 0,
                    'analysis': f'AI服务调用失败，状态码: {response.status_code}',
                    'feedback': 'AI服务调用失败，请稍后重试'
                }
        except Exception as e:
            return {
                'score': 0,
                'analysis': f'AI服务调用异常: {str(e)}',
                'feedback': 'AI服务调用异常，请稍后重试'
            }

    def generate_question_analysis(self, question_content, topic_knowledge):
        """
        使用通义千问生成题目解析
        :param question_content: 题目内容
        :param topic_knowledge: 相关知识点
        :return: 题目解析
        """
        prompt = f"""
        请为以下题目生成详细的解析：

        题目内容：
        {question_content}

        相关知识点：
        {topic_knowledge}

        请提供：
        1. 题目考察的知识点
        2. 解题思路和步骤
        3. 正确答案及解析
        4. 易错点提醒
        """

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model,
            'input': {
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一个专业的教育题库分析师'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            },
            'parameters': {
                'temperature': 0.5,
                'top_p': 0.8,
                'max_tokens': 2000
            }
        }

        try:
            response = requests.post(
                f'{self.base_url}/services/aigc/text-generation/generation',
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['output']['text']
            else:
                return f"AI服务调用失败，状态码: {response.status_code}"
        except Exception as e:
            return f"AI服务调用异常: {str(e)}"

    def grade_subjective_question(self, question_content, student_answer, standard_answer, max_score):
        """
        使用通义千问对主观题进行AI打分
        :param question_content: 题目内容
        :param student_answer: 学生答案
        :param standard_answer: 标准答案
        :param max_score: 满分
        :return: 分数 (0-max_score)
        """
        prompt = f"""你是一位经验丰富的阅卷老师，请根据以下信息为这道主观题打分：

【题目内容】
{question_content}

【学生答案】
{student_answer}

【标准答案】
{standard_answer}

【满分】
{max_score}分

【评分标准】
1. 答案与标准答案的核心要点匹配程度
2. 论述的完整性和逻辑性
3. 表达的准确性和规范性
4. 如果有创新性见解可适当加分

请严格按照以下格式返回结果，只返回一个0-{max_score}之间的整数分数，不要返回任何其他内容：
分数"""

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # 使用 OpenAI 兼容格式
        data = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'top_p': 0.8,
            'max_tokens': 100
        }

        try:
            # 使用 OpenAI 兼容的 API 端点
            api_url = f'{self.base_url}/chat/completions'
            
            response = requests.post(
                api_url,
                headers=headers,
                data=json.dumps(data),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # OpenAI 兼容格式的响应
                output_text = result['choices'][0]['message']['content'].strip()
                
                # 提取数字
                import re
                numbers = re.findall(r'\d+', output_text)
                if numbers:
                    score = int(numbers[0])
                    # 确保分数不超过满分
                    return min(score, max_score)
                else:
                    raise Exception(f"AI返回格式不正确: {output_text}")
            else:
                raise Exception(f"AI服务调用失败，状态码: {response.status_code}, 响应: {response.text}")
        except Exception as e:
            raise Exception(f"调用AI打分失败: {str(e)}")