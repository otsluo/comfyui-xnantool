class StringReplaceNode:
    """
    字符串替换节点 - 替换文本中的指定内容，支持多种替换模式
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "find": ("STRING", {"default": "", "multiline": False, "placeholder": "要查找的内容"}),
                "replace": ("STRING", {"default": "", "multiline": False, "placeholder": "替换为的内容"}),
                "mode": (["全部替换", "替换第一个", "替换最后一个", "替换前N个", "替换后N个", "替换指定数量"], {"default": "全部替换"}),
                "count": ("INT", {"default": 1, "min": 1, "max": 9999, "step": 1, "tooltip": "替换数量（仅在前N个/后N个/指定数量模式下生效）"}),
                "enabled": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "replace"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def replace(self, text, find, replace, mode, count, enabled):
        """
        替换文本中的指定内容，支持多种替换模式
        
        Args:
            text: 原始文本
            find: 要查找的内容
            replace: 替换为的内容
            mode: 替换模式（全部替换/替换第一个/替换最后一个/替换前N个/替换后N个/替换指定数量）
            count: 替换数量（仅在前N个/后N个/指定数量模式下生效）
            enabled: 是否启用替换
            
        Returns:
            tuple: 替换后的文本
        """
        if not enabled or not find:
            return (text,)
        
        # 根据模式执行不同的替换逻辑
        if mode == "全部替换":
            result = text.replace(find, replace)
        elif mode == "替换第一个":
            result = text.replace(find, replace, 1)
        elif mode == "替换最后一个":
            result = self._replace_last(text, find, replace)
        elif mode == "替换前N个":
            result = text.replace(find, replace, count)
        elif mode == "替换后N个":
            result = self._replace_last_n(text, find, replace, count)
        elif mode == "替换指定数量":
            result = text.replace(find, replace, count)
        else:
            result = text.replace(find, replace)
        
        return (result,)
    
    def _replace_last(self, text, find, replace):
        """
        替换最后一个匹配项
        
        Args:
            text: 原始文本
            find: 要查找的内容
            replace: 替换为的内容
            
        Returns:
            str: 替换后的文本
        """
        # 找到最后一个匹配位置
        idx = text.rfind(find)
        if idx == -1:
            return text
        # 替换该位置
        return text[:idx] + replace + text[idx + len(find):]
    
    def _replace_last_n(self, text, find, replace, count):
        """
        替换最后N个匹配项
        
        Args:
            text: 原始文本
            find: 要查找的内容
            replace: 替换为的内容
            count: 替换数量
            
        Returns:
            str: 替换后的文本
        """
        # 找到所有匹配位置
        positions = []
        start = 0
        while True:
            idx = text.find(find, start)
            if idx == -1:
                break
            positions.append(idx)
            start = idx + len(find)
        
        # 如果没有匹配项，直接返回
        if not positions:
            return text
        
        # 取最后N个位置
        last_n_positions = positions[-count:]
        
        # 从后往前替换，避免位置偏移
        result = text
        for pos in reversed(last_n_positions):
            result = result[:pos] + replace + result[pos + len(find):]
        
        return result

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
