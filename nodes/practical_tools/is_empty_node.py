class IsEmptyNode:
    """
    是否为空节点 - 判断输入是否为空
    支持多种数据类型输入（字符串、列表、字典、整数、浮点数等）
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "input_value": ("*",),  # 通配符类型，可以接受任何类型的输入
            }
        }
    
    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("是否为空",)
    FUNCTION = "check_is_empty"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    
    def check_is_empty(self, input_value=None):
        """
        检查输入是否为空
        
        Args:
            input_value: 任意类型的输入值（可选）
            
        Returns:
            tuple: (布尔值，表示输入是否为空)
        """
        # 判断是否为空
        is_empty = False
        
        if input_value is None:
            is_empty = True
        elif isinstance(input_value, str):
            is_empty = input_value.strip() == ""
        elif isinstance(input_value, (list, tuple)):
            is_empty = len(input_value) == 0
        elif isinstance(input_value, dict):
            is_empty = len(input_value) == 0
        elif isinstance(input_value, (int, float)):
            is_empty = input_value == 0
        else:
            # 对于其他类型，尝试判断是否为空
            try:
                if hasattr(input_value, '__len__'):
                    is_empty = len(input_value) == 0
                else:
                    is_empty = False
            except:
                is_empty = False
        
        return (is_empty,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "IsEmptyNode": IsEmptyNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "IsEmptyNode": "是否为空"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
