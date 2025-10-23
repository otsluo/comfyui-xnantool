import json
import os
import numpy as np
import torch
from PIL import Image, ImageOps

# 默认预设列表
DEFAULT_PROMPT_PRESETS = [
    ["当朋友来敲门", "温馨的朋友来访场景"],
    ["浪漫晚餐", "浪漫的烛光晚餐场景"],
    ["户外野餐", "阳光明媚的户外野餐"]
]

def load_prompt_presets_config():
    """加载图片视频提示词预设配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'image_video_prompt_presets.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 确保presets字段存在
            if "presets" not in data:
                data["presets"] = []
            return data
    except Exception as e:
        print(f"加载预设配置失败: {e}")
        # 默认配置
        return {
            "presets": []
        }

def save_prompt_presets_config(config: dict) -> bool:
    """保存图片视频提示词预设配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'image_video_prompt_presets.json')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存预设配置失败: {e}")
        return False

def load_image_from_path(image_path):
    """从路径加载图像并转换为ComfyUI格式，参考ComfyUI标准实现"""
    try:
        if not image_path or not os.path.exists(image_path):
            # 返回一个空白图像
            blank_img = np.zeros((512, 512, 3), dtype=np.float32)
            # 转换为tensor格式 (H, W, C) -> (1, H, W, C)
            blank_tensor = torch.from_numpy(blank_img)[None,]
            return blank_tensor
        
        # 加载图像
        img = Image.open(image_path)
        
        # 处理EXIF方向信息
        img = ImageOps.exif_transpose(img)
        
        # 处理特殊的图像模式
        if img.mode == 'I':
            img = img.point(lambda i: i * (1 / 255))
        
        # 转换为RGB模式
        img = img.convert("RGB")
        
        # 转换为numpy数组并归一化到0-1范围
        img_array = np.array(img).astype(np.float32) / 255.0
        
        # 转换为tensor格式 (H, W, C) -> (1, H, W, C)
        img_tensor = torch.from_numpy(img_array)[None,]
        
        return img_tensor
    except Exception as e:
        print(f"加载图像失败: {e}")
        # 出错时返回空白图像
        blank_img = np.zeros((512, 512, 3), dtype=np.float32)
        # 转换为tensor格式 (H, W, C) -> (1, H, W, C)
        blank_tensor = torch.from_numpy(blank_img)[None,]
        return blank_tensor

class ImageVideoPromptPresetSelector:
    """图片视频提示词预设选择器节点 - 提供预设提示词的快速选择"""
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_prompt_presets_config()
        presets = config.get("presets", [])
        
        # 提取所有预设名称和描述
        preset_names = [preset["name"] for preset in presets] if presets else [p[0] for p in DEFAULT_PROMPT_PRESETS]
        preset_descriptions = {}
        
        # 构建预设描述字典
        if presets:
            for preset in presets:
                preset_descriptions[preset["name"]] = preset.get("description", "")
        else:
            preset_descriptions = {p[0]: p[1] for p in DEFAULT_PROMPT_PRESETS}
        
        # 返回输入类型配置
        return {
            "required": {
                "prompt_preset": (preset_names, {
                    "default": preset_names[0] if preset_names else "",
                    "labels": preset_descriptions,
                    "label": "提示词预设",
                    "description": "选择预设的图片和视频提示词"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("image_prompt", "video_prompt")
    FUNCTION = "get_prompts"
    CATEGORY = "XnanTool/实用工具/预设"
    OUTPUT_NODE = True  # 标记为输出节点，可以在UI中显示图像
    
    def get_prompts(self, prompt_preset):
        """根据选中的预设返回对应的图片和视频提示词，并在节点UI中显示预览图像"""
        config = load_prompt_presets_config()
        presets = config.get("presets", [])
        
        # 查找匹配的预设
        for preset in presets:
            if preset["name"] == prompt_preset:
                image_prompt = preset.get("image_prompt", "")
                video_prompt = preset.get("video_prompt", "")
                
                # 获取图像路径并加载图像
                image_path = preset.get("image_path", "")
                # 如果是相对路径，则相对于nodes目录
                if image_path and not os.path.isabs(image_path):
                    image_path = os.path.join(os.path.dirname(__file__), image_path)
                
                # 加载预览图像但不作为输出端口返回
                image_preview = load_image_from_path(image_path)
                
                # 获取文件名用于UI显示
                filename = os.path.basename(image_path) if image_path else "preview.png"
                
                # 返回提示词和预览图像（用于节点UI显示）
                return {"ui": {"images": [{"filename": filename, "type": "temp", "subfolder": ""}]}, 
                        "result": (image_prompt, video_prompt)}
        
        # 如果没有找到匹配的预设，返回空字符串
        return {"ui": {}, "result": ("", "")}

class ImageVideoPromptPresetManager:
    """图片视频提示词预设管理节点 - 用于查看和管理预设提示词"""
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_prompt_presets_config()
        presets = config.get("presets", [])
        
        # 提取所有预设名称，用于delete操作的下拉选择
        preset_names = [preset["name"] for preset in presets] if presets else [p[0] for p in DEFAULT_PROMPT_PRESETS]
        
        return {
            "required": {
                "action": (["list", "add", "delete"], {
                    "default": "list",
                    "label": "操作类型",
                    "description": "选择要执行的操作：list(查看预设列表)、add(添加新预设)或delete(删除预设)"
                })
            },
            "optional": {
                "preset_name": ("STRING", {
                    "default": "",
                    "placeholder": "例如: 我的新预设",
                    "label": "预设名称",
                    "description": "预设的名称，用于在选择器中识别，仅在add操作时需要填写"
                }),
                "preset_description": ("STRING", {
                    "default": "",
                    "placeholder": "例如: 这是一个新预设的描述",
                    "label": "预设描述",
                    "description": "预设的描述信息，仅在add操作时需要填写"
                }),
                "image_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "例如: 描述图片内容的中文、英文提示词...",
                    "label": "图片提示词",
                    "description": "用于生成图片的中文、英文提示词，仅在add操作时需要填写"
                }),
                "video_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "例如: 描述视频内容的中文、英文提示词...",
                    "label": "视频提示词",
                    "description": "用于生成视频的中文、英文提示词，仅在add操作时需要填写"
                }),
                "preset_to_delete": (preset_names, {
                    "default": preset_names[0] if preset_names else "",
                    "label": "要删除的预设",
                    "description": "选择要删除的预设，仅在delete操作时有效"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status_message",)
    FUNCTION = "manage_presets"
    CATEGORY = "XnanTool/实用工具/预设"
    
    def manage_presets(self, action, preset_name="", preset_description="", image_prompt="", video_prompt="", preset_to_delete=""):
        config = load_prompt_presets_config()
        presets = config.get("presets", [])
        
        if action == "list":
            # 列出所有可用预设
            message = "图片视频提示词预设列表:\n"
            message += "========================\n"
            message += "使用说明:\n"
            message += "1. 选择预设名称可直接用于提示词预设选择器节点\n"
            message += "2. 通过add操作可添加新的预设\n"
            message += "3. 通过delete操作可删除现有预设（直接下拉选择）\n"
            message += "4. 添加或删除后需重启ComfyUI才能在选择器中看到变化\n"
            message += "========================\n"
            message += "预设列表:\n"
            
            if presets:
                for i, preset in enumerate(presets):
                    try:
                        name = preset.get("name", "未知名称")
                        desc = preset.get("description", "无描述")
                        image_path = preset.get("image_path", "")
                        if image_path:
                            desc = f"{desc} [有预览图]"
                        message += f"{i+1}. {name} - {desc}\n"
                    except Exception as e:
                        message += f"{i+1}. 处理预设时出错: {str(e)}\n"
            else:
                message += "暂无自定义预设，使用默认预设\n"
                for i, preset in enumerate(DEFAULT_PROMPT_PRESETS):
                    message += f"{i+1}. {preset[0]} - {preset[1]}\n"
            
            return (message,)
        
        elif action == "add":
            # 添加新预设
            if not preset_name:
                return ("添加失败: 预设名称不能为空",)
            
            if not image_prompt and not video_prompt:
                return ("添加失败: 图片提示词和视频提示词至少需要填写一个",)
            
            # 检查是否已存在
            for preset in presets:
                if preset.get("name") == preset_name:
                    return ("添加失败: 该预设名称已存在，请使用不同的名称",)
            
            # 添加新预设
            new_preset = {
                "name": preset_name,
                "description": preset_description or preset_name,
                "image_prompt": image_prompt,
                "video_prompt": video_prompt,
                "image_path": ""
            }
            
            presets.append(new_preset)
            config["presets"] = presets
            success = save_prompt_presets_config(config)
            
            if success:
                return (f"成功添加预设: {preset_name}\n提示：请重启ComfyUI以在提示词预设选择器中看到新添加的预设",)
            else:
                return ("添加预设失败，请检查日志",)
        
        elif action == "delete":
            # 删除预设
            if not preset_to_delete:
                return ("删除失败: 请从下拉列表中选择要删除的预设",)
            
            # 查找并删除预设
            preset_index = -1
            for i, preset in enumerate(presets):
                if preset.get("name") == preset_to_delete:
                    preset_index = i
                    break
            
            if preset_index == -1:
                return ("删除失败: 未找到指定的预设",)
            
            # 删除预设
            preset_removed = presets.pop(preset_index)
            config["presets"] = presets
            success = save_prompt_presets_config(config)
            
            if success:
                return (f"成功删除预设: {preset_removed.get('name', '未知名称')}\n提示：请重启ComfyUI以在提示词预设选择器中看到更新",)
            else:
                return ("删除预设失败，请检查日志",)
        
        return ("未知操作，请选择有效的操作类型（list、add或delete）",)

class ImageVideoPromptPresetSelectorDev:
    """图片视频提示词预设选择器节点（Dev版） - 提供预设提示词的快速选择，并在节点区域内显示图像预览"""
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_prompt_presets_config()
        presets = config.get("presets", [])
        
        # 提取所有预设名称和描述
        preset_names = [preset["name"] for preset in presets] if presets else [p[0] for p in DEFAULT_PROMPT_PRESETS]
        preset_descriptions = {}
        
        # 构建预设描述字典
        if presets:
            for preset in presets:
                preset_descriptions[preset["name"]] = preset.get("description", "")
        else:
            preset_descriptions = {p[0]: p[1] for p in DEFAULT_PROMPT_PRESETS}
        
        # 返回输入类型配置
        return {
            "required": {
                "prompt_preset": (preset_names, {
                    "default": preset_names[0] if preset_names else "",
                    "labels": preset_descriptions,
                    "label": "提示词预设",
                    "description": "选择预设的图片和视频提示词"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("image_prompt", "video_prompt")
    FUNCTION = "get_prompts"
    CATEGORY = "XnanTool/实用工具/预设"
    OUTPUT_NODE = True  # 标记为输出节点，可以在UI中显示图像
    
    def get_prompts(self, prompt_preset):
        """根据选中的预设返回对应的图片和视频提示词，并在节点UI中显示预览图像"""
        config = load_prompt_presets_config()
        presets = config.get("presets", [])
        
        # 查找匹配的预设
        for preset in presets:
            if preset["name"] == prompt_preset:
                image_prompt = preset.get("image_prompt", "")
                video_prompt = preset.get("video_prompt", "")
                
                # 获取图像路径并加载图像
                image_path = preset.get("image_path", "")
                # 如果是相对路径，则相对于nodes目录
                if image_path and not os.path.isabs(image_path):
                    image_path = os.path.join(os.path.dirname(__file__), image_path)
                
                # 获取文件名用于UI显示
                filename = os.path.basename(image_path) if image_path else "preview.png"
                
                # 返回提示词和预览图像（用于节点UI显示）
                return {"ui": {"images": [{"filename": filename, "type": "temp", "subfolder": ""}]}, 
                        "result": (image_prompt, video_prompt)}
        
        # 如果没有找到匹配的预设，返回空字符串
        return {"ui": {}, "result": ("", "")}

# 导出节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "ImageVideoPromptPresetSelector": ImageVideoPromptPresetSelector,
    "ImageVideoPromptPresetSelectorDev": ImageVideoPromptPresetSelectorDev,
    "ImageVideoPromptPresetManager": ImageVideoPromptPresetManager
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageVideoPromptPresetSelector": "图片视频提示词预设选择器",
    "ImageVideoPromptPresetSelectorDev": "图片视频提示词预设选择器-【新-dev版】",
    "ImageVideoPromptPresetManager": "图片视频提示词预设管理器"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]