class LoopGeneratorNode:
    """
    循环生成器节点
    支持最多3层嵌套循环，每层使用多行字符串输入
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "layer1_items": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "第1层项目，每行一个，例如：1,2,3"
                }),
                "layer2_items": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "第2层项目，每行一个，例如：11,22"
                }),
                "layer3_items": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "第3层项目，每行一个（可选）"
                }),
                "separator": ("STRING", {
                    "default": "-",
                    "multiline": False,
                    "placeholder": "分隔符",
                    "label": "分隔符",
                    "description": "层与层之间的分隔符"
                }),
                "line_separator": (["换行", "逗号", "分号", "制表符"], {
                    "default": "换行",
                    "label": "输出分隔",
                    "description": "每行结果之间的分隔符"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("结果", "总数")
    FUNCTION = "generate_combinations"
    CATEGORY = "XnanTool/实用工具"
    
    def generate_combinations(self, layer1_items, layer2_items, layer3_items, separator, line_separator):
        """
        生成循环组合
        
        Args:
            layer1_items: 第1层项目（多行字符串）
            layer2_items: 第2层项目（多行字符串）
            layer3_items: 第3层项目（多行字符串，可选）
            separator: 层与层之间的分隔符
            line_separator: 输出行之间的分隔符
            
        Returns:
            结果: 组合结果字符串
            总数: 组合总数
        """
        # 解析各层项目
        def parse_items(items_str):
            if not items_str.strip():
                return []
            return [item.strip() for item in items_str.split('\n') if item.strip()]
        
        layer1 = parse_items(layer1_items)
        layer2 = parse_items(layer2_items)
        layer3 = parse_items(layer3_items)
        
        # 确定行分隔符
        line_sep_map = {
            "换行": "\n",
            "逗号": ",",
            "分号": ";",
            "制表符": "\t"
        }
        sep = line_sep_map[line_separator]
        
        # 生成组合
        results = []
        
        if not layer3:
            # 2层循环
            for item1 in layer1:
                for item2 in layer2:
                    results.append(f"{item1}{separator}{item2}")
        else:
            # 3层循环
            for item1 in layer1:
                for item2 in layer2:
                    for item3 in layer3:
                        results.append(f"{item1}{separator}{item2}{separator}{item3}")
        
        # 返回结果
        result_str = sep.join(results)
        return (result_str, len(results))


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "LoopGeneratorNode": LoopGeneratorNode
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoopGeneratorNode": "循环生成器"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
