import json
import os

# 定义AI生图常用尺寸列表，每个尺寸都标注比例
DEFAULT_SIZE_PRESETS = [
    # 正方形 (1:1)
    ["1:1-正方形：512x512", "512x512"],
    ["1:1-大正方形：768x768", "768x768"],
    ["1:1-高清正方形：1024x1024", "1024x1024"],
    ["1:1-Qwen正方形：1328x1328", "1328x1328"],
    ["1:1-超高清正方形：2048x2048", "2048x2048"],
    
    # 2:3 比例 (竖屏)
    ["2:3-竖屏：512x768", "512x768"],
    ["2:3-高清竖屏：1056x1584", "1056x1584"],
    
    # 3:2 比例 (横屏)
    ["3:2-横屏：768x512", "768x512"],
    ["3:2-高清横屏：1584x1056", "1584x1056"],
    
    # 3:4 比例 (竖屏)
    ["3:4-中等竖屏：896x1152", "896x1152"],
    ["3:4-高清竖屏：1140x1472", "1140x1472"],
    ["3:4-超清竖屏：1200x1600", "1200x1600"],
    
    # 4:3 比例 (横屏)
    ["4:3-中等横屏：1152x896", "1152x896"],
    ["4:3-高清横屏：1472x1140", "1472x1140"],
    ["4:3-超清横屏：1600x1200", "1600x1200"],
    
    # 16:9 比例 (横屏)
    ["16:9-宽屏：1664x928", "1664x928"],
    
    # 9:16 比例 (竖屏)
    ["9:16-竖屏：928x1664", "928x1664"],
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
    """尺寸选择器节点 - 提供常用图像尺寸的快速选择，格式为'比例-名称：宽x高'"""
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_size_config()
        sizes = config.get("sizes", DEFAULT_SIZE_PRESETS)
        
        # 提取所有标签作为选项
        size_options = [size[0] for size in sizes]
        
        # 返回输入类型配置
        return {
            "required": {
                "size_preset": (size_options, {
                    "default": size_options[0] if size_options else "",
                    "label": "尺寸预设",
                    "description": "选择预设的图像尺寸，格式为'比例-名称：宽x高'"
                })
            }
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "get_size"
    CATEGORY = "XnanTool/预设"
    
    def get_size(self, size_preset):
        """解析选中的尺寸预设，返回宽度和高度"""
        config = load_size_config()
        sizes = config.get("sizes", DEFAULT_SIZE_PRESETS)
        
        # 创建标签到尺寸的映射
        size_map = {size[0]: size[1] for size in sizes}
        
        # 获取对应的尺寸字符串
        size_str = size_map.get(size_preset, "512x512")
        
        try:
            width, height = map(int, size_str.split('x'))
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