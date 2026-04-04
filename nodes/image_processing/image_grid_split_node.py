import numpy as np
import torch


class ImageGridSplitNode:
    """
    图像拆分网格节点 - 将图像按网格拆分成多个小图像
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"label": "输入图像"}),
                "grid_rows": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "label": "网格行数"
                }),
                "grid_cols": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "label": "网格列数"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_grid",)
    FUNCTION = "split_image_grid"
    CATEGORY = "XnanTool/图像处理"
    
    def split_image_grid(self, images, grid_rows, grid_cols):
        """
        将图像按网格拆分成多个小图像
        
        Args:
            images: 输入图像批次 (B, H, W, C)
            grid_rows: 网格行数
            grid_cols: 网格列数
            
        Returns:
            tuple: (图像网格,)
        """
        try:
            if images is None:
                raise ValueError("输入图像为空")
            
            batch_size, height, width, channels = images.shape
            
            if batch_size != 1:
                raise ValueError("当前版本仅支持单张图像拆分")
            
            image = images[0]
            
            cell_height = height // grid_rows
            cell_width = width // grid_cols
            
            split_images = []
            
            for row in range(grid_rows):
                for col in range(grid_cols):
                    y_start = row * cell_height
                    y_end = y_start + cell_height
                    x_start = col * cell_width
                    x_end = x_start + cell_width
                    
                    cell = image[y_start:y_end, x_start:x_end, :]
                    split_images.append(cell)
            
            if len(split_images) == 0:
                raise ValueError("没有拆分出任何图像")
            
            split_images_tensor = torch.stack(split_images, dim=0)
            
            return (split_images_tensor,)
            
        except Exception as e:
            print(f"[ImageGridSplitNode] 拆分图像时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return (None,)


NODE_CLASS_MAPPINGS = {
    "ImageGridSplitNode": ImageGridSplitNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageGridSplitNode": "图像拆分网格"
}
