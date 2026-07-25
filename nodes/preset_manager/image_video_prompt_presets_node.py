import json
import os
import folder_paths
from PIL import Image, ImageOps
import numpy as np
import torch

# 预设配置相关函数
def load_prompt_config():
    """加载提示词预设配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'image_video_prompt_presets.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 验证配置结构
        if not isinstance(config, dict):
            raise ValueError("配置文件格式错误：根节点应为对象")
        
        prompt_presets = config.get("prompt_presets", [])
        if not isinstance(prompt_presets, list):
            raise ValueError("配置文件格式错误：prompt_presets应为数组")
        
        # 验证每个预设的必需字段
        for i, preset in enumerate(prompt_presets):
            if not isinstance(preset, dict):
                raise ValueError(f"配置文件格式错误：第{i+1}个预设应为对象")
            
            if "name" not in preset:
                raise ValueError(f"配置文件格式错误：第{i+1}个预设缺少'name'字段")
            
            # 确保每个预设至少有一个提示词字段
            if "prompt" not in preset and "image_prompt" not in preset and "video_prompt" not in preset:
                preset["prompt"] = ""  # 添加空提示词以避免错误
            
            # 为每个预设添加默认图片路径
            if "image_path" not in preset:
                preset["image_path"] = f"image_video_prompt_presets_node/{preset['name']}.png"
        
        return config
    except FileNotFoundError:
        print(f"提示词预设配置文件未找到: {config_path}")
        # 返回默认配置
        return {
            "prompt_presets": [
                {
                    "name": "默认提示词",
                    "prompt": "high quality image",
                    "negative_prompt": "low quality, blurry"
                }
            ]
        }
    except json.JSONDecodeError as e:
        print(f"提示词预设配置文件JSON格式错误: {e}")
        # 返回默认配置
        return {
            "prompt_presets": [
                {
                    "name": "默认提示词",
                    "prompt": "high quality image",
                    "negative_prompt": "low quality, blurry"
                }
            ]
        }
    except Exception as e:
        print(f"加载提示词预设配置失败: {e}")
        # 返回默认配置
        return {
            "prompt_presets": [
                {
                    "name": "默认提示词",
                    "prompt": "high quality image",
                    "negative_prompt": "low quality, blurry"
                }
            ]
        }

def save_prompt_config(config: dict) -> bool:
    """保存提示词预设配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'image_video_prompt_presets.json')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存提示词预设配置失败: {e}")
        return False

def load_preset_image(preset_name: str):
    """加载预设对应的图片"""
    try:
        # 构建图片路径
        image_dir = os.path.join(os.path.dirname(__file__), 'image_video_prompt_presets_node')
        image_path = os.path.join(image_dir, f'{preset_name}.png')
        
        # 检查图片是否存在
        if os.path.exists(image_path):
            # 加载图片
            img = Image.open(image_path)
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")
            img = np.array(img).astype(np.float32) / 255.0
            img = torch.from_numpy(img)[None,]
            return img
        else:
            # 如果图片不存在，返回None
            print(f"预设图片未找到: {image_path}")
            return None
    except Exception as e:
        print(f"加载预设图片失败: {e}")
        return None

class ImageVideoPromptSelector:
    """图片视频提示词选预设节点 - 提供图片和视频提示词预设选择功能"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        try:
            config = load_prompt_config()
            prompt_presets = config.get("prompt_presets", [])
            
            # 提取所有预设名称
            preset_names = [preset["name"] for preset in prompt_presets]
            
            # 确保至少有一个预设
            if not preset_names:
                preset_names = ["默认提示词"]
            
            # 创建名称到预设的映射，用于显示详细信息
            preset_details = {}
            for preset in prompt_presets:
                # 兼容不同版本的配置格式
                if "prompt" in preset:
                    preset_details[preset["name"]] = preset["prompt"]
                elif "image_prompt" in preset:
                    preset_details[preset["name"]] = preset["image_prompt"]
                else:
                    preset_details[preset["name"]] = ""
            
            return {
                "required": {
                    "prompt_preset": (preset_names, {
                        "default": preset_names[0],
                        "label": "提示词预设",
                        "description": "选择预设的图片或视频提示词"
                    })
                }
            }
        except Exception as e:
            print(f"ImageVideoPromptSelector.INPUT_TYPES 错误: {e}")
            # 出现错误时返回默认配置
            return {
                "required": {
                    "prompt_preset": (["默认提示词"], {
                        "default": "默认提示词",
                        "label": "提示词预设",
                        "description": "选择预设的图片或视频提示词"
                    })
                }
            }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("image_prompt", "video_prompt")
    FUNCTION = "get_prompts"
    CATEGORY = "❤️❤️❤️XnanTool/预设"
    
    def get_prompts(self, prompt_preset):
        """根据选择的预设返回图片提示词和视频提示词"""
        try:
            config = load_prompt_config()
            prompt_presets = config.get("prompt_presets", [])
            
            # 查找匹配的预设
            selected_preset = None
            for preset in prompt_presets:
                if preset["name"] == prompt_preset:
                    selected_preset = preset
                    break
            
            # 如果找到了预设，返回对应的提示词
            if selected_preset:
                # 处理图片提示词
                if "image_prompt" in selected_preset:
                    image_prompt = selected_preset["image_prompt"]
                elif "prompt" in selected_preset:
                    # 向后兼容旧格式
                    image_prompt = selected_preset["prompt"]
                else:
                    image_prompt = ""
                
                # 处理视频提示词
                if "video_prompt" in selected_preset:
                    video_prompt = selected_preset["video_prompt"]
                elif "prompt" in selected_preset:
                    # 向后兼容旧格式
                    video_prompt = selected_preset["prompt"]
                else:
                    video_prompt = ""
                
                return (image_prompt, video_prompt)
            else:
                # 如果没有找到，返回默认值
                print(f"警告: 未找到预设 '{prompt_preset}'，使用默认值")
                return ("", "")
        except Exception as e:
            print(f"ImageVideoPromptSelector.get_prompts 错误: {e}")
            # 出现错误时返回默认值
            return ("", "")

# 注册节点
NODE_CLASS_MAPPINGS = {
    "ImageVideoPromptSelector": ImageVideoPromptSelector,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageVideoPromptSelector": "图片视频提示词预设",
}

# 导出映射（必须）
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]