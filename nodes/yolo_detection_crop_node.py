import torch
import numpy as np
from PIL import Image
import cv2
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YoloDetectionCropNode:
    """
    YOLO检测结果裁切节点
    根据YOLO检测节点的检测结果，对图像中的每个检测对象进行裁切
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "detection_results": ("JSON",),
                "padding": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "number",
                    "description": "裁切边距（像素）"
                }),
                "square_crop": ("BOOLEAN", {
                    "default": False,
                    "label": "方形裁切",
                    "description": "是否将裁切区域调整为正方形"
                }),
            },
            "optional": {
                "crop_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "number",
                    "description": "裁切结果索引（0表示第一个检测对象）"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK", "INT", "STRING")
    RETURN_NAMES = ("cropped_images", "masks", "crop_count", "info")
    FUNCTION = "crop_detections"
    CATEGORY = "XnanTool/YOLO"
    
    def crop_detections(self, image, detection_results, padding, square_crop, crop_index=0):
        """
        根据检测结果裁切图像
        
        Args:
            image: 输入图像 (tensor格式)
            detection_results: YOLO检测结果JSON字符串
            padding: 裁切边距（像素）
            square_crop: 是否将裁切区域调整为正方形
            crop_index: 裁切结果索引（0表示第一个检测对象）
            
        Returns:
            cropped_images: 裁切后的图像列表
            masks: 裁切区域的掩码列表
            crop_count: 裁切图像的数量
            info: 处理信息
        """
        try:
            # 解析检测结果
            detections = json.loads(detection_results) if isinstance(detection_results, str) else detection_results
            
            # 转换图像格式
            image_np = self.tensor_to_numpy(image)
            h, w = image_np.shape[:2]
            
            cropped_images_list = []
            masks_list = []
            
            # 为每个检测对象创建裁切图像
            for detection in detections:
                bbox = detection["bbox"]
                x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]
                
                # 应用边距
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(w, x2 + padding)
                y2 = min(h, y2 + padding)
                
                # 如果需要方形裁切
                if square_crop:
                    crop_w = x2 - x1
                    crop_h = y2 - y1
                    if crop_w > crop_h:
                        # 宽度大于高度，调整高度
                        diff = crop_w - crop_h
                        y1 = max(0, y1 - diff // 2)
                        y2 = min(h, y1 + crop_w)
                    elif crop_h > crop_w:
                        # 高度大于宽度，调整宽度
                        diff = crop_h - crop_w
                        x1 = max(0, x1 - diff // 2)
                        x2 = min(w, x1 + crop_h)
                
                # 裁切图像
                cropped = image_np[y1:y2, x1:x2]
                
                # 创建掩码
                mask = np.zeros((h, w), dtype=np.uint8)
                mask[y1:y2, x1:x2] = 255
                
                # 转换格式并添加到列表
                cropped_tensor = self.numpy_to_tensor(cropped)
                mask_tensor = self.mask_to_tensor(mask)
                
                cropped_images_list.append(cropped_tensor)
                masks_list.append(mask_tensor)
            
            # 合并结果
            if cropped_images_list:
                if len(cropped_images_list) > 1:
                    # 根据索引返回特定的裁切结果
                    # 确保索引在有效范围内
                    valid_index = max(0, min(crop_index, len(cropped_images_list) - 1))
                    cropped_batch = cropped_images_list[valid_index]
                    mask_batch = masks_list[valid_index]
                    info = f"成功裁切{len(detections)}个检测对象，返回第{valid_index}个裁切结果"
                else:
                    # 只有一个裁切结果，直接返回
                    cropped_batch = cropped_images_list[0]
                    mask_batch = masks_list[0]
                    info = f"成功裁切{len(detections)}个检测对象，返回唯一裁切结果"
            else:
                # 如果没有检测到对象，返回原始图像和全零掩码
                cropped_batch = image
                mask_batch = torch.zeros((1, h, w), dtype=torch.float32)
                info = "未检测到任何对象，返回原始图像"
            
            return (
                cropped_batch,
                mask_batch,
                len(detections),
                info
            )
            
        except Exception as e:
            logger.error(f"裁切过程中出错: {str(e)}")
            raise Exception(f"裁切失败: {str(e)}")
    
    def tensor_to_numpy(self, tensor):
        """将tensor格式转换为numpy数组 (B,H,W,C) -> (H,W,C) -> (H,W,C) RGB"""
        # 确保tensor在CPU上并转换为numpy
        tensor = tensor.cpu()
        # 如果是批处理格式，取第一张图片
        if tensor.dim() == 4:
            tensor = tensor[0]
        # 转换为numpy并调整维度顺序 (H,W,C)
        numpy_image = tensor.numpy()
        # 转换范围从[0,1]到[0,255]
        numpy_image = (numpy_image * 255).astype(np.uint8)
        # 转换颜色空间从RGB到BGR（OpenCV使用BGR）
        numpy_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
        return numpy_image
    
    def numpy_to_tensor(self, numpy_image):
        """将numpy数组转换为tensor格式 (H,W,C) -> (1,H,W,C)"""
        # 转换颜色空间从BGR到RGB
        if len(numpy_image.shape) == 3 and numpy_image.shape[2] == 3:
            numpy_image = cv2.cvtColor(numpy_image, cv2.COLOR_BGR2RGB)
        # 转换范围从[0,255]到[0,1]
        numpy_image = numpy_image.astype(np.float32) / 255.0
        # 添加批次维度
        if len(numpy_image.shape) == 3:
            tensor = torch.from_numpy(numpy_image).unsqueeze(0)
        else:
            tensor = torch.from_numpy(numpy_image).unsqueeze(0).unsqueeze(-1)
        return tensor
    
    def mask_to_tensor(self, mask):
        """将掩码转换为tensor格式 (H,W) -> (1,H,W)"""
        # 转换范围从[0,255]到[0,1]
        mask = mask.astype(np.float32) / 255.0
        # 添加批次维度
        tensor = torch.from_numpy(mask).unsqueeze(0)
        return tensor

# 注册节点
NODE_CLASS_MAPPINGS = {
    "YoloDetectionCropNode": YoloDetectionCropNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloDetectionCropNode": "YOLO检测裁切节点-【新-dev版】"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']