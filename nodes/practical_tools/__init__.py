# 实用工具节点模块初始化文件

# 导入实用工具相关节点
from .toggle_value_node import ToggleValueNode
from .toggle_any_node import ToggleAnyNode
from .random_execution_node import RandomExecutionNode
from .batch_copy_files_node import BatchCopyFilesNode
from .string_merge_node import StringMergeNode
from .text_input_node import TextInputNode
from .string_to_any_node import StringToAnyNode
from .markdown_to_excel_node import MarkdownToExcelNode

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "ToggleValueNode": ToggleValueNode,
    "ToggleAnyNode": ToggleAnyNode,
    "StringMergeNode": StringMergeNode,
    "RandomExecutionNode": RandomExecutionNode,
    "BatchCopyFilesNode": BatchCopyFilesNode,
    "TextInputNode": TextInputNode,
    "StringToAnyNode": StringToAnyNode,
    "MarkdownToExcelNode": MarkdownToExcelNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleValueNode": "切换值节点",
    "ToggleAnyNode": "切换任意值",
    "RandomExecutionNode": "随机执行",
    "BatchCopyFilesNode": "批量复制文件",
    "StringMergeNode": "字符串合并节点",
    "TextInputNode": "文本输入",
    "StringToAnyNode": "字符串到任意类型",
    "MarkdownToExcelNode": "MD转Excel",
    "AdvancedMarkdownToExcelNode": "高级MD转Excel",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']