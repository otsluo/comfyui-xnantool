import folder_paths
import os
import av
import numpy as np
import torch
from fractions import Fraction

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


class VideoStream:
    """视频流对象 - 封装视频文件路径和元数据，兼容官方节点接口"""
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        self._width = None
        self._height = None
        self._has_audio = False
        self._duration = None
        self._frame_count = None
        self._frame_rate = None
        self._read_metadata()
    
    def _read_metadata(self):
        """读取视频元数据"""
        try:
            with av.open(self.path) as container:
                for stream in container.streams:
                    if stream.type == 'video':
                        self._width = stream.width
                        self._height = stream.height
                        # 获取帧率
                        if stream.average_rate:
                            self._frame_rate = Fraction(stream.average_rate)
                        else:
                            self._frame_rate = Fraction(30)
                        # 获取帧数
                        if stream.frames and stream.frames > 0:
                            self._frame_count = stream.frames
                        # 计算视频时长（秒）
                        if stream.duration and stream.time_base:
                            self._duration = float(stream.duration * stream.time_base)
                        elif container.duration:
                            self._duration = float(container.duration) / av.time_base
                        else:
                            self._duration = 0.0
                    elif stream.type == 'audio':
                        self._has_audio = True
        except:
            self._width = 1920
            self._height = 1080
            self._duration = 0.0
            self._frame_rate = Fraction(30)
            self._frame_count = 0
    
    def get_stream_source(self):
        """返回视频文件路径"""
        return self.path
    
    def get_dimensions(self):
        """获取视频尺寸"""
        return (self._width, self._height)
    
    def get_width(self):
        return self._width
    
    def get_height(self):
        return self._height
    
    def get_duration(self):
        """获取视频时长（秒）"""
        return self._duration
    
    def get_frame_count(self):
        """获取视频帧数"""
        return self._frame_count
    
    def get_frame_rate(self):
        """获取视频帧率"""
        return self._frame_rate
    
    def get_bit_depth(self):
        """获取位深"""
        return 8
    
    def get_color_space(self):
        """获取色彩空间"""
        return "sRGB"
    
    def has_audio(self):
        """检查是否包含音频"""
        return self._has_audio
    
    def save_to(self, output_path, format=None, codec=None, metadata=None):
        """保存视频到指定路径 - 兼容ComfyUI官方SaveVideo节点"""
        import shutil
        shutil.copy2(self.path, output_path)
        print(f"💾 视频已保存: {output_path}")
    
    def get_components(self):
        """
        获取视频组件 - 兼容官方"获取视频元素"节点
        返回包含视频帧、音频等信息的对象
        """
        try:
            import cv2
            
            # 读取视频帧
            cap = cv2.VideoCapture(self.path)
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {self.path}")
            
            frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 转换为 RGB 格式（OpenCV 使用 BGR）
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 转换为 numpy 数组并归一化到 [0, 1]
                frame_np = frame_rgb.astype(np.float32) / 255.0
                
                # 转换为 torch 张量
                frame_tensor = torch.from_numpy(frame_np)
                frames.append(frame_tensor)
            
            cap.release()
            
            if not frames:
                raise ValueError(f"视频中没有帧: {self.path}")
            
            # 堆叠所有帧为 [B, H, W, C]
            video_tensor = torch.stack(frames)
            
            # 构建返回对象
            class VideoComponentsResult:
                def __init__(self, images, frame_rate, audio=None, metadata=None, alpha=None):
                    self.images = images
                    self.frame_rate = frame_rate
                    self.audio = audio
                    self.metadata = metadata or {}
                    self.alpha = alpha
            
            # 尝试加载音频
            audio_data = None
            if self._has_audio:
                try:
                    audio_stream = AudioStream(self.path, has_audio=True)
                    audio_data = {
                        'waveform': audio_stream._load_waveform(),
                        'sample_rate': audio_stream.get_sample_rate()
                    }
                except:
                    pass
            
            return VideoComponentsResult(
                images=video_tensor,
                frame_rate=self._frame_rate,
                audio=audio_data,
                metadata={},
                alpha=None
            )
            
        except Exception as e:
            print(f"[VideoStream] 获取视频组件时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

class LoadVideoNode:
    """加载视频节点 - 加载本地视频文件"""
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        video_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm'))]
        return {
            "required": {
                "video_file": (sorted(video_files), {"video_upload": True}),
            },
        }
    
    RETURN_TYPES = ("VIDEO", "AUDIO", "STRING", "FLOAT")
    RETURN_NAMES = ("video", "audio", "filename", "duration")
    FUNCTION = "load_video"
    CATEGORY = "❤️❤️❤️XnanTool/媒体处理"
    
    def load_video(self, video_file):
        """
        加载视频文件
        
        Args:
            video_file: 视频文件名
            
        Returns:
            tuple: (视频对象, 音频对象, 文件名, 时长)
        """
        video_path = os.path.join(folder_paths.get_input_directory(), video_file)
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        has_audio = False
        try:
            with av.open(video_path) as container:
                for stream in container.streams:
                    if stream.type == 'audio':
                        has_audio = True
                        break
        except:
            pass
        
        # 使用自定义的视频流对象
        video_stream = VideoStream(video_path)
        audio_stream = AudioStream(video_path, has_audio=has_audio)
        
        # 去掉文件后缀
        filename_without_ext = os.path.splitext(video_file)[0]
        
        # 获取视频时长
        duration = video_stream.get_duration()
        
        return (video_stream, audio_stream, filename_without_ext, duration)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "LoadVideoNode": LoadVideoNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadVideoNode": "加载视频"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
