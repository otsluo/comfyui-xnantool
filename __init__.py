"""
ComfyUI XNAN Tool
提供各种实用的ComfyUI节点，包括LoRA模型支持等功能。
"""

# 从节点文件导入节点类和映射字典
from .modelscope_api_lora_node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 版本信息
__version__ = "0.0.1"

# 包的描述信息
__description__ = "ComfyUI XNAN Tool - 提供各种扩展节点功能"

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "__version__",
    "__description__"
]