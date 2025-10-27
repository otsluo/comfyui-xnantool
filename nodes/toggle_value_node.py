import torch
import comfy.utils

class ToggleValueNode:
    """
    切换值节点 - 可以在两个值之间切换的节点
    支持多种数据类型输入（FLOAT, INT, STRING）
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

    RETURN_TYPES = ("*", "STRING", "INT", "FLOAT")
    RETURN_NAMES = ("原始类型输出", "字符串输出", "整数输出", "浮点输出")
    FUNCTION = "toggle_value"
    CATEGORY = "XnanTool/实用工具/小工具"

    def toggle_value(self, input_value, value_a, value_b):
        """
        根据输入布尔值在两个值之间切换
        
        Args:
            input_value: 布尔值，决定选择哪个输入值
            value_a: 第一个可选值
            value_b: 第二个可选值
            
        Returns:
            tuple: 包含不同类型的选定值
        """
        # 根据输入布尔值在两个值之间切换
        selected_value = value_b if input_value else value_a
        
        # 保持原始类型输出
        original_output = selected_value
        
        # 转换为字符串输出
        if isinstance(selected_value, (int, float)):
            string_output = str(selected_value)
        elif isinstance(selected_value, str):
            string_output = selected_value
        else:
            # 对于其他类型，尝试转换为字符串
            try:
                string_output = str(selected_value)
            except:
                string_output = "无法转换为字符串"
        
        # 转换为整数输出
        try:
            if isinstance(selected_value, str):
                # 如果是字符串，尝试解析为数字
                int_output = int(float(selected_value)) if selected_value.replace('.', '', 1).isdigit() or (selected_value.startswith('-') and selected_value[1:].replace('.', '', 1).isdigit()) else len(selected_value)
            else:
                int_output = int(selected_value)
        except:
            int_output = 0
            
        # 转换为浮点输出
        try:
            if isinstance(selected_value, str):
                # 如果是字符串，尝试解析为数字
                float_output = float(selected_value) if selected_value.replace('.', '', 1).replace('-', '', 1).isdigit() else float(len(selected_value))
            else:
                float_output = float(selected_value)
        except:
            float_output = 0.0
        
        return (original_output, string_output, int_output, float_output)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "ToggleValueNode": ToggleValueNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleValueNode": "切换值节点"
}