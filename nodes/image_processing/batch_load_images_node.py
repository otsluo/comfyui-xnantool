import os
import folder_paths
import numpy as np
from PIL import Image, ImageOps
import torch
import torch.nn.functional as F

class BatchLoadImagesNode:
    """
    批量加载图片节点
    支持两种模式：
    1. 加载全部图片：从指定目录加载所有图片，可设置最高加载数量
    2. 加载单张图片：根据索引加载单张图片
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["加载全部", "加载单张"], {
                    "default": "加载全部",
                    "tooltip": "选择加载模式：加载全部图片或按索引加载单张图片"
                }),
                "image_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "图片目录路径或单张图片路径"
                }),
            },
            "optional": {
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "tooltip": "当模式为'加载单张'时，指定要加载的图片索引"
                }),
                "max_images": ("INT", {
                    "default": 100,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "tooltip": "当模式为'加载全部'时，限制最多加载的图片数量，设置为0表示加载全部图片"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "INT")
    RETURN_NAMES = ("images", "filenames", "filenames_without_extension", "count")
    OUTPUT_IS_LIST = (True, True, True, False)
    FUNCTION = "load_images"
    CATEGORY = "XnanTool/图像处理"
    DESCRIPTION = """
批量加载图片节点：
- 支持两种模式：加载全部图片或加载单张图片
- 可自定义图片路径
- 加载全部模式支持设置最高加载数量限制，设置为0表示加载全部图片
- 保持原始图片尺寸，不进行任何调整
- 返回图片张量列表、文件名列表和图片数量
"""

    def load_images(self, mode, image_path, index=0, max_images=100):
        if not image_path:
            raise ValueError("图片路径不能为空")
            
        # 检查路径是否存在
        if not os.path.exists(image_path):
            raise ValueError(f"指定的路径不存在: {image_path}")
        
        if mode == "加载全部":
            return self.load_all_images(image_path, max_images)
        else:
            return self.load_single_image(image_path, index)

    def load_all_images(self, image_path, max_images):
        """加载目录中的所有图片"""
        if not os.path.isdir(image_path):
            raise ValueError("加载全部模式需要指定一个目录路径")
            
        # 支持的图片格式
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
        
        # 获取所有图片文件
        image_files = []
        for file in os.listdir(image_path):
            if file.lower().endswith(supported_formats):
                image_files.append(file)
                
        # 按文件名排序
        image_files.sort()
        
        # 限制最大图片数量，当max_images为0时加载全部图片
        if max_images > 0 and len(image_files) > max_images:
            image_files = image_files[:max_images]
            
        if not image_files:
            raise ValueError(f"在目录 {image_path} 中未找到支持的图片文件")
            
        # 加载所有图片
        images = []
        filenames = []
        image_sizes = []  # 记录所有图片的尺寸
        
        for file in image_files:
            file_path = os.path.join(image_path, file)
            try:
                img = Image.open(file_path)
                img = ImageOps.exif_transpose(img)  # 处理EXIF方向
                
                # 转换为RGB（如果需要）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 记录图片尺寸
                image_sizes.append(img.size)
                # 转换为numpy数组并归一化到0-1范围
                img_array = np.array(img).astype(np.float32) / 255.0
                
                # 转换为tensor (H, W, C) -> (1, H, W, C)
                img_tensor = torch.from_numpy(img_array)[None,]
                images.append(img_tensor)
                filenames.append(file)
            except Exception as e:
                print(f"警告: 无法加载图片 {file}: {str(e)}")
                continue
                
        if not images:
            raise ValueError("未能成功加载任何图片")
            
        # 生成不带后缀名的文件名列表
        filenames_without_extension = [os.path.splitext(file)[0] for file in filenames]
        return (images, filenames, filenames_without_extension, len(images))

    def load_single_image(self, image_path, index):
        """根据索引加载单张图片"""
        if os.path.isfile(image_path):
            # 如果路径指向具体文件
            file_path = image_path
            filename = os.path.basename(image_path)
        else:
            # 如果路径指向目录，根据索引查找文件
            if not os.path.isdir(image_path):
                raise ValueError("加载单张模式需要指定一个有效目录或图片文件路径")
                
            # 支持的图片格式
            supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
            
            # 获取所有图片文件并排序
            image_files = []
            for file in os.listdir(image_path):
                if file.lower().endswith(supported_formats):
                    image_files.append(file)
                    
            image_files.sort()
            
            if not image_files:
                raise ValueError(f"在目录 {image_path} 中未找到支持的图片文件")
                
            if index >= len(image_files):
                raise ValueError(f"索引 {index} 超出范围，目录中只有 {len(image_files)} 张图片")
                
            file_path = os.path.join(image_path, image_files[index])
            filename = image_files[index]
            
        # 加载图片
        try:
            img = Image.open(file_path)
            img = ImageOps.exif_transpose(img)  # 处理EXIF方向
            
            # 转换为RGB（如果需要）
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            # 转换为numpy数组并归一化到0-1范围
            img_array = np.array(img).astype(np.float32) / 255.0
            
            # 转换为tensor (H, W, C) -> (1, H, W, C)
            img_tensor = torch.from_numpy(img_array)[None,]
            
            # 生成不带后缀名的文件名
            filename_without_extension = os.path.splitext(filename)[0]
            return ([img_tensor], [filename], [filename_without_extension], 1)
        except Exception as e:
            raise ValueError(f"无法加载图片 {file_path}: {str(e)}")

# 注册节点
NODE_CLASS_MAPPINGS = {
    "BatchLoadImagesNode": BatchLoadImagesNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchLoadImagesNode": "批量加载图片-【Beta】"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']