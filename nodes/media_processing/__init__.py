# 媒体处理节点模块初始化文件

# 导入媒体处理相关节点
from .video_to_gif_node import VideoToGifNode
from .video_to_audio_node import VideoToAudioNode
from .images_to_gif_node import ImagesToGifNodeV2, ImagesToGifNodeV1
from .extract_frame_from_video_node import ExtractFrameFromVideoNode
from .batch_extract_frame_from_video_node import BatchExtractFrameFromVideoNode

# 定义节点映射
NODE_CLASS_MAPPINGS = {
    "VideoToGifNode": VideoToGifNode,
    "VideoToAudioNode": VideoToAudioNode,
    "ImagesToGifNodeV2": ImagesToGifNodeV2,
    "ImagesToGifNodeV1": ImagesToGifNodeV1,
    "ExtractFrameFromVideoNode": ExtractFrameFromVideoNode,
    "BatchExtractFrameFromVideoNode": BatchExtractFrameFromVideoNode,
}

# 定义节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoToGifNode": "视频转GIF",
    "VideoToAudioNode": "视频转音频",
    "ImagesToGifNodeV2": "图片转GIF-V2",
    "ImagesToGifNodeV1": "图片转GIF-V1",
    "ExtractFrameFromVideoNode": "视频帧提取",
    "BatchExtractFrameFromVideoNode": "批量视频帧提取",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']