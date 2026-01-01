class ToggleStringOutputNode:
    """
    切换字符串（输出）节点
    
    根据布尔值将字符串输入路由到两个输出端口中的一个
    - 当toggle为False时，字符串输出到output_a，output_b输出None
    - 当toggle为True时，字符串输出到output_b，output_a输出None
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
                "input_string": ("STRING", {
                    "label": "输入字符串",
                    "description": "要切换输出的字符串",
                    "default": ""
                })
            }
        }

    OUTPUT_NODE = False

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("output_a", "output_b")
    FUNCTION = "toggle_string_output"
    CATEGORY = "XnanTool/实用工具"
    DESCRIPTION = "切换字符串（输出）节点，根据布尔值将字符串输入路由到两个输出端口中的一个"

    def toggle_string_output(self, toggle, input_string=""):
        """
        根据布尔值切换字符串输出
        
        Args:
            toggle (bool): 切换值，决定输出到哪个端口
            input_string (str): 输入字符串
            
        Returns:
            tuple: 根据toggle值将字符串路由到相应的输出端口
        """
        if toggle:
            # 当toggle为True时，将字符串输出到output_b，output_a输出None
            return (None, input_string)
        else:
            # 当toggle为False时，将字符串输出到output_a，output_b输出None
            return (input_string, None)


NODE_CLASS_MAPPINGS = {
    "ToggleStringOutputNode": ToggleStringOutputNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleStringOutputNode": "切换字符串（输出）"
}