import torch
import numpy as np
from PIL import Image
import folder_paths

class ToggleAnyOutputNode:
    """
    切换任意值（输出）节点
    
    该节点接收一个布尔值输入和两个任意类型的值输入，
    根据布尔值的真假来决定输出哪一个值。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "toggle": ("BOOLEAN", {
                    "default": False,
                    "label": "切换",
                    "description": "选择输出哪个端口：关闭时输出到A，开启时输出到B"
                }),
            },
            "optional": {
                "input_value": ("*", {
                    "label": "输入值",
                    "description": "要切换输出的输入值"
                })
            }
        }

    OUTPUT_NODE = False

    RETURN_TYPES = ("*", "*")
    RETURN_NAMES = ("output_a", "output_b")
    FUNCTION = "toggle_output"
    CATEGORY = "XnanTool/实用工具"
    DESCRIPTION = "切换任意值（输出）节点，根据布尔值将单个输入值路由到两个输出端口中的一个"

    def toggle_output(self, toggle, input_value=None):
        """
        根据布尔值切换输出
        
        Args:
            toggle (bool): 切换值，决定输出到哪个端口
            input_value: 输入值
            
        Returns:
            tuple: 根据toggle值将输入路由到相应的输出端口
        """
        if toggle:
            # 当toggle为True时，将输入值输出到output_b，output_a输出None
            return (None, input_value)
        else:
            # 当toggle为False时，将输入值输出到output_a，output_b输出None
            return (input_value, None)


# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "ToggleAnyOutputNode": ToggleAnyOutputNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleAnyOutputNode": "切换任意值（输出）"
}

# 确保模块被正确导入
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']