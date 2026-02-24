import json
import os

class DimensionMultiplierNode:
    """尺寸倍数节点 - 根据倍数调整输入的宽度和高度
    
    支持根据设定的倍数调整输入的宽度和高度值
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "multiplier": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 100.0,
                    "step": 0.01,
                    "label": "倍数",
                    "description": "尺寸调整倍数"
                })
            },
            "optional": {
                "width": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                    "label": "宽度",
                    "description": "输入的宽度值",
                    "forceInput": True
                }),
                "height": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                    "label": "高度",
                    "description": "输入的高度值",
                    "forceInput": True
                })
            }
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "multiply_dimensions"
    CATEGORY = "XnanTool/预设"
    
    def multiply_dimensions(self, multiplier, width=None, height=None):
        """根据倍数调整尺寸"""
        # 如果没有从端口输入宽高，则使用默认值
        if width is None:
            width = 512
        if height is None:
            height = 512
            
        output_width = int(width * multiplier)
        output_height = int(height * multiplier)
        
        return (output_width, output_height)

# 导出节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "DimensionMultiplierNode": DimensionMultiplierNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DimensionMultiplierNode": "尺寸倍数",
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]