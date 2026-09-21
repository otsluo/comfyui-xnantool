"""
视频拼接节点
功能：将两个视频拼接为一个视频，使用 FFmpeg concat 拼接
"""

import os
import subprocess
import tempfile
import folder_paths
import av
import numpy as np
import torch


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
        """支持字典式访问，兼容 ComfyUI 官方音频节点"""
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


class VideoConcatNode:
    """视频拼接节点"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video1": ("VIDEO",),
                "video2": ("VIDEO",),
                "resolution_mode": (["保持原样", "使用视频1分辨率", "使用视频2分辨率", "使用较大分辨率", "自定义分辨率"], {
                    "default": "保持原样",
                    "label": "分辨率处理",
                    "description": "当两个视频分辨率不一致时的处理方式"
                }),
                "custom_width": ("INT", {
                    "default": 1920,
                    "min": 16,
                    "max": 8192,
                    "step": 2,
                    "label": "自定义宽度",
                    "description": "自定义输出视频宽度（仅在分辨率模式为'自定义分辨率'时生效）"
                }),
                "custom_height": ("INT", {
                    "default": 1080,
                    "min": 16,
                    "max": 8192,
                    "step": 2,
                    "label": "自定义高度",
                    "description": "自定义输出视频高度（仅在分辨率模式为'自定义分辨率'时生效）"
                }),
                "fps_mode": (["保持原样", "使用视频1帧率", "使用视频2帧率", "使用较高帧率", "自定义帧率"], {
                    "default": "保持原样",
                    "label": "帧率处理",
                    "description": "当两个视频帧率不一致时的处理方式"
                }),
                "custom_fps": ("FLOAT", {
                    "default": 30.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 0.1,
                    "label": "自定义帧率",
                    "description": "自定义输出视频帧率（仅在帧率模式为'自定义帧率'时生效）"
                }),
                "reencode": (["自动", "强制重新编码", "禁止重新编码"], {
                    "default": "自动",
                    "label": "编码模式",
                    "description": "自动：参数不一致时重新编码；强制：始终重新编码；禁止：始终直接拼接（可能失败）"
                }),
                "encode_quality": (["高质量", "中等质量", "低质量", "无损"], {
                    "default": "高质量",
                    "label": "编码质量",
                    "description": "重新编码时的质量设置"
                }),
            },
        }
    
    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "info")
    FUNCTION = "concat_videos"
    CATEGORY = "❤️❤️❤️XnanTool/媒体处理"
    
    def _get_video_path(self, video):
        """从 VIDEO 对象中获取视频文件路径"""
        # 尝试 get_stream_source 方法
        if hasattr(video, 'get_stream_source'):
            try:
                path = video.get_stream_source()
                if path and isinstance(path, str):
                    return path
            except Exception as e:
                print(f"[VideoConcatNode] get_stream_source 失败: {e}")
        
        # 尝试 __file 属性（ComfyUI 官方 VideoFromFile）
        if hasattr(video, '_VideoFromFile__file'):
            file_obj = getattr(video, '_VideoFromFile__file')
            if hasattr(file_obj, 'name'):
                return file_obj.name
            elif isinstance(file_obj, str):
                return file_obj
        
        return None
    
    def _get_video_info(self, video_path):
        """获取视频的分辨率和帧率信息"""
        try:
            with av.open(video_path) as container:
                video_stream = None
                for stream in container.streams:
                    if stream.type == 'video':
                        video_stream = stream
                        break
                if video_stream:
                    width = video_stream.width
                    height = video_stream.height
                    fps = float(video_stream.average_rate) if video_stream.average_rate else 30.0
                    return width, height, fps
        except:
            pass
        return 1920, 1080, 30.0
    
    def _has_audio_stream(self, video_path):
        """检查视频是否有音频流"""
        try:
            with av.open(video_path) as container:
                for stream in container.streams:
                    if stream.type == 'audio':
                        return True
        except:
            pass
        return False
    
    def concat_videos(self, video1, video2, resolution_mode, custom_width, custom_height, fps_mode, custom_fps, reencode, encode_quality):
        """拼接两个视频"""
        try:
            # 获取视频路径
            video1_path = self._get_video_path(video1)
            video2_path = self._get_video_path(video2)
            
            if not video1_path:
                return (None, "错误：无法从视频1获取文件路径")
            
            if not video2_path:
                return (None, "错误：无法从视频2获取文件路径")
            
            if not os.path.exists(video1_path):
                return (None, f"错误：视频1文件不存在: {video1_path}")
            
            if not os.path.exists(video2_path):
                return (None, f"错误：视频2文件不存在: {video2_path}")
            
            # 获取两个视频的参数
            w1, h1, fps1 = self._get_video_info(video1_path)
            w2, h2, fps2 = self._get_video_info(video2_path)
            
            print(f"[VideoConcatNode] 视频1: {os.path.basename(video1_path)} ({w1}x{h1}, {fps1:.2f}fps)")
            print(f"[VideoConcatNode] 视频2: {os.path.basename(video2_path)} ({w2}x{h2}, {fps2:.2f}fps)")
            
            # 判断是否需要重新编码
            need_reencode = False
            filters = []
            info_lines = []
            
            # 判断分辨率是否一致
            resolution_same = (w1 == w2 and h1 == h2)
            # 判断帧率是否一致
            fps_same = abs(fps1 - fps2) < 0.01
            
            # 根据编码模式决定是否需要重新编码
            if reencode == "强制重新编码":
                need_reencode = True
            elif reencode == "禁止重新编码":
                need_reencode = False
            else:  # 自动
                if not resolution_same or not fps_same:
                    need_reencode = True
            
            # 计算目标分辨率
            target_w, target_h = w1, h1
            if not resolution_same:
                if resolution_mode == "使用视频1分辨率":
                    target_w, target_h = w1, h1
                elif resolution_mode == "使用视频2分辨率":
                    target_w, target_h = w2, h2
                elif resolution_mode == "使用较大分辨率":
                    target_w, target_h = max(w1, w2), max(h1, h2)
                elif resolution_mode == "自定义分辨率":
                    target_w, target_h = custom_width, custom_height
                else:  # 保持原样
                    target_w, target_h = w1, h1
            
            # 计算目标帧率
            target_fps = fps1
            if not fps_same:
                if fps_mode == "使用视频1帧率":
                    target_fps = fps1
                elif fps_mode == "使用视频2帧率":
                    target_fps = fps2
                elif fps_mode == "使用较高帧率":
                    target_fps = max(fps1, fps2)
                elif fps_mode == "自定义帧率":
                    target_fps = custom_fps
                else:  # 保持原样
                    target_fps = fps1
            
            # 检查视频是否有音频
            has_audio1 = self._has_audio_stream(video1_path)
            has_audio2 = self._has_audio_stream(video2_path)
            has_audio = has_audio1 and has_audio2
            
            # 构建视频滤镜
            if need_reencode:
                # 视频滤镜（统一使用 setsar=1 标准化像素宽高比）
                if target_w != w1 or target_h != h1:
                    filters.append(f"[0:v]scale={target_w}:{target_h},setsar=1[v1]")
                else:
                    filters.append("[0:v]setsar=1[v1]")
                
                if target_w != w2 or target_h != h2:
                    filters.append(f"[1:v]scale={target_w}:{target_h},setsar=1[v2]")
                else:
                    filters.append("[1:v]setsar=1[v2]")
                
                # 音频滤镜（仅当两个视频都有音频时）
                if has_audio:
                    filters.append("[0:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a1]")
                    filters.append("[1:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a2]")
            
            # 获取输出目录（使用缓存目录）
            output_dir = folder_paths.get_output_directory()
            output_dir_full = os.path.join(output_dir, "tmp")
            os.makedirs(output_dir_full, exist_ok=True)
            
            # 使用输入视频路径和参数的哈希作为文件名，避免冲突
            import hashlib
            hash_input = f"{video1_path}_{video2_path}_{target_w}_{target_h}_{target_fps}_{reencode}_{encode_quality}"
            hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
            output_filename = f"temp_concat_{hash_value}.mp4"
            output_path_full = os.path.join(output_dir_full, output_filename)
            
            # 构建 FFmpeg 命令
            cmd = ["ffmpeg"]
            
            if need_reencode:
                # 使用滤镜方式拼接（支持不同分辨率/帧率）
                cmd.extend(["-i", video1_path, "-i", video2_path])
                
                # 构建滤镜链
                filter_complex = ";".join(filters)
                if has_audio:
                    filter_complex += f";[v1][a1][v2][a2]concat=n=2:v=1:a=1[outv][outa]"
                    map_args = ["-map", "[outv]", "-map", "[outa]"]
                else:
                    filter_complex += f";[v1][v2]concat=n=2:v=1:a=0[outv]"
                    map_args = ["-map", "[outv]"]
                
                # 编码质量设置
                quality_map = {
                    "无损": {"video": "libx264", "crf": "0", "preset": "veryslow"},
                    "高质量": {"video": "libx264", "crf": "18", "preset": "slow"},
                    "中等质量": {"video": "libx264", "crf": "23", "preset": "medium"},
                    "低质量": {"video": "libx264", "crf": "28", "preset": "fast"},
                }
                q = quality_map.get(encode_quality, quality_map["高质量"])
                
                cmd.extend([
                    "-filter_complex", filter_complex,
                ])
                cmd.extend(map_args)
                cmd.extend([
                    "-c:v", q["video"],
                    "-crf", q["crf"],
                    "-preset", q["preset"],
                    "-r", str(target_fps),
                ])
                if has_audio:
                    cmd.extend(["-c:a", "aac", "-b:a", "192k"])
                cmd.extend(["-y", output_path_full])
            else:
                # 使用 concat demuxer 直接拼接（无需重新编码）
                concat_list_path = None
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                        concat_list_path = f.name
                        escaped_path1 = video1_path.replace("'", "'\\''")
                        escaped_path2 = video2_path.replace("'", "'\\''")
                        f.write(f"file '{escaped_path1}'\n")
                        f.write(f"file '{escaped_path2}'\n")
                    
                    cmd.extend([
                        "-f", "concat",
                        "-safe", "0",
                        "-i", concat_list_path,
                        "-c", "copy",
                        "-y",
                        output_path_full
                    ])
                except:
                    if concat_list_path and os.path.exists(concat_list_path):
                        os.remove(concat_list_path)
                    raise
            
            print(f"[VideoConcatNode] FFmpeg 命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                error_msg = f"FFmpeg 拼接失败: {result.stderr}"
                print(f"[VideoConcatNode] {error_msg}")
                return (None, error_msg)
            
            # 加载拼接后的视频为 VideoStream
            concat_video = VideoStream(output_path_full)
            
            # 构建信息
            info_lines.append(f"视频拼接完成")
            info_lines.append(f"视频1: {os.path.basename(video1_path)} ({w1}x{h1}, {fps1:.2f}fps)")
            info_lines.append(f"视频2: {os.path.basename(video2_path)} ({w2}x{h2}, {fps2:.2f}fps)")
            info_lines.append(f"输出: {target_w}x{target_h}, {target_fps:.2f}fps")
            info_lines.append(f"编码模式: {'重新编码' if need_reencode else '直接拼接'}")
            if need_reencode:
                info_lines.append(f"编码质量: {encode_quality}")
            
            info = "\n".join(info_lines)
            
            print(f"[VideoConcatNode] 视频拼接成功: {output_path_full}")
            return (concat_video, info)
            
        except subprocess.TimeoutExpired:
            return (None, "视频拼接超时（超过10分钟）")
        except FileNotFoundError:
            return (None, "错误：未找到 FFmpeg，请确保已安装 FFmpeg 并添加到系统 PATH")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return (None, f"视频拼接过程中发生错误: {str(e)}")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "VideoConcatNode": VideoConcatNode,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoConcatNode": "视频拼接",
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
