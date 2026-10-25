import os
import av
import cv2
import numpy as np
import torch


class AudioStream:
    """音频流对象 - 封装音频文件路径和元数据"""
    def __init__(self, path, has_audio=False):
        self.path = path
        self.has_audio = has_audio
        self._sample_rate = None
        self._channels = None
        self._read_metadata()
    
    def _read_metadata(self):
        """读取音频元数据"""
        try:
            with av.open(self.path) as container:
                for stream in container.streams:
                    if stream.type == 'audio':
                        self._sample_rate = stream.rate
                        self._channels = stream.channels
                        break
        except:
            self._sample_rate = 44100
            self._channels = 2
    
    def get_stream_source(self):
        return self.path
    
    def get_sample_rate(self):
        return self._sample_rate
    
    def get_channels(self):
        return self._channels
    
    def __getitem__(self, key):
        if key == "waveform":
            return self._load_waveform()
        elif key == "sample_rate":
            return self._sample_rate
        raise KeyError(key)
    
    def _load_waveform(self):
        """加载音频波形数据"""
        if not self.has_audio:
            return torch.zeros((1, 1, 1))
        
        try:
            with av.open(self.path) as container:
                audio_stream = None
                for stream in container.streams:
                    if stream.type == 'audio':
                        audio_stream = stream
                        break
                
                if audio_stream is None:
                    return torch.zeros((1, 1, 1))
                
                audio_data = []
                for frame in container.decode(audio_stream):
                    audio_data.append(frame.to_ndarray())
                
                if not audio_data:
                    return torch.zeros((1, 1, 1))
                
                waveform = np.concatenate(audio_data, axis=1)
                
                if waveform.ndim == 1:
                    waveform = waveform.reshape(1, 1, -1)
                elif waveform.ndim == 2:
                    waveform = waveform.reshape(1, waveform.shape[0], -1)
                
                return torch.from_numpy(waveform)
        except:
            return torch.zeros((1, 1, 1))


class GetVideoInfoNode:
    """
    获取视频信息节点 - 获取视频文件的详细元数据信息
    支持从视频路径或视频对象获取信息
    包含视频首帧和尾帧提取功能
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "视频文件路径",
                    "description": "视频文件的完整路径"
                }),
            },
            "optional": {
                "video": ("VIDEO", {
                    "label": "视频对象",
                    "description": "视频对象（可选，如果提供则优先使用）"
                }),
                "max_frames": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100000,
                    "step": 1,
                    "label": "加载帧上限",
                    "description": "提取首尾帧时最多读取的帧数，0表示不限制"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "INT", "INT", "FLOAT", "FLOAT", "INT", "AUDIO", "STRING")
    RETURN_NAMES = (
        "首帧",
        "尾帧",
        "宽度",
        "高度",
        "时长",
        "帧率",
        "总帧数",
        "音频",
        "视频信息"
    )
    FUNCTION = "get_video_info"
    CATEGORY = "❤️❤️❤️XnanTool/媒体处理"

    def get_video_info(self, video_path, video=None, max_frames=0):
        """
        获取视频文件的详细信息

        Args:
            video_path: 视频文件路径
            video: 视频对象（可选）
            max_frames: 加载帧上限（默认0，表示不限制）

        Returns:
            tuple: (首帧, 尾帧, 宽度, 高度, 时长, 帧率, 总帧数, 音频, 视频信息字符串)
        """
        # 创建空的图像张量（用于错误情况）
        empty_frame = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
        
        try:
            # 优先使用视频对象的路径
            if video is not None and hasattr(video, 'path'):
                actual_path = video.path
            elif video_path and video_path.strip():
                actual_path = video_path.strip()
            else:
                print("[GetVideoInfoNode] 错误：未提供有效的视频路径或视频对象")
                return (empty_frame, empty_frame, 0, 0, 0.0, 0.0, 0, None, "错误：未提供有效的视频路径")

            # 检查文件是否存在
            if not os.path.exists(actual_path):
                print(f"[GetVideoInfoNode] 错误：视频文件不存在: {actual_path}")
                return (empty_frame, empty_frame, 0, 0, 0.0, 0.0, 0, None, f"错误：文件不存在 {actual_path}")

            # 使用 pyav 读取视频信息
            with av.open(actual_path) as container:
                duration = 0.0
                width = 0
                height = 0
                fps = 0.0
                total_frames = 0
                codec_name = "unknown"
                has_audio = False

                # 获取视频流信息
                for stream in container.streams:
                    if stream.type == 'video':
                        width = stream.width
                        height = stream.height
                        
                        # 计算时长
                        if stream.duration and stream.time_base:
                            duration = float(stream.duration * stream.time_base)
                        elif container.duration:
                            duration = float(container.duration) / 1000000  # 微秒转秒
                        
                        # 计算帧率
                        if stream.average_rate:
                            fps = float(stream.average_rate)
                        elif stream.base_rate:
                            fps = float(stream.base_rate)
                        
                        # 计算总帧数
                        if stream.frames > 0:
                            total_frames = stream.frames
                        elif duration > 0 and fps > 0:
                            total_frames = int(duration * fps)
                        
                        # 获取编码格式
                        if stream.codec_context:
                            codec_name = stream.codec_context.name
                    elif stream.type == 'audio':
                        has_audio = True

            # 提取首帧和尾帧
            first_frame, last_frame = self._extract_first_last_frames(actual_path, max_frames)
            
            # 提取音频
            audio_stream = AudioStream(actual_path, has_audio=has_audio) if has_audio else None

            # 构造视频信息字符串
            video_info = f"视频信息:\n"
            video_info += f"  文件路径: {os.path.basename(actual_path)}\n"
            video_info += f"  时长: {duration:.2f} 秒\n"
            video_info += f"  分辨率: {width} x {height}\n"
            video_info += f"  帧率: {fps:.2f} FPS\n"
            video_info += f"  总帧数: {total_frames}\n"
            video_info += f"  编码格式: {codec_name}"

            print(f"[GetVideoInfoNode] 成功获取视频信息: {os.path.basename(actual_path)}")

            return (
                first_frame,
                last_frame,
                width,
                height,
                round(duration, 2),
                round(fps, 2),
                total_frames,
                audio_stream,
                video_info
            )

        except Exception as e:
            print(f"[GetVideoInfoNode] 获取视频信息时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return (empty_frame, empty_frame, 0, 0, 0.0, 0.0, 0, None, f"错误：{str(e)}")

    def _extract_first_last_frames(self, video_path, max_frames=0):
        """
        提取视频的首帧和尾帧

        Args:
            video_path: 视频文件路径
            max_frames: 加载帧上限（默认0，表示不限制）

        Returns:
            tuple: (首帧张量, 尾帧张量)
        """
        try:
            # 使用 pyav 提取首帧和尾帧（更可靠）
            with av.open(video_path) as container:
                video_stream = None
                for stream in container.streams:
                    if stream.type == 'video':
                        video_stream = stream
                        break
                
                if video_stream is None:
                    print(f"[GetVideoInfoNode] 警告：未找到视频流")
                    empty_frame = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                    return empty_frame, empty_frame

                # 提取首帧和尾帧
                first_frame = None
                last_frame = None
                frame_count = 0
                
                # 逐帧读取，记录第一帧和最后一帧
                for frame in container.decode(video_stream):
                    # 检查是否超过上限（0表示不限制）
                    if max_frames > 0 and frame_count >= max_frames:
                        print(f"[GetVideoInfoNode] 提示：已达到帧数上限 {max_frames}，停止读取")
                        break
                    
                    # 转换为 RGB
                    frame_rgb = frame.to_ndarray(format='rgb24')
                    frame_np = frame_rgb.astype(np.float32) / 255.0
                    frame_tensor = torch.from_numpy(frame_np).unsqueeze(0)  # [1, H, W, C]
                    
                    # 记录首帧
                    if first_frame is None:
                        first_frame = frame_tensor
                    
                    # 不断更新尾帧（最后一帧会覆盖之前的）
                    last_frame = frame_tensor
                    frame_count += 1
                
                if first_frame is None:
                    print(f"[GetVideoInfoNode] 警告：无法读取首帧")
                    empty_frame = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                    first_frame = empty_frame
                
                if last_frame is None:
                    print(f"[GetVideoInfoNode] 警告：无法读取尾帧")
                    empty_frame = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                    last_frame = empty_frame

                return first_frame, last_frame

        except Exception as e:
            print(f"[GetVideoInfoNode] 提取首尾帧时发生错误: {str(e)}")
            empty_frame = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            return empty_frame, empty_frame


# 注册节点
NODE_CLASS_MAPPINGS = {
    "GetVideoInfoNode": GetVideoInfoNode,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetVideoInfoNode": "获取视频信息",
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
