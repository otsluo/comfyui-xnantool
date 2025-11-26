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

class BatchExtractFrameFromVideoNode:
    """
    批量视频帧提取节点
    从指定文件夹中的所有视频文件提取指定帧并导出为图片
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取输入目录
        input_dir = folder_paths.get_input_directory()
        # 获取所有文件夹
        folders = [f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f))]
        
        return {
            "required": {
                "folder_selection_mode": (["select_from_input_dir", "custom_path"], {
                    "default": "select_from_input_dir",
                    "label": "文件夹选择模式",
                    "description": "选择文件夹的方式：从输入目录选择或自定义路径"
                }),
                "video_folder": (["选择视频文件夹"] + sorted(folders), {
                    "label": "视频文件夹",
                    "description": "从输入目录中选择包含视频文件的文件夹"
                }),
                "custom_video_folder_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输入自定义视频文件夹的完整路径",
                    "label": "自定义视频文件夹路径"
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
                "output_filename_prefix": ("STRING", {
                    "default": "batch_frame",
                    "multiline": False,
                    "placeholder": "可选：输出文件名前缀"
                }),
                "output_folder": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "可选：输出文件夹路径（留空则使用源文件夹）",
                    "label": "输出文件夹路径"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("image_paths", "frame_indices", "status_message")
    FUNCTION = "batch_extract_frames"
    CATEGORY = "XnanTool/媒体处理"
    
    @classmethod
    def IS_CHANGED(cls, folder_selection_mode, video_folder, custom_video_folder_path, frame_extraction_method, frame_number, timestamp, output_format, image_quality, output_filename_prefix="", output_folder=""):
        # 如果文件夹或参数发生变化，返回当前时间戳
        return float("NaN")  # 总是重新执行
    
    @classmethod
    def VALIDATE_INPUTS(cls, folder_selection_mode, video_folder, custom_video_folder_path, frame_extraction_method, frame_number, timestamp, output_format, image_quality, output_filename_prefix="", output_folder=""):
        # 根据选择模式确定文件夹路径
        if folder_selection_mode == "custom_path":
            if not custom_video_folder_path:
                return "请提供自定义视频文件夹的完整路径"
            folder_path = custom_video_folder_path
        else:  # select_from_input_dir
            if not video_folder or video_folder == "选择视频文件夹":
                return "请选择一个有效的视频文件夹"
            
            # 获取视频文件夹的完整路径
            input_dir = folder_paths.get_input_directory()
            folder_path = os.path.join(input_dir, video_folder)
        
        if not os.path.exists(folder_path):
            return "视频文件夹不存在: {}".format(folder_path)
        
        if not os.path.isdir(folder_path):
            return "指定路径不是文件夹: {}".format(folder_path)
        
        # 检查文件夹中是否有视频文件
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
        video_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[1].lower() in video_extensions]
        
        if not video_files:
            return "指定文件夹中没有找到视频文件"
        
        # 验证输出文件夹（如果指定了）
        if output_folder:
            if not os.path.exists(output_folder):
                try:
                    os.makedirs(output_folder)
                except Exception as e:
                    return "无法创建输出文件夹 '{}': {}".format(output_folder, str(e))
            elif not os.path.isdir(output_folder):
                return "指定的输出路径不是文件夹: {}".format(output_folder)
        
        return True

    def batch_extract_frames(self, folder_selection_mode, video_folder, custom_video_folder_path, frame_extraction_method, frame_number, timestamp, output_format, image_quality, output_filename_prefix="batch_frame", output_folder=""):
        """
        从指定文件夹中的所有视频文件提取指定帧并导出为图片
        
        Args:
            folder_selection_mode (str): 文件夹选择模式 ("select_from_input_dir" 或 "custom_path")
            video_folder (str): 包含视频文件的文件夹名称（从输入目录选择时使用）
            custom_video_folder_path (str): 自定义视频文件夹路径（自定义路径时使用）
            frame_extraction_method (str): 帧提取方式 ("frame_number" 或 "timestamp")
            frame_number (int): 要提取的帧号（从1开始）
            timestamp (float): 要提取帧的时间点（秒）
            output_format (str): 输出图片格式 ("png", "jpg", "bmp")
            image_quality (int): 输出图片质量（1-100，仅对JPG有效）
            output_filename_prefix (str): 输出文件名前缀
            output_folder (str): 输出文件夹路径（可选，留空则使用源文件夹）
            
        Returns:
            tuple: 包含图像张量列表、图像路径列表、帧索引列表和状态信息的元组
        """
        try:
            # 根据选择模式确定文件夹路径
            if folder_selection_mode == "custom_path":
                if not custom_video_folder_path:
                    error_msg = "错误：未提供自定义视频文件夹路径"
                    logger.error(error_msg)
                    return ([], [], error_msg)
                folder_path = custom_video_folder_path
            else:  # select_from_input_dir
                if not video_folder or video_folder == "选择视频文件夹":
                    error_msg = "错误：未选择视频文件夹"
                    logger.error(error_msg)
                    return ([], [], error_msg)
                
                # 获取视频文件夹的完整路径
                input_dir = folder_paths.get_input_directory()
                folder_path = os.path.join(input_dir, video_folder)
            
            # 检查文件夹是否存在
            if not os.path.exists(folder_path):
                error_msg = f"错误：视频文件夹不存在: {folder_path}"
                logger.error(error_msg)
                return ([], [], error_msg)
            
            # 获取文件夹中的所有视频文件
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
            video_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[1].lower() in video_extensions]
            
            if not video_files:
                error_msg = f"错误：在文件夹 '{video_folder}' 中没有找到视频文件"
                logger.error(error_msg)
                return ([], [], error_msg)
            
            # 按文件名排序
            video_files.sort()
            
            image_tensors = []
            image_paths = []
            frame_indices = []
            status_messages = []
            
            success_count = 0
            fail_count = 0
            
            # 处理每个视频文件
            for i, video_file in enumerate(video_files):
                try:
                    # 获取视频文件的完整路径
                    video_path = os.path.join(folder_path, video_file)
                    
                    # 使用OpenCV打开视频文件
                    cap = cv2.VideoCapture(video_path)
                    
                    # 检查视频是否成功打开
                    if not cap.isOpened():
                        error_msg = f"错误：无法打开视频文件: {video_file}"
                        logger.error(error_msg)
                        status_messages.append(f"[{i+1}] {error_msg}")
                        fail_count += 1
                        continue
                    
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
                            status_messages.append(f"[{i+1}] {error_msg}")
                            fail_count += 1
                            continue
                    else:  # timestamp
                        target_frame_index = int(timestamp * fps)
                        if target_frame_index >= total_frames:
                            error_msg = f"错误：指定的时间点({timestamp}秒)超出了视频总时长({total_frames/fps:.2f}秒)"
                            logger.error(error_msg)
                            cap.release()
                            status_messages.append(f"[{i+1}] {error_msg}")
                            fail_count += 1
                            continue
                    
                    # 设置视频读取位置到目标帧
                    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_index)
                    
                    # 读取帧
                    ret, frame = cap.read()
                    
                    # 释放视频捕获对象
                    cap.release()
                    
                    if not ret:
                        error_msg = f"错误：无法读取第 {target_frame_index + 1} 帧"
                        logger.error(error_msg)
                        status_messages.append(f"[{i+1}] {error_msg}")
                        fail_count += 1
                        continue
                    
                    # 将BGR格式转换为RGB格式
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # 转换为PIL图像
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # 转换为torch张量 (H, W, C) -> (1, H, W, C)
                    image_tensor = torch.from_numpy(np.array(pil_image)).float() / 255.0
                    image_tensor = image_tensor.unsqueeze(0)  # 添加批次维度
                    
                    # 添加到结果列表
                    image_tensors.append(image_tensor)
                    
                    # 确定输出目录
                    if output_folder and os.path.exists(output_folder):
                        # 使用用户指定的输出文件夹
                        output_dir = output_folder
                    else:
                        # 使用默认输出目录
                        output_dir = folder_paths.get_output_directory()
                        # 如果指定了输出文件夹但不存在，则记录警告并使用默认输出目录
                        if output_folder:
                            logger.warning(f"指定的输出文件夹 '{output_folder}' 不存在，将使用默认输出目录")
                    
                    # 确定输出文件名
                    video_name = os.path.splitext(os.path.basename(video_path))[0]
                    output_filename = f"{output_filename_prefix}_{video_name}_frame_{target_frame_index + 1}"
                    
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
                    
                    # 添加到结果列表
                    image_paths.append(output_file)
                    frame_indices.append(target_frame_index + 1)
                    
                    success_msg = f"[{i+1}] ✅ 帧提取成功！帧号: {target_frame_index + 1}, 时间点: {target_frame_index / fps:.2f}秒, 文件: {os.path.basename(output_file)}"
                    logger.info(success_msg)
                    status_messages.append(success_msg)
                    success_count += 1
                    
                except Exception as e:
                    error_msg = f"[{i+1}] ❌ 处理视频 '{video_file}' 时出现错误: {str(e)}"
                    logger.error(error_msg)
                    status_messages.append(error_msg)
                    fail_count += 1
                    continue
            
            # 汇总状态信息
            summary_msg = f"✅ 批量帧提取完成！成功: {success_count}, 失败: {fail_count}\n" + "\n".join(status_messages)
            
            # 返回图像路径、帧索引和状态信息（移除了图像张量）
            return (image_paths, frame_indices, summary_msg)
                
        except Exception as e:
            error_msg = f"❌ 批量处理过程中出现严重错误: {str(e)}"
            logger.error(error_msg)
            return ([], [], error_msg)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "BatchExtractFrameFromVideoNode": BatchExtractFrameFromVideoNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchExtractFrameFromVideoNode": "批量视频帧提取节点"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]