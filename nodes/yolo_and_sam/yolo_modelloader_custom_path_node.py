import json
import torch
import os
from ultralytics import YOLO

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


class YoloModelLoaderCustomPath:
    """YOLO模型加载器(自定义路径) - 支持直接指定本地模型文件的完整路径"""
    def __init__(self):
        self.models_cache = {}
        self.config = load_yolo_config()
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_yolo_config()
        
        return {
            "required": {
                "custom_model_path": ("STRING", {
                    "default": "",
                    "label": "模型完整路径",
                    "description": "直接输入本地YOLO模型文件的完整路径(.pt或.onnx格式)"
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
                })
            }
        }
    
    RETURN_TYPES = ("YOLO_MODEL", "STRING")
    RETURN_NAMES = ("model", "model_info")
    FUNCTION = "load_custom_path_model"
    CATEGORY = "❤️❤️❤️XnanTool/yolo和sam/yolo"
    
    def load_custom_path_model(self, custom_model_path, confidence_threshold, iou_threshold, use_cache=True):
        """从自定义路径加载YOLO模型"""
        if not custom_model_path:
            raise Exception("请输入有效的模型文件路径")
        
        cache_key = f"custom_path_{os.path.basename(custom_model_path)}_{confidence_threshold}_{iou_threshold}"
        
        if use_cache and cache_key in self.models_cache:
            model = self.models_cache[cache_key]
            model_info = f"已从缓存加载自定义路径模型: {custom_model_path}"
            return (model, model_info)
        
        try:
            if not os.path.exists(custom_model_path):
                raise FileNotFoundError(f"模型文件不存在: {custom_model_path}")
            
            if os.path.getsize(custom_model_path) < 1024 * 1024:
                raise ValueError(f"模型文件可能损坏，大小过小: {custom_model_path}")
            
            model = YOLO(custom_model_path)
            
            model.conf = confidence_threshold
            model.iou = iou_threshold
            
            if use_cache:
                self.models_cache[cache_key] = model
            
            model_info = f"成功加载自定义路径模型: {custom_model_path}\n置信度阈值: {confidence_threshold}\nIOU阈值: {iou_threshold}"
            return (model, model_info)
        except Exception as e:
            error_msg = f"加载自定义路径YOLO模型失败: {str(e)}"
            if "PytorchStreamReader" in str(e):
                error_msg += "\n\n可能的解决方案:\n1. 检查模型文件是否完整\n2. 确认模型文件格式正确(.pt或.onnx)\n3. 确认文件路径正确且有权限访问"
            raise Exception(error_msg)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "YoloModelLoaderCustomPath": YoloModelLoaderCustomPath,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloModelLoaderCustomPath": "YOLO模型加载器(自定义路径)",
}
