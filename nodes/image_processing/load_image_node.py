import torch
import numpy as np
from PIL import Image
import os
import logging
import folder_paths

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadImageNode:
    """
    图像加载节点
    加载图像文件并转换为ComfyUI可用的格式
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取image_video_prompt_presets_node文件夹路径
        presets_dir = os.path.join(os.path.dirname(__file__), "image_video_prompt_presets_node")
        # 确保目录存在
        if not os.path.exists(presets_dir):
            os.makedirs(presets_dir)
            
        # 获取该目录下的所有文件
        files = [f for f in os.listdir(presets_dir) if os.path.isfile(os.path.join(presets_dir, f))]
        # 过滤图像文件
        image_files = folder_paths.filter_files_content_types(files, ["image"])
        
        return {
            "required": {
                "image_file": (sorted(image_files), {
                    "label": "图像文件",
                    "description": "选择要加载的图像文件（来自image_video_prompt_presets_node文件夹）",
                    "image_upload": True  # 添加图像上传支持
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "image_path")
    FUNCTION = "load_image"
    CATEGORY = "XnanTool/图像处理"
    
    @classmethod
    def IS_CHANGED(cls, image_file):
        # 获取image_video_prompt_presets_node文件夹路径
        presets_dir = os.path.join(os.path.dirname(__file__), "image_video_prompt_presets_node")
        # 构建完整的图像文件路径
        image_path = os.path.join(presets_dir, image_file)
        # 如果图像文件存在，返回其修改时间，否则返回0
        if os.path.exists(image_path):
            return os.path.getmtime(image_path)
        return 0

    @classmethod
    def VALIDATE_INPUTS(cls, image_file):
        # 获取image_video_prompt_presets_node文件夹路径
        presets_dir = os.path.join(os.path.dirname(__file__), "image_video_prompt_presets_node")
        # 构建完整的图像文件路径
        image_path = os.path.join(presets_dir, image_file)
        if not os.path.exists(image_path):
            return "Invalid image file: {}".format(image_file)
        return True

    def load_image(self, image_file):
        """
        加载图像文件并转换为ComfyUI可用的格式
        
        Args:
            image_file (str): 图像文件路径
            
        Returns:
            tuple: 包含图像张量和文件路径的元组
        """
        try:
            # 获取image_video_prompt_presets_node文件夹路径
            presets_dir = os.path.join(os.path.dirname(__file__), "image_video_prompt_presets_node")
            # 构建完整的图像文件路径
            image_path = os.path.join(presets_dir, image_file)
            
            # 检查图像文件是否存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图像文件不存在: {image_path}")
            
            # 使用PIL加载图像
            image = Image.open(image_path)
            
            # 转换为RGB格式（如果需要）
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # 转换为numpy数组
            image_np = np.array(image).astype(np.float32) / 255.0
            
            # 转换为PyTorch张量 (H, W, C) -> (1, H, W, C)
            image_tensor = torch.from_numpy(image_np)[None,]
            
            logger.info(f"图像已加载: {image_path}")
            logger.info(f"图像尺寸: {image.size}")
            logger.info(f"图像模式: {image.mode}")
            
            return (image_tensor, image_path)
            
        except Exception as e:
            logger.error(f"加载图像过程中发生错误: {str(e)}")
            raise e

# 注册节点
NODE_CLASS_MAPPINGS = {
    "LoadImageNode": LoadImageNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageNode": "加载图像-【Beta】"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]