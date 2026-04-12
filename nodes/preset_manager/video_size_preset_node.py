import os
from math import gcd

class VideoSizePresetNode:
    """
    视频尺寸预设节点
    提供常用视频尺寸的快速选择
    所有尺寸均能被32整除，按比例和分辨率分类
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "size_preset": cls.get_size_presets(),
            }
        }
    
    @classmethod
    def get_size_presets(cls):
        """
        获取尺寸预设列表，按比例和分辨率分类
        保留常用比例：1:1、3:4、4:3、9:16、16:9
        分类：480p、720p、1080p、4K、8K
        9:16竖屏尺寸与16:9横屏尺寸对应（宽高互换）
        括号内排序：比例-分辨率-尺寸
        3:4和4:3不写分辨率
        1:1写正方形 1:1
        """
        # 定义尺寸列表，确保能被32整除
        sizes = [
            # 1:1 比例
            (512, 512, "1:1-正方形-512x512"),
            (640, 640, "1:1-正方形-640x640"),
            (768, 768, "1:1-正方形-768x768"),
            (1024, 1024, "1:1-正方形-1024x1024"),
            (1536, 1536, "1:1-正方形-1536x1536"),
            
            # 3:4 比例 (竖屏)
            (576, 768, "3:4-竖版-576x768"),
            (768, 1024, "3:4-竖版-768x1024"),
            (1152, 1536, "3:4-竖版-1152x1536"),
            (1536, 2048, "3:4-竖版-1536x2048"),
            
            # 4:3 比例 (横屏)
            (768, 576, "4:3-横版-768x576"),
            (1024, 768, "4:3-横版-1024x768"),
            (1536, 1152, "4:3-横版-1536x1152"),
            (2048, 1536, "4:3-横版-2048x1536"),
            
            # 9:16 比例 (竖屏)
            (480, 832, "9:16-竖版-480x832 480p"),
            (704, 1280, "9:16-竖版-704x1280 720p"),
            (1056, 1920, "9:16-竖版-1056x1920 1080p"),
            (1440, 2560, "9:16-竖版-1440x2560 2K"),
            (2144, 3840, "9:16-竖版-2144x3840 4K"),
            (4320, 7680, "9:16-竖版-4320x7680 8K"),
            
            # 16:9 比例 (横屏)
            (832, 480, "16:9-横版-832x480 480p"),
            (1280, 704, "16:9-横版-1280x704 720p"),
            (1920, 1056, "16:9-横版-1920x1056 1080p"),
            (2560, 1440, "16:9-横版-2560x1440 2K"),
            (3840, 2144, "16:9-横版-3840x2144 4K"),
            (7680, 4320, "16:9-横版-7680x4320 8K"),
        ]
        
        # 格式化显示名称：宽x高 (描述)
        display_names = []
        for width, height, desc in sizes:
            display_names.append(desc)
        
        return (display_names, {
            "default": display_names[0] if display_names else "1:1-正方形-1024x1024",
            "label": "尺寸预设",
            "description": "选择视频尺寸预设（所有尺寸均能被32整除）"
        })
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("宽度", "高度")
    FUNCTION = "get_size_preset"
    CATEGORY = "XnanTool/预设"
    
    def get_size_preset(self, size_preset):
        """
        获取视频尺寸预设
        
        Args:
            size_preset: 尺寸预设字符串（格式：比例-名称-宽x高）
            
        Returns:
            宽度: 视频宽度
            高度: 视频高度
        """
        # 解析尺寸预设字符串（格式：比例-名称-宽x高）
        try:
            parts = size_preset.split("-")
            if len(parts) >= 3:
                resolution = parts[-1]
                width, height = map(int, resolution.split("x"))
                return (width, height)
        except (ValueError, IndexError):
            pass
        
        # 默认返回1080p
        return (1920, 1080)


NODE_CLASS_MAPPINGS = {
    "VideoSizePresetNode": VideoSizePresetNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoSizePresetNode": "视频尺寸预设"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
