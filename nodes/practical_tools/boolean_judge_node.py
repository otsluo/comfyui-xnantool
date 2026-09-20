class BooleanJudgeNode:
    """
    布尔判断节点 - 根据布尔值判断并输出对应的值
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_value": ("BOOLEAN", {
                    "default": True,
                    "label": "布尔值",
                    "description": "输入的布尔值，用于判断"
                }),
                "true_value": ("*", {
                    "label": "真值",
                    "description": "当布尔值为True时输出的值"
                }),
                "false_value": ("*", {
                    "label": "假值",
                    "description": "当布尔值为False时输出的值"
                }),
            }
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("输出",)
    FUNCTION = "judge_boolean"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def judge_boolean(self, boolean_value, true_value, false_value):
        """
        根据布尔值判断并输出对应的值
        
        Args:
            boolean_value: 输入的布尔值
            true_value: 布尔值为True时输出的值
            false_value: 布尔值为False时输出的值
            
        Returns:
            tuple: 包含选定值的元组
        """
        # 根据布尔值选择输出
        selected_value = true_value if boolean_value else false_value
        
        return (selected_value,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "BooleanJudgeNode": BooleanJudgeNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "BooleanJudgeNode": "布尔判断"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
