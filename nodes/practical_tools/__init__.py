# 实用工具节点模块初始化文件

# 导入实用工具相关节点
from .toggle_value_node import ToggleValueNode

# 定义节点映射
NODE_CLASS_MAPPINGS = {
    "ToggleValueNode": ToggleValueNode,
}

# 定义节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleValueNode": "切换值",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']