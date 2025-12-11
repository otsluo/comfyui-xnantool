import torch
import comfy.utils

class StringMergeNode:
    """
    字符串合并节点 - 可以将多个字符串合并为一个字符串的节点
    支持自定义分隔符
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string1": ("STRING", {"default": "", "multiline": True}),
                "string2": ("STRING", {"default": "", "multiline": True}),
                "string3": ("STRING", {"default": "", "multiline": True}),
                "string4": ("STRING", {"default": "", "multiline": True}),
                "string5": ("STRING", {"default": "", "multiline": True}),
                "separator": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("merged_string",)
    FUNCTION = "merge_strings"
    CATEGORY = "XnanTool/实用工具"

    def merge_strings(self, string1, string2, string3, string4, string5, separator=""):
        """
        将多个字符串合并为一个字符串
        
        Args:
            string1: 第一个字符串
            string2: 第二个字符串
            string3: 第三个字符串
            string4: 第四个字符串
            string5: 第五个字符串
            separator: 分隔符
            
        Returns:
            tuple: 包含合并后字符串的元组
        """
        # 收集所有非空字符串
        strings = [string1, string2, string3, string4, string5]
        non_empty_strings = [s for s in strings if s]
        
        # 使用分隔符合并字符串
        merged_string = separator.join(non_empty_strings)
        
        return (merged_string,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "StringMergeNode": StringMergeNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StringMergeNode": "字符串合并"
}