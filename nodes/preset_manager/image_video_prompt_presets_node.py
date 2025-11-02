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
    
    RETURN_TYPES = ("STRING", "STRING", "IMAGE")
    RETURN_NAMES = ("image_prompt", "video_prompt", "preset_image")
    FUNCTION = "get_prompts"
    CATEGORY = "XnanTool/实用工具/预设"
    
    def get_prompts(self, prompt_preset):
        """根据选择的预设返回图片提示词、视频提示词和预设图片"""
        try:
            config = load_prompt_config()
            prompt_presets = config.get("prompt_presets", [])
            
            # 查找匹配的预设
            selected_preset = None
            for preset in prompt_presets:
                if preset["name"] == prompt_preset:
                    selected_preset = preset
                    break
            
            # 加载预设图片
            if selected_preset and "image_path" in selected_preset:
                # 从配置中获取图片路径
                image_path = selected_preset["image_path"]
                # 提取文件名（去掉路径部分）
                image_filename = os.path.basename(image_path)
                # 去掉扩展名获取预设名称
                preset_name = os.path.splitext(image_filename)[0]
                preset_image = load_preset_image(preset_name)
            else:
                # 默认方式加载图片
                preset_image = load_preset_image(prompt_preset)
            
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
                    
                return (image_prompt, video_prompt, preset_image)
            else:
                # 如果没有找到，返回默认值
                print(f"警告: 未找到预设 '{prompt_preset}'，使用默认值")
                return ("", "", preset_image)
        except Exception as e:
            print(f"ImageVideoPromptSelector.get_prompts 错误: {e}")
            # 出现错误时返回默认值
            return ("", "", None)

class ImageVideoPromptManager:
    """图片视频提示词选预设管理器节点 - 用于管理图片和视频提示词预设"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取现有预设名称用于删除操作
        config = load_prompt_config()
        prompt_presets = config.get("prompt_presets", [])
        preset_names = [preset["name"] for preset in prompt_presets]
        
        return {
            "required": {
                "action": (["list", "add", "delete"], {
                    "default": "list",
                    "label": "操作类型",
                    "description": "选择要执行的操作：列出、添加或删除预设"
                }),
            },
            "optional": {
                "preset_name": ("STRING", {
                    "default": "",
                    "label": "预设名称",
                    "description": "要添加的预设名称（仅在添加操作时使用）"
                }),
                "image_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "图片提示词",
                    "description": "用于生成图片的中文、英文提示词（仅在添加操作时使用）"
                }),
                "video_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "视频提示词",
                    "description": "用于生成视频的中文、英文提示词（仅在添加操作时使用）"
                }),
                "preset_to_delete": (preset_names, {
                    "default": preset_names[0] if preset_names else "",
                    "label": "要删除的预设",
                    "description": "选择要删除的预设（仅在删除操作时使用）"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status_message",)
    FUNCTION = "manage_prompts"
    CATEGORY = "XnanTool/实用工具/预设"
    
    def manage_prompts(self, action, preset_name="", image_prompt="", video_prompt="", preset_to_delete=""):
        """管理图片视频提示词预设"""
        config = load_prompt_config()
        prompt_presets = config.get("prompt_presets", [])
        
        if action == "list":
            # 列出所有预设
            message = "图片视频提示词预设列表:\n"
            message += "=" * 40 + "\n"
            message += "使用说明:\n"
            message += "1. 通过ImageVideoPromptSelector节点选择预设\n"
            message += "2. 通过add操作可添加新的提示词预设\n"
            message += "3. 通过delete操作可删除现有预设\n"
            message += "4. 添加或删除后需重启ComfyUI才能在选择器中看到变化\n"
            message += "=" * 40 + "\n"
            
            # 显示预设
            message += "\n预设列表:\n"
            for i, preset in enumerate(prompt_presets):
                message += f"  {i+1}. {preset['name']}\n"
                image_prompt_text = preset.get('image_prompt', preset.get('prompt', ''))[:50]
                video_prompt_text = preset.get('video_prompt', preset.get('prompt', ''))[:50]
                message += f"     图片提示词: {image_prompt_text}...\n"
                message += f"     视频提示词: {video_prompt_text}...\n"
            
            # 对于list操作，不返回图片
            return (message, None)
        
        elif action == "add":
            # 添加新预设
            if not preset_name:
                return ("添加失败: 请输入预设名称", None)
            
            # 检查是否已存在同名预设
            for preset in prompt_presets:
                if preset["name"] == preset_name:
                    return (f"添加失败: 已存在名为'{preset_name}'的预设", None)
            
            # 添加新预设
            new_preset = {
                "name": preset_name,
                "image_path": f"image_video_prompt_presets_node/{preset_name}.png"
            }
            
            # 如果提供了图片提示词，则添加
            if image_prompt:
                new_preset["image_prompt"] = image_prompt
            
            # 如果提供了视频提示词，则添加
            if video_prompt:
                new_preset["video_prompt"] = video_prompt
            
            # 如果都没有提供，则添加通用提示词字段（为了向后兼容）
            if not image_prompt and not video_prompt:
                new_preset["prompt"] = ""
            
            prompt_presets.append(new_preset)
            config["prompt_presets"] = prompt_presets
            
            # 保存配置
            if save_prompt_config(config):
                # 添加成功后，返回新添加预设的图片
                preset_image = load_preset_image(preset_name)
                return (f"成功添加提示词预设: {preset_name}", preset_image)
            else:
                return ("添加失败: 无法保存配置文件", None)
        
        elif action == "delete":
            # 删除预设
            if not preset_to_delete:
                return ("删除失败: 请选择要删除的预设",)
            
            # 查找并删除预设
            deleted = False
            for i, preset in enumerate(prompt_presets):
                if preset["name"] == preset_to_delete:
                    # 保留至少一个预设
                    if len(prompt_presets) <= 1:
                        return ("删除失败: 至少需要保留一个预设",)
                    
                    del prompt_presets[i]
                    deleted = True
                    break
            
            if not deleted:
                return (f"删除失败: 未找到名为'{preset_to_delete}'的预设",)
            
            # 保存配置
            config["prompt_presets"] = prompt_presets
            if save_prompt_config(config):
                return (f"成功删除提示词预设: {preset_to_delete}",)
            else:
                return ("删除失败: 无法保存配置文件",)

class PresetImageUploadNode:
    """预设图像上传节点 - 用于为预设添加图像预览"""
    
    def __init__(self):
        # 获取预设配置文件路径
        self.config_path = os.path.join(
            os.path.dirname(__file__), 
            "image_video_prompt_presets.json"
        )
        
        # 获取预设图片存储目录
        self.images_dir = os.path.join(
            os.path.dirname(__file__), 
            "image_video_prompt_presets_node"
        )
        
        # 确保图片目录存在
        os.makedirs(self.images_dir, exist_ok=True)
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取现有预设名称
        config_path = os.path.join(
            os.path.dirname(__file__), 
            "image_video_prompt_presets.json"
        )
        
        preset_names = []
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                preset_names = [preset["name"] for preset in config.get("prompt_presets", [])]
        except Exception as e:
            print(f"读取预设配置时出错: {e}")
        
        return {
            "required": {
                "preset_name": (preset_names, {
                    "default": preset_names[0] if preset_names else "",
                    "label": "预设名称",
                    "description": "选择要添加图像预览的预设"
                }),
                "image": ("IMAGE", {
                    "label": "图像",
                    "description": "要保存为预览的图像"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status_message",)
    FUNCTION = "save_preset_image"
    CATEGORY = "XnanTool/实用工具/预设"
    
    def save_preset_image(self, preset_name, image):
        """保存预设图像"""
        try:
            # 将tensor转换为PIL图像
            # 输入图像格式为 [B, H, W, C]，值范围为 0-1
            image_tensor = image[0]  # 取第一张图像
            image_array = (image_tensor.cpu().numpy() * 255).astype(np.uint8)
            pil_image = Image.fromarray(image_array, 'RGB')
            
            # 保持原始宽高比，设置最大尺寸限制为1024x1024
            max_size = 1024
            width, height = pil_image.size
            
            # 如果图像任一边超过最大尺寸，则按比例缩放
            if width > max_size or height > max_size:
                # 计算缩放比例
                ratio = min(max_size / width, max_size / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                # 按比例调整图像大小
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存图像
            image_path = os.path.join(self.images_dir, f"{preset_name}.png")
            pil_image.save(image_path, "PNG")
            
            return (f"成功为预设 '{preset_name}' 保存图像预览",)
        except Exception as e:
            return (f"保存图像时出错: {str(e)}",)

# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "ImageVideoPromptSelector": ImageVideoPromptSelector,
    "ImageVideoPromptManager": ImageVideoPromptManager,
    "PresetImageUploadNode": PresetImageUploadNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageVideoPromptSelector": "图片视频提示词预设",
    "ImageVideoPromptManager": "图片视频提示词预设管理器",
    "PresetImageUploadNode": "预设图像上传节点"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]