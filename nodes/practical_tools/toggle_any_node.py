import torch
import comfy.utils

class ToggleAnyNode:
    """
    任意类型切换节点 - 可以在两个任意类型的值之间切换的节点
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_value": ("BOOLEAN", {"default": False}),
                "value_a": ("*",),  # 通配符类型，可以接受任何类型的输入
                "value_b": ("*",),  # 通配符类型，可以接受任何类型的输入
            }
        }

    RETURN_TYPES = ("*",)  # 动态类型输出
    RETURN_NAMES = ("any_output",)
    FUNCTION = "toggle_any"
    CATEGORY = "XnanTool/实用工具"

    @classmethod
    def VALIDATE_INPUTS(cls, input_types):
        # 获取输入类型
        type_a = input_types["value_a"]
        type_b = input_types["value_b"]
        
        # 验证两个输入类型是否相同
        if type_a != type_b:
            return f"输入类型不匹配: value_a 是 {type_a}, value_b 是 {type_b}"
            
        return True

    @classmethod
    def IS_CHANGED(cls, input_value, value_a, value_b):
        # 返回输入值的哈希，用于检测变化
        return hash((input_value, value_a, value_b))

    def toggle_any(self, input_value, value_a, value_b):
        """
        根据输入布尔值在两个值之间切换

        Args:
            input_value: 布尔值，决定选择哪个输入值
            value_a: 第一个可选值
            value_b: 第二个可选值

        Returns:
            tuple: 包含选定值的元组
        """
        # 根据输入布尔值在两个值之间切换
        selected_value = value_b if input_value else value_a

        # 直接返回选定的值，保持其原始类型
        return (selected_value,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "ToggleAnyNode": ToggleAnyNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleAnyNode": "切换任意值"
}