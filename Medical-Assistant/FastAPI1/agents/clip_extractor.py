"""
CLIP 特征提取器
使用 BioMedCLIP 实现图文统一编码
"""
import torch
import torch.nn.functional as F
from core import settings
import logging

logger = logging.getLogger(__name__)


class CLIPFeatureExtractor:
    """医疗领域 CLIP 特征提取器"""
    
    def __init__(self, model_name: str = None):
        """
        初始化 CLIP 特征提取器
        
        Args:
            model_name: 模型名称，默认使用备用 CLIP 模型
        """
        self.model_name = model_name or settings.CLIP_MODEL_NAME
        logger.info(f"正在加载 CLIP 模型：{self.model_name}")
        
        # 设置国内镜像源和环境变量
        import os
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        os.environ['TRANSFORMERS_CACHE'] = './cache'
        
        try:
            from transformers import CLIPProcessor, CLIPModel
            
            # 直接使用 CLIP 模型 (更稳定)
            self.processor = CLIPProcessor.from_pretrained(
                self.model_name,
                cache_dir="./cache",
                local_files_only=False,  # 优先尝试下载，失败则使用缓存
                use_fast=True  # 使用快速处理器
            )
            self.model = CLIPModel.from_pretrained(
                self.model_name,
                cache_dir="./cache",
                local_files_only=False
            )
            
            self.processor_type = "clip"
            logger.info(f"✅ CLIP 模型加载成功：{self.model_name}")
            
        except Exception as e:
            logger.warning(f"CLIP 模型加载失败：{e}")
            logger.error("请检查网络连接或手动下载模型到 ./cache 目录")
            raise RuntimeError(f"CLIP 模型加载失败：{e}")
        
        # 设置设备和模型
        self.model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # 自动检测特征维度
        if hasattr(self.model.config, 'projection_dim'):
            self.feature_dim = self.model.config.projection_dim
        else:
            self.feature_dim = 512
        
        logger.info(f"模型加载完成，设备：{self.device}, 特征维度：{self.feature_dim}")
    
    def extract_image_features(self, image):
        """
        提取图片特征
        
        Args:
            image: PIL.Image 图片对象
            
        Returns:
            np.ndarray 特征向量（已归一化）
        """
        try:
            if self.processor_type == "huggingface" or self.processor_type == "clip":
                # BioMedCLIP
                inputs = self.processor(images=image, return_tensors="pt", padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    image_features = self.model.get_image_features(**inputs)
                    image_features = F.normalize(image_features, p=2, dim=-1)
                    
            elif self.processor_type == "clip_backup" or self.processor_type == "clip":
                # CLIP 模型 (包括备用)
                inputs = self.processor(images=image, return_tensors="pt", padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    image_features = self.model.get_image_features(**inputs)
                    image_features = F.normalize(image_features, p=2, dim=-1)
            else:
                raise RuntimeError("未知的处理器类型")
            
            return image_features.squeeze().cpu().numpy()
            
        except Exception as e:
            logger.error(f"提取图片特征失败：{e}")
            raise
    
    def encode_text(self, text: str):
        """
        编码文本为特征向量
        
        Args:
            text: 文本内容
            
        Returns:
            np.ndarray 特征向量（已归一化）
        """
        try:
            if self.processor_type == "huggingface" or self.processor_type == "clip":
                # BioMedCLIP
                inputs = self.processor(text=[text], return_tensors="pt", padding=True, truncation=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    text_features = self.model.get_text_features(**inputs)
                    text_features = F.normalize(text_features, p=2, dim=-1)
                    
            elif self.processor_type == "clip_backup" or self.processor_type == "clip":
                # CLIP 模型 (包括备用)
                inputs = self.processor(text=[text], return_tensors="pt", padding=True, truncation=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    text_features = self.model.get_text_features(**inputs)
                    text_features = F.normalize(text_features, p=2, dim=-1)
            else:
                raise RuntimeError("未知的处理器类型")
            
            return text_features.squeeze().cpu().numpy()
            
        except Exception as e:
            logger.error(f"编码文本失败：{e}")
            raise


# 全局 CLIP 特征提取器实例
clip_feature_extractor = CLIPFeatureExtractor()
