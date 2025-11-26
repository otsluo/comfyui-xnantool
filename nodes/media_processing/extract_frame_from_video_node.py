import torch
import numpy as np
from PIL import Image
import cv2
import os
import logging
import folder_paths

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExtractFrameFromVideoNode:
    """
    视频帧提取节点
    从视频文件中提取指定帧并导出为图片
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
                    "description": "选择要提取帧的视频文件",
                    "video_upload": True  # 添加视频上传支持
                }),
                "frame_extraction_method": (["frame_number", "timestamp"], {
                    "default": "frame_number",
                    "label": "提取方式",
                    "description": "选择帧提取的方式：按帧号或按时间戳"
                }),
                "frame_number": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 100000,
                    "step": 1,
                    "display": "number",
                    "label": "帧号",
                    "description": "要提取的帧号（从1开始）"
                }),
                "timestamp": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 3600.0,
                    "step": 0.1,
                    "display": "number",
                    "label": "时间戳（秒）",
                    "description": "要提取帧的时间点（秒）"
                }),
                "output_format": (["png", "jpg", "bmp"], {
                    "default": "png",
                    "label": "输出格式",
                    "description": "输出图片的格式"
                }),
                "image_quality": ("INT", {
                    "default": 100,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "display": "slider",
                    "label": "图片质量",
                    "description": "输出图片的质量（仅对JPG格式有效）"
                }),
            },
            "optional": {
                "output_filename": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "可选：自定义输出文件名（不含扩展名）"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "INT", "STRING")
    RETURN_NAMES = ("image", "image_path", "frame_index", "status_message")
    FUNCTION = "extract_frame"
    CATEGORY = "XnanTool/媒体处理"
    
    @classmethod
    def IS_CHANGED(cls, video_file, frame_extraction_method, frame_number, timestamp, output_format, image_quality, output_filename=""):
        # 如果视频文件存在，返回其修改时间，否则返回0
        video_path = folder_paths.get_annotated_filepath(video_file)
        if os.path.exists(video_path):
            return os.path.getmtime(video_path)
        return 0
    
    @classmethod
    def VALIDATE_INPUTS(cls, video_file, frame_extraction_method, frame_number, timestamp, output_format, image_quality, output_filename=""):
        video_path = folder_paths.get_annotated_filepath(video_file)
        if not os.path.exists(video_path):
            return "Invalid video file: {}".format(video_file)
        return True

    def extract_frame(self, video_file, frame_extraction_method, frame_number, timestamp, output_format, image_quality, output_filename=""):
        """
        从视频文件中提取指定帧并导出为图片
        
        Args:
            video_file (str): 视频文件路径
            frame_extraction_method (str): 帧提取方式 ("frame_number" 或 "timestamp")
            frame_number (int): 要提取的帧号（从1开始）
            timestamp (float): 要提取帧的时间点（秒）
            output_format (str): 输出图片格式 ("png", "jpg", "bmp")
            image_quality (int): 输出图片质量（1-100，仅对JPG有效）
            output_filename (str): 自定义输出文件名（不含扩展名）
            
        Returns:
            tuple: 包含图像张量、图像路径、帧索引和状态信息的元组
        """
        try:
            # 获取视频文件的完整路径
            video_path = folder_paths.get_annotated_filepath(video_file)
            
            # 检查视频文件是否存在
            if not os.path.exists(video_path):
                error_msg = f"错误：视频文件不存在: {video_path}"
                logger.error(error_msg)
                return (torch.zeros(1, 64, 64, 3), "", -1, error_msg)
            
            # 使用OpenCV打开视频文件
            cap = cv2.VideoCapture(video_path)
            
            # 检查视频是否成功打开
            if not cap.isOpened():
                error_msg = f"错误：无法打开视频文件: {video_path}"
                logger.error(error_msg)
                return (torch.zeros(1, 64, 64, 3), "", -1, error_msg)
            
            # 获取视频属性
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"视频信息 - 总帧数: {total_frames}, FPS: {fps}, 分辨率: {width}x{height}")
            
            # 确定要提取的帧索引
            if frame_extraction_method == "frame_number":
                target_frame_index = frame_number - 1  # 转换为0基索引
                if target_frame_index >= total_frames:
                    error_msg = f"错误：指定的帧号({frame_number})超出了视频总帧数({total_frames})"
                    logger.error(error_msg)
                    cap.release()
                    return (torch.zeros(1, 64, 64, 3), "", -1, error_msg)
            else:  # timestamp
                target_frame_index = int(timestamp * fps)
                if target_frame_index >= total_frames:
                    error_msg = f"错误：指定的时间点({timestamp}秒)超出了视频总时长({total_frames/fps:.2f}秒)"
                    logger.error(error_msg)
                    cap.release()
                    return (torch.zeros(1, 64, 64, 3), "", -1, error_msg)
            
            # 设置视频读取位置到目标帧
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_index)
            
            # 读取帧
            ret, frame = cap.read()
            
            # 释放视频捕获对象
            cap.release()
            
            if not ret:
                error_msg = f"错误：无法读取第 {target_frame_index + 1} 帧"
                logger.error(error_msg)
                return (torch.zeros(1, 64, 64, 3), "", -1, error_msg)
            
            # 将BGR格式转换为RGB格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 转换为PIL图像
            pil_image = Image.fromarray(frame_rgb)
            
            # 转换为torch张量 (H, W, C) -> (1, H, W, C)
            image_tensor = torch.from_numpy(np.array(pil_image)).float() / 255.0
            image_tensor = image_tensor.unsqueeze(0)  # 添加批次维度
            
            # 获取输出目录
            output_dir = folder_paths.get_output_directory()
            
            # 确定输出文件名
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            
            if not output_filename:
                output_filename = f"{video_name}_frame_{target_frame_index + 1}"
            
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
            
            # 保存图像到文件
            if output_format == "jpg":
                pil_image.save(output_file, "JPEG", quality=image_quality, optimize=True)
            elif output_format == "png":
                pil_image.save(output_file, "PNG", optimize=True)
            else:  # bmp
                pil_image.save(output_file, "BMP")
            
            success_msg = f"✅ 帧提取成功！\n帧号: {target_frame_index + 1}\n时间点: {target_frame_index / fps:.2f}秒\n文件路径: {output_file}\n格式: {output_format}"
            logger.info(success_msg)
            
            return (image_tensor, output_file, target_frame_index + 1, success_msg)
            
        except Exception as e:
            error_msg = f"❌ 处理过程中出现错误: {str(e)}"
            logger.error(error_msg)
            return (torch.zeros(1, 64, 64, 3), "", -1, error_msg)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "ExtractFrameFromVideoNode": ExtractFrameFromVideoNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ExtractFrameFromVideoNode": "视频帧提取节点"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]