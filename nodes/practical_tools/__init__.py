# 实用工具节点模块初始化文件

# 导入实用工具相关节点
from .toggle_value_node import ToggleValueNode
from .toggle_any_node import ToggleAnyNode
from .toggle_any_output_node import ToggleAnyOutputNode
from .toggle_string_output_node import ToggleStringOutputNode
from .random_execution_node import RandomExecutionNode

from .batch_copy_files_node import BatchCopyFilesNode
from .string_merge_node import StringMergeNode
from .text_input_node import TextInputNode
from .string_to_any_node import StringToAnyNode
from .markdown_to_excel_node import MarkdownToExcelNode
from .save_image_node import SaveImageNode
from .save_text_node import SaveTextNode
from .text_to_excel_node import TextToExcelNode
from .get_current_time_node import GetCurrentTimeNode


# 新增导入的节点
from .image_encrypt_basic_node import ImageEncryptNode
from .image_encrypt_advanced_node import ImageEncryptNodeAdvanced


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "ToggleValueNode": ToggleValueNode,
    "ToggleAnyNode": ToggleAnyNode,
    "ToggleAnyOutputNode": ToggleAnyOutputNode,
    "ToggleStringOutputNode": ToggleStringOutputNode,
    "StringMergeNode": StringMergeNode,
    "RandomExecutionNode": RandomExecutionNode,
    "BatchCopyFilesNode": BatchCopyFilesNode,
    "TextInputNode": TextInputNode,
    "StringToAnyNode": StringToAnyNode,
    "MarkdownToExcelNode": MarkdownToExcelNode,
    "SaveImageNode": SaveImageNode,
    "SaveTextNode": SaveTextNode,
    "TextToExcelNode": TextToExcelNode,
    "GetCurrentTimeNode": GetCurrentTimeNode,
    "ImageEncryptNode": ImageEncryptNode,
    "ImageEncryptNodeAdvanced": ImageEncryptNodeAdvanced,

}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleValueNode": "切换值节点",
    "ToggleAnyNode": "切换任意值",
    "ToggleAnyOutputNode": "切换任意值（输出）",
    "ToggleStringOutputNode": "切换字符串（输出）",
    "StringMergeNode": "字符串合并节点",
    "RandomExecutionNode": "随机执行",
    "BatchCopyFilesNode": "批量复制文件",
    "TextInputNode": "文本输入",
    "StringToAnyNode": "字符串到任意类型",
    "MarkdownToExcelNode": "MD转Excel",
    "SaveImageNode": "保存图片节点",
    "SaveTextNode": "保存文本节点",
    "TextToExcelNode": "文本转Excel节点",
    "GetCurrentTimeNode": "获取当前时间节点",
    "ImageEncryptNode": "图片加密基础节点",
    "ImageEncryptNodeAdvanced": "图片加密高级节点",

}

WEB_DIRECTORY = "./js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']