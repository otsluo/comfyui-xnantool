import os
import torch
import numpy as np
import json
import subprocess
import platform
from PIL import Image
import folder_paths
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoToAudioNode:
    """视频转音频节点 - 从视频文件中提取音频轨道并保存为音频文件"""
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        # 过滤视频文件
        video_files = folder_paths.filter_files_content_types(files, ["video"])
        
        return {
            "required": {
                "video_file": (sorted(video_files), {
                    "label": "视频文件",
                    "description": "选择要提取音频的视频文件",
                    "video_upload": True  # 添加视频上传支持
                }),
                "output_format": (["mp3", "wav", "aac", "flac"], {
                    "default": "mp3",
                    "label": "输出格式",
                    "description": "选择输出音频文件的格式"
                }),
                "audio_quality": (["high", "medium", "low"], {
                    "default": "medium",
                    "label": "音频质量",
                    "description": "选择输出音频的质量"
                })
            },
            "optional": {
                "output_filename": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "可选：自定义输出文件名（不含扩展名）"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "AUDIO")
    RETURN_NAMES = ("audio_file_path", "status_message", "audio")
    FUNCTION = "extract_audio"
    CATEGORY = "XnanTool/媒体处理"
    OUTPUT_NODE = True
    
    @classmethod
    def IS_CHANGED(cls, video_file, output_format, audio_quality, output_filename=""):
        # 如果视频文件存在，返回其修改时间，否则返回0
        video_path = folder_paths.get_annotated_filepath(video_file)
        if os.path.exists(video_path):
            return os.path.getmtime(video_path)
        return 0
    
    @classmethod
    def VALIDATE_INPUTS(cls, video_file):
        video_path = folder_paths.get_annotated_filepath(video_file)
        if not os.path.exists(video_path):
            return "Invalid video file: {}".format(video_file)
        return True
    
    def extract_audio(self, video_file, output_format, audio_quality, output_filename=""):
        """
        从视频文件中提取音频
        
        Args:
            video_file: 视频文件路径
            output_format: 输出音频格式 (mp3, wav, aac, flac)
            audio_quality: 音频质量 (high, medium, low)
            output_filename: 自定义输出文件名
            
        Returns:
            audio_file_path: 输出音频文件路径
            status_message: 状态信息
        """
        try:
            # 获取视频文件的完整路径
            video_path = folder_paths.get_annotated_filepath(video_file)
            
            # 检查输入文件是否存在
            if not os.path.exists(video_path):
                return ("", f"错误：视频文件不存在: {video_path}")
            
            # 检查是否为视频文件
            if not self._is_video_file(video_path):
                return ("", f"错误：文件不是有效的视频格式: {video_path}")
            
            # 获取输出目录
            output_dir = folder_paths.get_output_directory()
            
            # 确定输出文件名
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            
            if not output_filename:
                output_filename = f"{video_name}_audio"
            
            # 构建输出文件路径并处理文件名冲突
            output_file = os.path.join(output_dir, f"{output_filename}.{output_format}")
            counter = 1
            original_output_file = output_file
            while os.path.exists(output_file):
                output_file = os.path.join(output_dir, f"{output_filename}_{counter}.{output_format}")
                counter += 1
            
            # 如果文件被重命名，记录日志
            if original_output_file != output_file:
                logger.info(f"检测到同名文件，已自动重命名为: {os.path.basename(output_file)}")
            
            # 设置音频质量参数
            quality_params = self._get_quality_params(output_format, audio_quality)
            
            # 使用ffmpeg提取音频
            success = self._extract_audio_with_ffmpeg(video_path, output_file, quality_params)
            
            # 加载音频数据
            audio_data = self._load_audio_data(output_file)
            
            if success:
                message = f"✅ 音频提取成功！\n文件路径: {output_file}\n格式: {output_format}\n质量: {audio_quality}"
                return (output_file, message, audio_data)
            else:
                return ("", "❌ 音频提取失败，请检查日志信息", None)
                
        except Exception as e:
            error_msg = f"❌ 处理过程中出现错误: {str(e)}"
            print(error_msg)
            return ("", error_msg, None)
    
    def _load_audio_data(self, audio_file_path):
        """
        从音频文件中加载音频数据
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            dict: ComfyUI音频格式字典 {'waveform': tensor, 'sample_rate': int}
        """
        try:
            import soundfile as sf
            
            # 读取音频文件
            audio_data, sample_rate = sf.read(audio_file_path)
            
            # 转换为 torch 张量
            audio_tensor = torch.from_numpy(audio_data).float()
            
            # 确保音频是2D张量 (C, L)
            if audio_tensor.dim() == 1:
                audio_tensor = audio_tensor.unsqueeze(0)
            elif audio_tensor.dim() == 2:
                if audio_tensor.shape[0] > audio_tensor.shape[1]:
                    audio_tensor = audio_tensor.transpose(0, 1)
            
            # 归一化到 [-1, 1]
            if audio_tensor.max() > 1.0 or audio_tensor.min() < -1.0:
                audio_tensor = torch.clamp(audio_tensor, -1.0, 1.0)
            
            # 返回ComfyUI音频格式字典
            audio_dict = {
                'waveform': audio_tensor.unsqueeze(0),
                'sample_rate': sample_rate
            }
            
            return audio_dict
            
        except Exception as e:
            print(f"[VideoToAudioNode] 加载音频数据时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _is_video_file(self, file_path):
        """检查文件是否为视频格式"""
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']
        _, ext = os.path.splitext(file_path.lower())
        return ext in video_extensions
    
    def _get_quality_params(self, format, quality):
        """根据格式和质量返回ffmpeg参数"""
        # 基础质量映射
        quality_mapping = {
            "high": {"mp3": "320k", "wav": "pcm_s16le", "aac": "320k", "flac": " compression_level=8"},
            "medium": {"mp3": "192k", "wav": "pcm_s16le", "aac": "192k", "flac": " compression_level=5"},
            "low": {"mp3": "128k", "wav": "pcm_s16le", "aac": "128k", "flac": " compression_level=2"}
        }
        
        bitrate = quality_mapping.get(quality, quality_mapping["medium"]).get(format, "192k")
        return bitrate
    
    def _extract_audio_with_ffmpeg(self, input_file, output_file, quality_params):
        """使用ffmpeg提取音频"""
        try:
            # 构建ffmpeg命令
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-y"  # 覆盖输出文件
            ]
            
            # 根据格式添加特定参数
            if output_file.endswith(".mp3"):
                cmd.extend(["-vn", "-ar", "44100", "-ac", "2", "-ab", quality_params, "-f", "mp3"])
            elif output_file.endswith(".wav"):
                cmd.extend(["-vn", "-ar", "44100", "-ac", "2", "-acodec", quality_params])
            elif output_file.endswith(".aac"):
                cmd.extend(["-vn", "-ar", "44100", "-ac", "2", "-ab", quality_params, "-f", "adts"])
            elif output_file.endswith(".flac"):
                cmd.extend(["-vn", "-ar", "44100", "-ac", "2", "-compression_level", quality_params.split("=")[-1]])
            
            cmd.append(output_file)
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"🎵 音频提取完成: {output_file}")
                return True
            else:
                print(f"🎵 音频提取失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("🎵 音频提取超时")
            return False
        except Exception as e:
            print(f"🎵 音频提取出错: {str(e)}")
            return False

# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "VideoToAudioNode": VideoToAudioNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoToAudioNode": "视频转音频"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']