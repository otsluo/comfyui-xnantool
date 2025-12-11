import torch
import comfy.utils

class TextInputNode:
    """
    文本输入节点 - 允许用户输入文本的节点
    支持多行文本输入
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "get_text"
    CATEGORY = "XnanTool/实用工具"

    def get_text(self, text):
        """
        返回输入的文本
        
        Args:
            text: 输入的文本
            
        Returns:
            tuple: 包含输入文本的元组
        """
        return (text,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "TextInputNode": TextInputNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextInputNode": "文本输入"
}