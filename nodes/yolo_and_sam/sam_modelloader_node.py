import os
import json
import torch
import requests

# 尝试导入SAM，如果不存在则提供安装提示
try:
    from segment_anything import sam_model_registry
    sam_available = True
except ImportError:
    sam_available = False
    print("⚠️ SAM库未安装，将提供安装提示")

# 支持的SAM模型类型
supported_sam_models = [
    ("vit_h", "SAM ViT-H (大型)", "sam_vit_h_4b8939.pth"),
    ("vit_l", "SAM ViT-L (中型)", "sam_vit_l_0b3195.pth"),
    ("vit_b", "SAM ViT-B (小型)", "sam_vit_b_01ec64.pth"),
]

# SAM模型下载链接
sam_model_urls = {
    "sam_vit_h_4b8939.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
    "sam_vit_l_0b3195.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
    "sam_vit_b_01ec64.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
}

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
            "points_per_side": 32,
            "pred_iou_thresh": 0.86,
            "stability_score_thresh": 0.92,
            "crop_n_layers": 1,
            "crop_n_points_downscale_factor": 2,
            "min_mask_region_area": 100,
            "custom_models": []
        }

# 下载SAM模型
def download_sam_model(model_name, save_dir):
    """下载SAM预训练模型"""
    if not sam_available:
        raise ImportError("SAM库未安装，请先安装: pip install git+https://github.com/facebookresearch/segment-anything.git")
    
    os.makedirs(save_dir, exist_ok=True)
    
    save_path = os.path.join(save_dir, model_name)
    if os.path.exists(save_path):
        print(f"✅ 模型 {model_name} 已存在，跳过下载")
        return save_path
    
    if model_name not in sam_model_urls:
        raise ValueError(f"未知的SAM模型: {model_name}")
    
    url = sam_model_urls[model_name]
    print(f"📥 开始下载SAM模型: {model_name}")
    print(f"🔗 下载链接: {url}")
    print("⏳ 模型较大（约2-3GB），下载可能需要一些时间...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = downloaded_size / total_size * 100
                        print(f"📊 下载进度: {progress:.1f}%", end='\r')
        
        print("\n✅ SAM模型下载完成！")
        return save_path
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise Exception(f"下载SAM模型失败: {str(e)}")


class SamModelLoader:
    """SAM模型加载器节点 - 加载和配置SAM模型"""
    def __init__(self):
        self.models_cache = {}        
        self.config = load_sam_config()
        os.makedirs(self.config["model_dir"], exist_ok=True)
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_sam_config()
        
        model_types = [model[0] for model in supported_sam_models]
        model_labels = {model[0]: model[1] for model in supported_sam_models}
        
        return {
            "required": {
                "model_type": (model_types, {
                    "default": config["default_model_type"],
                    "labels": model_labels,
                    "label": "模型类型",
                    "description": "选择SAM模型类型"
                }),
                "auto_download": ("BOOLEAN", {
                    "default": True,
                    "label": "自动下载",
                    "description": "模型不存在时自动下载"
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
    FUNCTION = "load_model"
    CATEGORY = "❤️❤️❤️XnanTool/yolo和sam/sam"
    
    def load_model(self, model_type, auto_download=True, use_cache=True):
        """加载SAM模型"""
        if not sam_available:
            raise ImportError("SAM库未安装，请先安装: pip install git+https://github.com/facebookresearch/segment-anything.git")
        
        model_file = None
        for model in supported_sam_models:
            if model[0] == model_type:
                model_file = model[2]
                break
        
        if not model_file:
            raise ValueError(f"未知的SAM模型类型: {model_type}")
        
        cache_key = model_type
        if use_cache and cache_key in self.models_cache:
            model = self.models_cache[cache_key]
            model_info = f"已从缓存加载: {model_type}"
            return (model, model_info)
        
        try:
            model_path = os.path.join(self.config["model_dir"], model_file)
            
            if not os.path.exists(model_path) and auto_download:
                model_path = download_sam_model(model_file, self.config["model_dir"])
            elif not os.path.exists(model_path):
                raise FileNotFoundError(f"SAM模型文件不存在: {model_path}\n请启用自动下载或手动下载模型")
            
            print(f"🚀 加载SAM模型: {model_type} ({model_file})")
            sam = sam_model_registry[model_type](checkpoint=model_path)
            
            if torch.cuda.is_available():
                sam.to(device='cuda')
                device_info = "GPU"
            else:
                device_info = "CPU"
            
            if use_cache:
                self.models_cache[cache_key] = sam
            
            model_info = f"成功加载SAM模型: {model_type}\n运行设备: {device_info}\n模型路径: {model_path}"
            return (sam, model_info)
        except Exception as e:
            raise Exception(f"加载SAM模型失败: {str(e)}")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "SamModelLoader": SamModelLoader,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "SamModelLoader": "SAM模型加载器（预设）",
}
