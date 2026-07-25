import json
import torch
import os
import glob
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


class YoloModelLoaderV2:
    """YOLO模型加载器V2节点 - 自动扫描并加载本地models/yolo目录中的模型"""
    def __init__(self):
        self.models_cache = {}
        self.config = load_yolo_config()
        os.makedirs(self.config["download_dir"], exist_ok=True)
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_yolo_config()
        model_dir = config["download_dir"]
        
        local_models = []
        if os.path.exists(model_dir):
            pt_files = glob.glob(os.path.join(model_dir, "*.pt"))
            onnx_files = glob.glob(os.path.join(model_dir, "*.onnx"))
            all_model_files = pt_files + onnx_files
            
            for model_file in all_model_files:
                model_name = os.path.basename(model_file)
                display_name = model_name
                local_models.append((model_name, display_name, "local"))
        
        if not local_models:
            local_models.append(("no_models_found", "未找到本地模型，请放入models/yolo目录", "empty"))
        
        model_ids = [model[0] for model in local_models]
        model_labels = {model[0]: model[1] for model in local_models}
        
        return {
            "required": {
                "model_name": (model_ids, {
                    "default": model_ids[0] if model_ids else "",
                    "labels": model_labels,
                    "label": "本地模型",
                    "description": "选择要加载的本地YOLO模型"
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
    FUNCTION = "load_local_model"
    CATEGORY = "❤️❤️❤️XnanTool/yolo和sam/yolo"
    
    def load_local_model(self, model_name, confidence_threshold, iou_threshold, use_cache=True):
        """加载本地YOLO模型"""
        if model_name == "no_models_found":
            raise Exception("未找到本地模型，请将YOLO模型文件(.pt或.onnx)放入models/yolo目录后重新加载")
        
        cache_key = f"local_{model_name}_{confidence_threshold}_{iou_threshold}"
        
        if use_cache and cache_key in self.models_cache:
            model = self.models_cache[cache_key]
            model_info = f"已从缓存加载本地模型: {model_name}"
            return (model, model_info)
        
        try:
            model_path = os.path.join(self.config["download_dir"], model_name)
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"模型文件不存在: {model_path}")
            
            if os.path.getsize(model_path) < 1024 * 1024:
                raise ValueError(f"模型文件可能损坏，大小过小: {model_path}")
            
            model = YOLO(model_path)
            
            model.conf = confidence_threshold
            model.iou = iou_threshold
            
            if use_cache:
                self.models_cache[cache_key] = model
            
            model_info = f"成功加载本地模型: {model_name}\n置信度阈值: {confidence_threshold}\nIOU阈值: {iou_threshold}"
            return (model, model_info)
        except Exception as e:
            error_msg = f"加载本地YOLO模型失败: {str(e)}"
            if "PytorchStreamReader" in str(e):
                error_msg += "\n\n可能的解决方案:\n1. 检查模型文件是否完整\n2. 确认模型文件格式正确(.pt或.onnx)\n3. 确认文件权限正确"
            raise Exception(error_msg)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "YoloModelLoaderV2": YoloModelLoaderV2,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloModelLoaderV2": "YOLO模型加载器V2(本地模型)",
}
