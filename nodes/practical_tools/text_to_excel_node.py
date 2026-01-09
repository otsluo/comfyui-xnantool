#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文本转Excel节点
功能：将文本内容转换为Excel文件
"""

import os
import pandas as pd
import folder_paths

class TextToExcelNode:
    """
    文本转Excel节点
    功能：将文本内容转换为Excel文件
    支持多种分隔符和自定义工作表名称
    """
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "placeholder": "输入要转换为Excel的文本内容"}),
                "output_excel_path": ("STRING", {"default": "ComfyUI", "placeholder": "输出Excel文件名（不含扩展名）"}),
                "separator": (["逗号", "分号", "制表符", "空格", "竖线"], {"default": "逗号"}),
                "sheet_name": ("STRING", {"default": "Sheet1"}),
                "filename_conflict_resolution": (["跳过", "覆盖", "递增"], {"default": "跳过"}),
            },
            "optional": {
                "has_header": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("save_result",)
    OUTPUT_NODE = True
    CATEGORY = "XnanTool/实用工具"

    FUNCTION = "text_to_excel"

    def text_to_excel(self, text, output_excel_path, separator, sheet_name, filename_conflict_resolution, has_header=True):
        # 确定分隔符
        sep_map = {
            "逗号": ",",
            "分号": ";",
            "制表符": "\t",
            "空格": " ",
            "竖线": "|"
        }
        sep = sep_map.get(separator, ",")
        
        # 将文本按行分割
        lines = text.strip().split('\n')
        
        # 如果文本为空
        if not text.strip():
            return ("输入文本为空，无法转换为Excel",)
        
        # 解析文本内容
        data = []
        for line in lines:
            if line.strip():  # 忽略空行
                row = line.split(sep)
                data.append(row)
        
        # 如果没有数据
        if not data:
            return ("没有有效的数据可以转换为Excel",)
        
        try:
            # 创建DataFrame
            if has_header and len(data) > 0:
                # 第一行作为列名
                df = pd.DataFrame(data[1:], columns=data[0])
            else:
                # 没有列名
                df = pd.DataFrame(data)
            
            # 确定输出路径
            if not output_excel_path.endswith('.xlsx'):
                output_excel_path += '.xlsx'
            
            full_path = os.path.join(self.output_dir, output_excel_path)
            
            # 处理同名文件冲突
            if os.path.exists(full_path):
                if filename_conflict_resolution == "跳过":
                    return (f"文件已存在，跳过保存: {full_path}",)
                elif filename_conflict_resolution == "递增":
                    # 分离文件名和扩展名
                    name, ext = os.path.splitext(output_excel_path)
                    
                    # 查找递增的文件名
                    counter = 1
                    while True:
                        new_name = f"{name}_{counter}{ext}"
                        new_full_path = os.path.join(self.output_dir, new_name)
                        if not os.path.exists(new_full_path):
                            full_path = new_full_path
                            break
                        counter += 1
            
            # 保存为Excel文件
            with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            result = f"Excel文件已保存: {full_path}"
            return (result,)
        
        except Exception as e:
            return (f"转换失败: {str(e)}",)


NODE_CLASS_MAPPINGS = {
    "TextToExcelNode": TextToExcelNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextToExcelNode": "文本转Excel节点"
}