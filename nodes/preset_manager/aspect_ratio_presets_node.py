import json
import os

# 定义常用比例预设列表
DEFAULT_ASPECT_RATIO_PRESETS = [
    # 正方形
    "1:1",
    
    # 竖屏比例
    "2:3",
    "3:4",
    "9:16",
    
    # 横屏比例
    "3:2",
    "4:3",
    "16:9",
    
    # 电影比例
    "21:9",
    "2:1",
    
    # 特殊比例
    "1:2",
    "5:4",
    "4:5",
]

class AspectRatioPresetSelector:
    """比例预设选择器节点 - 提供常用比例的快速选择
     
     支持常见的正方形、竖屏、横屏、电影和特殊比例预设
     """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # 比例预设选项
        ratio_options = DEFAULT_ASPECT_RATIO_PRESETS
        
        return {
            "required": {
                "aspect_ratio_preset": (ratio_options, {
                    "default": ratio_options[0] if ratio_options else "",
                    "label": "比例预设",
                    "description": "选择预设的宽高比"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("aspect_ratio",)
    FUNCTION = "get_aspect_ratio"
    CATEGORY = "XnanTool/预设"
    
    def get_aspect_ratio(self, aspect_ratio_preset):
        """解析选中的比例预设，返回比例值"""
        # 直接返回用户选择的比例预设
        return (aspect_ratio_preset,)

# 导出节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "AspectRatioPresetSelector": AspectRatioPresetSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioPresetSelector": "比例预设",
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]