import torch
import torchvision.transforms as transforms
import numpy as np
from PIL import Image
import math

class ImageMergeNode:
    """
    图片合并节点 - 将多张图片合并成一张图片
    支持多种合并方式：水平合并、垂直合并、网格合并
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "operation": (["horizontal", "vertical", "grid"], {"default": "grid"}),
                "resize_to_same_size": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "image4": ("IMAGE",),
                "image5": ("IMAGE",),
                "image6": ("IMAGE",),
                "image7": ("IMAGE",),
                "image8": ("IMAGE",),
                "image9": ("IMAGE",),
                "image10": ("IMAGE",),
                "columns": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10,
                    "step": 1,
                    "tooltip": "网格列数，设置为0时自动计算最优列数"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("merged_image",)
    FUNCTION = "merge_images"
    CATEGORY = "XnanTool/图像处理"

    def tensor_to_pil(self, img_tensor):
        """
        将tensor图像转换为PIL图像
        """
        # 确保输入是四维张量 (batch, height, width, channel)
        if len(img_tensor.shape) == 3:
            img_tensor = img_tensor.unsqueeze(0)
        
        # 将tensor转换为numpy数组 (height, width, channel)
        i = 255. * img_tensor.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8)[0])
        return img

    def pil_to_tensor(self, pil_image):
        """
        将PIL图像转换为tensor
        """
        # 将PIL图像转换为numpy数组
        rgb_image = pil_image.convert("RGB")
        img_array = np.array(rgb_image).astype(np.float32) / 255.0
        # 转换为 (height, width, channel) 格式
        tensor = torch.from_numpy(img_array).unsqueeze(0)
        return tensor

    def resize_to_same_size(self, pil_images):
        """
        将所有图片调整为相同尺寸（以最小尺寸为准）
        """
        if not pil_images:
            return pil_images
            
        # 找到最小宽度和高度
        min_width = min(img.width for img in pil_images)
        min_height = min(img.height for img in pil_images)
        
        # 调整所有图片到最小尺寸
        resized_images = []
        for img in pil_images:
            resized_img = img.resize((min_width, min_height), Image.Resampling.LANCZOS)
            resized_images.append(resized_img)
        
        return resized_images

    def merge_images(self, operation, resize_to_same_size, image1=None, image2=None, image3=None, 
                    image4=None, image5=None, image6=None, image7=None, image8=None, 
                    image9=None, image10=None, columns=0):
        """
        合并多张图片
        """
        # 收集所有有效的图片
        images = [img for img in [image1, image2, image3, image4, image5, 
                                 image6, image7, image8, image9, image10] if img is not None]
        
        if not images:
            # 如果没有输入图片，返回一个空白图像
            blank_image = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            return (blank_image,)
        
        # 将tensor图像转换为PIL图像
        pil_images = []
        for img_tensor in images:
            pil_img = self.tensor_to_pil(img_tensor)
            pil_images.append(pil_img)
        
        # 如果需要，调整所有图片到相同尺寸
        if resize_to_same_size:
            pil_images = self.resize_to_same_size(pil_images)
        
        if operation == "horizontal":
            # 水平合并
            total_width = sum(img.width for img in pil_images)
            max_height = max(img.height for img in pil_images)
            
            # 创建合并后的图像
            merged_img = Image.new('RGB', (total_width, max_height))
            
            x_offset = 0
            for img in pil_images:
                merged_img.paste(img, (x_offset, 0))
                x_offset += img.width
                
        elif operation == "vertical":
            # 垂直合并
            max_width = max(img.width for img in pil_images)
            total_height = sum(img.height for img in pil_images)
            
            # 创建合并后的图像
            merged_img = Image.new('RGB', (max_width, total_height))
            
            y_offset = 0
            for img in pil_images:
                merged_img.paste(img, (0, y_offset))
                y_offset += img.height
                
        else:  # grid
            # 网格合并
            num_images = len(pil_images)
            
            # 根据用户输入的列数或自动计算列数
            if columns > 0:
                # 用户指定了列数
                cols = min(columns, num_images)  # 列数不能超过图片总数
                rows = math.ceil(num_images / cols)
            else:
                # 自动计算最优列数（接近正方形布局）
                cols = math.ceil(math.sqrt(num_images))
                rows = math.ceil(num_images / cols)
            
            max_width = max(img.width for img in pil_images)
            max_height = max(img.height for img in pil_images)
            
            # 创建合并后的图像
            total_width = cols * max_width
            total_height = rows * max_height
            merged_img = Image.new('RGB', (total_width, total_height))
            
            for idx, img in enumerate(pil_images):
                row = idx // cols
                col = idx % cols
                x = col * max_width
                y = row * max_height
                merged_img.paste(img, (x, y))
        
        # 将合并后的PIL图像转换回tensor
        merged_tensor = self.pil_to_tensor(merged_img)
        
        return (merged_tensor,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "ImageMergeNode": ImageMergeNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageMergeNode": "图片合并"
}