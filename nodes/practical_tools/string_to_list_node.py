class StringToListNode:
    """
    字符串转列表节点 - 将字符串转换为列表
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("list",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "convert"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def convert(self, string):
        """
        将字符串转换为列表
        
        Args:
            string: 输入的字符串
            
        Returns:
            tuple: 转换后的列表
        """
        if not string or not string.strip():
            return ([],)
        
        # 按行分割并过滤空行
        lines = [line.strip() for line in string.strip().split("\n") if line.strip()]
        
        return (lines,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "StringToListNode": StringToListNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "StringToListNode": "字符串转列表"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
