#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSON格式化输出节点
功能：将输入的JSON字符串或对象格式化输出，支持不同的缩进级别
"""

import json

class JSONFormatterNode:
    """JSON格式化输出节点 - 将JSON字符串或对象格式化输出"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_input": ("STRING", {
                    "multiline": True,
                    "default": "{\"key\": \"value\"}",
                    "label": "JSON输入",
                    "description": "要格式化的JSON字符串"
                }),
                "indent": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 8,
                    "step": 1,
                    "label": "缩进空格数",
                    "description": "格式化时的缩进空格数"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_json",)
    FUNCTION = "format_json"
    CATEGORY = "XnanTool/实用工具"
    DESCRIPTION = "将输入的JSON字符串格式化输出，支持不同的缩进级别"
    
    def format_json(self, json_input, indent=2):
        """格式化JSON字符串"""
        try:
            # 尝试解析JSON字符串
            if isinstance(json_input, str):
                # 去除字符串两端的引号（如果有的话）
                json_input = json_input.strip()
                if json_input.startswith('"') and json_input.endswith('"'):
                    json_input = json_input[1:-1]
                # 解析JSON
                data = json.loads(json_input)
            else:
                # 如果不是字符串，直接使用
                data = json_input
            
            # 格式化JSON
            formatted_json = json.dumps(data, ensure_ascii=False, indent=indent)
            
            return (formatted_json,)
            
        except json.JSONDecodeError as e:
            # JSON解析错误
            error_msg = f"JSON解析错误: {str(e)}"
            return (error_msg,)
        except Exception as e:
            # 其他错误
            error_msg = f"格式化失败: {str(e)}"
            return (error_msg,)


# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "JSONFormatterNode": JSONFormatterNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JSONFormatterNode": "JSON格式化",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
