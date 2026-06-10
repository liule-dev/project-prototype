"""
AI 批改服务
用于主观题智能批改
"""
import re
from .base import QwenAIService


class GradingService(QwenAIService):
    """AI 批改服务类"""
    
    def grade_subjective_question(self, question_content, student_answer, 
                                   standard_answer, max_score):
        """
        使用通义千问对主观题进行 AI 打分
        
        Args:
            question_content: 题目内容
            student_answer: 学生答案
            standard_answer: 标准答案
            max_score: 满分分数
        
        Returns:
            int: AI 给出的分数（不超过 max_score）
        """
        prompt = f"""你是一位经验丰富的阅卷老师，请根据以下信息为学生答案打分：

题目：{question_content}
标准答案：{standard_answer}
学生答案：{student_answer}
满分：{max_score}分

评分要求：
1. 仔细对比学生答案与标准答案的关键点
2. 根据答案的完整性、准确性给出合理分数
3. 只返回一个数字分数，不要有任何其他文字

请打分："""

        try:
            output_text = self._call_qwen_api(
                messages=[{'role': 'user', 'content': prompt}],
                model='qwen-plus',
                temperature=0.3,  # 控制输出确定性
                max_tokens=100
            )
            
            # 正则提取分数
            numbers = re.findall(r'\d+', output_text)
            if numbers:
                score = int(numbers[0])
                # 范围校验：确保分数在合理范围内
                return min(score, max_score)
            else:
                raise Exception("无法从 AI 响应中提取分数")
                
        except Exception as e:
            print(f"AI 批改失败: {str(e)}")
            raise
