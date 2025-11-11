import torch
import numpy as np
from PIL import Image
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageFormatConverterNode:
    """
    图像格式转换器节点
    支持将图像转换为JPEG、PNG、WEBP或BMP格式
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {
                    "label": "输入图像",
                    "description": "需要转换格式的图像批次"
                }),
                "format": (["JPEG", "PNG", "WEBP", "BMP"], {
                    "label": "目标格式",
                    "description": "选择输出图像格式",
                    "default": "PNG"
                }),
                "quality": ("INT", {
                    "label": "JPEG/WebP质量",
                    "description": "JPEG或WebP格式的质量（1-100）",
                    "default": 100,
                    "min": 1,
                    "max": 100,
                    "step": 1
                }),
                "optimize": ("BOOLEAN", {
                    "label": "优化PNG",
                    "description": "是否优化PNG文件大小",
                    "default": True
                })
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("converted_images",)
    FUNCTION = "convert_format"
    CATEGORY = "XnanTool/图像处理"

    def convert_format(self, images, format, quality, optimize):
        """
        批量转换图像格式
        
        Args:
            images: 输入图像张量 (B, H, W, C)
            format: 目标格式
            quality: JPEG/WebP质量
            optimize: 是否优化PNG
            
        Returns:
            tuple: 处理后的图像
        """
        try:
            # 处理单个图像或图像批次
            if images.dim() == 3:
                # 单个图像 (H, W, C)
                images = images.unsqueeze(0)
            
            batch_size = images.shape[0]
            processed_images = []
            
            for i in range(batch_size):
                # 将tensor转换为PIL图像
                image_tensor = images[i]
                # 转换为0-255范围的numpy数组
                image_np = (image_tensor.cpu().numpy() * 255).astype(np.uint8)
                # 创建PIL图像
                pil_image = Image.fromarray(image_np, 'RGB')
                
                # 转换格式
                converted_image = self._convert_image_format(pil_image, format, quality, optimize)
                
                # 转换回tensor格式
                processed_tensor = self._pil_to_tensor(converted_image)
                processed_images.append(processed_tensor)
            
            # 合并批次
            result_batch = torch.cat(processed_images, dim=0)
            
            return (result_batch,)
            
        except Exception as e:
            logger.error(f"转换图像格式时发生错误: {str(e)}")
            raise Exception(f"图像格式转换失败: {str(e)}")

    def _convert_image_format(self, image, format, quality, optimize):
        """转换图像格式"""
        # 创建一个临时的BytesIO对象来保存转换后的图像
        from io import BytesIO
        buffer = BytesIO()
        
        # 根据格式保存图像
        if format == "JPEG":
            # 确保图像是RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(buffer, format="JPEG", quality=quality, optimize=True)
        elif format == "WEBP":
            # 确保图像是RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(buffer, format="WEBP", quality=quality, method=6)
        elif format == "PNG":
            image.save(buffer, format="PNG", optimize=optimize)
        elif format == "BMP":
            image.save(buffer, format="BMP")
        
        # 从缓冲区重新加载图像
        buffer.seek(0)
        converted_image = Image.open(buffer).copy()
        
        return converted_image

    def _pil_to_tensor(self, pil_image):
        """将PIL图像转换为tensor格式"""
        # 转换为numpy数组并归一化到0-1范围
        numpy_image = np.array(pil_image).astype(np.float32) / 255.0
        # 转换为tensor并添加批次维度
        tensor_image = torch.from_numpy(numpy_image).unsqueeze(0)
        return tensor_image


# 注册节点
NODE_CLASS_MAPPINGS = {
    "ImageFormatConverterNode": ImageFormatConverterNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageFormatConverterNode": "图像格式转换器"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]