"""
YOLO+SAM背景去除和裁剪节点
使用YOLO进行物体检测，然后使用SAM进行精确分割和背景去除
"""

import torch
import numpy as np
from PIL import Image
import cv2
import logging
from typing import Tuple, Dict, Any, List
import json

# 尝试导入SAM
try:
    from segment_anything import SamPredictor
    sam_available = True
except ImportError:
    sam_available = False
    print("⚠️ SAM库未安装")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YoloSamBackgroundRemovalNode:
    """
    YOLO+SAM背景去除节点
    使用YOLO进行物体检测，然后使用SAM进行精确分割和背景去除
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "yolo_model": ("YOLO_MODEL",),
                "sam_model": ("SAM_MODEL",),
                "image": ("IMAGE",),
                "classes": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "可选，指定要检测的类别，如 'person,dog,cat'，留空则检测所有类别"
                }),
                "selection_mode": (["最高置信度", "手动索引"], {
                    "default": "最高置信度",
                    "label": "选择模式"
                }),
                "object_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "label": "物体索引（手动模式下使用）"
                }),
                "confidence_threshold": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "number",
                    "label": "YOLO置信度阈值"
                }),
                "padding": ("INT", {
                    "default": 50,
                    "min": 0,
                    "max": 500,
                    "step": 1,
                    "label": "边界填充"
                }),
            },
            "optional": {
                "mask_dilation": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "label": "遮罩扩张"
                }),
                "mask_blur": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "label": "遮罩模糊"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("cropped_image", "foreground_mask", "info")
    FUNCTION = "remove_background_with_yolo_sam"
    CATEGORY = "XnanTool/SAM"
    
    def remove_background_with_yolo_sam(self, yolo_model, sam_model, image, classes, selection_mode, object_index, confidence_threshold, padding, mask_dilation=0, mask_blur=0):
        """
        使用YOLO+SAM进行背景去除和裁剪
        
        Args:
            yolo_model: YOLO模型对象
            sam_model: SAM模型对象
            image: 输入图像 (tensor格式)
            classes: 要检测的类别列表
            selection_mode: 选择模式（"最高置信度" 或 "手动索引"）
            object_index: 物体索引（手动模式下使用）
            confidence_threshold: YOLO置信度阈值
            padding: 裁剪边界填充像素数
            mask_dilation: 遮罩扩张像素数
            mask_blur: 遮罩模糊强度
            
        Returns:
            cropped_image: 裁剪后的图像
            foreground_mask: 前景遮罩
            info: 处理信息
        """
        try:
            # 设置YOLO模型参数
            original_conf = yolo_model.conf
            yolo_model.conf = confidence_threshold
            
            # 转换图像格式
            image_np = self.tensor_to_numpy(image)
            
            # 确定最佳设备运行YOLO模型
            device = self._get_optimal_device(yolo_model)
            logger.info(f"使用设备: {device}")
            
            # 将YOLO模型移动到最佳设备
            yolo_model.to(device)
            
            # 执行YOLO检测
            results = yolo_model(image_np, verbose=False)
            
            # 恢复原始置信度阈值
            yolo_model.conf = original_conf
            
            # 解析检测结果
            detections = self.parse_detections(results, classes)
            
            # 如果没有检测到对象，返回原始图像
            if len(detections) == 0:
                logger.warning("未检测到任何对象，返回原始图像")
                info = "未检测到任何对象，返回原始图像"
                return (image, self.create_empty_mask(image), info)
            
            # 根据选择模式选择检测结果
            if selection_mode == "手动索引":
                # 手动索引模式
                if object_index >= len(detections):
                    logger.warning(f"指定的索引 {object_index} 超出检测到的对象数量 {len(detections)}，使用最高置信度的对象")
                    best_detection = max(detections, key=lambda x: x["confidence"])
                    selection_info = f"索引{object_index}超出范围，自动选择"
                else:
                    best_detection = detections[object_index]
                    selection_info = f"手动选择索引{object_index}"
            else:
                # 最高置信度模式
                best_detection = max(detections, key=lambda x: x["confidence"])
                selection_info = "自动选择最高置信度"
            
            # 使用SAM进行精确分割
            mask = self.generate_mask_with_sam(sam_model, image_np, best_detection)
            
            # 后处理遮罩
            mask = self.post_process_mask(mask, mask_dilation, mask_blur)
            
            # 去除背景
            foreground_image = self.remove_background(image_np, mask)
            
            # 根据遮罩裁剪图像
            cropped_image, crop_info = self.crop_image_by_mask(foreground_image, mask, padding)
            
            # 转换回tensor格式
            cropped_tensor = self.numpy_to_tensor(cropped_image)
            mask_tensor = self.mask_to_tensor(mask)
            
            # 构建检测对象信息列表
            detection_info_list = []
            for i, detection in enumerate(detections):
                detection_info_list.append(f"{i}: {detection['class_name']}(置信度:{detection['confidence']:.2f})")
            detection_info_str = ", ".join(detection_info_list)
            
            # 构建info字符串
            info = f"背景去除和裁剪完成。检测到{len(detections)}个对象: {detection_info_str}。{selection_info} '{best_detection['class_name']}'(置信度:{best_detection['confidence']:.2f})进行分割。裁剪区域: {crop_info['width']}x{crop_info['height']}px，填充: {padding}px"
            if mask_dilation > 0:
                info += f"，遮罩扩张: {mask_dilation}px"
            if mask_blur > 0:
                info += f"，遮罩模糊: {mask_blur}px"
            
            return (cropped_tensor, mask_tensor, info)
            
        except Exception as e:
            logger.error(f"背景去除和裁剪过程中出错: {str(e)}")
            raise Exception(f"背景去除和裁剪失败: {str(e)}")
    
    def _get_optimal_device(self, yolo_model):
        """
        获取最优设备用于运行模型
        """
        try:
            # 首先检查CUDA是否可用且能正常工作
            if torch.cuda.is_available():
                # 测试CUDA是否能正常工作
                try:
                    test_tensor = torch.randn(10, 10).cuda()
                    test_result = torch.mm(test_tensor, test_tensor)
                    # 测试NMS操作
                    from torchvision.ops import nms
                    boxes = torch.tensor([[0, 0, 10, 10], [5, 5, 15, 15]], dtype=torch.float).cuda()
                    scores = torch.tensor([0.9, 0.8], dtype=torch.float).cuda()
                    keep = nms(boxes, scores, 0.5)
                    return torch.device('cuda')
                except Exception as cuda_test_error:
                    logger.warning(f"CUDA测试失败，回退到CPU: {str(cuda_test_error)}")
                    return torch.device('cpu')
            else:
                return torch.device('cpu')
        except Exception as e:
            logger.warning(f"设备检测出错，使用CPU: {str(e)}")
            return torch.device('cpu')
    
    def tensor_to_numpy(self, tensor):
        """将tensor格式转换为numpy数组 (B,H,W,C) -> (H,W,C) RGB"""
        # 确保tensor在CPU上并转换为numpy
        tensor = tensor.cpu()
        # 如果是批处理格式，取第一张图片
        if tensor.dim() == 4:
            tensor = tensor[0]
        # 转换为numpy并调整维度顺序 (H,W,C)
        numpy_image = tensor.numpy()
        # 转换范围从[0,1]到[0,255]
        numpy_image = (numpy_image * 255).astype(np.uint8)
        # 转换颜色空间从RGB到BGR（因为OpenCV通常使用BGR）
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
        """将遮罩转换为tensor格式"""
        # 确保遮罩是二维的
        if len(mask.shape) == 3:
            mask = mask[:, :, 0]
        # 转换为浮点数并归一化到[0,1]
        mask = mask.astype(np.float32) / 255.0
        # 添加批次和通道维度
        mask_tensor = torch.from_numpy(mask).unsqueeze(0).unsqueeze(0)
        return mask_tensor
    
    def create_empty_mask(self, image_tensor):
        """创建空遮罩"""
        # 获取图像尺寸
        if image_tensor.dim() == 4:
            h, w = image_tensor.shape[1:3]
        else:
            h, w = image_tensor.shape[0:2]
        # 创建全零遮罩
        empty_mask = torch.zeros((1, 1, h, w), dtype=torch.float32)
        return empty_mask
    
    def parse_detections(self, results, classes_filter):
        """解析YOLO检测结果"""
        detections = []
        
        # 解析类别过滤器
        if classes_filter:
            class_names = [cls.strip().lower() for cls in classes_filter.split(',')]
        else:
            class_names = None
        
        # 遍历检测结果
        for result in results:
            if hasattr(result, 'boxes') and result.boxes is not None:
                boxes = result.boxes
                for i, box in enumerate(boxes):
                    # 获取边界框坐标
                    xyxy = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = map(int, xyxy)
                    
                    # 获取置信度
                    confidence = float(box.conf[0].cpu())
                    
                    # 获取类别信息
                    class_id = int(box.cls[0].cpu())
                    class_name = result.names[class_id]
                    
                    # 过滤类别
                    if class_names and class_name.lower() not in class_names:
                        continue
                    
                    detection = {
                        "index": i,
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox": {
                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2,
                            "width": x2 - x1,
                            "height": y2 - y1
                        }
                    }
                    detections.append(detection)
        
        return detections
    
    def generate_mask_with_sam(self, sam_model, image: np.ndarray, detection: Dict) -> np.ndarray:
        """使用SAM模型生成遮罩"""
        try:
            # 确保图像是RGB格式
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            # 创建SAM预测器
            predictor = SamPredictor(sam_model)
            
            # 设置图像
            predictor.set_image(rgb_image)
            
            # 计算边界框中心点作为提示点
            bbox = detection["bbox"]
            center_x = (bbox["x1"] + bbox["x2"]) // 2
            center_y = (bbox["y1"] + bbox["y2"]) // 2
            
            # 设置提示点（中心点作为前景点）
            input_point = np.array([[center_x, center_y]])
            input_label = np.array([1])  # 1表示前景点
            
            # 生成遮罩
            masks, scores, logits = predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                box=np.array([bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]]),
                multimask_output=False,
            )
            
            # 使用第一个遮罩
            mask = masks[0]
            
            # 转换遮罩为uint8格式
            if mask.dtype != np.uint8:
                mask = (mask * 255).astype(np.uint8)
            
            return mask
        except Exception as e:
            logger.error(f"SAM遮罩生成失败: {str(e)}")
            # 如果SAM失败，创建一个基于边界框的简单遮罩
            bbox = detection["bbox"]
            mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
            mask[bbox["y1"]:bbox["y2"], bbox["x1"]:bbox["x2"]] = 255
            return mask
    
    def post_process_mask(self, mask: np.ndarray, dilation: int, blur: int) -> np.ndarray:
        """后处理遮罩"""
        try:
            # 确保遮罩是二值的
            binary_mask = (mask > 127).astype(np.uint8) * 255
            
            # 遮罩扩张
            if dilation > 0:
                kernel = np.ones((dilation, dilation), np.uint8)
                binary_mask = cv2.dilate(binary_mask, kernel, iterations=1)
            
            # 遮罩模糊
            if blur > 0:
                binary_mask = cv2.GaussianBlur(binary_mask, (blur*2+1, blur*2+1), 0)
            
            return binary_mask
        except Exception as e:
            logger.warning(f"遮罩后处理失败，返回原始遮罩: {str(e)}")
            return mask
    
    def remove_background(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """根据遮罩去除背景"""
        try:
            # 确保遮罩和图像尺寸匹配
            if mask.shape[:2] != image.shape[:2]:
                mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
            
            # 如果遮罩是单通道，扩展为三通道
            if len(mask.shape) == 2:
                mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            elif len(mask.shape) == 3 and mask.shape[2] == 1:
                mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            
            # 应用遮罩
            foreground = cv2.bitwise_and(image, mask)
            
            # 创建透明背景（将背景设为白色）
            background = np.ones_like(image, dtype=np.uint8) * 255
            background = cv2.bitwise_and(background, cv2.bitwise_not(mask))
            
            # 合成结果
            result = cv2.add(foreground, background)
            
            return result
        except Exception as e:
            logger.warning(f"背景去除失败，返回原始图像: {str(e)}")
            return image
    
    def crop_image_by_mask(self, image: np.ndarray, mask: np.ndarray, padding: int) -> Tuple[np.ndarray, Dict]:
        """根据遮罩裁剪图像"""
        try:
            # 确保遮罩是二值的
            binary_mask = (mask > 127).astype(np.uint8) * 255
            
            # 找到遮罩的边界框
            coords = cv2.findNonZero(cv2.cvtColor(binary_mask, cv2.COLOR_BGR2GRAY) if len(binary_mask.shape) == 3 else binary_mask)
            if coords is None:
                # 如果没有找到非零像素，返回原始图像
                return image, {"width": image.shape[1], "height": image.shape[0], "message": "未找到遮罩区域"}
            
            x, y, w, h = cv2.boundingRect(coords)
            
            # 添加边界填充
            h_img, w_img = image.shape[:2]
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(w_img, x + w + padding)
            y2 = min(h_img, y + h + padding)
            
            # 裁剪图像
            cropped_image = image[y1:y2, x1:x2]
            
            # 构建裁剪信息
            crop_info = {
                "original_width": w_img,
                "original_height": h_img,
                "crop_x1": x1,
                "crop_y1": y1,
                "crop_x2": x2,
                "crop_y2": y2,
                "width": x2 - x1,
                "height": y2 - y1,
                "padding": padding
            }
            
            return cropped_image, crop_info
        except Exception as e:
            logger.warning(f"根据遮罩裁剪图像失败，返回原始图像: {str(e)}")
            return image, {"width": image.shape[1], "height": image.shape[0], "message": "裁剪失败"}

# 注册节点
NODE_CLASS_MAPPINGS = {
    "YoloSamBackgroundRemovalNode": YoloSamBackgroundRemovalNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloSamBackgroundRemovalNode": "YOLO+SAM背景去除"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']