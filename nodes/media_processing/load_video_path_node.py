import os
import folder_paths
import cv2
import numpy as np
import torch
import tempfile
import av


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
    """视频流对象 - 封装视频文件路径和元数据"""
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        self._width = None
        self._height = None
        self._has_audio = False
        self._read_metadata()
    
    def _read_metadata(self):
        """读取视频元数据"""
        try:
            with av.open(self.path) as container:
                for stream in container.streams:
                    if stream.type == 'video':
                        self._width = stream.width
                        self._height = stream.height
                    elif stream.type == 'audio':
                        self._has_audio = True
        except:
            self._width = 1920
            self._height = 1080
    
    def get_stream_source(self):
        return self.path
    
    def get_dimensions(self):
        """获取视频尺寸"""
        return (self._width, self._height)
    
    def get_width(self):
        return self._width
    
    def get_height(self):
        return self._height
    
    def has_audio(self):
        """检查是否包含音频"""
        return self._has_audio
    
    def save_to(self, output_path=None, format=None, codec=None, metadata=None):
        """保存视频到指定路径 - 兼容ComfyUI官方SaveVideo节点"""
        import shutil
        
        # 如果未指定路径，默认保存到 output/tmp 目录
        if output_path is None:
            output_dir = os.path.join(folder_paths.get_output_directory(), "tmp")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, os.path.basename(self.path))
        
        shutil.copy2(self.path, output_path)
        print(f"💾 视频已保存: {output_path}")


class LoadVideoPathNode:
    """
    加载视频路径节点 - 加载视频文件路径和数据
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
                    "description": "视频文件的完整路径或相对路径"
                }),
                "max_frames": ("INT", {
                    "default": 500,
                    "min": 1,
                    "max": 10000,
                    "step": 1,
                    "label": "最大帧数",
                    "description": "限制加载的最大帧数，防止内存溢出"
                }),
            }
        }
    
    RETURN_TYPES = ("VIDEO", "IMAGE", "STRING", "AUDIO", "STRING")
    RETURN_NAMES = ("video", "video_frames", "video_path", "audio", "filename")
    FUNCTION = "load_video"
    CATEGORY = "❤️❤️❤️XnanTool/媒体处理"
    
    def load_video(self, video_path, max_frames=500):
        """
        加载视频文件路径和数据
        
        Args:
            video_path: 视频文件路径
            max_frames: 最大帧数限制
            
        Returns:
            tuple: (视频对象, 视频帧, 视频路径, 音频)
        """
        try:
            if not video_path or not video_path.strip():
                return (None, None, "", None, "")

            # 检查文件是否存在
            if not os.path.exists(video_path):
                print(f"[LoadVideoPathNode] 错误：视频文件不存在: {video_path}")
                return (None, None, "", None, "")
            
            # 创建视频对象
            video_obj = VideoStream(video_path)
            
            # 检查是否有音频
            has_audio = video_obj.has_audio()
            
            # 读取视频帧（限制最大帧数，防止内存溢出）
            video_frames = self.read_video_frames(video_path, max_frames=max_frames)
            
            # 创建音频对象
            audio_data = AudioStream(video_path, has_audio=has_audio)

            # 获取文件名（不带后缀）
            filename = os.path.splitext(os.path.basename(video_path))[0]

            return (video_obj, video_frames, video_path, audio_data, filename)
            
        except Exception as e:
            print(f"[LoadVideoPathNode] 加载视频时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return (None, "")
    
    def read_video_frames(self, video_path, max_frames=1000):
        """
        读取视频帧并转换为 ComfyUI 格式
        
        Args:
            video_path: 视频文件路径
            max_frames: 最大帧数限制，防止内存溢出
            
        Returns:
            torch.Tensor: 视频帧张量 [B, H, W, C]
        """
        try:
            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                print(f"[LoadVideoPathNode] 错误：无法打开视频文件: {video_path}")
                return None
            
            # 获取视频总帧数
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"[LoadVideoPathNode] 视频总帧数: {total_frames}")
            
            # 如果帧数太多，限制加载
            if total_frames > max_frames:
                print(f"[LoadVideoPathNode] 警告：视频帧数过多 ({total_frames} > {max_frames})，将限制加载前 {max_frames} 帧")
                total_frames = max_frames
            
            frames = []
            frame_count = 0
            
            while frame_count < total_frames:
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
                frame_count += 1
            
            cap.release()
            
            if frame_count == 0:
                print(f"[LoadVideoPathNode] 警告：视频中没有读取到帧")
                return None
            
            print(f"[LoadVideoPathNode] 成功读取 {frame_count} 帧")
            
            # 堆叠所有帧为 [B, H, W, C]
            try:
                video_tensor = torch.stack(frames)
            except RuntimeError as e:
                print(f"[LoadVideoPathNode] 堆叠帧时发生内存错误: {str(e)}")
                print(f"[LoadVideoPathNode] 建议：减少视频长度或降低分辨率")
                return None
            
            print(f"[LoadVideoPathNode] 成功读取 {frame_count} 帧")
            
            return video_tensor
            
        except Exception as e:
            print(f"[LoadVideoPathNode] 读取视频帧时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_audio(self, video_path):
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            tuple: (音频数据, "")
        """
        try:
            import subprocess
            import tempfile
            
            # 创建临时音频文件
            temp_audio_path = tempfile.mktemp(suffix='.wav')
            
            # 使用ffmpeg提取音频
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn',  # 不包含视频
                '-acodec', 'pcm_s16le',  # PCM 16位音频
                '-ar', '44100',  # 采样率44100Hz
                '-ac', '2',  # 立体声
                '-y',  # 覆盖输出文件
                temp_audio_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # 读取音频文件
            import soundfile as sf
            audio_data, sample_rate = sf.read(temp_audio_path)
            
            print(f"[LoadVideoPathNode] 音频数据形状: {audio_data.shape}, 数据类型: {audio_data.dtype}")
            
            # soundfile.read() 返回的格式是 (length, channels) 或 (length,) 对于单声道
            # 我们需要转换为 (channels, length) 格式
            if audio_data.ndim == 1:
                # 单声道
                audio_tensor = torch.from_numpy(audio_data).float().unsqueeze(0)
            else:
                # 多声道，转置为 (channels, length)
                audio_tensor = torch.from_numpy(audio_data).float().t()
            
            print(f"[LoadVideoPathNode] 音频张量维度: {audio_tensor.dim()}, 形状: {audio_tensor.shape}")
            
            # 归一化到 [-1, 1]
            if audio_tensor.max() > 1.0 or audio_tensor.min() < -1.0:
                audio_tensor = torch.clamp(audio_tensor, -1.0, 1.0)
            
            print(f"[LoadVideoPathNode] 最终音频张量形状: {audio_tensor.shape}")
            
            # 保存音频路径
            audio_path = temp_audio_path
            
            # 清理临时文件
            try:
                os.remove(temp_audio_path)
            except:
                pass
            
            # 返回ComfyUI音频格式字典
            audio_dict = {
                'waveform': audio_tensor.unsqueeze(0),
                'sample_rate': 44100
            }
            
            return (audio_dict, "")
            
        except Exception as e:
            print(f"[LoadVideoPathNode] 提取音频时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return (None, "")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "LoadVideoPathNode": LoadVideoPathNode,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadVideoPathNode": "加载视频路径",
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
