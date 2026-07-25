import json
import os

# 定义常见分辨率预设列表
DEFAULT_RESOLUTION_PRESETS = [
    "1K",
    "2K",
    "4K",
    "8K",
]

# 分辨率预设对应的数值映射
RESOLUTION_VALUE_MAP = {
    "1K": 1024,
    "2K": 2048,
    "4K": 4096,
    "8K": 8192,
}

class ResolutionPresetSelector:
    """分辨率预设选择器节点 - 提供常见分辨率名称的快速选择
    支持从预设列表中快速选择常用的分辨率名称，包括1K、2K、4K和8K等标准分辨率名称
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # 分辨率预设选项
        resolution_options = DEFAULT_RESOLUTION_PRESETS
        
        return {
            "required": {
                "resolution_preset": (resolution_options, {
                    "default": resolution_options[0] if resolution_options else "",
                    "label": "分辨率预设",
                    "description": "选择预设的分辨率"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("resolution", "resolution_value")
    FUNCTION = "get_resolution"
    CATEGORY = "❤️❤️❤️XnanTool/预设"
    
    def get_resolution(self, resolution_preset):
        """解析选中的分辨率预设，返回用户选择的选项名称和对应的数值"""
        # 获取对应的数值
        value = RESOLUTION_VALUE_MAP.get(resolution_preset, 0)
        # 返回分辨率名称和数值
        return (resolution_preset, value)

# 导出节点映射和显示名称映射
# 注册节点
NODE_CLASS_MAPPINGS = {
    "ResolutionPresetSelector": ResolutionPresetSelector,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "ResolutionPresetSelector": "分辨率预设",
}

# 导出映射（必须）
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]