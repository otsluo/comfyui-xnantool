# comfyui-xnantool 插件版本信息
__version__ = "0.6.6"

# 导入所有节点模块
# ==================== YOLO和SAM节点模块 ====================
from .nodes.yolo_and_sam import NODE_CLASS_MAPPINGS as YOLO_AND_SAM_NODE_CLASS_MAPPINGS
from .nodes.yolo_and_sam import NODE_DISPLAY_NAME_MAPPINGS as YOLO_AND_SAM_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 预设管理节点模块 ====================
from .nodes.preset_manager import NODE_CLASS_MAPPINGS as PRESET_MANAGER_NODE_CLASS_MAPPINGS
from .nodes.preset_manager import NODE_DISPLAY_NAME_MAPPINGS as PRESET_MANAGER_NODE_DISPLAY_NAME_MAPPINGS

# ==================== ModelScope API节点模块 ====================
from .nodes.modelscope_api import NODE_CLASS_MAPPINGS as MODELSCOPE_API_NODE_CLASS_MAPPINGS
from .nodes.modelscope_api import NODE_DISPLAY_NAME_MAPPINGS as MODELSCOPE_API_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 媒体处理节点模块 ====================
from .nodes.media_processing import NODE_CLASS_MAPPINGS as MEDIA_PROCESSING_NODE_CLASS_MAPPINGS
from .nodes.media_processing import NODE_DISPLAY_NAME_MAPPINGS as MEDIA_PROCESSING_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 图像处理节点模块 ====================
from .nodes.image_processing import NODE_CLASS_MAPPINGS as IMAGE_PROCESSING_NODE_CLASS_MAPPINGS
from .nodes.image_processing import NODE_DISPLAY_NAME_MAPPINGS as IMAGE_PROCESSING_NODE_DISPLAY_NAME_MAPPINGS

# ==================== Ollama节点模块 ====================
from .nodes.ollama import NODE_CLASS_MAPPINGS as OLLAMA_NODE_CLASS_MAPPINGS
from .nodes.ollama import NODE_DISPLAY_NAME_MAPPINGS as OLLAMA_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 实用工具节点模块 ====================
from .nodes.practical_tools import NODE_CLASS_MAPPINGS as PRACTICAL_TOOLS_NODE_CLASS_MAPPINGS
from .nodes.practical_tools import NODE_DISPLAY_NAME_MAPPINGS as PRACTICAL_TOOLS_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 版本信息节点 ====================
from .nodes.version_info_node import NODE_CLASS_MAPPINGS as VERSION_INFO_NODE_CLASS_MAPPINGS
from .nodes.version_info_node import NODE_DISPLAY_NAME_MAPPINGS as VERSION_INFO_NODE_DISPLAY_NAME_MAPPINGS

# 合并所有节点映射的工具函数
def merge_node_mappings(*mappings):
    merged = {}
    for mapping in mappings:
        merged.update(mapping)
    return merged

# 合并所有节点类映射
NODE_CLASS_MAPPINGS = merge_node_mappings(
    # YOLO和SAM节点
    YOLO_AND_SAM_NODE_CLASS_MAPPINGS,
    
    # 预设管理节点
    PRESET_MANAGER_NODE_CLASS_MAPPINGS,
    
    # ModelScope API节点
    MODELSCOPE_API_NODE_CLASS_MAPPINGS,
    
    # 媒体处理节点
    MEDIA_PROCESSING_NODE_CLASS_MAPPINGS,
    
    # 图像处理节点
    IMAGE_PROCESSING_NODE_CLASS_MAPPINGS,
    
    # Ollama节点
    OLLAMA_NODE_CLASS_MAPPINGS,
    
    # 实用工具节点
    PRACTICAL_TOOLS_NODE_CLASS_MAPPINGS,
    
    # 版本信息节点
    VERSION_INFO_NODE_CLASS_MAPPINGS,
)

# 合并所有节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = merge_node_mappings(
    # YOLO和SAM节点
    YOLO_AND_SAM_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 预设管理节点
    PRESET_MANAGER_NODE_DISPLAY_NAME_MAPPINGS,
    
    # ModelScope API节点
    MODELSCOPE_API_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 媒体处理节点
    MEDIA_PROCESSING_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 图像处理节点
    IMAGE_PROCESSING_NODE_DISPLAY_NAME_MAPPINGS,
    
    # Ollama节点
    OLLAMA_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 实用工具节点
    PRACTICAL_TOOLS_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 版本信息节点
    VERSION_INFO_NODE_DISPLAY_NAME_MAPPINGS,
)

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']