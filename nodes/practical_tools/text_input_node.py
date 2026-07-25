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
                "enabled": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "get_text"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def get_text(self, text, enabled):
        """
        返回输入的文本
        
        Args:
            text: 输入的文本
            enabled: 是否启用
            
        Returns:
            tuple: 包含输入文本的元组
        """
        if not enabled:
            return ("",)
        return (text,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "TextInputNode": TextInputNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "TextInputNode": "文本"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']