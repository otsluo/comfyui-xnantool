import torch
import numpy as np
from PIL import Image
import cv2
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YoloDetectionMultiOutputCropNode:
    """
    YOLO检测多输出裁切节点
    根据YOLO检测节点的检测结果，对图像中的每个检测对象进行裁切，
    并通过多个独立输出端口分别输出裁切图像1至裁切图像5
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
            }
        }

    # 定义5个独立的图像输出端口和1个掩码输出端口
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE", "MASK", "MASK", "MASK", "MASK", "MASK", "INT", "STRING")
    RETURN_NAMES = ("cropped_image_1", "cropped_image_2", "cropped_image_3", "cropped_image_4", "cropped_image_5", 
                   "mask_1", "mask_2", "mask_3", "mask_4", "mask_5", "crop_count", "info")
    FUNCTION = "crop_detections"
    CATEGORY = "XnanTool/yolo和sam/yolo"
    
    def crop_detections(self, image, detection_results, padding, square_crop):
        """
        根据检测结果裁切图像，通过多个独立输出端口分别输出裁切图像1至裁切图像5
        
        Args:
            image: 输入图像 (tensor格式)
            detection_results: YOLO检测结果JSON字符串
            padding: 裁切边距（像素）
            square_crop: 是否将裁切区域调整为正方形
            
        Returns:
            cropped_image_1-5: 前5个裁切后的图像（每个都是独立输出）
            mask_1-5: 前5个裁切区域的掩码（每个都是独立输出）
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
            
            # 为每个检测对象创建裁切图像（最多处理5个）
            for i, detection in enumerate(detections[:5]):  # 限制最多处理5个检测对象
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
            
            # 确保始终返回5个图像和掩码输出
            # 如果检测到的对象少于5个，用原始图像和空掩码填充
            while len(cropped_images_list) < 5:
                cropped_images_list.append(image)  # 使用原始图像填充
                empty_mask = torch.zeros((1, h, w), dtype=torch.float32)
                masks_list.append(empty_mask)  # 使用空掩码填充
            
            # 构建信息字符串
            info = f"成功裁切{len(detections)}个检测对象，返回前5个裁切结果"
            if len(detections) > 5:
                info += f"（共检测到{len(detections)}个对象，仅返回前5个）"
            
            return (
                cropped_images_list[0],  # cropped_image_1
                cropped_images_list[1],  # cropped_image_2
                cropped_images_list[2],  # cropped_image_3
                cropped_images_list[3],  # cropped_image_4
                cropped_images_list[4],  # cropped_image_5
                masks_list[0],           # mask_1
                masks_list[1],           # mask_2
                masks_list[2],           # mask_3
                masks_list[3],           # mask_4
                masks_list[4],           # mask_5
                min(len(detections), 5), # crop_count (最多5个)
                info                     # info
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
        # 转换颜色空间从RGB到BGR（因为YOLO通常使用BGR）
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
    "YoloDetectionMultiOutputCropNode": YoloDetectionMultiOutputCropNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloDetectionMultiOutputCropNode": "YOLO检测多输出裁切节点"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']