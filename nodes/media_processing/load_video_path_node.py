import os
import folder_paths
import cv2
import numpy as np
import torch
import tempfile


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
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "AUDIO")
    RETURN_NAMES = ("video_frames", "video_path", "audio")
    FUNCTION = "load_video"
    CATEGORY = "XnanTool/媒体处理"
    
    def load_video(self, video_path):
        """
        加载视频文件路径和数据
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            tuple: (视频数据, 视频路径)
        """
        try:
            if not video_path or not video_path.strip():
                return (None, "")
            
            # 检查文件是否存在
            if not os.path.exists(video_path):
                print(f"[LoadVideoPathNode] 错误：视频文件不存在: {video_path}")
                return (None, "")
            
            # 检查是否是视频文件
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
            _, ext = os.path.splitext(video_path.lower())
            
            if ext not in video_extensions:
                print(f"[LoadVideoPathNode] 警告：文件扩展名可能不是视频格式: {ext}")
            
            # 读取视频帧（限制最大帧数为500，防止内存溢出）
            video_frames = self.read_video_frames(video_path, max_frames=500)
            
            # 提取音频
            audio_data = None
            try:
                audio_data, _ = self.extract_audio(video_path)
            except Exception as e:
                print(f"[LoadVideoPathNode] 警告：提取音频失败: {str(e)}")
            
            return (video_frames, video_path, audio_data)
            
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

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadVideoPathNode": "加载视频路径",
}
