import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from ultralytics import YOLO
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YoloDetectionNode:
    """
    YOLO检测节点
    直接输入图片，执行YOLO检测并输出检测结果和带标注的图像
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
                "show_annotations": ("BOOLEAN", {
                    "default": True,
                    "label": "显示标注",
                    "description": "是否在输出图像上显示检测框和标签"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "JSON", "INT", "STRING")
    RETURN_NAMES = ("annotated_image", "detection_results", "detected_objects_count", "info")
    FUNCTION = "detect"
    CATEGORY = "XnanTool/YOLO"
    
    def detect(self, yolo_model, image, classes, confidence_threshold, show_annotations):
        """
        执行YOLO检测
        
        Args:
            yolo_model: YOLO模型对象
            image: 输入图像 (tensor格式)
            classes: 要检测的类别列表
            confidence_threshold: 置信度阈值
            show_annotations: 是否显示标注
            
        Returns:
            annotated_image: 带标注的图像
            detection_results: 检测结果JSON
            detected_objects_count: 检测到的对象数量
            info: 处理信息
        """
        try:
            # 保存原始置信度阈值
            original_conf = yolo_model.conf
            yolo_model.conf = confidence_threshold
            
            # 转换图像格式
            image_np = self.tensor_to_numpy(image)
            
            # 保存原始图像用于可能的标注绘制
            if show_annotations:
                annotated_image_np = image_np.copy()
            
            # 确定最佳设备运行模型
            device = self._get_optimal_device(yolo_model)
            logger.info(f"使用设备: {device}")
            
            # 将模型移动到最佳设备
            yolo_model.to(device)
            
            # 执行YOLO检测
            results = yolo_model(image_np, verbose=False)
            
            # 恢复原始置信度阈值
            yolo_model.conf = original_conf
            
            # 解析检测结果
            detections = self.parse_detections(results, classes)
            
            # 在图像上绘制标注（如果启用）
            if show_annotations and len(detections) > 0:
                annotated_image_np = self.draw_annotations(annotated_image_np, detections)
            
            # 转换回tensor格式
            if show_annotations:
                annotated_tensor = self.numpy_to_tensor(annotated_image_np)
            else:
                annotated_tensor = image  # 如果不显示标注，返回原始图像
            
            # 构建info字符串
            if len(detections) == 0:
                info = f"检测完成，未发现任何对象。置信度阈值: {confidence_threshold}，设备: {device}"
            else:
                detected_classes = list(set([det["class_name"] for det in detections]))
                info = f"检测完成，发现{len(detections)}个对象: {', '.join(detected_classes)}。置信度阈值: {confidence_threshold}，设备: {device}"
            
            return (
                annotated_tensor,
                json.dumps(detections),
                len(detections),
                info
            )
            
        except Exception as e:
            logger.error(f"检测过程中出错: {str(e)}")
            # 尝试使用CPU作为后备方案
            try:
                logger.info("尝试使用CPU作为后备方案...")
                yolo_model.conf = original_conf
                yolo_model.to('cpu')
                
                # 转换图像格式
                image_np = self.tensor_to_numpy(image)
                
                # 保存原始图像用于可能的标注绘制
                if show_annotations:
                    annotated_image_np = image_np.copy()
                
                # 执行YOLO检测
                results = yolo_model(image_np, verbose=False)
                
                # 解析检测结果
                detections = self.parse_detections(results, classes)
                
                # 在图像上绘制标注（如果启用）
                if show_annotations and len(detections) > 0:
                    annotated_image_np = self.draw_annotations(annotated_image_np, detections)
                
                # 转换回tensor格式
                if show_annotations:
                    annotated_tensor = self.numpy_to_tensor(annotated_image_np)
                else:
                    annotated_tensor = image  # 如果不显示标注，返回原始图像
                
                # 构建info字符串
                if len(detections) == 0:
                    info = f"检测完成，未发现任何对象。置信度阈值: {confidence_threshold}，设备: CPU(后备)"
                else:
                    detected_classes = list(set([det["class_name"] for det in detections]))
                    info = f"检测完成，发现{len(detections)}个对象: {', '.join(detected_classes)}。置信度阈值: {confidence_threshold}，设备: CPU(后备)"
                
                return (
                    annotated_tensor,
                    json.dumps(detections),
                    len(detections),
                    info
                )
            except Exception as fallback_error:
                logger.error(f"后备方案也失败了: {str(fallback_error)}")
                raise Exception(f"检测失败: {str(e)}")
    
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
    
    def draw_annotations(self, image, detections):
        """在图像上绘制检测框和标签"""
        # 创建PIL图像用于绘制文本
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        
        # 尝试加载中文字体，如果失败则使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            try:
                font = ImageFont.truetype("simhei.ttf", 16)  # 中文字体
            except:
                font = ImageFont.load_default()
        
        # 定义多种颜色用于不同的检测对象
        colors = [
            (0, 255, 0),    # 绿色
            (255, 0, 0),    # 红色
            (0, 0, 255),    # 蓝色
            (255, 255, 0),  # 青色
            (255, 0, 255),  # 紫色
            (0, 255, 255),  # 黄色
            (128, 0, 128),  # 深紫色
            (255, 165, 0),  # 橙色
            (128, 128, 0),  # 橄榄绿
            (0, 128, 128),  # 深青色
        ]
        
        # 为每个检测对象绘制边界框和标签
        for i, detection in enumerate(detections):
            bbox = detection["bbox"]
            class_name = detection["class_name"]
            confidence = detection["confidence"]
            
            # 选择颜色（循环使用颜色列表）
            color = colors[i % len(colors)]
            
            # 绘制边界框
            x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # 准备标签文本
            label = f"{class_name}: {confidence:.2f}"
            
            # 计算文本尺寸
            try:
                left, top, right, bottom = font.getbbox(label)
                text_width = right - left
                text_height = bottom - top
            except:
                # 兼容旧版本PIL
                text_width, text_height = draw.textsize(label, font=font)
            
            # 绘制标签背景
            cv2.rectangle(image, (x1, y1 - text_height - 4), (x1 + text_width, y1), color, -1)
            
            # 绘制标签文本
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)
            draw.text((x1, y1 - text_height - 2), label, fill=(0, 0, 0), font=font)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return image

# 注册节点
NODE_CLASS_MAPPINGS = {
    "YoloDetectionNode": YoloDetectionNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloDetectionNode": "YOLO检测节点"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']