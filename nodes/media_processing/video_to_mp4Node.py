import os
import cv2
import numpy as np
from PIL import Image
import torch
import folder_paths

class VideoToMp4Node:
    """
    视频转MP4节点 - 将视频文件转换为MP4格式
    """
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {"default": "", "multiline": False}),
                "start_time": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3600.0, "step": 0.1}),
                "duration": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 3600.0, "step": 0.1}),  # -1 表示整个视频
                "fps": ("INT", {"default": 25, "min": 1, "max": 60}),
                "quality": (["high", "medium", "low", "custom"], {"default": "medium"}),
                "crf_value": ("INT", {"default": 18, "min": 0, "max": 51}),  # CRF值，0-51，数值越小质量越高
                "preset": (["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"], {"default": "medium"}),
                "codec": (["libx264", "libx265"], {"default": "libx264"}),
                "audio_bitrate": (["128k", "192k", "256k", "320k"], {"default": "192k"}),
                "audio_sample_rate": (["original", "22050", "44100", "48000", "96000"], {"default": "original"}),
                "copy_audio": ("BOOLEAN", {"default": True}),
                "output_resolution": (["original", "custom", "320x240", "640x480", "1280x720", "1920x1080", "2560x1440", "3840x2160", "7680x4320"], {"default": "original"}),
                "custom_width": ("INT", {"default": 1920, "min": 1, "max": 7680}),
                "custom_height": ("INT", {"default": 1080, "min": 1, "max": 4320}),
                "output_path": ("STRING", {"default": "ComfyUI/output"}),
                "output_filename": ("STRING", {"default": "converted_video_mp4"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("output_path", "info")
    FUNCTION = "convert_video_to_mp4"
    CATEGORY = "XnanTool/媒体处理"

    def convert_video_to_mp4(self, video_path, start_time, duration, fps, quality, crf_value, preset, codec, audio_bitrate, audio_sample_rate, copy_audio, output_resolution, custom_width, custom_height, output_path, output_filename):
        """
        将视频转换为MP4格式
        """
        import subprocess
        import os
        
        if not os.path.exists(video_path):
            return ("", f"错误：视频文件不存在: {video_path}")

        # 获取视频信息
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return ("", f"错误：无法打开视频文件: {video_path}")

        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        # 确定输出尺寸
        if output_resolution == "original":
            new_width = width
            new_height = height
        elif output_resolution == "custom":
            new_width = custom_width
            new_height = custom_height
        else:
            # 解析预设分辨率
            res_parts = output_resolution.split('x')
            new_width = int(res_parts[0])
            new_height = int(res_parts[1])
        
        # 计算起始时间和持续时间
        calculated_start_time = start_time
        calculated_duration = duration if duration > 0 else -1
        
        # 准备输出
        output_dir = folder_paths.get_output_directory()
        output_file = os.path.join(output_dir, output_path, f"{output_filename}.mp4")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 根据质量预设确定CRF值
        if quality == "high":
            crf = 18  # 高质量，视觉无损
        elif quality == "medium":
            crf = 23  # 中等质量，平衡大小和质量
        elif quality == "low":
            crf = 28  # 低质量，较小文件
        else:  # custom
            crf = crf_value  # 使用用户自定义的CRF值

        # 构建FFmpeg命令
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(calculated_start_time) if calculated_start_time > 0 else "0",
        ]
        
        if calculated_duration > 0:
            cmd.extend(["-t", str(calculated_duration)])
        
        # 设置输出参数
        cmd.extend([
            "-c:v", codec,
            "-crf", str(crf),
            "-preset", preset,
            "-r", str(fps),
        ])
        
        # 添加分辨率设置
        if (new_width != width or new_height != height):
            cmd.extend(["-s", f"{new_width}x{new_height}"])
        
        # 处理音频参数
        if copy_audio:
            cmd.extend(["-c:a", "copy"])  # 直接复制音频流
        else:
            cmd.extend(["-c:a", "aac", f"-b:a", audio_bitrate])  # 重新编码音频
            
        # 添加音频采样率设置
        if audio_sample_rate != "original":
            cmd.extend(["-ar", audio_sample_rate])  # 设置音频采样率
        
        cmd.extend([
            "-y",  # 覆盖输出文件
            output_file
        ])
        
        try:
            # 执行FFmpeg命令
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                return ("", f"错误：FFmpeg转换失败: {result.stderr}")
            
            info = f"视频MP4转换完成: {video_path} -> {output_file}\n" \
                   f"原始尺寸: {width}x{height}, 输出尺寸: {new_width}x{new_height}\n" \
                   f"原始FPS: {original_fps}, 输出FPS: {fps}\n" \
                   f"CRF: {crf}, 预设: {preset}, 编码: {codec}"
            
            return (output_file, info)
            
        except FileNotFoundError:
            # 如果FFmpeg不可用，则回退到OpenCV方法
            return self.convert_video_to_mp4_opencv(video_path, start_time, duration, fps, quality, crf_value, preset, codec, audio_bitrate, audio_sample_rate, copy_audio, output_resolution, custom_width, custom_height, output_path, output_filename, width, height)
    
    def convert_video_to_mp4_opencv(self, video_path, start_time, duration, fps, quality, crf_value, preset, codec, audio_bitrate, audio_sample_rate, copy_audio, output_resolution, custom_width, custom_height, output_path, output_filename, width, height):
        """
        使用OpenCV作为回退方案将视频转换为MP4格式
        """
        # 获取视频信息
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return ("", f"错误：无法打开视频文件: {video_path}")

        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 确定输出尺寸
        if output_resolution == "original":
            new_width = width
            new_height = height
        elif output_resolution == "custom":
            new_width = custom_width
            new_height = custom_height
        else:
            # 解析预设分辨率
            res_parts = output_resolution.split('x')
            new_width = int(res_parts[0])
            new_height = int(res_parts[1])
        
        # 计算起始帧和结束帧
        start_frame = int(start_time * original_fps)
        total_frames = int(duration * original_fps) if duration > 0 else frame_count - start_frame
        
        # 设置起始位置
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # 准备输出
        output_dir = folder_paths.get_output_directory()
        output_file = os.path.join(output_dir, output_path, f"{output_filename}.mp4")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 创建视频写入对象
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, fps, (new_width, new_height))
        
        processed_frames = 0
        for i in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
            
            # 调整大小到目标尺寸
            if (frame.shape[1] != new_width or frame.shape[0] != new_height):
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            
            # 写入帧
            out.write(frame)
            processed_frames += 1
            
            # 按FPS抽帧
            for skip in range(int(original_fps/fps) - 1):
                cap.read()
        
        out.release()
        cap.release()
        
        info = f"视频MP4转换完成(OpenCV): {video_path} -> {output_file}\n" \
               f"原始尺寸: {width}x{height}, 输出尺寸: {new_width}x{new_height}\n" \
               f"原始FPS: {original_fps}, 输出FPS: {fps}\n" \
               f"处理帧数: {processed_frames}"
        
        return (output_file, info)





# 注册节点
NODE_CLASS_MAPPINGS = {
    "VideoToMp4Node": VideoToMp4Node,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoToMp4Node": "视频转MP4节点",
}