import os
import torch
import numpy as np
from PIL import Image
import random

class BatchImageLoaderNode:
    """多行路径图片批次输出节点 - 从多行图片路径中逐批次加载并输出图片"""
    
    _current_batch_index = {}
    _line_order = {}
    _has_completed = {}
    
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
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 10000,
                    "step": 1,
                    "label": "每次输出数量",
                    "description": "每次运行输出的图片数量，0表示输出所有图片"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999999,
                    "label": "随机种子",
                    "description": "随机打乱时的种子值"
                }),
                "shuffle": (["否", "是"], {
                    "default": "否",
                    "label": "打乱顺序",
                    "description": "是否每次随机打乱顺序输出"
                }),
                "restart": (["否", "是"], {
                    "default": "否",
                    "label": "重新开始",
                    "description": "是否重新开始读取"
                }),
            },
            "optional": {
                "usage_notes": ("STRING", {
                    "default": "多行路径图片批次输出节点\n每次运行输出指定数量的图片，支持打乱顺序\n\n使用说明：\n  每行输入一个图片路径\n  设置每次输出的图片数量\n  支持打乱顺序和重新开始\n\n输出说明：\n  输出端口1：图片数据（IMAGE）\n  输出端口2：当前批次的图片路径列表\n  输出端口3：当前批次号\n  输出端口4：是否已完成全部输出",
                    "multiline": True
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "INT", "BOOL")
    RETURN_NAMES = ("图片", "路径列表", "当前批次", "是否完成")
    FUNCTION = "load_batch_images"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    DESCRIPTION = "从多行图片路径中逐批次加载并输出图片"
    
    def load_batch_images(self, image_paths, batch_size=1, seed=0, shuffle="否", restart="否", usage_notes=None):
        """从多行路径中逐批次加载图片"""
        try:
            if not image_paths or image_paths.strip() == "":
                empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return (empty_tensor, "", 0, True)
            
            paths = [line.strip() for line in image_paths.split('\n') if line.strip()]
            
            if not paths:
                empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return (empty_tensor, "", 0, True)
            
            node_id = id(self)
            
            if restart == "是":
                BatchImageLoaderNode._current_batch_index[node_id] = 0
                BatchImageLoaderNode._line_order[node_id] = None
                BatchImageLoaderNode._has_completed[node_id] = False
            
            if node_id not in BatchImageLoaderNode._current_batch_index:
                BatchImageLoaderNode._current_batch_index[node_id] = 0
                BatchImageLoaderNode._line_order[node_id] = None
                BatchImageLoaderNode._has_completed[node_id] = False
            
            if BatchImageLoaderNode._has_completed.get(node_id, False):
                if restart == "是":
                    BatchImageLoaderNode._current_batch_index[node_id] = 0
                    BatchImageLoaderNode._line_order[node_id] = None
                    BatchImageLoaderNode._has_completed[node_id] = False
                else:
                    empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                    return (empty_tensor, "", 0, True)
            
            current_batch = BatchImageLoaderNode._current_batch_index[node_id]
            
            if batch_size == 0:
                batch_size = len(paths)
            
            if shuffle == "是":
                random.seed(seed)
                shuffled_indices = list(range(len(paths)))
                random.shuffle(shuffled_indices)
                
                start_idx = current_batch * batch_size
                end_idx = min(start_idx + batch_size, len(paths))
                
                if start_idx >= len(paths):
                    BatchImageLoaderNode._has_completed[node_id] = True
                    if restart == "是":
                        BatchImageLoaderNode._current_batch_index[node_id] = 0
                        BatchImageLoaderNode._line_order[node_id] = None
                        BatchImageLoaderNode._has_completed[node_id] = False
                        current_batch = 0
                        start_idx = 0
                        end_idx = min(batch_size, len(paths))
                        shuffled_indices = list(range(len(paths)))
                        random.shuffle(shuffled_indices)
                        selected_indices = shuffled_indices[start_idx:end_idx]
                        selected_paths = [paths[i] for i in selected_indices]
                        images, loaded_paths = self._load_images(selected_paths)
                        path_list = '\n'.join(loaded_paths)
                        BatchImageLoaderNode._current_batch_index[node_id] = 1
                        is_completed = (batch_size >= len(paths))
                        return (images, path_list, 1, is_completed)
                    else:
                        empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                        return (empty_tensor, "", 0, True)
                
                selected_indices = shuffled_indices[start_idx:end_idx]
                selected_paths = [paths[i] for i in selected_indices]
                
                images, loaded_paths = self._load_images(selected_paths)
                path_list = '\n'.join(loaded_paths)
                
                next_batch = current_batch + 1
                BatchImageLoaderNode._current_batch_index[node_id] = next_batch
                
                is_completed = (next_batch * batch_size >= len(paths))
                
                return (images, path_list, current_batch + 1, is_completed)
            else:
                start_idx = current_batch * batch_size
                end_idx = min(start_idx + batch_size, len(paths))
                
                if start_idx >= len(paths):
                    BatchImageLoaderNode._has_completed[node_id] = True
                    if restart == "是":
                        BatchImageLoaderNode._current_batch_index[node_id] = 0
                        BatchImageLoaderNode._has_completed[node_id] = False
                        current_batch = 0
                        start_idx = 0
                        end_idx = min(batch_size, len(paths))
                        selected_paths = paths[start_idx:end_idx]
                        images, loaded_paths = self._load_images(selected_paths)
                        path_list = '\n'.join(loaded_paths)
                        BatchImageLoaderNode._current_batch_index[node_id] = 1
                        is_completed = (batch_size >= len(paths))
                        return (images, path_list, 1, is_completed)
                    else:
                        empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                        return (empty_tensor, "", 0, True)
                
                selected_paths = paths[start_idx:end_idx]
                images, loaded_paths = self._load_images(selected_paths)
                path_list = '\n'.join(loaded_paths)
                
                next_batch = current_batch + 1
                BatchImageLoaderNode._current_batch_index[node_id] = next_batch
                
                is_completed = (next_batch * batch_size >= len(paths))
                
                return (images, path_list, current_batch + 1, is_completed)
            
        except Exception as e:
            error_msg = f"加载失败: {str(e)}"
            empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            return (empty_tensor, error_msg, 0, True)
    
    def _load_images(self, paths):
        """加载图片文件并转换为张量"""
        images = []
        loaded_paths = []
        
        for path in paths:
            try:
                if not os.path.exists(path):
                    continue
                
                img = Image.open(path).convert("RGB")
                img_array = np.array(img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_array).unsqueeze(0)
                images.append(img_tensor)
                loaded_paths.append(path)
            except Exception as e:
                print(f"加载图片失败 {path}: {str(e)}")
                continue
        
        if not images:
            empty_tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            return (empty_tensor, loaded_paths)
        
        batch_tensor = torch.cat(images, dim=0)
        return (batch_tensor, loaded_paths)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "BatchImageLoaderNode": BatchImageLoaderNode,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchImageLoaderNode": "多行路径图片批次输出",
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
