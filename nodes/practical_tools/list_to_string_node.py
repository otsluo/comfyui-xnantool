class ListToStringNode:
    """
    列表转字符串节点 - 将列表转换为字符串
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "list": ("STRING", {"forceInput": True}),
            }
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "convert"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def convert(self, list):
        """
        将列表转换为字符串
        
        Args:
            list: 输入的列表
            
        Returns:
            tuple: 转换后的字符串（每行一个元素）
        """
        if len(list) == 0:
            return ("",)
        
        # 将列表元素转为字符串并用换行连接
        result = "\n".join([str(item) for item in list])
        return (result,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "ListToStringNode": ListToStringNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "ListToStringNode": "列表转字符串"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
