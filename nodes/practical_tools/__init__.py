# 实用工具节点模块初始化文件

# 导入实用工具相关节点
from .toggle_value_node import ToggleValueNode
from .random_execution_node import RandomExecutionNode

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "ToggleValueNode": ToggleValueNode,
    "RandomExecutionNode": RandomExecutionNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleValueNode": "切换值",
    "RandomExecutionNode": "随机执行",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']