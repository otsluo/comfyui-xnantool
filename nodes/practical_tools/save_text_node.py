#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
保存文本节点
功能：将输入的文本保存为指定格式的文件，支持txt、csv、md格式
"""

import os
import json
import folder_paths
from datetime import datetime
import uuid
import platform
import random
import string
import logging

# 配置日志
logger = logging.getLogger(__name__)

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
                "file_path": ("STRING", {"default": "", "placeholder": "输入文件路径"}),
                "filename": ("STRING", {"default": "ComfyUI"}),
                "extension": (["txt", "csv", "md", "srt"], {"default": "txt"}),
                "exist_mode": (["覆盖", "直接追加", "换行追加", "跳过"], {"default": "换行追加"}),
            },
            "optional": {
                "text_prefix": ("STRING", {"multiline": True, "default": "", "placeholder": "输入要添加到文本前的前缀"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("保存信息",)
    OUTPUT_NODE = True
    CATEGORY = "XnanTool/实用工具"

    FUNCTION = "save_text"

    def save_text(self, text, file_path, filename, extension, exist_mode, text_prefix=""):
        try:
            # 解析路径中的日期变量
            file_path = self._parse_path_variables(file_path)
            filename = self._parse_path_variables(filename)
            
            # 如果路径为空，使用output目录
            if not file_path or file_path.strip() == "":
                full_path = self.output_dir
            else:
                # 检查是否为绝对路径
                if os.path.isabs(file_path):
                    full_path = file_path
                else:
                    full_path = os.path.join(self.output_dir, file_path)
            
            # 确保目录存在，并检查是否可写
            try:
                os.makedirs(full_path, exist_ok=True)
                # 测试目录是否可写
                test_file = os.path.join(full_path, ".write_test")
                with open(test_file, 'w') as f:
                    f.write('')
                os.remove(test_file)
            except PermissionError as e:
                error_msg = f"❌ 权限错误：无法写入目录 {full_path}\n\n请检查：\n1. 目录权限设置\n2. 是否有写入权限\n3. 尝试使用绝对路径\n\n错误详情：{str(e)}"
                logger.error(error_msg)
                return (error_msg,)
            except OSError as e:
                error_msg = f"❌ 目录创建失败：{full_path}\n\n错误详情：{str(e)}"
                logger.error(error_msg)
                return (error_msg,)
            
            # 获取目录中的文件列表以计算编号
            counter = 1
            try:
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
            except Exception as e:
                logger.warning(f"读取文件列表失败：{str(e)}")
            
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
                elif exist_mode == "直接追加":
                    # 直接追加到现有内容，不换行
                    with open(file_path_full, 'a', encoding='utf-8') as f:
                        if text_prefix:
                            f.write(text_prefix)
                        f.write(text)
                elif exist_mode == "换行追加":
                    # 换行追加到现有内容
                    with open(file_path_full, 'a', encoding='utf-8') as f:
                        f.write('\n')
                        # 如果存在text_prefix则先写入前缀
                        if text_prefix:
                            f.write(text_prefix + '\n')
                        f.write(text)
                elif exist_mode == "跳过":
                    # 跳过，不保存
                    save_info = f"⚠️ 跳过保存，文件已存在: {file_path_full}"
                    return (save_info,)
            else:
                # 文件不存在，直接保存
                # 处理文本前缀
                final_text = text
                if text_prefix:
                    final_text = text_prefix + final_text
                with open(file_path_full, 'w', encoding='utf-8') as f:
                    f.write(final_text)
            
            save_info = (
                f"✅ 文本已保存\n\n"
                f"📄 文件: {file_path_full}\n"
                f"📊 格式: {extension.upper()}\n"
                f"📝 模式: {exist_mode}"
            )
            logger.info(f"文本保存成功：{file_path_full}")
            return (save_info,)
        except Exception as e:
            error_msg = f"❌ 保存文本时发生错误\n\n错误类型：{type(e).__name__}\n错误详情：{str(e)}\n\n请检查：\n1. 文件路径是否正确\n2. 是否有足够的权限\n3. 磁盘空间是否充足"
            logger.error(error_msg)
            return (error_msg,)
    
    def _parse_path_variables(self, path):
        """解析路径中的日期变量"""
        if not path:
            return path
        
        now = datetime.now()
        
        # 支持的变量
        variables = {
            # 日期相关
            '%date:yyyyMMdd%': now.strftime('%Y%m%d'),
            '%date:yyyy-MM-dd%': now.strftime('%Y-%m-%d'),
            '%date:yyyy/MM/dd%': now.strftime('%Y/%m/%d'),
            '%date:yyMMdd%': now.strftime('%y%m%d'),
            '%date:MMdd%': now.strftime('%m%d'),
            '%date:MM-dd%': now.strftime('%m-%d'),
            '%date:hhmm%': now.strftime('%H%M'),
            '%date:hh-mm%': now.strftime('%H-%M'),
            # 时间相关
            '%date:yyyyMMddHHmmss%': now.strftime('%Y%m%d%H%M%S'),
            '%date:yyyy-MM-dd HH:mm:ss%': now.strftime('%Y-%m-%d %H:%M:%S'),
            '%time:HHmmss%': now.strftime('%H%M%S'),
            '%time:HH-mm-ss%': now.strftime('%H-%M-%S'),
            '%time:HHmm%': now.strftime('%H%M'),
            '%time:HH-mm%': now.strftime('%H-%M'),
            '%time:HHmmssfff%': now.strftime('%H%M%S') + f'{now.microsecond // 1000:03d}',
            # 单独的时间单位
            '%year%': now.strftime('%Y'),
            '%month%': now.strftime('%m'),
            '%day%': now.strftime('%d'),
            '%hour%': now.strftime('%H'),
            '%minute%': now.strftime('%M'),
            '%second%': now.strftime('%S'),
            '%millisecond%': str(now.microsecond // 1000).zfill(3),
            # 星期相关
            '%weekday:name%': now.strftime('%A'),
            '%weekday:name:cn%': ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][now.weekday()],
            '%weekday:num%': str(now.weekday() + 1),
            # 周数
            '%week:num%': str(now.isocalendar()[1]).zfill(2),
            '%yearweek%': now.strftime('%Y') + str(now.isocalendar()[1]).zfill(2),
            # 一年中的第几天
            '%yearday%': str(now.timetuple().tm_yday).zfill(3),
            # 时间戳
            '%timestamp%': str(int(now.timestamp())),
            '%timestamp:ms%': str(int(now.timestamp() * 1000)),
            # 随机数
            '%random:4%': ''.join(random.choices(string.digits, k=4)),
            '%random:6%': ''.join(random.choices(string.digits, k=6)),
            '%random:8%': ''.join(random.choices(string.digits, k=8)),
            '%random:letter:4%': ''.join(random.choices(string.ascii_lowercase, k=4)),
            '%random:letter:6%': ''.join(random.choices(string.ascii_lowercase, k=6)),
            '%random:alnum:6%': ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
            '%random:alnum:8%': ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)),
            # UUID
            '%uuid%': str(uuid.uuid4()),
            '%uuid:short%': str(uuid.uuid4())[:8],
            # 系统信息
            '%computer%': platform.node(),
            '%user%': platform.user() if hasattr(platform, 'user') else os.environ.get('USERNAME', os.environ.get('USER', 'unknown')),
            # 文件计数器（如果路径中包含%counter%）
            '%counter:3%': '{counter:03d}',
            '%counter:4%': '{counter:04d}',
            '%counter:5%': '{counter:05d}',
        }
        
        for var, value in variables.items():
            path = path.replace(var, value)
        
        return path


NODE_CLASS_MAPPINGS = {
    "SaveTextNode": SaveTextNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveTextNode": "保存文本"
}