import torch
import comfy.utils

class StringToAnyNode:
    """
    字符串到任意类型转换节点 - 将字符串转换为指定的任意类型
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("*",)  # 任意类型输出
    RETURN_NAMES = ("any",)
    FUNCTION = "convert_string_to_any"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def convert_string_to_any(self, string):
        """
        将输入的字符串转换为任意类型
        
        Args:
            string (str): 输入的字符串
            
        Returns:
            tuple: 包含转换后结果的元组
        """
        # 直接返回输入的字符串，作为任意类型输出
        # 在ComfyUI中，"*" 类型可以接受任何类型的数据
        return (string,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "StringToAnyNode": StringToAnyNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "StringToAnyNode": "字符串到任意类型"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']