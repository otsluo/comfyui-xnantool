# 预设管理节点模块初始化文件

# 导入预设管理相关节点
from .size_presets_node import SizeSelector
from .image_video_prompt_presets_node import ImageVideoPromptSelector, ImageVideoPromptManager, PresetImageUploadNode
from .random_prompt_generator_group_node import RandomPromptGeneratorGroupNode, RandomPromptGeneratorNode


# 定义节点映射
NODE_CLASS_MAPPINGS = {
    "SizeSelector": SizeSelector,
    "ImageVideoPromptSelector": ImageVideoPromptSelector,
    "ImageVideoPromptManager": ImageVideoPromptManager,
    "PresetImageUploadNode": PresetImageUploadNode,
    "RandomPromptGeneratorGroupNode": RandomPromptGeneratorGroupNode,
    "RandomPromptGeneratorNode": RandomPromptGeneratorNode,
}

# 定义节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "SizeSelector": "尺寸预设",
    "ImageVideoPromptSelector": "图片视频提示词预设",
    "ImageVideoPromptManager": "图片视频提示词预设管理器",
    "PresetImageUploadNode": "预设图像上传节点",
    "RandomPromptGeneratorGroupNode": "随机提示词生成器组",
    "RandomPromptGeneratorNode": "随机提示词生成器",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']