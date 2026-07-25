class StringReplaceNode:
    """
    字符串替换节点 - 替换文本中的指定内容
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "find": ("STRING", {"default": "", "multiline": False, "placeholder": "要查找的内容"}),
                "replace": ("STRING", {"default": "", "multiline": False, "placeholder": "替换为的内容"}),
                "enabled": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "replace"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def replace(self, text, find, replace, enabled):
        """
        替换文本中的指定内容
        
        Args:
            text: 原始文本
            find: 要查找的内容
            replace: 替换为的内容
            enabled: 是否启用替换
            
        Returns:
            tuple: 替换后的文本
        """
        if not enabled or not find:
            return (text,)
        
        result = text.replace(find, replace)
        return (result,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "StringReplaceNode": StringReplaceNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "StringReplaceNode": "字符串替换"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
