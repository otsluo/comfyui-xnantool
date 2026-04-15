#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文本逐行读取节点
功能：输入多行文本，每次运行输出一行，文本输出完毕后输出"运行完毕"
"""

import random

class TextLineReaderNode:
    """文本逐行读取节点 - 每次运行输出一行文本"""
    
    # 类变量，用于保存当前读取位置
    _current_line_index = {}
    _line_order = {}
    _has_completed = {}
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "多行文本",
                    "description": "包含多行内容的文本"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999999,
                    "label": "随机种子",
                    "description": "随机读取时的种子值"
                }),
                "random_order": (["否", "是"], {
                    "default": "否",
                    "label": "随机顺序",
                    "description": "是否随机顺序读取"
                }),
                "restart": (["否", "是"], {
                    "default": "否",
                    "label": "重新开始",
                    "description": "是否重新开始读取"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "BOOL")
    RETURN_NAMES = ("当前行", "行号", "是否最后一行")
    FUNCTION = "read_line"
    CATEGORY = "XnanTool/实用工具"
    DESCRIPTION = "文本逐行读取，每次运行输出一行，文本输出完毕后输出“运行完毕”"
    
    def read_line(self, text, seed=0, random_order="否", restart="否"):
        """读取下一行文本"""
        try:
            # 如果文本为空，返回空
            if not text or text.strip() == "":
                return ("", 0, True)
            
            # 分割文本为行列表
            lines = text.split('\n')
            
            # 获取当前节点的唯一标识
            node_id = id(self)
            
            # 如果需要重新开始，重置状态
            if restart == "是":
                TextLineReaderNode._current_line_index[node_id] = 0
                TextLineReaderNode._line_order[node_id] = None
                TextLineReaderNode._has_completed[node_id] = False
                # 如果启用随机顺序，需要重新打乱
                if random_order == "是":
                    random.seed(seed)
                    TextLineReaderNode._line_order[node_id] = list(range(len(lines)))
                    random.shuffle(TextLineReaderNode._line_order[node_id])
                # 重新开始后读取第一行
                return (lines[0], 1, len(lines) <= 1)
            
            # 如果是第一次运行，初始化索引
            if node_id not in TextLineReaderNode._current_line_index:
                TextLineReaderNode._current_line_index[node_id] = 0
                TextLineReaderNode._line_order[node_id] = None
                TextLineReaderNode._has_completed[node_id] = False
            
            # 如果文本已经输出完毕，返回"运行完毕"
            if TextLineReaderNode._has_completed.get(node_id, False):
                return ("运行完毕", 0, True)
            
            # 如果启用随机顺序
            if random_order == "是":
                # 如果需要重新打乱顺序
                if TextLineReaderNode._line_order.get(node_id) is None:
                    random.seed(seed)
                    TextLineReaderNode._line_order[node_id] = list(range(len(lines)))
                    random.shuffle(TextLineReaderNode._line_order[node_id])
                    TextLineReaderNode._current_line_index[node_id] = 0
                
                # 使用随机顺序获取行索引
                line_order = TextLineReaderNode._line_order[node_id]
                current_index = TextLineReaderNode._current_line_index[node_id]
                
                if current_index >= len(line_order):
                    # 文本输出完毕
                    TextLineReaderNode._has_completed[node_id] = True
                    return ("运行完毕", 0, True)
                
                actual_line_index = line_order[current_index]
                current_line = lines[actual_line_index]
                
                # 更新索引到下一行
                next_index = current_index + 1
                TextLineReaderNode._current_line_index[node_id] = next_index
                
                # 判断是否是最后一行
                is_last_line = (next_index >= len(line_order))
                
                return (current_line, actual_line_index + 1, is_last_line)
            
            # 正常顺序读取
            current_index = TextLineReaderNode._current_line_index[node_id]
            
            # 检查是否超出范围
            if current_index >= len(lines):
                # 文本输出完毕
                TextLineReaderNode._has_completed[node_id] = True
                return ("运行完毕", 0, True)
            
            # 获取当前行
            current_line = lines[current_index]
            
            # 更新索引到下一行
            next_index = current_index + 1
            TextLineReaderNode._current_line_index[node_id] = next_index
            
            # 判断是否是最后一行
            is_last_line = (next_index >= len(lines))
            
            return (current_line, current_index + 1, is_last_line)
            
        except Exception as e:
            error_msg = f"读取失败: {str(e)}"
            return (error_msg, 0, True)


# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "TextLineReaderNode": TextLineReaderNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextLineReaderNode": "文本逐行读取",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
