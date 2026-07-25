import folder_paths
import os
import cv2
import numpy as np
from PIL import Image


class VideoToFramesNode:
    """视频转序列帧节点 - 将视频拆分为图片序列"""
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
    
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
                "output_path": ("STRING", {
                    "default": "frames",
                    "multiline": False,
                    "label": "输出路径",
                    "description": "输出目录路径，留空使用默认路径"
                }),
                "filename_prefix": ("STRING", {
                    "default": "frame",
                    "label": "文件名前缀",
                    "description": "输出文件名的前缀"
                }),
                "image_format": (["png", "jpg", "jpeg", "webp", "bmp"], {
                    "default": "png",
                    "label": "图片格式"
                }),
                "quality": ("INT", {
                    "default": 100,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "label": "图片质量",
                    "description": "图片质量（仅对jpg/webp有效）"
                }),
                "num_padding_digits": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "label": "数字位数",
                    "description": "帧号数字的填充位数"
                }),
                "target_fps": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 120.0,
                    "step": 0.1,
                    "label": "目标帧率",
                    "description": "目标帧率（0表示使用原始帧率）"
                }),
                "max_frames": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100000,
                    "step": 1,
                    "label": "最大帧数",
                    "description": "最大输出帧数（0表示不限制）"
                }),
            },
            "optional": {
                "video": ("VIDEO",),
            }
        }
    
    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("输出信息", "frames")
    OUTPUT_NODE = True
    FUNCTION = "video_to_frames"
    CATEGORY = "❤️❤️❤️XnanTool/媒体处理"
    
    def video_to_frames(self, video_path, output_path="frames", filename_prefix="frame", 
                        image_format="png", quality=95, num_padding_digits=5,
                        target_fps=0.0, max_frames=0, video=None):
        """将视频拆分为图片序列"""
        try:
            # 如果提供了视频对象，优先使用视频对象的路径
            if video is not None:
                if hasattr(video, 'get_stream_source'):
                    video_path = video.get_stream_source()
                elif hasattr(video, 'path'):
                    video_path = video.path
            
            if not video_path or not video_path.strip():
                return {"result": ("", None), "ui": {"text": "错误: 请提供视频路径或视频对象"}}
            
            # 检查文件是否存在
            if not os.path.exists(video_path):
                return {"result": ("", None), "ui": {"text": f"错误: 视频文件不存在: {video_path}"}}
            
            # 确定输出目录
            if output_path.strip() != "":
                if os.path.isabs(output_path):
                    full_output_dir = output_path
                else:
                    full_output_dir = os.path.join(self.output_dir, output_path)
            else:
                full_output_dir = os.path.join(self.output_dir, "frames")
            
            # 创建输出目录
            os.makedirs(full_output_dir, exist_ok=True)
            
            # 打开视频
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {"result": ("", None), "ui": {"text": f"错误: 无法打开视频文件: {video_path}"}}
            
            # 获取视频信息
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"🎬 视频信息: {total_frames}帧, {fps}fps, {width}x{height}")
            
            # 计算帧提取间隔
            if target_fps > 0 and fps > 0:
                frame_interval = max(1, round(fps / target_fps))
                effective_fps = fps / frame_interval
                print(f"🎬 目标帧率: {target_fps}fps, 每隔{frame_interval}帧提取1帧, 实际输出帧率: {effective_fps:.2f}fps")
            else:
                frame_interval = 1
                effective_fps = fps
            
            # 计算预期输出帧数
            expected_output_frames = (total_frames + frame_interval - 1) // frame_interval
            if max_frames > 0:
                expected_output_frames = min(expected_output_frames, max_frames)
            print(f"🎬 预期输出帧数: {expected_output_frames}")
            
            # 读取并保存帧
            saved_files = []
            frames_list = []
            frame_count = 0
            read_frame_index = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 按帧间隔跳帧
                if read_frame_index % frame_interval != 0:
                    read_frame_index += 1
                    continue
                
                # 检查是否达到最大帧数
                if max_frames > 0 and frame_count >= max_frames:
                    break
                
                # 转换为 RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 保存为 numpy 数组（用于输出）
                frame_np = frame_rgb.astype(np.float32) / 255.0
                frames_list.append(frame_np)
                
                # 生成文件名
                filename = f"{filename_prefix}_{frame_count:0{num_padding_digits}d}.{image_format}"
                file_path = os.path.join(full_output_dir, filename)
                
                # 保存图片
                if image_format.lower() in ["jpg", "jpeg"]:
                    # JPEG 需要转换为 BGR
                    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(file_path, frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
                elif image_format.lower() == "webp":
                    img = Image.fromarray(frame_rgb)
                    img.save(file_path, format="WEBP", quality=quality)
                elif image_format.lower() == "png":
                    img = Image.fromarray(frame_rgb)
                    img.save(file_path, format="PNG")
                elif image_format.lower() == "bmp":
                    img = Image.fromarray(frame_rgb)
                    img.save(file_path, format="BMP")
                else:
                    img = Image.fromarray(frame_rgb)
                    img.save(file_path)
                
                saved_files.append(file_path)
                frame_count += 1
                read_frame_index += 1
                
                if frame_count % 50 == 0:
                    print(f"🎬 已提取 {frame_count}/{expected_output_frames} 帧")
            
            cap.release()
            
            # 堆叠帧为张量
            if frames_list:
                import torch
                frames_tensor = torch.from_numpy(np.stack(frames_list))
            else:
                frames_tensor = None
            
            # 生成输出信息
            info_text = (
                f"✅ 成功提取 {len(saved_files)} 帧\n\n"
                f"📁 输出目录: {full_output_dir}\n"
                f"🖼️ 格式: {image_format.upper()}\n"
                f"📐 尺寸: {width}x{height}\n"
                f"🎞️ 原始帧率: {fps:.2f} fps\n"
            )
            
            if target_fps > 0:
                info_text += f"🎯 目标帧率: {target_fps:.2f} fps → 每隔{frame_interval}帧提取1帧 → 实际输出帧率: {effective_fps:.2f} fps\n"
            
            info_text += f"🖼️ 输出帧数: {len(saved_files)}"
            
            if max_frames > 0:
                info_text += f" (上限: {max_frames})"
            
            print(f"🎬 视频转序列帧完成: {len(saved_files)} 帧")
            
            return {"result": (info_text, frames_tensor), "ui": {"text": info_text}}
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"result": ("", None), "ui": {"text": f"错误: {str(e)}"}}


# 注册节点
NODE_CLASS_MAPPINGS = {
    "VideoToFramesNode": VideoToFramesNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoToFramesNode": "视频转序列帧"
}

# 导出映射
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
