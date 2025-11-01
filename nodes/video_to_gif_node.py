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
                    "description": "图像缩放比例（0.1-1.0）"
                }),
                "optimize": ("BOOLEAN", {
                    "default": True,
                    "label": "优化GIF",
                    "description": "是否优化GIF文件大小"
                }),
                "palette_size": (["2", "4", "8", "16", "32", "64", "128", "256"], {
                    "default": "256",
                    "label": "调色板大小",
                    "description": "GIF的颜色数量"
                }),
                "quality": (["1", "2", "3", "4", "5"], {
                    "default": "3",
                    "label": "质量等级",
                    "description": "GIF质量等级（1=最低，2=低，3=中，4=高，5=最高）"
                }),
            },
            "optional": {
                "output_filename": ("STRING", {
                    "default": "视频转gif.gif",
                    "multiline": False,
                    "label": "输出文件名",
                    "description": "GIF文件的输出名称"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_path",)
    FUNCTION = "convert_video_to_gif"
    CATEGORY = "XnanTool/媒体处理"
    
    @classmethod
    def IS_CHANGED(cls, video_file, duration, fps, resize_factor, optimize, palette_size, quality, output_filename="视频转gif.gif"):
        # 如果视频文件存在，返回其修改时间，否则返回0
        if os.path.exists(video_file):
            return os.path.getmtime(video_file)
        return 0
    
    @classmethod
    def VALIDATE_INPUTS(cls, video_file):
        if not folder_paths.exists_annotated_filepath(video_file):
            return "Invalid video file: {}".format(video_file)
        return True

    def convert_video_to_gif(self, video_file, duration, fps, resize_factor, optimize, palette_size, quality, output_filename="视频转gif.gif"):
        """
        将视频文件转换为GIF动画
        
        Args:
            video_file (str): 视频文件路径
            duration (float): GIF的持续时间（秒）
            fps (int): GIF的帧率
            resize_factor (float): 图像缩放比例（0.1-1.0）
            optimize (bool): 是否优化GIF文件大小
            palette_size (str): GIF使用的颜色数量（"2"-"256"）
            quality (str): GIF质量等级（"1"=低，"2"=中，"3"=高）
            output_filename (str): GIF文件的输出名称
            
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
            
            # 构建输出文件路径并处理文件名冲突
            if not output_filename.lower().endswith('.gif'):
                output_filename += '.gif'
            
            # 处理文件名冲突，自动添加序号
            base_name, ext = os.path.splitext(output_filename)
            output_path = os.path.join(output_dir, output_filename)
            counter = 1
            original_output_path = output_path
            while os.path.exists(output_path):
                new_filename = f"{base_name}_{counter}{ext}"
                output_path = os.path.join(output_dir, new_filename)
                counter += 1
            
            # 如果文件被重命名，记录日志
            if original_output_path != output_path:
                logger.info(f"检测到同名文件，已自动重命名为: {os.path.basename(output_path)}")
            
            # 使用imageio读取视频
            reader = imageio.get_reader(video_path, 'ffmpeg')
            
            # 获取视频元数据
            video_fps = reader.get_meta_data()['fps']
            logger.info(f"视频帧率: {video_fps}")
            
            # 收集帧数据
            frames = []
            frame_count = 0
            for i, frame in enumerate(reader):
                # 停止在结束帧之后（基于持续时间）
                if i >= int(duration * video_fps):
                    break
                
                # 按指定帧率采样
                if i % int(video_fps / fps) == 0:
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
                # 将所有numpy数组帧转换为PIL图像对象
                pil_frames = [Image.fromarray(frame) for frame in frames]
                
                # 将palette_size从字符串转换为整数
                palette_size_int = int(palette_size)
                
                # 准备GIF保存参数
                gif_kwargs = {
                    'format': 'GIF',
                    'save_all': True,
                    'append_images': pil_frames[1:],
                    'duration': int(1000 / fps),  # 每帧持续时间（毫秒）
                    'loop': 0,
                    'optimize': optimize,
                    'palettesize': palette_size_int
                }
                
                # 根据质量等级设置不同的优化参数
                # 质量等级1: 最低质量，最小文件大小
                # 质量等级2: 低质量
                # 质量等级3: 中等质量
                # 质量等级4: 高质量
                # 质量等级5: 最高质量，最大文件大小
                
                if quality == "1":
                    # 最低质量设置
                    gif_kwargs['subrectangles'] = False  # 不使用子矩形优化
                    gif_kwargs['optimize'] = True  # 优化文件大小
                elif quality == "2":
                    # 低质量设置
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = True  # 优化文件大小
                elif quality == "3":
                    # 中等质量设置
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = True  # 优化文件大小
                elif quality == "4":
                    # 高质量设置
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = False  # 不优化文件大小以保持质量
                else:  # quality == "5"
                    # 最高质量设置
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = False  # 不优化文件大小以保持质量
                
                # 写入GIF文件
                pil_frames[0].save(output_path, **gif_kwargs)
            
            # 记录最终保存的文件路径
            logger.info(f"GIF已保存到: {output_path}")
            logger.info(f"总帧数: {frame_count}")
            logger.info(f"调色板大小: {palette_size}")
            logger.info(f"是否优化: {optimize}")
            
            return (output_path,)
            
        except Exception as e:
            logger.error(f"视频转GIF过程中发生错误: {str(e)}")
            raise e

# 注册节点
NODE_CLASS_MAPPINGS = {
    "VideoToGifNode": VideoToGifNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoToGifNode": "视频转GIF节点"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]