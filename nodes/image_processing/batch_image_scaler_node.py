import torch
import numpy as np
from PIL import Image, ImageOps
import os
import folder_paths

class BatchImageScalerNode:
    """
    批量图像缩放节点
    支持多种缩放模式和尺寸调整选项
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_directory": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输入图像文件夹路径"
                }),
                "save_directory": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输出图像保存路径（留空则保存到输入目录）"
                }),
                "scale_factor": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.1,
                    "display": "slider"
                }),
                "resize_mode": (["按比例缩放", "固定宽度", "固定高度", "固定尺寸"],),
                "target_width": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1
                }),
                "target_height": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1
                }),
                "resampling_filter": (["LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"],),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result_info",)
    FUNCTION = "scale_images"
    CATEGORY = "XnanTool/图像处理"

    def scale_images(self, image_directory, scale_factor, resize_mode, target_width, target_height, resampling_filter, save_directory):
        # 检查输入目录是否存在
        if not os.path.exists(image_directory):
            return (f"错误: 输入目录不存在 - {image_directory}",)
        
        # 获取支持的图像格式
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')
        image_files = [f for f in os.listdir(image_directory) if f.lower().endswith(supported_formats)]
        
        if not image_files:
            return (f"警告: 在指定目录中未找到支持的图像文件 - {image_directory}",)
        
        # 设置保存目录
        if not save_directory:
            save_directory = image_directory
        elif not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        # 设置重采样过滤器
        resample_filters = {
            "LANCZOS": Image.LANCZOS,
            "BICUBIC": Image.BICUBIC,
            "BILINEAR": Image.BILINEAR,
            "NEAREST": Image.NEAREST
        }
        resample_filter = resample_filters[resampling_filter]
        
        # 处理每个图像文件
        processed_count = 0
        for image_file in image_files:
            try:
                # 构建完整的文件路径
                input_path = os.path.join(image_directory, image_file)
                
                # 打开图像
                with Image.open(input_path) as img:
                    # 转换为RGB模式（如果需要）
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 根据缩放模式调整尺寸
                    if resize_mode == "按比例缩放":
                        new_width = int(img.width * scale_factor)
                        new_height = int(img.height * scale_factor)
                        resized_img = img.resize((new_width, new_height), resample_filter)
                    elif resize_mode == "固定宽度":
                        new_width = target_width
                        new_height = int(img.height * (target_width / img.width))
                        resized_img = img.resize((new_width, new_height), resample_filter)
                    elif resize_mode == "固定高度":
                        new_height = target_height
                        new_width = int(img.width * (target_height / img.height))
                        resized_img = img.resize((new_width, new_height), resample_filter)
                    else:  # 固定尺寸
                        resized_img = img.resize((target_width, target_height), resample_filter)
                    
                    # 构建输出文件路径
                    file_name, file_ext = os.path.splitext(image_file)
                    output_path = os.path.join(save_directory, f"{file_name}_scaled{file_ext}")
                    
                    # 保存调整后的图像
                    resized_img.save(output_path, quality=95)
                    processed_count += 1
                    
            except Exception as e:
                print(f"处理图像时出错 {image_file}: {str(e)}")
                continue
        
        # 返回处理结果信息
        return (f"成功处理 {processed_count}/{len(image_files)} 个图像文件。保存路径: {save_directory}",)

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "BatchImageScalerNode": BatchImageScalerNode
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchImageScalerNode": "批量图像缩放"
}