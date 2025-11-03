import torch
import numpy as np
from PIL import Image
import os
import logging
import folder_paths

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchFolderImageFormatConverterNode:
    """
    批量图像格式转换器节点
    支持将指定文件夹中的图像转换为JPEG、PNG、WEBP或BMP格式
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_folder": ("STRING", {
                    "label": "输入文件夹",
                    "description": "输入文件夹路径",
                    "default": "",
                    "multiline": False
                }),
                "output_format": (["JPEG", "PNG", "WEBP", "BMP"], {
                    "label": "输出格式",
                    "description": "选择输出格式",
                    "default": "JPEG"
                }),
                "quality": ("INT", {
                    "label": "图像质量",
                    "description": "JPEG/WEBP格式的图像质量（1-100）",
                    "default": 100,
                    "min": 1,
                    "max": 100,
                    "step": 1
                }),
                "output_folder": ("STRING", {
                    "label": "输出文件夹",
                    "description": "输出文件夹路径（留空则保存到输入文件夹）",
                    "default": "",
                    "multiline": False
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_paths",)
    FUNCTION = "convert_images"
    CATEGORY = "XnanTool/图像处理"

    def get_supported_formats(self):
        """获取支持的图片格式"""
        return ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif')

    def is_supported_image(self, filename):
        """检查文件是否为支持的图片格式"""
        return filename.lower().endswith(self.get_supported_formats())

    def pil_to_tensor(self, pil_image):
        """将PIL图像转换为tensor格式"""
        # 转换为RGB模式（如果需要）
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 转换为numpy数组
        numpy_image = np.array(pil_image).astype(np.float32) / 255.0
        
        # 调整维度顺序为 (H, W, C)
        # ComfyUI期望的格式是 (B, H, W, C)，所以我们需要添加批次维度
        tensor_image = torch.from_numpy(numpy_image)[None,]
        
        return tensor_image

    def get_file_extension(self, format):
        """根据格式获取文件扩展名"""
        extensions = {
            "JPEG": ".jpg",
            "PNG": ".png",
            "WEBP": ".webp",
            "BMP": ".bmp"
        }
        return extensions.get(format, ".jpg")

    def convert_images(self, input_folder, output_format, quality, output_folder):
        """
        批量转换文件夹中的图像格式
        
        Args:
            input_folder (str): 输入文件夹路径
            output_format (str): 输出图像格式
            quality (int): 图像质量（1-100）
            output_folder (str): 输出文件夹路径
            
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
                    
                    # 生成输出文件名
                    base_name = os.path.splitext(image_file)[0]
                    output_filename = f"{base_name}{self.get_file_extension(output_format)}"
                    
                    # 构建完整的输出文件路径
                    output_path = os.path.join(full_output_dir, output_filename)
                    
                    # 保存图像
                    if output_format == "JPEG":
                        # 确保图像是RGB模式
                        if pil_image.mode != 'RGB':
                            pil_image = pil_image.convert('RGB')
                        pil_image.save(output_path, "JPEG", quality=quality, optimize=True)
                    elif output_format == "WEBP":
                        # 确保图像是RGB模式
                        if pil_image.mode != 'RGB':
                            pil_image = pil_image.convert('RGB')
                        pil_image.save(output_path, "WEBP", quality=quality, method=6)
                    elif output_format == "PNG":
                        pil_image.save(output_path, "PNG", optimize=True)
                    elif output_format == "BMP":
                        pil_image.save(output_path, "BMP")
                    else:
                        # 默认使用JPEG格式
                        if pil_image.mode != 'RGB':
                            pil_image = pil_image.convert('RGB')
                        pil_image.save(output_path, "JPEG", quality=quality, optimize=True)
                    
                    output_paths.append(output_path)
                    logger.info(f"图像已保存: {output_path}")
                    
                except Exception as e:
                    logger.error(f"处理图片 {image_file} 时发生错误: {str(e)}")
                    continue
            
            if not output_paths:
                raise Exception("没有成功转换任何图片")
            
            return (output_paths,)
            
        except Exception as e:
            logger.error(f"批量转换图像格式时发生错误: {str(e)}")
            raise Exception(f"图像格式转换失败: {str(e)}")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "BatchFolderImageFormatConverterNode": BatchFolderImageFormatConverterNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchFolderImageFormatConverterNode": "批量图像格式转换器"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]