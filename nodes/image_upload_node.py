import json
import os
import numpy as np
from PIL import Image

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

def save_image_to_file(image_array, file_path):
    """将numpy数组保存为图像文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 将0-1范围的浮点数转换为0-255的整数
        if image_array.dtype == np.float32 or image_array.dtype == np.float64:
            image_array = (image_array * 255).astype(np.uint8)
        
        # 创建PIL图像
        image = Image.fromarray(image_array)
        
        # 保存图像
        image.save(file_path, format="PNG")
        return True
    except Exception as e:
        print(f"保存图像失败: {e}")
        return False

class ImageUploadNode:
    """图像上传节点 - 用于为预设添加图像预览"""
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_prompt_presets_config()
        presets = config.get("presets", [])
        
        # 提取所有预设名称
        preset_names = [preset["name"] for preset in presets] if presets else []
        
        return {
            "required": {
                "preset_name": (preset_names, {
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
    FUNCTION = "upload_image"
    CATEGORY = "XnanTool/实用工具/预设"
    
    def upload_image(self, preset_name, image):
        """上传并保存图像到指定预设"""
        try:
            # 将图像张量转换为numpy数组
            image_array = image.cpu().numpy()
            
            # 如果是四维张量（批次），取第一张图像
            if len(image_array.shape) == 4:
                image_array = image_array[0]
            
            # 转换为HWC格式（如果需要）
            if image_array.shape[0] < image_array.shape[2]:  # CHW格式
                image_array = np.transpose(image_array, (1, 2, 0))
            
            # 加载配置
            config = load_prompt_presets_config()
            presets = config.get("presets", [])
            
            # 查找匹配的预设
            preset_found = False
            for preset in presets:
                if preset["name"] == preset_name:
                    preset_found = True
                    # 生成图像文件名（使用预设描述作为文件名）
                    description = preset.get("description", preset_name)
                    # 清理文件名中的非法字符
                    safe_description = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_description = safe_description.replace(" ", "_")
                    
                    # 创建图像文件路径（相对于nodes目录）
                    image_filename = f"{safe_description}.png"
                    image_dir = os.path.join(os.path.dirname(__file__), "image_video_prompt_presets_node")
                    os.makedirs(image_dir, exist_ok=True)
                    image_path = os.path.join(image_dir, image_filename)
                    
                    # 保存图像
                    if save_image_to_file(image_array, image_path):
                        # 更新配置中的图像路径（使用相对路径）
                        preset["image_path"] = os.path.join("image_video_prompt_presets_node", image_filename)
                        
                        # 保存更新后的配置
                        if save_prompt_presets_config(config):
                            return (f"成功为预设'{preset_name}'添加图像预览\n文件: {image_filename}",)
                        else:
                            return ("保存配置失败",)
                    else:
                        return ("保存图像文件失败",)
            
            if not preset_found:
                return (f"未找到预设: {preset_name}",)
                
        except Exception as e:
            return (f"处理图像时出错: {str(e)}",)

# 导出节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "ImageUploadNode": ImageUploadNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageUploadNode": "图像上传节点-【新-dev版】"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]