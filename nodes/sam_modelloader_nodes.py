import os
import json
import torch
import numpy as np
from PIL import Image, ImageDraw
import cv2
import requests
from io import BytesIO
import tempfile

# 尝试导入SAM，如果不存在则提供安装提示
try:
    from segment_anything import SamPredictor, SamAutomaticMaskGenerator, sam_model_registry
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
        # 默认配置
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

# 保存SAM配置
def save_sam_config(config: dict) -> bool:
    config_path = os.path.join(os.path.dirname(__file__), 'sam_config.json')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存SAM配置失败: {e}")
        return False

# 下载SAM模型
def download_sam_model(model_name, save_dir):
    """下载SAM预训练模型"""
    if not sam_available:
        raise ImportError("SAM库未安装，请先安装: pip install git+https://github.com/facebookresearch/segment-anything.git")
    
    # 确保保存目录存在
    os.makedirs(save_dir, exist_ok=True)
    
    # 检查模型是否已存在
    save_path = os.path.join(save_dir, model_name)
    if os.path.exists(save_path):
        print(f"✅ 模型 {model_name} 已存在，跳过下载")
        return save_path
    
    # 获取下载链接
    if model_name not in sam_model_urls:
        raise ValueError(f"未知的SAM模型: {model_name}")
    
    url = sam_model_urls[model_name]
    print(f"📥 开始下载SAM模型: {model_name}")
    print(f"🔗 下载链接: {url}")
    print("⏳ 模型较大（约2-3GB），下载可能需要一些时间...")
    
    try:
        # 发送请求
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 保存文件
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    # 显示下载进度
                    if total_size > 0:
                        progress = downloaded_size / total_size * 100
                        print(f"📊 下载进度: {progress:.1f}%", end='\r')
        
        print("\n✅ SAM模型下载完成！")
        return save_path
    except Exception as e:
        # 下载失败，删除部分文件
        if os.path.exists(save_path):
            os.remove(save_path)
        raise Exception(f"下载SAM模型失败: {str(e)}")

class SamModelLoader:
    """SAM模型加载器节点 - 加载和配置SAM模型"""
    def __init__(self):
        self.models_cache = {}        
        self.config = load_sam_config()
        # 确保模型目录存在
        os.makedirs(self.config["model_dir"], exist_ok=True)
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_sam_config()
        
        # 构建模型类型选择列表
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
    CATEGORY = "XnanTool/SAM"
    
    def load_model(self, model_type, auto_download=True, use_cache=True):
        """加载SAM模型"""
        # 检查SAM库是否安装
        if not sam_available:
            raise ImportError("SAM库未安装，请先安装: pip install git+https://github.com/facebookresearch/segment-anything.git")
        
        # 查找模型文件名称
        model_file = None
        for model in supported_sam_models:
            if model[0] == model_type:
                model_file = model[2]
                break
        
        if not model_file:
            raise ValueError(f"未知的SAM模型类型: {model_type}")
        
        # 检查缓存
        cache_key = model_type
        if use_cache and cache_key in self.models_cache:
            model = self.models_cache[cache_key]
            model_info = f"已从缓存加载: {model_type}"
            return (model, model_info)
        
        try:
            # 模型路径
            model_path = os.path.join(self.config["model_dir"], model_file)
            
            # 如果模型不存在且设置了自动下载
            if not os.path.exists(model_path) and auto_download:
                model_path = download_sam_model(model_file, self.config["model_dir"])
            elif not os.path.exists(model_path):
                raise FileNotFoundError(f"SAM模型文件不存在: {model_path}\n请启用自动下载或手动下载模型")
            
            # 加载模型
            print(f"🚀 加载SAM模型: {model_type} ({model_file})")
            sam = sam_model_registry[model_type](checkpoint=model_path)
            
            # 如果有GPU，移至GPU
            if torch.cuda.is_available():
                sam.to(device='cuda')
                device_info = "GPU"
            else:
                device_info = "CPU"
            
            # 添加到缓存
            if use_cache:
                self.models_cache[cache_key] = sam
            
            model_info = f"成功加载SAM模型: {model_type}\n运行设备: {device_info}\n模型路径: {model_path}"
            return (sam, model_info)
        except Exception as e:
            raise Exception(f"加载SAM模型失败: {str(e)}")

class SamModelLoaderV2:
    """SAM模型加载器V2 - 读取本地models/sam目录中的所有模型文件"""
    def __init__(self):
        self.models_cache = {}
        self.config = load_sam_config()
        # 确保模型目录存在
        os.makedirs(self.config["model_dir"], exist_ok=True)
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_sam_config()
        
        # 获取模型目录中的所有.pth文件
        model_dir = config["model_dir"]
        local_models = []
        if os.path.exists(model_dir):
            try:
                # 列出目录中的所有.pth文件
                files = [f for f in os.listdir(model_dir) if f.endswith('.pth')]
                # 按文件名排序
                files.sort()
                local_models = files
            except Exception as e:
                print(f"扫描模型目录失败: {e}")
        
        # 如果没有找到模型，提供一个默认选项
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
    CATEGORY = "XnanTool/SAM"
    
    def load_local_model(self, model_file, use_cache=True):
        """加载本地SAM模型文件"""
        # 检查SAM库是否安装
        if not sam_available:
            raise ImportError("SAM库未安装，请先安装: pip install git+https://github.com/facebookresearch/segment-anything.git")
        
        # 检查是否有可用模型
        if model_file == "无可用模型":
            raise FileNotFoundError(f"models/sam目录中没有找到.pth模型文件，请先下载或放入模型文件")
        
        # 检查缓存
        cache_key = model_file
        if use_cache and cache_key in self.models_cache:
            model = self.models_cache[cache_key]
            model_info = f"已从缓存加载: {model_file}"
            return (model, model_info)
        
        try:
            # 模型路径
            model_path = os.path.join(self.config["model_dir"], model_file)
            
            # 检查模型文件是否存在
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"SAM模型文件不存在: {model_path}")
            
            # 尝试确定模型类型
            model_type = self._infer_model_type(model_file)
            
            # 加载模型
            print(f"🚀 加载本地SAM模型: {model_file}")
            sam = sam_model_registry[model_type](checkpoint=model_path)
            
            # 如果有GPU，移至GPU
            if torch.cuda.is_available():
                sam.to(device='cuda')
                device_info = "GPU"
            else:
                device_info = "CPU"
            
            # 添加到缓存
            if use_cache:
                self.models_cache[cache_key] = sam
            
            model_info = f"成功加载本地SAM模型: {model_file}\n运行设备: {device_info}\n模型路径: {model_path}\n模型类型: {model_type}"
            return (sam, model_info)
        except Exception as e:
            raise Exception(f"加载本地SAM模型失败: {str(e)}")
    
    def _infer_model_type(self, model_file):
        """从文件名推断模型类型"""
        # 检查已知的模型文件名模式
        if "vit_h" in model_file.lower():
            return "vit_h"
        elif "vit_l" in model_file.lower():
            return "vit_l"
        elif "vit_b" in model_file.lower():
            return "vit_b"
        else:
            # 默认返回vit_b，如果不确定
            print(f"警告: 无法从文件名{model_file}确定模型类型，默认使用vit_b")
            return "vit_b"


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
    CATEGORY = "XnanTool/SAM"
    
    def load_custom_path_model(self, custom_model_path, use_cache=True):
        """从自定义路径加载SAM模型"""
        # 验证路径不为空
        if not custom_model_path:
            raise Exception("请输入有效的模型文件路径")
        
        # 生成缓存键
        cache_key = f"custom_path_{os.path.basename(custom_model_path)}"
        
        # 检查缓存
        if use_cache and cache_key in self.models_cache:
            model = self.models_cache[cache_key]
            model_info = f"已从缓存加载自定义路径模型: {custom_model_path}"
            return (model, model_info)
        
        try:
            # 检查模型文件是否存在
            if not os.path.exists(custom_model_path):
                raise FileNotFoundError(f"模型文件不存在: {custom_model_path}")
            
            # 检查文件大小，太小可能是损坏的
            if os.path.getsize(custom_model_path) < 1024 * 1024:  # 小于1MB
                raise ValueError(f"模型文件可能损坏，大小过小: {custom_model_path}")
            
            # 尝试确定模型类型
            model_type = self._infer_model_type(os.path.basename(custom_model_path))
            
            # 加载模型
            print(f"🚀 加载自定义路径SAM模型: {custom_model_path}")
            sam = sam_model_registry[model_type](checkpoint=custom_model_path)
            
            # 如果有GPU，移至GPU
            if torch.cuda.is_available():
                sam.to(device='cuda')
                device_info = "GPU"
            else:
                device_info = "CPU"
            
            # 添加到缓存
            if use_cache:
                self.models_cache[cache_key] = sam
            
            model_info = f"成功加载自定义路径SAM模型: {custom_model_path}\n运行设备: {device_info}\n模型类型: {model_type}"
            return (sam, model_info)
        except Exception as e:
            # 提供更详细的错误信息
            error_msg = f"加载自定义路径SAM模型失败: {str(e)}"
            raise Exception(error_msg)
    
    def _infer_model_type(self, model_file):
        """从文件名推断模型类型"""
        # 检查已知的模型文件名模式
        if "vit_h" in model_file.lower():
            return "vit_h"
        elif "vit_l" in model_file.lower():
            return "vit_l"
        elif "vit_b" in model_file.lower():
            return "vit_b"
        else:
            # 默认返回vit_b，如果不确定
            print(f"警告: 无法从文件名{model_file}确定模型类型，默认使用vit_b")
            return "vit_b"


# 更新节点映射
NODE_CLASS_MAPPINGS = {
    "SamModelLoader": SamModelLoader,
    "SamModelLoaderV2": SamModelLoaderV2,
    "SamModelLoaderCustomPath": SamModelLoaderCustomPath,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SamModelLoader": "SAM模型加载器（预设）-【新】",
    "SamModelLoaderV2": "SAM模型加载器V2 (本地模型)-【新】",
    "SamModelLoaderCustomPath": "SAM模型加载器(自定义路径)-【新】",
}

# 确保模块被正确导入
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']