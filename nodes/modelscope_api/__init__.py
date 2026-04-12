# ModelScope API节点模块初始化文件

# 导入ModelScope API相关节点
from .modelscope_api_text_to_image_node import modelscopeLoraTextToImageNode
from .modelscope_api_image_edit_node import modelscopeLoraImageEditNode
from .modelscope_api_text_generation_node import ModelscopeApiTextGenerationNode
from .modelscope_api_image_caption_node import ModelscopeApiImageCaptionNode
from .modelscope_api_video_caption_node import ModelscopeApiVideoCaptionNode

# 定义节点映射
NODE_CLASS_MAPPINGS = {
    "modelscopeLoraTextToImageNode": modelscopeLoraTextToImageNode,
    "modelscopeLoraImageEditNode": modelscopeLoraImageEditNode,
    "ModelscopeApiTextGenerationNode": ModelscopeApiTextGenerationNode,
    "ModelscopeApiImageCaptionNode": ModelscopeApiImageCaptionNode,
    "ModelscopeApiVideoCaptionNode": ModelscopeApiVideoCaptionNode,
}

# 定义节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "modelscopeLoraTextToImageNode": "魔搭API-文生图",
    "modelscopeLoraImageEditNode": "魔搭API-图像编辑",
    "ModelscopeApiTextGenerationNode": "魔搭API-文本生成",
    "ModelscopeApiImageCaptionNode": "魔搭API-图片反推",
    "ModelscopeApiVideoCaptionNode": "魔搭API-视频反推",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']