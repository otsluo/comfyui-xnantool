# comfyui-xnantool 插件版本信息
__version__ = "0.8.5"

# 导入所有节点模块
# ==================== YOLO和SAM节点模块 ====================
from .nodes.yolo_and_sam import NODE_CLASS_MAPPINGS as YOLO_AND_SAM_NODE_CLASS_MAPPINGS
from .nodes.yolo_and_sam import NODE_DISPLAY_NAME_MAPPINGS as YOLO_AND_SAM_NODE_DISPLAY_NAME_MAPPINGS

# ==================== 预设管理节点模块 ====================
from .nodes.preset_manager import NODE_CLASS_MAPPINGS as PRESET_MANAGER_NODE_CLASS_MAPPINGS
from .nodes.preset_manager import NODE_DISPLAY_NAME_MAPPINGS as PRESET_MANAGER_NODE_DISPLAY_NAME_MAPPINGS

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

# ==================== API节点模块 ====================
from .nodes.api import NODE_CLASS_MAPPINGS as API_NODE_CLASS_MAPPINGS
from .nodes.api import NODE_DISPLAY_NAME_MAPPINGS as API_NODE_DISPLAY_NAME_MAPPINGS

# ==================== Pro节点模块（可选） ====================
try:
    from .nodes.pro import NODE_CLASS_MAPPINGS as PRO_NODE_CLASS_MAPPINGS
    from .nodes.pro import NODE_DISPLAY_NAME_MAPPINGS as PRO_NODE_DISPLAY_NAME_MAPPINGS
    PRO_MODULE_AVAILABLE = True
except ImportError:
    PRO_MODULE_AVAILABLE = False
    PRO_NODE_CLASS_MAPPINGS = {}
    PRO_NODE_DISPLAY_NAME_MAPPINGS = {}

# ==================== 插件设置节点模块 ====================
from .nodes.Plugin_settings import NODE_CLASS_MAPPINGS as PLUGIN_SETTINGS_NODE_CLASS_MAPPINGS
from .nodes.Plugin_settings import NODE_DISPLAY_NAME_MAPPINGS as PLUGIN_SETTINGS_NODE_DISPLAY_NAME_MAPPINGS

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
    
    # 媒体处理节点
    MEDIA_PROCESSING_NODE_CLASS_MAPPINGS,
    
    # 图像处理节点
    IMAGE_PROCESSING_NODE_CLASS_MAPPINGS,
    
    # Ollama节点
    OLLAMA_NODE_CLASS_MAPPINGS,
    
    # 实用工具节点
    PRACTICAL_TOOLS_NODE_CLASS_MAPPINGS,
    
    # API节点
    API_NODE_CLASS_MAPPINGS,
    
    # Pro节点
    PRO_NODE_CLASS_MAPPINGS,
    
    # 插件设置节点
    PLUGIN_SETTINGS_NODE_CLASS_MAPPINGS,
)

# 合并所有节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = merge_node_mappings(
    # YOLO和SAM节点
    YOLO_AND_SAM_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 预设管理节点
    PRESET_MANAGER_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 媒体处理节点
    MEDIA_PROCESSING_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 图像处理节点
    IMAGE_PROCESSING_NODE_DISPLAY_NAME_MAPPINGS,
    
    # Ollama节点
    OLLAMA_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 实用工具节点
    PRACTICAL_TOOLS_NODE_DISPLAY_NAME_MAPPINGS,
    
    # API节点
    API_NODE_DISPLAY_NAME_MAPPINGS,
    
    # Pro节点
    PRO_NODE_DISPLAY_NAME_MAPPINGS,
    
    # 插件设置节点
    PLUGIN_SETTINGS_NODE_DISPLAY_NAME_MAPPINGS,
)

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
