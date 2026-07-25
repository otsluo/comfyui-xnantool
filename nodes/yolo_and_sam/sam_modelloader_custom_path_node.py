import os
import json
import torch

# 尝试导入SAM，如果不存在则提供安装提示
try:
    from segment_anything import sam_model_registry
    sam_available = True
except ImportError:
    sam_available = False
    print("⚠️ SAM库未安装，将提供安装提示")

# 加载SAM配置
def load_sam_config():
    config_path = os.path.join(os.path.dirname(__file__), 'sam_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "default_model_type": "vit_b",
            "model_dir": "models/sam",
        }


class SamModelLoaderCustomPath:
    """SAM模型加载器(自定义路径) - 支持直接指定本地模型文件的完整路径"""
    def __init__(self):
        self.models_cache = {}
        self.config = load_sam_config()
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_sam_config()
        
        return {
            "required": {
                "custom_model_path": ("STRING", {
                    "default": "",
                    "label": "模型完整路径",
                    "description": "直接输入本地SAM模型文件的完整路径(.pth格式)"
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
    
    RETURN_TYPES = ("SAM_MODEL", "STRING")
    RETURN_NAMES = ("model", "model_info")
    FUNCTION = "load_custom_path_model"
    CATEGORY = "❤️❤️❤️XnanTool/yolo和sam/sam"
    
    def load_custom_path_model(self, custom_model_path, use_cache=True):
        """从自定义路径加载SAM模型"""
        if not custom_model_path:
            raise Exception("请输入有效的模型文件路径")
        
        cache_key = f"custom_path_{os.path.basename(custom_model_path)}"
        
        if use_cache and cache_key in self.models_cache:
            model = self.models_cache[cache_key]
            model_info = f"已从缓存加载自定义路径模型: {custom_model_path}"
            return (model, model_info)
        
        try:
            if not os.path.exists(custom_model_path):
                raise FileNotFoundError(f"模型文件不存在: {custom_model_path}")
            
            if os.path.getsize(custom_model_path) < 1024 * 1024:
                raise ValueError(f"模型文件可能损坏，大小过小: {custom_model_path}")
            
            model_type = self._infer_model_type(os.path.basename(custom_model_path))
            
            print(f"🚀 加载自定义路径SAM模型: {custom_model_path}")
            sam = sam_model_registry[model_type](checkpoint=custom_model_path)
            
            if torch.cuda.is_available():
                sam.to(device='cuda')
                device_info = "GPU"
            else:
                device_info = "CPU"
            
            if use_cache:
                self.models_cache[cache_key] = sam
            
            model_info = f"成功加载自定义路径SAM模型: {custom_model_path}\n运行设备: {device_info}\n模型类型: {model_type}"
            return (sam, model_info)
        except Exception as e:
            error_msg = f"加载自定义路径SAM模型失败: {str(e)}"
            raise Exception(error_msg)
    
    def _infer_model_type(self, model_file):
        """从文件名推断模型类型"""
        if "vit_h" in model_file.lower():
            return "vit_h"
        elif "vit_l" in model_file.lower():
            return "vit_l"
        elif "vit_b" in model_file.lower():
            return "vit_b"
        else:
            print(f"警告: 无法从文件名{model_file}确定模型类型，默认使用vit_b")
            return "vit_b"


# 注册节点
NODE_CLASS_MAPPINGS = {
    "SamModelLoaderCustomPath": SamModelLoaderCustomPath,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "SamModelLoaderCustomPath": "SAM模型加载器(自定义路径)",
}
