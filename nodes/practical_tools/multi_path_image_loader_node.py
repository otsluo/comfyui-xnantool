import os
import torch
import numpy as np
from PIL import Image

class MultiPathImageLoaderNode:
    """多行路径图片列表输出节点 - 从多行图片路径中加载所有图片并输出为列表"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_paths": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "图片路径列表",
                    "description": "每行一个图片路径，支持绝对路径和相对路径"
                }),
            },
            "optional": {
                "usage_notes": ("STRING", {
                    "default": "多行路径图片列表输出节点\n一次性加载所有有效的图片路径并输出\n\n使用说明：\n  每行输入一个图片路径\n  自动跳过无效路径和无法加载的图片\n  一次性输出所有成功加载的图片\n\n输出说明：\n  输出端口1：图片列表（IMAGE）\n  输出端口2：成功加载的路径列表\n  输出端口3：成功加载的数量\n  输出端口4：跳过的路径列表",
                    "multiline": True
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("图片列表", "文件名列表", "成功路径列表", "成功数量", "跳过路径列表")
    OUTPUT_IS_LIST = (True, True, False, False, False)
    FUNCTION = "load_all_images"
    CATEGORY = "XnanTool/实用工具"
    DESCRIPTION = "从多行图片路径中加载所有图片并一次性输出为列表"
    
    def load_all_images(self, image_paths, usage_notes=None):
        """从多行路径中加载所有图片"""
        try:
            if not image_paths or image_paths.strip() == "":
                empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return ([empty_tensor], [], "", 0, "")
            
            paths = [line.strip() for line in image_paths.split('\n') if line.strip()]
            
            if not paths:
                empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return ([empty_tensor], [], "", 0, "")
            
            images = []
            filenames = []
            loaded_paths = []
            skipped_paths = []
            
            for path in paths:
                try:
                    if not os.path.exists(path):
                        skipped_paths.append(path)
                        continue
                    
                    img = Image.open(path).convert("RGB")
                    img_array = np.array(img).astype(np.float32) / 255.0
                    img_tensor = torch.from_numpy(img_array)[None,]
                    images.append(img_tensor)
                    filename = os.path.basename(path)
                    filenames.append(filename)
                    loaded_paths.append(path)
                except Exception as e:
                    skipped_paths.append(f"{path} (错误: {str(e)})")
                    continue
            
            if not images:
                empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return ([empty_tensor], [], "", 0, '\n'.join(skipped_paths))
            
            success_count = len(loaded_paths)
            loaded_paths_str = '\n'.join(loaded_paths)
            skipped_paths_str = '\n'.join(skipped_paths)
            
            return (images, filenames, loaded_paths_str, success_count, skipped_paths_str)
            
        except Exception as e:
            error_msg = f"加载失败: {str(e)}"
            empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            return ([empty_tensor], [], error_msg, 0, "")


NODE_CLASS_MAPPINGS = {
    "MultiPathImageLoaderNode": MultiPathImageLoaderNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiPathImageLoaderNode": "多行路径图片列表输出",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
