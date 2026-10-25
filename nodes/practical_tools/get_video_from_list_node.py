class GetVideoFromListNode:
    """
    从列表获取视频节点 - 从视频列表中获取指定索引的视频
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_list": ("VIDEO", {
                    "label": "视频列表",
                    "description": "视频列表（来自加载ZIP等节点）"
                }),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "label": "索引",
                    "description": "要获取的视频索引（从0开始）"
                }),
            }
        }
    
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("视频",)
    FUNCTION = "get_video"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    INPUT_IS_LIST = True
    
    def get_video(self, video_list, index):
        """
        从视频列表中获取指定索引的视频
        
        Args:
            video_list: 视频列表（会被包装成列表的列表）
            index: 要获取的索引（会被包装成列表）
            
        Returns:
            tuple: (视频,)
        """
        # 处理列表输入
        # video_list 会被包装成 [[video1, video2, ...]]
        # index 会被包装成 [index_value]
        if isinstance(video_list, list) and len(video_list) > 0:
            if isinstance(video_list[0], list):
                videos = video_list[0]
            else:
                videos = video_list
        else:
            videos = video_list
        
        # 提取索引值
        if isinstance(index, list) and len(index) > 0:
            index_value = index[0]
        else:
            index_value = index
        
        # 确保 videos 是列表
        if not isinstance(videos, list):
            videos = [videos]
        
        # 检查索引范围
        if len(videos) == 0:
            raise ValueError("视频列表为空")
        
        if index_value >= len(videos):
            raise ValueError(f"索引 {index_value} 超出范围，列表长度为 {len(videos)}")
        
        # 获取指定索引的视频
        video = videos[index_value]
        
        return (video,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "GetVideoFromListNode": GetVideoFromListNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetVideoFromListNode": "从列表获取视频-BETA"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
