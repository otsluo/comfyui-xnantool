import json
import os

# 定义AI生图常用尺寸列表，每个尺寸都标注比例
DEFAULT_SIZE_PRESETS = [
    # SD 1.5 推荐尺寸
    ["512x512", "SD 1.5 - 正方形 (1:1)"],
    ["512x768", "SD 1.5 - 竖屏 (2:3)"],
    ["768x512", "SD 1.5 - 横屏 (3:2)"],
    ["768x768", "SD 1.5 - 大正方形 (1:1)"],
    
    # SDXL 推荐尺寸
    ["1024x1024", "SDXL - 正方形 (1:1)"],
    ["1152x896", "SDXL - 竖屏 (4:3)"],
    ["896x1152", "SDXL - 横屏 (3:4)"],


    # Flux 推荐尺寸
    ["1024x1024", "Flux - 标准正方形 (1:1)"],
    ["1600x1200", "Flux - 高清横屏 (4:3)"],
    ["1200x1600", "Flux - 高清竖屏 (3:4)"],
    ["2048x2048", "Flux - 超高清正方形 (1:1)"],
    

    # Qwen-Image 推荐尺寸
    ["1328x1328", "Qwen-Image - 正方形 (1:1)"],
    ["1664x928", "Qwen-Image - 横屏 (16:9)"],
    ["928x1664", "Qwen-Image - 竖屏 (9:16)"],
    ["1472x1140", "Qwen-Image - 横屏 (4:3)"],
    ["1140x1472", "Qwen-Image - 竖屏 (3:4)"],
    ["1584x1056", "Qwen-Image - 横屏 (3:2)"],
    ["1056x1584", "Qwen-Image - 竖屏 (2:3)"],
]

# 尺寸配置相关函数
def load_size_config():
    config_path = os.path.join(os.path.dirname(__file__), 'size_presets.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 确保sizes字段存在
            if "sizes" not in data:
                data["sizes"] = DEFAULT_SIZE_PRESETS
            return data
    except:
        # 默认配置
        return {
            "sizes": DEFAULT_SIZE_PRESETS
        }

class SizeSelector:
    """尺寸选择器节点 - 提供常用图像尺寸的快速选择"""
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_size_config()
        sizes = config.get("sizes", DEFAULT_SIZE_PRESETS)
        
        # 提取所有尺寸字符串和显示名称
        size_strings = [size[0] for size in sizes]
        size_labels = {size[0]: size[1] for size in sizes}
        
        # 返回输入类型配置
        return {
            "required": {
                "size_preset": (size_strings, {
                    "default": size_strings[0] if size_strings else "",
                    "labels": size_labels,
                    "label": "尺寸预设",
                    "description": "选择预设的图像尺寸，格式为'宽x高'"
                })
            }
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "get_size"
    CATEGORY = "XnanTool/预设"
    
    def get_size(self, size_preset):
        """解析选中的尺寸预设，返回宽度和高度"""
        try:
            width, height = map(int, size_preset.split('x'))
            return (width, height)
        except ValueError:
            # 如果解析失败，返回默认值
            return (512, 512)

# 导出节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "SizeSelector": SizeSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SizeSelector": "尺寸预设",
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]