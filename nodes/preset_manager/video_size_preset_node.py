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
            # 1:1 比例 - 写正方形 1:1
            (512, 512, "512x512 (正方形 1:1)"),
            (640, 640, "640x640 (正方形 1:1)"),
            (768, 768, "768x768 (正方形 1:1)"),
            (1024, 1024, "1024x1024 (正方形 1:1)"),
            (1536, 1536, "1536x1536 (正方形 1:1)"),
            
            # 3:4 比例 (竖屏 4:3) - 不写分辨率
            (576, 768, "576x768 (竖屏 3:4)"),
            (768, 1024, "768x1024 (竖屏 3:4)"),
            (1152, 1536, "1152x1536 (竖屏 3:4)"),
            (1536, 2048, "1536x2048 (竖屏 3:4)"),
            
            # 4:3 比例 (横屏 4:3) - 不写分辨率
            (768, 576, "768x576 (横屏 4:3)"),
            (1024, 768, "1024x768 (横屏 4:3)"),
            (1536, 1152, "1536x1152 (横屏 4:3)"),
            (2048, 1536, "2048x1536 (横屏 4:3)"),
            
            # 9:16 比例 (竖屏) - 与16:9横屏对应（宽高互换）
            (480, 832, "480x832 (竖屏 9:16 480p)"),
            (704, 1280, "704x1280 (竖屏 9:16 720p)"),
            (1056, 1920, "1056x1920 (竖屏 9:16 1080p)"),
            (1440, 2560, "1440x2560 (竖屏 9:16 2K)"),
            (2144, 3840, "2144x3840 (竖屏 9:16 4K)"),
            (4320, 7680, "4320x7680 (竖屏 9:16 8K)"),
            
            # 16:9 比例 (横屏)
            (832, 480, "832x480 (横屏 16:9 480p)"),
            (1280, 704, "1280x704 (横屏 16:9 720p)"),
            (1920, 1056, "1920x1056 (横屏 16:9 1080p)"),
            (2560, 1440, "2560x1440 (横屏 16:9 2K)"),
            (3840, 2144, "3840x2144 (横屏 16:9 4K)"),
            (7680, 4320, "7680x4320 (横屏 16:9 8K)"),
        ]
        
        # 按比例排序：1:1、竖屏(3:4、9:16)、横屏(4:3、16:9)
        sorted_sizes = []
        
        # 1:1 比例
        square_sizes = [s for s in sizes if s[0] == s[1]]
        square_sizes.sort(key=lambda x: x[0])
        sorted_sizes.extend(square_sizes)
        
        # 竖屏尺寸 (高度 > 宽度)
        portrait_sizes = [s for s in sizes if s[1] > s[0]]
        portrait_sizes.sort(key=lambda x: (x[1] // x[0], x[0]))
        sorted_sizes.extend(portrait_sizes)
        
        # 横屏尺寸 (宽度 > 高度)
        landscape_sizes = [s for s in sizes if s[0] > s[1]]
        landscape_sizes.sort(key=lambda x: (x[0] / x[1] if x[1] > 0 else 0, x[0]))
        sorted_sizes.extend(landscape_sizes)
        
        return ([f"{s[0]}x{s[1]} ({s[2].split(' ')[-1].replace(')', '')})" for s in sorted_sizes], {
            "default": "1024x1024 (正方形 1:1)",
            "label": "尺寸预设",
            "description": "选择视频尺寸预设（所有尺寸均能被32整除）"
        })
    
    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("宽度", "高度", "尺寸字符串")
    FUNCTION = "get_size_preset"
    CATEGORY = "XnanTool/视频处理"
    
    def get_size_preset(self, size_preset):
        """
        获取视频尺寸预设
        
        Args:
            size_preset: 尺寸预设字符串
            
        Returns:
            宽度: 视频宽度
            高度: 视频高度
            尺寸字符串: 尺寸字符串（格式：宽度x高度）
        """
        # 解析尺寸预设字符串
        parts = size_preset.split(" (")
        if len(parts) > 0:
            resolution = parts[0]
            width, height = map(int, resolution.split("x"))
            
            return (width, height, f"{width}x{height}")
        
        # 默认返回1080p
        return (1920, 1080, "1920x1080")


NODE_CLASS_MAPPINGS = {
    "VideoSizePresetNode": VideoSizePresetNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoSizePresetNode": "视频尺寸预设"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
