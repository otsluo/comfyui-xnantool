import torch
import comfy.utils

class IndexSwitchNode:
    """
    编号切换节点 - 根据索引值从多个输入中选择一个输出
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "index": ("INT", {"default": 0, "min": 0, "max": 19, "step": 1}),
                "value_0": ("*",),
                "value_1": ("*",),
                "value_2": ("*",),
                "value_3": ("*",),
                "value_4": ("*",),
                "value_5": ("*",),
                "value_6": ("*",),
                "value_7": ("*",),
                "value_8": ("*",),
                "value_9": ("*",),
                "value_10": ("*",),
                "value_11": ("*",),
                "value_12": ("*",),
                "value_13": ("*",),
                "value_14": ("*",),
                "value_15": ("*",),
                "value_16": ("*",),
                "value_17": ("*",),
                "value_18": ("*",),
                "value_19": ("*",),
            }
        }

    RETURN_TYPES = ("*",)  # 动态类型输出
    RETURN_NAMES = ("selected_value",)
    FUNCTION = "switch_by_index"
    CATEGORY = "XnanTool/实用工具"

    @classmethod
    def IS_CHANGED(cls, index, value_0, value_1, value_2, value_3, value_4):
        # 返回输入值的哈希，用于检测变化
        return hash((index, value_0, value_1, value_2, value_3, value_4))

    def switch_by_index(self, index, value_0, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8, value_9, value_10, value_11, value_12, value_13, value_14, value_15, value_16, value_17, value_18, value_19):
        """
        根据索引值从多个输入中选择一个输出

        Args:
            index: 索引值（0-19）
            value_0 到 value_19: 各索引对应的值

        Returns:
            tuple: 包含选定值的元组
        """
        values = [value_0, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8, value_9, value_10, value_11, value_12, value_13, value_14, value_15, value_16, value_17, value_18, value_19]
        
        # 确保索引在有效范围内
        if index < 0 or index >= len(values):
            index = 0
        
        selected_value = values[index]

        # 直接返回选定的值，保持其原始类型
        return (selected_value,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "IndexSwitchNode": IndexSwitchNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IndexSwitchNode": "编号切换"
}
