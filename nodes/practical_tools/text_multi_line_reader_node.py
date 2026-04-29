#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文本多行读取节点
功能：输入多行文本，可设置每次输出多行，支持打乱顺序
"""

import random

class TextMultiLineReaderNode:
    """文本多行读取节点 - 每次运行输出指定行数，支持打乱顺序"""
    
    _current_batch_index = {}
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
                "lines_per_output": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "label": "每次输出行数",
                    "description": "每次运行输出的行数"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999999,
                    "label": "随机种子",
                    "description": "随机打乱时的种子值"
                }),
                "shuffle": (["否", "是"], {
                    "default": "否",
                    "label": "打乱顺序",
                    "description": "是否每次随机打乱顺序输出"
                }),
                "restart": (["否", "是"], {
                    "default": "否",
                    "label": "重新开始",
                    "description": "是否重新开始读取"
                }),
            },
            "optional": {
                "usage_notes": ("STRING", {
                    "default": "文本多行读取节点\n每次运行输出指定行数的文本，支持打乱顺序\n\n行数说明：\n  例如有10行文本，设置每次输出3行\n  第1次输出：第1-3行（共3行）\n  第2次输出：第4-6行（共3行）\n  第3次输出：第7-9行（共3行）\n  第4次输出：第10行（共1行，最后一批可能不足设定行数）\n\n重新开始：\n  否 = 全部输出完毕后不再输出（输出\"运行完毕\"）\n  是 = 全部输出完毕后自动从头开始，无限循环输出",
                    "multiline": True
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "BOOL")
    RETURN_NAMES = ("输出文本", "行号列表", "当前批次", "是否完成")
    FUNCTION = "read_multi_lines"
    CATEGORY = "XnanTool/实用工具"
    DESCRIPTION = "文本多行读取，每次运行输出指定行数，可打乱顺序"
    
    def read_multi_lines(self, text, lines_per_output=1, seed=0, shuffle="否", restart="否", usage_notes=None):
        """读取指定行数的文本"""
        try:
            if not text or text.strip() == "":
                return ("", "", 0, True)
            
            lines = [line for line in text.split('\n') if line.strip()]
            
            if not lines:
                return ("", "", 0, True)
            
            node_id = id(self)
            
            if restart == "是":
                TextMultiLineReaderNode._current_batch_index[node_id] = 0
                TextMultiLineReaderNode._line_order[node_id] = None
                TextMultiLineReaderNode._has_completed[node_id] = False
            
            if node_id not in TextMultiLineReaderNode._current_batch_index:
                TextMultiLineReaderNode._current_batch_index[node_id] = 0
                TextMultiLineReaderNode._line_order[node_id] = None
                TextMultiLineReaderNode._has_completed[node_id] = False
            
            if TextMultiLineReaderNode._has_completed.get(node_id, False):
                if restart == "是":
                    TextMultiLineReaderNode._current_batch_index[node_id] = 0
                    TextMultiLineReaderNode._line_order[node_id] = None
                    TextMultiLineReaderNode._has_completed[node_id] = False
                else:
                    return ("运行完毕", "", 0, True)
            
            current_batch = TextMultiLineReaderNode._current_batch_index[node_id]
            
            if shuffle == "是":
                random.seed(seed)
                shuffled_indices = list(range(len(lines)))
                random.shuffle(shuffled_indices)
                
                start_idx = current_batch * lines_per_output
                end_idx = min(start_idx + lines_per_output, len(lines))
                
                if start_idx >= len(lines):
                    TextMultiLineReaderNode._has_completed[node_id] = True
                    if restart == "是":
                        TextMultiLineReaderNode._current_batch_index[node_id] = 0
                        TextMultiLineReaderNode._line_order[node_id] = None
                        TextMultiLineReaderNode._has_completed[node_id] = False
                        current_batch = 0
                        start_idx = 0
                        end_idx = min(lines_per_output, len(lines))
                        shuffled_indices = list(range(len(lines)))
                        random.shuffle(shuffled_indices)
                        selected_indices = shuffled_indices[start_idx:end_idx]
                        selected_lines = [lines[i] for i in selected_indices]
                        output_text = '\n'.join(selected_lines)
                        line_numbers = ','.join([str(i + 1) for i in selected_indices])
                        TextMultiLineReaderNode._current_batch_index[node_id] = 1
                        is_completed = (lines_per_output >= len(lines))
                        return (output_text, line_numbers, 1, is_completed)
                    else:
                        return ("运行完毕", "", 0, True)
                
                selected_indices = shuffled_indices[start_idx:end_idx]
                selected_lines = [lines[i] for i in selected_indices]
                
                output_text = '\n'.join(selected_lines)
                line_numbers = ','.join([str(i + 1) for i in selected_indices])
                
                next_batch = current_batch + 1
                TextMultiLineReaderNode._current_batch_index[node_id] = next_batch
                
                is_completed = (next_batch * lines_per_output >= len(lines))
                
                return (output_text, line_numbers, current_batch + 1, is_completed)
            else:
                start_idx = current_batch * lines_per_output
                end_idx = min(start_idx + lines_per_output, len(lines))
                
                if start_idx >= len(lines):
                    TextMultiLineReaderNode._has_completed[node_id] = True
                    if restart == "是":
                        TextMultiLineReaderNode._current_batch_index[node_id] = 0
                        TextMultiLineReaderNode._has_completed[node_id] = False
                        current_batch = 0
                        start_idx = 0
                        end_idx = min(lines_per_output, len(lines))
                        selected_lines = lines[start_idx:end_idx]
                        output_text = '\n'.join(selected_lines)
                        line_numbers = ','.join([str(i + 1) for i in range(start_idx, end_idx)])
                        TextMultiLineReaderNode._current_batch_index[node_id] = 1
                        is_completed = (lines_per_output >= len(lines))
                        return (output_text, line_numbers, 1, is_completed)
                    else:
                        return ("运行完毕", "", 0, True)
                
                selected_lines = lines[start_idx:end_idx]
                output_text = '\n'.join(selected_lines)
                line_numbers = ','.join([str(i + 1) for i in range(start_idx, end_idx)])
                
                next_batch = current_batch + 1
                TextMultiLineReaderNode._current_batch_index[node_id] = next_batch
                
                is_completed = (next_batch * lines_per_output >= len(lines))
                
                return (output_text, line_numbers, current_batch + 1, is_completed)
            
        except Exception as e:
            error_msg = f"读取失败: {str(e)}"
            return (error_msg, "", 0, True)


NODE_CLASS_MAPPINGS = {
    "TextMultiLineReaderNode": TextMultiLineReaderNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextMultiLineReaderNode": "文本多行读取",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
