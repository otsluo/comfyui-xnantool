import torch
import numpy as np
from PIL import Image


class BatchImageMergeNode:
    """
    批量图片合并节点 - 将多张图片帧合并成一张图片
    支持水平合并、垂直合并和网格合并
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "operation": (["horizontal", "vertical", "grid"], {"default": "grid"}),
                "resize_to_same_size": ("BOOLEAN", {"default": True}),
                "columns": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "label": "网格列数",
                    "description": "网格列数，设置为0时自动计算最优列数"
                }),
            },
            "optional": {
                "images": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("merged_image",)
    FUNCTION = "merge_batch_images"
    CATEGORY = "XnanTool/图像处理"
    
    def tensor_to_pil(self, img_tensor):
        """
        将tensor图像转换为PIL图像
        """
        if len(img_tensor.shape) == 3:
            img_tensor = img_tensor.unsqueeze(0)
        
        i = 255. * img_tensor.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8)[0])
        return img
    
    def pil_to_tensor(self, pil_image):
        """
        将PIL图像转换为tensor
        """
        rgb_image = pil_image.convert("RGB")
        img_array = np.array(rgb_image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img_array).unsqueeze(0)
        return tensor
    
    def resize_to_same_size(self, pil_images):
        """
        将所有图片调整为相同尺寸（以最小尺寸为准）
        """
        if not pil_images:
            return pil_images
        
        min_width = min(img.width for img in pil_images)
        min_height = min(img.height for img in pil_images)
        
        resized_images = []
        for img in pil_images:
            resized_img = img.resize((min_width, min_height), Image.Resampling.LANCZOS)
            resized_images.append(resized_img)
        
        return resized_images
    
    def merge_batch_images(self, operation, resize_to_same_size, columns, images=None):
        """
        合并批量图片
        """
        images_list = []
        
        if images is not None:
            if len(images.shape) == 3:
                images = images.unsqueeze(0)
            
            for i in range(images.shape[0]):
                img_tensor = images[i]
                pil_img = self.tensor_to_pil(img_tensor)
                images_list.append(pil_img)
        
        if not images_list:
            blank_image = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            return (blank_image,)
        
        if resize_to_same_size:
            images_list = self.resize_to_same_size(images_list)
        
        if operation == "horizontal":
            total_width = sum(img.width for img in images_list)
            max_height = max(img.height for img in images_list)
            
            merged_img = Image.new('RGB', (total_width, max_height))
            
            x_offset = 0
            for img in images_list:
                merged_img.paste(img, (x_offset, 0))
                x_offset += img.width
                
        elif operation == "vertical":
            max_width = max(img.width for img in images_list)
            total_height = sum(img.height for img in images_list)
            
            merged_img = Image.new('RGB', (max_width, total_height))
            
            y_offset = 0
            for img in images_list:
                merged_img.paste(img, (0, y_offset))
                y_offset += img.height
                
        else:
            num_images = len(images_list)
            
            if columns > 0:
                cols = min(columns, num_images)
                rows = (num_images + columns - 1) // columns
            else:
                cols = int(num_images ** 0.5)
                if cols * cols < num_images:
                    cols += 1
                rows = (num_images + cols - 1) // cols
            
            max_width = max(img.width for img in images_list)
            max_height = max(img.height for img in images_list)
            
            total_width = cols * max_width
            total_height = rows * max_height
            merged_img = Image.new('RGB', (total_width, total_height))
            
            for idx, img in enumerate(images_list):
                row = idx // cols
                col = idx % cols
                x = col * max_width
                y = row * max_height
                merged_img.paste(img, (x, y))
        
        merged_tensor = self.pil_to_tensor(merged_img)
        
        return (merged_tensor,)


NODE_CLASS_MAPPINGS = {
    "BatchImageMergeNode": BatchImageMergeNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchImageMergeNode": "批量图片合并"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
