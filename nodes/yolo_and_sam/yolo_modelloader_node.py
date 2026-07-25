import json
import torch
import os
import shutil
import logging
import tempfile
from ultralytics import YOLO

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 支持的YOLO模型列表
supported_yolo_models = [
    # 基础检测模型
    ("yolov8n.pt", "YOLOv8n (轻量检测)", "nano"),
    ("yolov8s.pt", "YOLOv8s (小型检测)", "small"),
    ("yolov8m.pt", "YOLOv8m (中型检测)", "medium"),
    ("yolov8l.pt", "YOLOv8l (大型检测)", "large"),
    ("yolov8x.pt", "YOLOv8x (超大型检测)", "extra_large"),
    
    # 分割模型变体
    ("yolov8n-seg.pt", "YOLOv8n (轻量分割)", "nano_seg"),
    ("yolov8s-seg.pt", "YOLOv8s (小型分割)", "small_seg"),
    ("yolov8m-seg.pt", "YOLOv8m (中型分割)", "medium_seg"),
    ("yolov8l-seg.pt", "YOLOv8l (大型分割)", "large_seg"),
    ("yolov8x-seg.pt", "YOLOv8x (超大型分割)", "extra_large_seg"),
    
    # 姿态估计模型变体
    ("yolov8n-pose.pt", "YOLOv8n (轻量姿态)", "nano_pose"),
    ("yolov8s-pose.pt", "YOLOv8s (小型姿态)", "small_pose"),
    ("yolov8m-pose.pt", "YOLOv8m (中型姿态)", "medium_pose"),
    ("yolov8l-pose.pt", "YOLOv8l (大型姿态)", "large_pose"),
    ("yolov8x-pose.pt", "YOLOv8x (超大型姿态)", "extra_large_pose"),
    
    # 分类模型变体
    ("yolov8n-cls.pt", "YOLOv8n (轻量分类)", "nano_cls"),
    ("yolov8s-cls.pt", "YOLOv8s (小型分类)", "small_cls"),
    ("yolov8m-cls.pt", "YOLOv8m (中型分类)", "medium_cls"),
    ("yolov8l-cls.pt", "YOLOv8l (大型分类)", "large_cls"),
    ("yolov8x-cls.pt", "YOLOv8x (超大型分类)", "extra_large_cls"),
]

# 加载模型配置
def load_yolo_config():
    config_path = os.path.join(os.path.dirname(__file__), 'yolo_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "default_model": "yolov8m.pt",
            "confidence_threshold": 0.5,
            "iou_threshold": 0.45,
            "download_dir": "models/yolo",
            "custom_models": []
        }

# 保存模型配置
def save_yolo_config(config: dict) -> bool:
    config_path = os.path.join(os.path.dirname(__file__), 'yolo_config.json')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存YOLO配置失败: {e}")
        return False


class YoloModelLoader:
    """YOLO模型加载器节点 - 加载和配置YOLO模型"""
    def __init__(self):
        self.models_cache = {}
        self.config = load_yolo_config()
        os.makedirs(self.config["download_dir"], exist_ok=True)
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_yolo_config()
        
        all_models = supported_yolo_models.copy()
        for custom_model in config.get("custom_models", []):
            all_models.append((custom_model["model_path"], custom_model["display_name"], "custom"))
        
        model_ids = [model[0] for model in all_models]
        model_labels = {model[0]: model[1] for model in all_models}
        
        return {
            "required": {
                "model_name": (model_ids, {
                    "default": config["default_model"],
                    "labels": model_labels,
                    "label": "模型名称",
                    "description": "选择要加载的YOLO模型"
                }),
                "confidence_threshold": ("FLOAT", {
                    "default": config["confidence_threshold"],
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.05,
                    "label": "置信度阈值",
                    "description": "检测结果的置信度阈值"
                }),
                "iou_threshold": ("FLOAT", {
                    "default": config["iou_threshold"],
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.05,
                    "label": "IOU阈值",
                    "description": "非最大值抑制的IOU阈值"
                }),
            },
            "optional": {
                "use_cache": ("BOOLEAN", {
                    "default": True,
                    "label": "使用缓存",
                    "description": "是否缓存已加载的模型"
                }),
                "force_reload": ("BOOLEAN", {
                    "default": False,
                    "label": "强制重新加载",
                    "description": "是否强制重新加载模型，忽略缓存和已存在的模型文件"
                })
            }
        }
    
    RETURN_TYPES = ("YOLO_MODEL", "STRING")
    RETURN_NAMES = ("model", "model_info")
    FUNCTION = "load_model"
    CATEGORY = "❤️❤️❤️XnanTool/yolo和sam/yolo"
    
    def load_model(self, model_name, confidence_threshold, iou_threshold, use_cache=True, force_reload=False):
        """加载YOLO模型"""
        cache_key = f"{model_name}_{confidence_threshold}_{iou_threshold}"
        
        if use_cache and not force_reload and cache_key in self.models_cache:
            model = self.models_cache[cache_key]
            model_info = f"已从缓存加载: {model_name}"
            return (model, model_info)
        
        try:
            is_builtin_model = any(model[0] == model_name for model in supported_yolo_models)
            
            if is_builtin_model:
                model_path = os.path.join(self.config["download_dir"], model_name)
                
                if force_reload or not os.path.exists(model_path):
                    logger.info(f"正在下载YOLO模型: {model_name} 到 {self.config['download_dir']}")
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        try:
                            temp_model = YOLO(model_name)
                            shutil.copy2(temp_model.ckpt_path, model_path)
                            logger.info(f"模型下载成功: {model_path}")
                        except Exception as download_error:
                            logger.error(f"模型下载失败: {str(download_error)}")
                            model = YOLO(model_name)
                else:
                    model = YOLO(model_path)
            else:
                if not os.path.exists(model_name):
                    raise FileNotFoundError(f"模型文件不存在: {model_name}")
                if os.path.getsize(model_name) < 1024 * 1024:
                    raise ValueError(f"模型文件可能损坏，大小过小: {model_name}")
                model = YOLO(model_name)
            
            model.conf = confidence_threshold
            model.iou = iou_threshold
            
            if use_cache:
                self.models_cache[cache_key] = model
            
            model_info = f"成功加载模型: {model_name}\n置信度阈值: {confidence_threshold}\nIOU阈值: {iou_threshold}"
            return (model, model_info)
        except Exception as e:
            error_msg = f"加载YOLO模型失败: {str(e)}"
            if "PytorchStreamReader" in str(e):
                error_msg += "\n\n可能的解决方案:\n1. 检查模型文件是否完整，可能需要重新下载\n2. 对于内置模型，尝试启用'强制重新加载'选项\n3. 确认磁盘空间充足\n4. 确认文件权限正确"
            raise Exception(error_msg)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "YoloModelLoader": YoloModelLoader,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloModelLoader": "YOLO模型加载器 (v8预设)",
}
