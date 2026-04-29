#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSON解析节点
功能：将JSON字符串解析为可用数据，支持提取指定字段
"""

import json

class JSONParserNode:
    """JSON解析节点 - 解析JSON字符串并提取指定字段"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_string": ("STRING", {
                    "multiline": True,
                    "default": "{\"key\": \"value\"}",
                    "label": "JSON字符串",
                    "description": "要解析的JSON字符串"
                }),
            },
            "optional": {
                "extract_field": ("STRING", {
                    "default": "",
                    "label": "提取字段",
                    "description": "要提取的字段名称，留空则输出整个解析后的对象（支持点号分隔的嵌套字段）"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("result", "string", "int", "float", "boolean")
    FUNCTION = "parse_json"
    CATEGORY = "XnanTool/实用工具"
    DESCRIPTION = "将JSON字符串解析为可用数据，支持提取指定字段"
    
    def parse_json(self, json_string, extract_field=""):
        """解析JSON字符串"""
        try:
            # 解析JSON字符串
            json_string = json_string.strip().removeprefix("```json").removesuffix("```")
            parsed_data = json.loads(json_string)
            
            # 如果没有指定提取字段，返回整个解析后的对象
            if not extract_field or extract_field.strip() == "":
                result = json.dumps(parsed_data, ensure_ascii=False, indent=2)
                return self._convert_types(result, parsed_data)
            
            # 尝试提取指定字段
            # 支持嵌套字段，使用点号分隔（如 "user.name"）
            fields = extract_field.strip().split('.')
            current_data = parsed_data
            
            for field in fields:
                if isinstance(current_data, dict):
                    if field in current_data:
                        current_data = current_data[field]
                    else:
                        return ("", "", 0, 0.0, False)
                elif isinstance(current_data, list):
                    try:
                        index = int(field)
                        current_data = current_data[index]
                    except (ValueError, IndexError):
                        return ("", "", 0, 0.0, False)
                else:
                    return ("", "", 0, 0.0, False)
            
            # 将提取的结果转换为字符串
            if isinstance(current_data, (dict, list)):
                result = json.dumps(current_data, ensure_ascii=False, indent=2)
            else:
                result = str(current_data)
            
            return self._convert_types(result, current_data)
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            return (error_msg, error_msg, 0, 0.0, False)
        except Exception as e:
            error_msg = f"解析失败: {str(e)}"
            return (error_msg, error_msg, 0, 0.0, False)
    
    def _convert_types(self, result, value):
        """将值转换为不同类型"""
        # 字符串类型
        try:
            string_value = str(value)
        except Exception:
            string_value = ""
        
        # 整数类型
        try:
            int_value = int(value)
        except Exception:
            int_value = 0
        
        # 浮点数类型
        try:
            float_value = float(value)
        except Exception:
            float_value = 0.0
        
        # 布尔值类型
        try:
            if isinstance(value, bool):
                bool_value = value
            else:
                bool_value = str(value).lower() == "true"
        except Exception:
            bool_value = False
        
        return (result, string_value, int_value, float_value, bool_value)


# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "JSONParserNode": JSONParserNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JSONParserNode": "JSON解析",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
