import torch
import numpy as np
from PIL import Image, ImageDraw

class CreateImageNode:
    """创建指定尺寸和颜色的图片节点"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                    "display": "number"
                }),
                "height": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                    "display": "number"
                }),
                "color": ("STRING", {
                    "default": "#FFFFFF",
                    "multiline": False
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "create_image"
    CATEGORY = "XnanTool/图像处理"
    OUTPUT_NODE = False
    
    def create_image(self, width, height, color):
        # 解析颜色值
        if color.startswith('#'):
            # 处理十六进制颜色值
            hex_color = color.lstrip('#')
            if len(hex_color) == 6:
                rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            elif len(hex_color) == 3:
                rgb_color = tuple(int(hex_color[i:i+1]*2, 16) for i in (0, 1, 2))
            else:
                # 默认为白色
                rgb_color = (255, 255, 255)
        else:
            # 默认为白色
            rgb_color = (255, 255, 255)
        
        # 创建纯色图像
        image = Image.new('RGB', (width, height), rgb_color)
        
        # 转换为numpy数组并归一化到0-1范围
        image_np = np.array(image).astype(np.float32) / 255.0
        
        # 转换为tensor格式 (H, W, C) -> (1, H, W, C)
        image_tensor = torch.from_numpy(image_np)[None,]
        
        print(f"🖼️ 创建图像: {width}x{height}, 颜色: {color}")
        
        return (image_tensor,)

# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "CreateImageNode": CreateImageNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CreateImageNode": "创建图像"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']