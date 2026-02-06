import json
import os

# 定义常见分辨率预设列表
DEFAULT_RESOLUTION_PRESETS = [
    "1K",
    "2K",
    "4K",
    "8K",
]

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
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("resolution",)
    FUNCTION = "get_resolution"
    CATEGORY = "XnanTool/预设"
    
    def get_resolution(self, resolution_preset):
        """解析选中的分辨率预设，返回用户选择的选项名称"""
        # 直接返回用户选择的选项名称
        return (resolution_preset,)

# 导出节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "ResolutionPresetSelector": ResolutionPresetSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ResolutionPresetSelector": "分辨率预设",
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]