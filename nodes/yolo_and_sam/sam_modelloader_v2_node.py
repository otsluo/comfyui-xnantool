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


class SamModelLoaderV2:
    """SAM模型加载器V2 - 读取本地models/sam目录中的所有模型文件"""
    def __init__(self):
        self.models_cache = {}
        self.config = load_sam_config()
        os.makedirs(self.config["model_dir"], exist_ok=True)
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_sam_config()
        
        model_dir = config["model_dir"]
        local_models = []
        if os.path.exists(model_dir):
            try:
                files = [f for f in os.listdir(model_dir) if f.endswith('.pth')]
                files.sort()
                local_models = files
            except Exception as e:
                print(f"扫描模型目录失败: {e}")
        
        if not local_models:
            local_models = ["无可用模型"]
        
        return {
            "required": {
                "model_file": (local_models, {
                    "label": "模型文件",
                    "description": "选择本地models/sam目录中的模型文件"
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
    FUNCTION = "load_local_model"
    CATEGORY = "❤️❤️❤️XnanTool/yolo和sam/sam"
    
    def load_local_model(self, model_file, use_cache=True):
        """加载本地SAM模型文件"""
        if not sam_available:
            raise ImportError("SAM库未安装，请先安装: pip install git+https://github.com/facebookresearch/segment-anything.git")
        
        if model_file == "无可用模型":
            raise FileNotFoundError(f"models/sam目录中没有找到.pth模型文件，请先下载或放入模型文件")
        
        cache_key = model_file
        if use_cache and cache_key in self.models_cache:
            model = self.models_cache[cache_key]
            model_info = f"已从缓存加载: {model_file}"
            return (model, model_info)
        
        try:
            model_path = os.path.join(self.config["model_dir"], model_file)
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"SAM模型文件不存在: {model_path}")
            
            model_type = self._infer_model_type(model_file)
            
            print(f"🚀 加载本地SAM模型: {model_file}")
            sam = sam_model_registry[model_type](checkpoint=model_path)
            
            if torch.cuda.is_available():
                sam.to(device='cuda')
                device_info = "GPU"
            else:
                device_info = "CPU"
            
            if use_cache:
                self.models_cache[cache_key] = sam
            
            model_info = f"成功加载本地SAM模型: {model_file}\n运行设备: {device_info}\n模型路径: {model_path}\n模型类型: {model_type}"
            return (sam, model_info)
        except Exception as e:
            raise Exception(f"加载本地SAM模型失败: {str(e)}")
    
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
    "SamModelLoaderV2": SamModelLoaderV2,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "SamModelLoaderV2": "SAM模型加载器V2 (本地模型)",
}
