class LoopGeneratorOutputSplitterNode:
    """
    循环生成器输出转接节点
    将循环生成器的输出按索引选择某一行，然后拆分成多个输出端口
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "循环生成器的输出结果"
                }),
                "separator": ("STRING", {
                    "default": "-",
                    "multiline": False,
                    "placeholder": "分隔符",
                    "label": "分隔符",
                    "description": "用于拆分的分隔符"
                }),
                "line_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10000,
                    "step": 1,
                    "label": "行索引",
                    "description": "要提取的行索引（从0开始）"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("端口1", "端口2", "端口3")
    FUNCTION = "split_output"
    CATEGORY = "XnanTool/工具"
    
    def split_output(self, input_string, separator, line_index):
        """
        拆分循环生成器的输出
        
        Args:
            input_string: 循环生成器的输出结果（多行字符串）
            separator: 分隔符
            line_index: 要提取的行索引（从0开始）
            
        Returns:
            端口1: 第1个值
            端口2: 第2个值
            端口3: 第3个值
        """
        if not input_string.strip():
            return ("", "", "")
        
        lines = input_string.strip().split('\n')
        
        if line_index >= len(lines):
            return ("", "", "")
        
        # 获取指定行
        line = lines[line_index]
        
        # 按分隔符拆分
        parts = line.split(separator)
        
        # 获取3个端口的值
        port1 = parts[0].strip() if len(parts) > 0 else ""
        port2 = parts[1].strip() if len(parts) > 1 else ""
        port3 = parts[2].strip() if len(parts) > 2 else ""
        
        return (port1, port2, port3)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "LoopGeneratorOutputSplitterNode": LoopGeneratorOutputSplitterNode
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoopGeneratorOutputSplitterNode": "循环生成器输出转接"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
