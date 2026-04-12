class TextToListNode:
    """文本到列表节点 - 将文本按指定分隔符分割成列表"""
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "输入文本",
                    "description": "要分割的文本内容"
                }),
                "delimiter": ("STRING", {
                    "default": "\\n",
                    "label": "分隔符",
                    "description": "用于分割文本的分隔符（默认换行符\\n）"
                }),
            },
            "optional": {
                "strip_whitespace": ("BOOLEAN", {
                    "default": True,
                    "label": "去除空白",
                    "description": "是否去除每个元素首尾的空白字符"
                }),
                "remove_empty": ("BOOLEAN", {
                    "default": True,
                    "label": "移除空值",
                    "description": "是否移除空字符串元素"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("列表",)
    FUNCTION = "text_to_list"
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "XnanTool/实用工具"
    
    def text_to_list(self, text, delimiter, strip_whitespace=True, remove_empty=True):
        # 如果文本为空，默认按换行符处理
        if not text:
            return ([""],)
        
        # 处理分隔符（将\\n转换为实际换行符）
        if delimiter == "\\n":
            delimiter = "\n"
        
        # 分割文本
        parts = text.split(delimiter)
        
        # 处理每个元素
        result = []
        for part in parts:
            # 去除空白
            if strip_whitespace:
                part = part.strip()
            
            # 移除空值
            if remove_empty and not part:
                continue
            
            result.append(part)
        
        return (result,)
    
    @classmethod
    def IS_CHANGED(cls, text, *args):
        return text
    
    @classmethod
    def VALIDATE_INPUTS(cls, text, delimiter, **kwargs):
        if not text:
            return "请输入文本"
        return True


NODE_CLASS_MAPPINGS = {
    "TextToListNode": TextToListNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextToListNode": "文本到列表",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
