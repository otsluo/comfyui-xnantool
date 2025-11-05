import torch
import numpy as np
from PIL import Image
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchImageResizerWithConversionNode:
    """
    批量图像缩放（带格式转换）节点
    支持将指定文件夹中的图片按宽度或高度进行批量缩放，并可转换图像格式
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_folder": ("STRING", {
                    "label": "输入文件夹",
                    "description": "包含需要缩放的图片的文件夹路径",
                    "default": "",
                    "multiline": False
                }),
                "resize_mode": (["width", "height"], {
                    "label": "缩放模式",
                    "description": "选择宽度或高度缩放",
                    "default": "width"
                }),
                "size": ("INT", {
                    "label": "目标尺寸",
                    "description": "目标宽度或高度的像素值",
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1
                }),
                "output_folder": ("STRING", {
                    "label": "输出文件夹",
                    "description": "保存的文件夹路径（留空则保存到输入文件夹）",
                    "default": "",
                    "multiline": False
                }),
                "output_format": (["保持原格式", "JPEG", "PNG", "WEBP", "BMP"], {
                    "label": "输出格式",
                    "description": "选择输出图像的格式，保持原格式或转换为指定格式",
                    "default": "保持原格式"
                }),
                "quality": ("INT", {
                    "label": "图像质量",
                    "description": "JPEG或WebP格式的质量（1-100）",
                    "default": 100,
                    "min": 1,
                    "max": 100,
                    "step": 1
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_paths",)
    FUNCTION = "resize_images"
    CATEGORY = "XnanTool/图像处理"

    def get_supported_formats(self):
        """获取支持的图片格式"""
        return ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif')

    def is_supported_image(self, filename):
        """检查文件是否为支持的图片格式"""
        return filename.lower().endswith(self.get_supported_formats())

    def resize_images(self, input_folder, resize_mode, size, output_folder, output_format="保持原格式", quality=95):
        """
        批量缩放文件夹中的图像
        
        Args:
            input_folder (str): 输入文件夹路径
            resize_mode (str): 缩放模式 ("width" 或 "height")
            size (int): 目标尺寸
            output_folder (str): 输出文件夹路径
            output_format (str): 输出图像格式
            quality (int): JPEG或WebP格式的质量（1-100）
            
        Returns:
            tuple: 包含输出文件路径列表的元组
        """
        try:
            # 检查输入文件夹是否存在
            if not os.path.exists(input_folder):
                raise Exception(f"输入文件夹不存在: {input_folder}")
            
            if not os.path.isdir(input_folder):
                raise Exception(f"输入路径不是文件夹: {input_folder}")
            
            # 确定输出文件夹路径
            if output_folder and output_folder.strip():
                # 使用手动设置的输出文件夹
                full_output_dir = output_folder
            else:
                # 如果未指定输出文件夹，则保存到输入文件夹
                full_output_dir = input_folder
            
            # 确保输出目录存在
            if not os.path.exists(full_output_dir):
                os.makedirs(full_output_dir)
            
            # 获取所有支持的图片文件
            image_files = [f for f in os.listdir(input_folder) if self.is_supported_image(f)]
            
            if not image_files:
                raise Exception(f"在文件夹中未找到支持的图片文件: {input_folder}")
            
            # 存储输出文件路径
            output_paths = []
            
            # 处理每个图片文件
            for image_file in image_files:
                try:
                    # 构建完整的输入文件路径
                    input_path = os.path.join(input_folder, image_file)
                    
                    # 打开图片
                    pil_image = Image.open(input_path)
                    
                    # 计算新的尺寸
                    original_width, original_height = pil_image.size
                    
                    if resize_mode == "width":
                        # 按宽度缩放，保持宽高比
                        new_width = size
                        new_height = int((original_height * size) / original_width)
                    else:  # height
                        # 按高度缩放，保持宽高比
                        new_height = size
                        new_width = int((original_width * size) / original_height)
                    
                    # 确保新尺寸至少为1像素
                    new_width = max(1, new_width)
                    new_height = max(1, new_height)
                    
                    # 调整图片尺寸
                    resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                    
                    # 生成输出文件名（根据输出格式更改扩展名）
                    if output_format == "保持原格式":
                        output_filename = image_file
                    else:
                        # 更改文件扩展名以匹配输出格式
                        name, _ = os.path.splitext(image_file)
                        if output_format == "JPEG":
                            output_filename = name + ".jpg"
                        elif output_format == "PNG":
                            output_filename = name + ".png"
                        elif output_format == "WEBP":
                            output_filename = name + ".webp"
                        elif output_format == "BMP":
                            output_filename = name + ".bmp"
                        else:
                            output_filename = image_file  # 保持原格式
                    
                    # 构建完整的输出文件路径
                    output_path = os.path.join(full_output_dir, output_filename)
                    
                    # 保存图像（根据输出格式保存）
                    if output_format == "保持原格式":
                        # 保持原始格式
                        if image_file.lower().endswith(('.jpg', '.jpeg')):
                            # 确保图像是RGB模式
                            if resized_image.mode != 'RGB':
                                resized_image = resized_image.convert('RGB')
                            resized_image.save(output_path, "JPEG", quality=quality, optimize=True)
                        elif image_file.lower().endswith('.png'):
                            resized_image.save(output_path, "PNG", optimize=True)
                        elif image_file.lower().endswith('.webp'):
                            resized_image.save(output_path, "WEBP", quality=quality, method=6)
                        elif image_file.lower().endswith('.bmp'):
                            resized_image.save(output_path, "BMP")
                        else:
                            # 默认保存为JPEG
                            if resized_image.mode != 'RGB':
                                resized_image = resized_image.convert('RGB')
                            resized_image.save(output_path, "JPEG", quality=quality, optimize=True)
                    else:
                        # 转换为指定格式
                        if output_format == "JPEG":
                            # 确保图像是RGB模式
                            if resized_image.mode != 'RGB':
                                resized_image = resized_image.convert('RGB')
                            resized_image.save(output_path, "JPEG", quality=quality, optimize=True)
                        elif output_format == "PNG":
                            resized_image.save(output_path, "PNG", optimize=True)
                        elif output_format == "WEBP":
                            resized_image.save(output_path, "WEBP", quality=quality, method=6)
                        elif output_format == "BMP":
                            resized_image.save(output_path, "BMP")
                    
                    output_paths.append(output_path)
                    logger.info(f"已处理: {input_path} -> {output_path}")
                    
                except Exception as e:
                    logger.error(f"处理图片 {image_file} 时出错: {str(e)}")
                    continue
            
            if not output_paths:
                raise Exception("没有成功处理任何图片")
            
            logger.info(f"批量缩放完成，共处理 {len(output_paths)} 张图片")
            return (output_paths,)
            
        except Exception as e:
            logger.error(f"批量缩放过程中发生错误: {str(e)}")
            raise e

# 注册节点
NODE_CLASS_MAPPINGS = {
    "BatchImageResizerWithConversionNode": BatchImageResizerWithConversionNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchImageResizerWithConversionNode": "批量图像缩放（带格式转换）"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]