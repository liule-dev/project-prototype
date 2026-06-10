"""
学习辅助服务
用于生成学习计划、分析错题等
"""
import dashscope
from django.conf import settings


class StudyAssistantService:
    """学习辅助服务类（使用 dashscope SDK）"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'TONGYI_API_KEY', '')
        dashscope.api_key = self.api_key
    
    def generate_study_plan(self, subjects, time_frame, goals):
        """
        生成个性化学习计划
        
        Args:
            subjects: 学习科目列表
            time_frame: 时间框架
            goals: 学习目标
        
        Returns:
            str: AI 生成的学习计划文本
        """
        prompt = f"""请为以下学习需求生成详细的学习计划：

学习科目：{', '.join(subjects)}
时间框架：{time_frame}
学习目标：{goals}

请提供：
1. 每日学习时间安排
2. 各科目学习重点
3. 阶段性目标检查点
4. 复习建议

请以清晰的格式输出学习计划。"""

        try:
            response = dashscope.Generation.call(
                model='qwen-plus',
                prompt=prompt,
                max_tokens=2000
            )
            
            if response.status_code == 200:
                return response.output.text
            else:
                raise Exception(f"API 调用失败: {response.message}")
                
        except Exception as e:
            print(f"生成学习计划失败: {str(e)}")
            raise
    
    def analyze_wrong_topics(self, wrong_topics_data):
        """
        分析错题本数据并提供学习建议
        
        Args:
            wrong_topics_data: 错题数据列表
        
        Returns:
            str: AI 分析结果和建议
        """
        # 构建错题摘要
        topics_summary = "\n".join([
            f"- {topic.get('subject', '未知科目')}: {topic.get('topic_content', '')[:50]}"
            for topic in wrong_topics_data[:10]  # 最多分析10道错题
        ])
        
        prompt = f"""请分析以下错题数据并提供学习建议：

错题列表：
{topics_summary}

请提供：
1. 薄弱知识点分析
2. 错误原因总结
3. 针对性学习建议
4. 推荐复习重点

请以专业教师的角度给出分析。"""

        try:
            response = dashscope.Generation.call(
                model='qwen-plus',
                prompt=prompt,
                max_tokens=1500
            )
            
            if response.status_code == 200:
                return response.output.text
            else:
                raise Exception(f"API 调用失败: {response.message}")
                
        except Exception as e:
            print(f"分析错题失败: {str(e)}")
            raise
    
    def chat_with_ai(self, user_message, conversation_history=None):
        """
        与 AI 进行对话
        
        Args:
            user_message: 用户消息
            conversation_history: 对话历史（可选）
        
        Returns:
            str: AI 回复
        """
        messages = [{'role': 'user', 'content': user_message}]
        
        # 如果有对话历史，添加到消息列表
        if conversation_history:
            messages = conversation_history + messages
        
        try:
            response = dashscope.Generation.call(
                model='qwen-turbo',
                messages=messages,
                result_format='message'
            )
            
            if response.status_code == 200:
                return response.output.choices[0]['message']['content']
            else:
                raise Exception(f"API 调用失败: {response.message}")
                
        except Exception as e:
            print(f"AI 对话失败: {str(e)}")
            raise
