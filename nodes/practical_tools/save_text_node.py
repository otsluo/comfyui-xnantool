#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
保存文本节点
功能：将输入的文本保存为指定格式的文件，支持txt、csv、md格式
"""

import os
import json
import folder_paths

class SaveTextNode:
    """
    保存文本节点
    功能：将输入的文本保存为指定格式的文件，支持txt、csv、md格式
    """
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "file_path": ("STRING", {"default": "", "placeholder": "输入文件路径，留空则保存到output目录"}),
                "filename": ("STRING", {"default": "ComfyUI"}),
                "extension": (["txt", "csv", "md"], {"default": "txt"}),
                "exist_mode": (["覆盖", "追加", "跳过"], {"default": "追加"}),
            },
            "optional": {
                "text_prefix": ("STRING", {"multiline": True, "default": "", "placeholder": "输入要添加到文本前的前缀"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("save_result",)
    OUTPUT_NODE = True
    CATEGORY = "XnanTool/实用工具"

    FUNCTION = "save_text"

    def save_text(self, text, file_path, filename, extension, exist_mode, text_prefix=""):
        # 如果路径为空，使用output目录
        if not file_path or file_path.strip() == "":
            full_path = self.output_dir
        else:
            full_path = os.path.join(self.output_dir, file_path)
        
        # 确保目录存在
        os.makedirs(full_path, exist_ok=True)
        
        # 获取目录中的文件列表以计算编号
        counter = 1
        existing_files = [f for f in os.listdir(full_path) if f.startswith(filename) and f.endswith(f'.{extension}')]
        
        if existing_files:
            # 提取编号并找到最大值
            numbers = []
            for f in existing_files:
                name_part = f[len(filename):-len(f'.{extension}')].lstrip('_')
                if name_part.isdigit():
                    numbers.append(int(name_part))
            
            if numbers:
                counter = max(numbers) + 1
        
        # 生成文件名
        if counter > 1:
            filename_with_counter = f"{filename}_{counter:03d}.{extension}"
        else:
            filename_with_counter = f"{filename}.{extension}"
        
        file_path_full = os.path.join(full_path, filename_with_counter)
        
        # 检查文件是否已存在并根据exist_mode处理
        if os.path.exists(file_path_full):
            if exist_mode == "覆盖":
                # 处理文本前缀
                final_text = text
                if text_prefix:
                    final_text = text_prefix + final_text
                # 直接覆盖
                with open(file_path_full, 'w', encoding='utf-8') as f:
                    f.write(final_text)
            elif exist_mode == "追加":
                # 追加到现有内容，如果存在text_prefix则换行再追加
                with open(file_path_full, 'a', encoding='utf-8') as f:
                    if text_prefix:
                        f.write('\n' + text_prefix)
                    f.write(text)
            elif exist_mode == "跳过":
                # 跳过，不保存
                return (f"跳过保存，文件已存在: {file_path_full}",)
        else:
            # 文件不存在，直接保存
            # 处理文本前缀
            final_text = text
            if text_prefix:
                final_text = text_prefix + final_text
            with open(file_path_full, 'w', encoding='utf-8') as f:
                f.write(final_text)
        
        result = f"文本已保存: {file_path_full}"
        return (result,)


NODE_CLASS_MAPPINGS = {
    "SaveTextNode": SaveTextNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveTextNode": "保存文本节点"
}