import torch
import numpy as np
from PIL import Image
import imageio
import os
import logging
import folder_paths

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoToGifNode:
    """
    视频转GIF节点
    将视频文件转换为GIF动画
    """
    
    def __init__(self):
        pass
    
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
                    "description": "选择要转换为GIF的视频文件",
                    "video_upload": True  # 添加视频上传支持
                }),
                "start_time": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 3600.0,
                    "step": 0.1,
                    "display": "number",
                    "label": "开始时间",
                    "description": "视频开始时间（秒）"
                }),
                "duration": ("FLOAT", {
                    "default": 5.0,
                    "min": 0.1,
                    "max": 60.0,
                    "step": 0.1,
                    "display": "number",
                    "label": "持续时间",
                    "description": "GIF的持续时间（秒）"
                }),
                "fps": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 30,
                    "step": 1,
                    "display": "number",
                    "label": "帧率",
                    "description": "GIF的帧率"
                }),
                "resize_factor": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "slider",
                    "label": "缩放因子",
                    "description": "图像缩放因子（0.1-1.0）"
                }),
                "optimize": ("BOOLEAN", {
                    "default": True,
                    "label": "优化GIF",
                    "description": "是否优化GIF文件大小"
                }),
                "palette_size": (["2", "4", "8", "16", "32", "64", "128", "256"], {
                    "default": "256",
                    "label": "调色板大小",
                    "description": "GIF使用的颜色数量"
                }),
            },
            "optional": {
                "output_filename": ("STRING", {
                    "default": "output.gif",
                    "multiline": False,
                    "label": "输出文件名",
                    "description": "GIF文件的输出名称"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_path",)
    FUNCTION = "convert_video_to_gif"
    CATEGORY = "XnanTool/实用工具"
    
    def convert_video_to_gif(self, video_file, start_time, duration, fps, resize_factor, optimize, palette_size, output_filename="output.gif"):
        """
        将视频文件转换为GIF动画
        
        Args:
            video_file: 视频文件名
            start_time: 开始时间（秒）
            duration: 持续时间（秒）
            fps: 帧率
            resize_factor: 缩放因子
            optimize: 是否优化GIF
            palette_size: 调色板大小（字符串类型，可选值："2", "4", "8", "16", "32", "64", "128", "256"）
            output_filename: 输出文件名
            
        Returns:
            tuple: 包含输出文件路径的元组
        """
        try:
            # 获取视频文件的完整路径
            video_path = folder_paths.get_annotated_filepath(video_file)
            
            # 检查视频文件是否存在
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            # 获取输出目录
            output_dir = folder_paths.get_output_directory()
            
            # 构建输出文件路径
            if not output_filename.lower().endswith('.gif'):
                output_filename += '.gif'
            output_path = os.path.join(output_dir, output_filename)
            
            # 使用imageio读取视频
            reader = imageio.get_reader(video_path, 'ffmpeg')
            
            # 获取视频元数据
            video_fps = reader.get_meta_data()['fps']
            logger.info(f"视频帧率: {video_fps}")
            
            # 计算开始和结束帧
            start_frame = int(start_time * video_fps)
            end_frame = int((start_time + duration) * video_fps)
            
            # 收集帧数据
            frames = []
            frame_count = 0
            for i, frame in enumerate(reader):
                # 跳过开始帧之前的帧
                if i < start_frame:
                    continue
                
                # 停止在结束帧之后
                if i > end_frame:
                    break
                
                # 按指定帧率采样
                if (i - start_frame) % int(video_fps / fps) == 0:
                    # 调整图像大小
                    if resize_factor != 1.0:
                        height, width = frame.shape[:2]
                        new_height = int(height * resize_factor)
                        new_width = int(width * resize_factor)
                        frame = Image.fromarray(frame).resize((new_width, new_height), Image.LANCZOS)
                        frame = np.array(frame)
                    
                    frames.append(frame)
                    frame_count += 1
            
            # 关闭读取器
            reader.close()
            
            # 创建GIF
            if frames:
                # 将palette_size从字符串转换为整数
                palette_size_int = int(palette_size)
                
                # 设置GIF参数
                gif_kwargs = {
                    'format': 'GIF',
                    'fps': fps,
                    'loop': 0,
                    'palettesize': palette_size_int,
                }
                
                # 如果启用优化，添加优化参数
                if optimize:
                    gif_kwargs['optimize'] = True
                    gif_kwargs['subrectangles'] = True
                
                # 写入GIF
                imageio.mimsave(output_path, frames, **gif_kwargs)
            
            logger.info(f"GIF已保存到: {output_path}")
            logger.info(f"总帧数: {frame_count}")
            logger.info(f"调色板大小: {palette_size}")
            logger.info(f"是否优化: {optimize}")
            
            return (output_path,)
            
        except Exception as e:
            logger.error(f"视频转GIF过程中发生错误: {str(e)}")
            raise e
    
    @classmethod
    def IS_CHANGED(cls, video_file, start_time, duration, fps, resize_factor, optimize, palette_size, output_filename="output.gif"):
        video_path = folder_paths.get_annotated_filepath(video_file)
        if os.path.exists(video_path):
            return os.path.getmtime(video_path)
        return 0
    
    @classmethod
    def VALIDATE_INPUTS(cls, video_file):
        if not folder_paths.exists_annotated_filepath(video_file):
            return "Invalid video file: {}".format(video_file)
        return True

# 注册节点
NODE_CLASS_MAPPINGS = {
    "VideoToGifNode": VideoToGifNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoToGifNode": "视频转GIF节点-【新】"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]