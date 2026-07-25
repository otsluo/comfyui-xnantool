class TransferNode:
    """
    传递节点 - 透传输入数据
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any_input": ("*", {
                    "label": "输入",
                    "description": "输入任意类型的数据，透传到输出端口"
                }),
            },
            "optional": {
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "step": 1,
                    "label": "种子",
                    "description": "种子值（可选，用于手动控制）"
                }),
            }
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("输出",)
    FUNCTION = "transfer"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def transfer(self, seed, any_input=None):
        """
        透传输入数据

        Args:
            seed: 种子值
            any_input: 任意输入，透传到输出

        Returns:
            tuple: (透传的值,)
        """
        return (any_input,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "TransferNode": TransferNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "TransferNode": "传递器"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
