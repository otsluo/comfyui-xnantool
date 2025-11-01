# 导入所有节点文件
# ==================== SAM相关节点 ====================
from .nodes.sam_modelloader_nodes import NODE_CLASS_MAPPINGS as SAM_NODE_CLASS_MAPPINGS
from .nodes.sam_modelloader_nodes import NODE_DISPLAY_NAME_MAPPINGS as SAM_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 尺寸预设相关节点 ====================
from .nodes.size_presets_node import NODE_CLASS_MAPPINGS as TOOL_SIZE_PRESETS_NODE_CLASS_MAPPINGS
from .nodes.size_presets_node import NODE_DISPLAY_NAME_MAPPINGS as TOOL_SIZE_PRESETS_NODE_DISPLAY_NAME_MAPPINGS

# ==================== ModelScope API相关节点 ====================
from .nodes.modelscope_api.modelscope_api_node import NODE_CLASS_MAPPINGS as MODELSCOPE_LORA_NODE_CLASS_MAPPINGS
from .nodes.modelscope_api.modelscope_api_node import NODE_DISPLAY_NAME_MAPPINGS as MODELSCOPE_LORA_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.modelscope_api.modelscope_api_model_presets_node import NODE_CLASS_MAPPINGS as MODELSCOPE_PRESETS_NODE_CLASS_MAPPINGS
from .nodes.modelscope_api.modelscope_api_model_presets_node import NODE_DISPLAY_NAME_MAPPINGS as MODELSCOPE_PRESETS_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.modelscope_api.modelscope_api_lora_presets_node import NODE_CLASS_MAPPINGS as MODELSCOPE_LORA_PRESETS_NODE_CLASS_MAPPINGS
from .nodes.modelscope_api.modelscope_api_lora_presets_node import NODE_DISPLAY_NAME_MAPPINGS as MODELSCOPE_LORA_PRESETS_NODE_DISPLAY_NAME_MAPPINGS

# ==================== YOLO相关节点 ====================
from .nodes.yolo_modelloader_nodes import NODE_CLASS_MAPPINGS as YOLO_MODEL_LOADER_NODE_CLASS_MAPPINGS
from .nodes.yolo_modelloader_nodes import NODE_DISPLAY_NAME_MAPPINGS as YOLO_MODEL_LOADER_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.yolo_detect_and_crop_node import NODE_CLASS_MAPPINGS as YOLO_DETECT_AND_CROP_NODE_CLASS_MAPPINGS
from .nodes.yolo_detect_and_crop_node import NODE_DISPLAY_NAME_MAPPINGS as YOLO_DETECT_AND_CROP_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.yolo_detection_node import NODE_CLASS_MAPPINGS as YOLO_DETECTION_NODE_CLASS_MAPPINGS
from .nodes.yolo_detection_node import NODE_DISPLAY_NAME_MAPPINGS as YOLO_DETECTION_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.yolo_sam_background_removal_node import NODE_CLASS_MAPPINGS as YOLO_SAM_BACKGROUND_REMOVAL_NODE_CLASS_MAPPINGS
from .nodes.yolo_sam_background_removal_node import NODE_DISPLAY_NAME_MAPPINGS as YOLO_SAM_BACKGROUND_REMOVAL_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.yolo_detection_crop_node import NODE_CLASS_MAPPINGS as YOLO_DETECTION_CROP_NODE_CLASS_MAPPINGS
from .nodes.yolo_detection_crop_node import NODE_DISPLAY_NAME_MAPPINGS as YOLO_DETECTION_CROP_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.yolo_detection_multi_output_crop_node import NODE_CLASS_MAPPINGS as YOLO_DETECTION_MULTI_OUTPUT_CROP_NODE_CLASS_MAPPINGS
from .nodes.yolo_detection_multi_output_crop_node import NODE_DISPLAY_NAME_MAPPINGS as YOLO_DETECTION_MULTI_OUTPUT_CROP_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 图形转换节点 ====================
from .nodes.square_converter_node import NODE_CLASS_MAPPINGS as SQUARE_CONVERTER_NODE_CLASS_MAPPINGS
from .nodes.square_converter_node import NODE_DISPLAY_NAME_MAPPINGS as SQUARE_CONVERTER_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.rectangle_converter_node import NODE_CLASS_MAPPINGS as RECTANGLE_CONVERTER_NODE_CLASS_MAPPINGS
from .nodes.rectangle_converter_node import NODE_DISPLAY_NAME_MAPPINGS as RECTANGLE_CONVERTER_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 实用工具节点 ====================
from .nodes.toggle_value_node import NODE_CLASS_MAPPINGS as TOGGLE_VALUE_NODE_CLASS_MAPPINGS
from .nodes.toggle_value_node import NODE_DISPLAY_NAME_MAPPINGS as TOGGLE_VALUE_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.create_image_node import NODE_CLASS_MAPPINGS as CREATE_IMAGE_NODE_CLASS_MAPPINGS
from .nodes.create_image_node import NODE_DISPLAY_NAME_MAPPINGS as CREATE_IMAGE_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.Image_encoding_generation_node import NODE_CLASS_MAPPINGS as IMAGE_UUID_NODE_CLASS_MAPPINGS
from .nodes.Image_encoding_generation_node import NODE_DISPLAY_NAME_MAPPINGS as IMAGE_UUID_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 提示词预设节点 ====================
from .nodes.image_video_prompt_presets_node import NODE_CLASS_MAPPINGS as IMAGE_VIDEO_PROMPT_PRESETS_NODE_CLASS_MAPPINGS
from .nodes.image_video_prompt_presets_node import NODE_DISPLAY_NAME_MAPPINGS as IMAGE_VIDEO_PROMPT_PRESETS_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 视频处理节点 ====================
from .nodes.video_to_gif_node import NODE_CLASS_MAPPINGS as VIDEO_TO_GIF_NODE_CLASS_MAPPINGS
from .nodes.video_to_gif_node import NODE_DISPLAY_NAME_MAPPINGS as VIDEO_TO_GIF_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 图片转GIF节点 ====================
from .nodes.images_to_gif_node import NODE_CLASS_MAPPINGS as images_to_gif_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as images_to_gif_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.video_to_audio_node import NODE_CLASS_MAPPINGS as VIDEO_TO_AUDIO_NODE_CLASS_MAPPINGS
from .nodes.video_to_audio_node import NODE_DISPLAY_NAME_MAPPINGS as VIDEO_TO_AUDIO_NODE_DISPLAY_NAME_MAPPINGS

# 合并所有节点映射的工具函数
def merge_node_mappings(*mappings):
    merged = {}
    for mapping in mappings:
        merged.update(mapping)
    return merged

# 合并所有节点类映射
NODE_CLASS_MAPPINGS = merge_node_mappings(
    # SAM相关节点
    SAM_NODE_CLASS_MAPPINGS,
    
    # 尺寸预设相关节点
    TOOL_SIZE_PRESETS_NODE_CLASS_MAPPINGS,
    
    # ModelScope API相关节点
    MODELSCOPE_LORA_NODE_CLASS_MAPPINGS,
    MODELSCOPE_PRESETS_NODE_CLASS_MAPPINGS,
    MODELSCOPE_LORA_PRESETS_NODE_CLASS_MAPPINGS,
    
    # YOLO相关节点
    YOLO_MODEL_LOADER_NODE_CLASS_MAPPINGS,
    YOLO_DETECT_AND_CROP_NODE_CLASS_MAPPINGS,
    YOLO_DETECTION_NODE_CLASS_MAPPINGS,
    YOLO_SAM_BACKGROUND_REMOVAL_NODE_CLASS_MAPPINGS,
    YOLO_DETECTION_CROP_NODE_CLASS_MAPPINGS,
    YOLO_DETECTION_MULTI_OUTPUT_CROP_NODE_CLASS_MAPPINGS,
    
    # 图形转换节点
    SQUARE_CONVERTER_NODE_CLASS_MAPPINGS,
    RECTANGLE_CONVERTER_NODE_CLASS_MAPPINGS,
    
    # 实用工具节点
    TOGGLE_VALUE_NODE_CLASS_MAPPINGS,
    CREATE_IMAGE_NODE_CLASS_MAPPINGS,
    IMAGE_UUID_NODE_CLASS_MAPPINGS,
    
    # 提示词预设节点
    IMAGE_VIDEO_PROMPT_PRESETS_NODE_CLASS_MAPPINGS,
    
    # 视频处理节点
    VIDEO_TO_GIF_NODE_CLASS_MAPPINGS,
    VIDEO_TO_AUDIO_NODE_CLASS_MAPPINGS,
    
    # 图片转GIF节点
    images_to_gif_NODE_CLASS_MAPPINGS,
)

# 合并所有节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = merge_node_mappings(
    # SAM相关节点
    SAM_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 尺寸预设相关节点
    TOOL_SIZE_PRESETS_NODE_DISPLAY_NAME_MAPPINGS,
    
    # ModelScope API相关节点
    MODELSCOPE_LORA_NODE_DISPLAY_NAME_MAPPINGS,
    MODELSCOPE_PRESETS_NODE_DISPLAY_NAME_MAPPINGS,
    MODELSCOPE_LORA_PRESETS_NODE_DISPLAY_NAME_MAPPINGS,
    
    # YOLO相关节点
    YOLO_MODEL_LOADER_NODE_DISPLAY_NAME_MAPPINGS,
    YOLO_DETECT_AND_CROP_NODE_DISPLAY_NAME_MAPPINGS,
    YOLO_DETECTION_NODE_DISPLAY_NAME_MAPPINGS,
    YOLO_SAM_BACKGROUND_REMOVAL_NODE_DISPLAY_NAME_MAPPINGS,
    YOLO_DETECTION_CROP_NODE_DISPLAY_NAME_MAPPINGS,
    YOLO_DETECTION_MULTI_OUTPUT_CROP_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 图形转换节点
    SQUARE_CONVERTER_NODE_DISPLAY_NAME_MAPPINGS,
    RECTANGLE_CONVERTER_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 实用工具节点
    TOGGLE_VALUE_NODE_DISPLAY_NAME_MAPPINGS,
    CREATE_IMAGE_NODE_DISPLAY_NAME_MAPPINGS,
    IMAGE_UUID_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 提示词预设节点
    IMAGE_VIDEO_PROMPT_PRESETS_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 视频处理节点
    VIDEO_TO_GIF_NODE_DISPLAY_NAME_MAPPINGS,
    VIDEO_TO_AUDIO_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 图片转GIF节点
    images_to_gif_NODE_DISPLAY_NAME_MAPPINGS,
)

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']