"""
AI 服务基础类
提供通用的 API 调用方法和配置
"""
import requests
import json
from django.conf import settings


class QwenAIService:
    """通义千问 AI 服务基类"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'TONGYI_API_KEY', '')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.timeout = 30  # 统一超时时间：30秒
    
    def _call_qwen_api(self, messages, model='qwen-plus', temperature=0.3, 
                       max_tokens=2000, top_p=0.8):
        """
        通用 Qwen API 调用方法
        
        Args:
            messages: 消息列表
            model: 模型名称 (qwen-plus / qwen-turbo)
            temperature: 温度参数 (0-1)，控制输出随机性
            max_tokens: 最大 token 数
            top_p: 核采样参数
        
        Returns:
            str: AI 返回的文本内容
        """
        api_url = f"{self.base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'top_p': top_p,
            'max_tokens': max_tokens
        }
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                data=json.dumps(data),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise Exception("API 返回格式异常")
                
        except requests.exceptions.Timeout:
            raise Exception(f"AI API 请求超时（{self.timeout}秒）")
        except requests.exceptions.RequestException as e:
            raise Exception(f"AI API 请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"AI 服务错误: {str(e)}")
