"""
AI 批改服务
用于主观题智能批改
"""
import re
import json
from .base import QwenAIService


class GradingAgent(QwenAIService):
    """
    基于 ReAct 思维模式的智能阅卷 Agent
    Reasoning (推理): 分析学生答案与标准答案的匹配度
    Acting (行动): 根据推理结果输出标准化分数
    """

    def grade_subjective_question(self, question_content, student_answer,
                                  standard_answer, max_score):
        """
        使用 ReAct 模式对主观题进行 AI 打分

        Args:
            question_content: 题目内容
            student_answer: 学生答案
            standard_answer: 标准答案
            max_score: 满分分数

        Returns:
            dict: {'score': int, 'reasoning': str}
        """
        # 1. ReAct Prompt 设计：引导模型先思考后行动
        prompt = f"""你是一位严谨的阅卷老师。请按照以下步骤（ReAct模式）为学生答案打分：

【题目】：{question_content}
【标准答案】：{standard_answer}
【学生答案】：{student_answer}
【满分】：{max_score}分

【执行步骤】：
1. Reasoning (推理)：逐条对比学生答案是否包含标准答案中的关键得分点，并说明理由。
2. Acting (行动)：根据推理结果，给出一个最终的整数分数。

【输出格式要求】：
请严格仅输出一个 JSON 对象，不要包含 Markdown 标记或其他文字：
{{
    "reasoning": "你的详细评分推理过程",
    "score": 最终分数
}}
"""

        try:
            # 2. Agent 执行：调用 LLM 进行推理和行动
            output_text = self._call_qwen_api(
                messages=[{'role': 'user', 'content': prompt}],
                model='qwen-plus',
                temperature=0.2,  # 降低温度，提高逻辑推理的稳定性
                max_tokens=500  # 增加 Token 以容纳推理过程
            )

            # 3. Output Parser (输出解析器)：处理模型的行动结果
            return self._parse_agent_output(output_text, max_score)

        except Exception as e:
            print(f"Grading Agent 执行失败: {str(e)}")
            # 容错处理：返回 0 分和错误信息，避免程序崩溃
            return {'score': 0, 'reasoning': f'Agent Error: {str(e)}'}

    def _parse_agent_output(self, text, max_score):
        """
        解析 Agent 输出的 JSON，并进行业务规则校验
        """
        # 尝试提取 JSON 部分（防止模型啰嗦）
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            raise Exception("Agent 未返回有效的 JSON 格式")

        try:
            data = json.loads(match.group())
            score = int(data.get('score', 0))
            reasoning = data.get('reasoning', '无推理过程')

            # 4. 业务规则校验 (Guardrails)
            # 确保分数在 0 到 max_score 之间
            final_score = max(0, min(score, max_score))

            return {
                'score': final_score,
                'reasoning': reasoning
            }
        except json.JSONDecodeError:
            raise Exception("Agent 输出的 JSON 解析失败")
