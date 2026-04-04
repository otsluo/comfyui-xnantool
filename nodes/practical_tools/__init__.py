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
from .save_video_node import SaveVideoNode


# 新增导入的节点
# from .image_encrypt_basic_node import ImageEncryptNode
# from .image_encrypt_advanced_node import ImageEncryptNodeAdvanced
from .list_folders_node import ListFoldersNode
from .list_files_node import ListFilesNode
from .create_folder_node import CreateFolderNode
from .loop_generator_node import LoopGeneratorNode
from .loop_generator_output_splitter_node import LoopGeneratorOutputSplitterNode
from .counter_node import CounterNode



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
    "SaveVideoNode": SaveVideoNode,
    # "ImageEncryptNode": ImageEncryptNode,
    # "ImageEncryptNodeAdvanced": ImageEncryptNodeAdvanced,
    "ListFoldersNode": ListFoldersNode,
    "ListFilesNode": ListFilesNode,
    "CreateFolderNode": CreateFolderNode,
    "LoopGeneratorNode": LoopGeneratorNode,
    "LoopGeneratorOutputSplitterNode": LoopGeneratorOutputSplitterNode,
    "CounterNode": CounterNode,

}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleValueNode": "切换值",
    "ToggleAnyNode": "切换任意值",
    "ToggleAnyOutputNode": "切换任意值（输出）",
    "ToggleStringOutputNode": "切换字符串（输出）",
    "StringMergeNode": "字符串合并",
    "RandomExecutionNode": "随机执行",
    "BatchCopyFilesNode": "批量复制文件",
    "TextInputNode": "文本输入",
    "StringToAnyNode": "字符串到任意类型",
    "MarkdownToExcelNode": "MD转Excel",
    "SaveImageNode": "保存图片",
    "SaveTextNode": "保存文本",
    "TextToExcelNode": "文本转Excel",
    "GetCurrentTimeNode": "获取当前时间",
    "SaveVideoNode": "保存视频",
    # "ImageEncryptNode": "图片加密基础",
    # "ImageEncryptNodeAdvanced": "图片加密高级",
    "ListFoldersNode": "列出文件夹",
    "ListFilesNode": "列出文件",
    "CreateFolderNode": "批量创建文件夹（支持多级）",
    "LoopGeneratorNode": "循环生成器",
    "LoopGeneratorOutputSplitterNode": "循环生成器输出转接",
    "CounterNode": "计数器",

}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
