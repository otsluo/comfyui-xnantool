class ListSliceNode:
    """
    列表切片节点 - 对列表进行切片操作
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_list": ("*", {"forceInput": True, "label": "列表", "description": "输入的列表"}),
                "start": ("INT", {
                    "default": 0,
                    "min": -9007199254740991,
                    "step": 1,
                    "label": "起始索引",
                    "description": "切片起始索引（支持负数，-1表示最后一个元素）"
                }),
                "end": ("INT", {
                    "default": -1,
                    "min": -9007199254740991,
                    "step": 1,
                    "label": "结束索引",
                    "description": "切片结束索引（不包含，-1表示到末尾）"
                }),
            }
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("切片结果",)
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "slice_list"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def slice_list(self, input_list: list, start: list[int], end: list[int]):
        """
        对列表进行切片

        Args:
            input_list: 输入的列表
            start: 起始索引列表
            end: 结束索引列表

        Returns:
            tuple: (切片后的列表,)
        """
        # 从输入列表中获取起始和结束值
        start_val = start[0] if start else 0
        end_val = end[0] if end else -1
        
        # 处理负数索引
        if start_val < 0:
            start_val = len(input_list) + start_val
        if end_val < 0:
            end_val = len(input_list) + end_val
        
        # 确保索引在有效范围内
        start_val = max(0, min(start_val, len(input_list)))
        end_val = max(0, min(end_val, len(input_list)))
        
        # 确保start不大于end
        if start_val > end_val:
            return ([],)
            
        # 执行切片操作
        sliced = input_list[start_val:end_val]
        return (sliced,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "ListSliceNode": ListSliceNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "ListSliceNode": "列表切片"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
