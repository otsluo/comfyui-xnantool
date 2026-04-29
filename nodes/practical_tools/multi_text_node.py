#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多文本节点
功能：提供5个独立的文本输入和5个独立的文本输出
"""

class MultiTextNode:
    """多文本节点 - 提供5个独立的文本输入和输出"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_1": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "文本1",
                    "description": "第一个文本输入"
                }),
                "text_2": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "文本2",
                    "description": "第二个文本输入"
                }),
                "text_3": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "文本3",
                    "description": "第三个文本输入"
                }),
                "text_4": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "文本4",
                    "description": "第四个文本输入"
                }),
                "text_5": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "文本5",
                    "description": "第五个文本输入"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("text_1", "text_2", "text_3", "text_4", "text_5")
    FUNCTION = "process_texts"
    CATEGORY = "XnanTool/实用工具"
    DESCRIPTION = "提供5个独立的文本输入和输出，每个输入直接传递到对应的输出"
    
    def process_texts(self, text_1, text_2, text_3, text_4, text_5):
        """处理多文本输入并返回对应的输出"""
        return (text_1, text_2, text_3, text_4, text_5)
    
    @classmethod
    def IS_CHANGED(cls, text_1, text_2, text_3, text_4, text_5):
        return (text_1, text_2, text_3, text_4, text_5)


# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "MultiTextNode": MultiTextNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiTextNode": "多文本",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
