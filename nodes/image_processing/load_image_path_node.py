import torch
import numpy as np
from PIL import Image
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadImagePathNode:
    """
    路径图片加载节点
    从指定文件路径加载图像文件并转换为ComfyUI可用的格式
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_path": ("STRING", {
                    "label": "图片路径",
                    "description": "输入图片的完整文件路径",
                    "default": "",
                    "multiline": True,
                    "dynamicPrompts": False
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "image_path")
    FUNCTION = "load_image_from_path"
    CATEGORY = "XnanTool/图像处理"
    
    @classmethod
    def IS_CHANGED(cls, image_path):
        # 如果图像文件存在，返回其修改时间，否则返回0
        if os.path.exists(image_path):
            return os.path.getmtime(image_path)
        return 0

    @classmethod
    def VALIDATE_INPUTS(cls, image_path):
        if not os.path.exists(image_path):
            return "Invalid image file path: {}".format(image_path)
        # 检查文件扩展名是否为支持的图像格式
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff']
        _, ext = os.path.splitext(image_path.lower())
        if ext not in supported_extensions:
            return "Unsupported image format: {}".format(ext)
        return True

    def load_image_from_path(self, image_path):
        """
        从指定路径加载图像文件并转换为ComfyUI可用的格式
        
        Args:
            image_path (str): 图像文件的完整路径
            
        Returns:
            tuple: 包含图像张量和文件路径的元组
        """
        try:
            # 检查图像文件是否存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图像文件不存在: {image_path}")
            
            # 检查是否为支持的图像格式
            supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff']
            _, ext = os.path.splitext(image_path.lower())
            if ext not in supported_extensions:
                raise ValueError(f"不支持的图像格式: {ext}")
            
            # 使用PIL加载图像
            image = Image.open(image_path)
            
            # 转换为RGB格式（如果需要）
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # 转换为numpy数组
            image_np = np.array(image).astype(np.float32) / 255.0
            
            # 转换为PyTorch张量 (H, W, C) -> (1, H, W, C)
            image_tensor = torch.from_numpy(image_np)[None,]
            
            logger.info(f"图像已从路径加载: {image_path}")
            logger.info(f"图像尺寸: {image.size}")
            logger.info(f"图像模式: {image.mode}")
            
            return (image_tensor, image_path)
            
        except Exception as e:
            logger.error(f"从路径加载图像过程中发生错误: {str(e)}")
            raise e

# 注册节点
NODE_CLASS_MAPPINGS = {
    "LoadImagePathNode": LoadImagePathNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImagePathNode": "路径图片加载节点"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]