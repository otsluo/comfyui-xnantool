import torch
import numpy as np
from PIL import Image, ImageDraw
import cv2
from ultralytics import YOLO
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YoloDetectAndCropNode:
    """
    YOLO检测与裁剪一体化节点
    直接输入图片，执行YOLO检测并输出裁剪结果
    支持自动切换CUDA/CPU设备
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "yolo_model": ("YOLO_MODEL",),
                "image": ("IMAGE",),
                "classes": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "可选，指定要检测的类别，如 'person,dog,cat'，留空则检测所有类别"
                }),
                "confidence_threshold": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "number"
                }),
                "padding": ("INT", {
                    "default": 20,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "number"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "JSON", "INT", "JSON", "INT", "STRING")
    RETURN_NAMES = ("cropped_image", "detection_results", "detected_objects_count", "crop_info", "crop_regions_count", "info")
    FUNCTION = "detect_and_crop"
    CATEGORY = "XnanTool/yolo和sam/yolo"
    
    def detect_and_crop(self, yolo_model, image, classes, confidence_threshold, padding):
        """
        执行YOLO检测并裁剪图像
        
        Args:
            yolo_model: YOLO模型对象
            image: 输入图像 (tensor格式)
            classes: 要检测的类别列表
            confidence_threshold: 置信度阈值
            padding: 裁剪边界填充像素数
            
        Returns:
            cropped_image: 裁剪后的图像
            detection_results: 检测结果JSON
            detected_objects_count: 检测到的对象数量
            crop_info: 裁剪信息
            crop_regions_count: 裁剪区域数量
        """
        try:
            # 设置模型参数
            original_conf = yolo_model.conf
            yolo_model.conf = confidence_threshold
            
            # 转换图像格式
            image_np = self.tensor_to_numpy(image)
            
            # 确定最佳设备运行模型
            device = self._get_optimal_device(yolo_model)
            logger.info(f"使用设备: {device}")
            
            # 将模型移动到最佳设备
            yolo_model.to(device)
            
            # 将图像也移动到相同设备（如果需要）
            if device.type == 'cuda':
                # 对于YOLO推理，我们实际上使用numpy图像，所以不需要移动tensor
                # 但我们需要确保模型在正确的设备上
                pass
            
            # 执行YOLO检测
            results = yolo_model(image_np, verbose=False)
            
            # 恢复原始置信度阈值
            yolo_model.conf = original_conf
            
            # 解析检测结果
            detections = self.parse_detections(results, classes)
            
            # 如果没有检测到对象，返回原始图像
            if len(detections) == 0:
                logger.warning("未检测到任何对象，返回原始图像")
                empty_info = {
                    "message": "未检测到任何对象",
                    "crop_regions": 0,
                    "padding": padding
                }
                info = f"检测完成，未发现任何对象。置信度阈值: {confidence_threshold}，填充: {padding}px"
                return (
                    image, 
                    json.dumps([]), 
                    0, 
                    json.dumps(empty_info), 
                    0,
                    info
                )
            
            # 执行裁剪
            cropped_image, crop_info = self.crop_image_by_detections(image_np, detections, padding)
            
            # 转换回tensor格式
            cropped_tensor = self.numpy_to_tensor(cropped_image)
            
            # 构建返回信息
            crop_info["padding"] = padding
            crop_info["detected_objects"] = len(detections)
            crop_info["device_used"] = str(device)
            
            # 构建info字符串
            detected_classes = list(set([det["class_name"] for det in detections]))
            info = f"检测完成，发现{len(detections)}个对象: {', '.join(detected_classes)}。置信度阈值: {confidence_threshold}，填充: {padding}px，设备: {device}"
            
            return (
                cropped_tensor,
                json.dumps(detections),
                len(detections),
                json.dumps(crop_info),
                len(detections),
                info
            )
            
        except Exception as e:
            logger.error(f"检测和裁剪过程中出错: {str(e)}")
            # 尝试使用CPU作为后备方案
            try:
                logger.info("尝试使用CPU作为后备方案...")
                yolo_model.conf = original_conf
                yolo_model.to('cpu')
                
                # 转换图像格式
                image_np = self.tensor_to_numpy(image)
                
                # 执行YOLO检测
                results = yolo_model(image_np, verbose=False)
                
                # 解析检测结果
                detections = self.parse_detections(results, classes)
                
                # 如果没有检测到对象，返回原始图像
                if len(detections) == 0:
                    logger.warning("未检测到任何对象，返回原始图像")
                    empty_info = {
                        "message": "未检测到任何对象",
                        "crop_regions": 0,
                        "padding": padding
                    }
                    info = f"检测完成，未发现任何对象。置信度阈值: {confidence_threshold}，填充: {padding}px，设备: CPU(后备)"
                    return (
                        image, 
                        json.dumps([]), 
                        0, 
                        json.dumps(empty_info), 
                        0,
                        info
                    )
                
                # 执行裁剪
                cropped_image, crop_info = self.crop_image_by_detections(image_np, detections, padding)
                
                # 转换回tensor格式
                cropped_tensor = self.numpy_to_tensor(cropped_image)
                
                # 构建返回信息
                crop_info["padding"] = padding
                crop_info["detected_objects"] = len(detections)
                crop_info["device_used"] = "cpu (后备)"
                
                # 构建info字符串
                detected_classes = list(set([det["class_name"] for det in detections]))
                info = f"检测完成，发现{len(detections)}个对象: {', '.join(detected_classes)}。置信度阈值: {confidence_threshold}，填充: {padding}px，设备: CPU(后备)"
                
                return (
                    cropped_tensor,
                    json.dumps(detections),
                    len(detections),
                    json.dumps(crop_info),
                    len(detections),
                    info
                )
            except Exception as fallback_error:
                logger.error(f"后备方案也失败了: {str(fallback_error)}")
                raise Exception(f"检测和裁剪失败: {str(e)}")
    
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
    
    def crop_image_by_detections(self, image, detections, padding):
        """根据检测结果裁剪图像"""
        if len(detections) == 0:
            return image, {"message": "无检测结果"}
        
        # 计算包含所有检测对象的边界框
        x1_min = min([det["bbox"]["x1"] for det in detections])
        y1_min = min([det["bbox"]["y1"] for det in detections])
        x2_max = max([det["bbox"]["x2"] for det in detections])
        y2_max = max([det["bbox"]["y2"] for det in detections])
        
        # 添加边界填充
        h, w = image.shape[:2]
        x1_min = max(0, x1_min - padding)
        y1_min = max(0, y1_min - padding)
        x2_max = min(w, x2_max + padding)
        y2_max = min(h, y2_max + padding)
        
        # 裁剪图像
        cropped_image = image[y1_min:y2_max, x1_min:x2_max]
        
        # 构建裁剪信息
        crop_info = {
            "original_size": {"width": w, "height": h},
            "crop_box": {
                "x1": x1_min,
                "y1": y1_min,
                "x2": x2_max,
                "y2": y2_max,
                "width": x2_max - x1_min,
                "height": y2_max - y1_min
            },
            "padding": padding,
            "detected_objects": len(detections)
        }
        
        return cropped_image, crop_info

# 注册节点
NODE_CLASS_MAPPINGS = {
    "YoloDetectAndCropNode": YoloDetectAndCropNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloDetectAndCropNode": "YOLO检测与裁剪一体化"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']