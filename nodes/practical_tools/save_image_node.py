import os
import folder_paths
from PIL import Image
import numpy as np
import torch
from datetime import datetime
import uuid
import platform
import random
import string

class SaveImageNode:
    """
    保存图片节点 - 将图像保存到指定路径
    """
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "file_path": ("STRING", {"default": ""}),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "folder_separator": ("STRING", {"default": "_"}),
                "num_padding_digits": ("INT", {"default": 3, "min": 1, "max": 10, "step": 1}),
                "extension": (["png", "jpg", "jpeg", "gif", "webp", "bmp"],),
                "quality": ("INT", {"default": 100, "min": 1, "max": 100, "step": 1}),
                "save_workflow": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    OUTPUT_NODE = True
    FUNCTION = "save_images"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def save_images(self, images, file_path, filename_prefix="ComfyUI", folder_separator="_", num_padding_digits=3, extension="png", quality=100, prompt=None, extra_pnginfo=None, save_workflow=False):
        """
        保存图片到指定路径
        """
        # 解析路径中的变量
        file_path = self._parse_path_variables(file_path)
        filename_prefix = self._parse_path_variables(filename_prefix)
        
        # 确保输出目录存在
        full_output_dir = os.path.join(self.output_dir, file_path)
        if not os.path.exists(full_output_dir):
            os.makedirs(full_output_dir, exist_ok=True)
        
        saved_files = []
        
        # 生成文件名前缀
        if filename_prefix and filename_prefix.strip():
            base_name = f"{filename_prefix}{folder_separator}"
        else:
            base_name = f"ComfyUI{folder_separator}"
        
        # 查找当前可用的起始编号
        start_counter = 1
        while True:
            test_filename = f"{base_name}{start_counter:0{num_padding_digits}d}.{extension}"
            test_file_path = os.path.join(full_output_dir, test_filename)
            if not os.path.exists(test_file_path):
                break
            start_counter += 1
        
        for idx, image in enumerate(images):
            # 转换图像格式
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # 使用连续编号
            counter = start_counter + idx
            filename = f"{base_name}{counter:0{num_padding_digits}d}.{extension}"
            file_path_full = os.path.join(full_output_dir, filename)
            
            # 保存图片
            try:
                # 格式名称映射
                format_map = {
                    "jpg": "JPEG",
                    "jpeg": "JPEG",
                    "png": "PNG",
                    "gif": "GIF",
                    "webp": "WEBP",
                    "bmp": "BMP"
                }
                pil_format = format_map.get(extension.lower(), extension.upper())

                if extension.lower() in ["jpg", "jpeg"]:
                    # JPEG不支持透明通道，需要特殊处理
                    if img.mode in ('RGBA', 'LA'):
                        # 创建白色背景
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        # 将透明区域合成到白色背景
                        if img.mode == 'RGBA':
                            background.paste(img, mask=img.split()[2])  # 使用alpha通道作为mask
                        else:
                            background.paste(img, mask=img.split()[0])  # LA模式使用亮度作为mask
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(file_path_full, format=pil_format, quality=quality)
                elif extension.lower() == "png":
                    # 仅PNG格式支持保存工作流信息
                    if save_workflow:
                        pnginfo_data = self._get_workflow_exif_data(prompt, extra_pnginfo)
                        if pnginfo_data:
                            img.save(file_path_full, format=pil_format, pnginfo=pnginfo_data)
                        else:
                            img.save(file_path_full, format=pil_format)
                    else:
                        img.save(file_path_full, format=pil_format)
                else:
                    # 其他格式（webp/gif/bmp等）不保存工作流信息
                    if extension.lower() in ["webp"]:
                        img.save(file_path_full, format=pil_format, quality=quality)
                    else:
                        img.save(file_path_full, format=pil_format)
                
                saved_files.append(file_path_full)
                    
            except Exception as e:
                return {"ui": {"status": f"保存失败: {str(e)}"}, "result": (images, f"保存失败: {str(e)}")}

        file_list = "\n".join([f"✅ 图片已保存: {f}" for f in saved_files])
        save_info = f"✅ 成功保存 {len(images)} 张图片\n\n{file_list}\n\n📄 格式: {extension.upper()}\n📊 质量: {quality}"
        
        return {"ui": {"status": save_info}, "result": (images, save_info)}

    @staticmethod
    def _get_workflow_exif_data(prompt, extra_pnginfo):
        """
        生成工作流EXIF/PNGINFO数据
        """
        from PIL.PngImagePlugin import PngInfo
        import json
        
        metadata = PngInfo()
        
        # 添加prompt信息
        if prompt:
            metadata.add_text("prompt", json.dumps(prompt))
        
        # 添加extra_pnginfo信息
        if extra_pnginfo:
            for x in extra_pnginfo:
                metadata.add_text(x, json.dumps(extra_pnginfo[x]))
        
        return metadata
    
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
        }
        
        for var, value in variables.items():
            path = path.replace(var, value)
        
        return path


# 注册节点
NODE_CLASS_MAPPINGS = {
    "SaveImageNode": SaveImageNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageNode": "保存图片"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']