# 实用工具节点模块初始化文件

# 导入实用工具相关节点
from .toggle_value_node import ToggleValueNode
from .random_execution_node import RandomExecutionNode
from .batch_copy_files_node import BatchCopyFilesNode
from .string_merge_node import StringMergeNode
from .text_input_node import TextInputNode

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "ToggleValueNode": ToggleValueNode,
    "RandomExecutionNode": RandomExecutionNode,
    "BatchCopyFilesNode": BatchCopyFilesNode,
    "StringMergeNode": StringMergeNode,
    "TextInputNode": TextInputNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleValueNode": "切换值",
    "RandomExecutionNode": "随机执行",
    "BatchCopyFilesNode": "批量复制文件",
    "StringMergeNode": "字符串合并节点",
    "TextInputNode": "文本输入",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']