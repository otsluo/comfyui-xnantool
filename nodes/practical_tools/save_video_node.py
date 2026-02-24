import folder_paths
import os
import cv2
import numpy as np
from PIL import Image

class SaveVideoNode:
    """保存视频节点 - 将图像序列保存为视频文件"""
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "视频"}),
                "fps": ("INT", {"default": 25, "min": 1, "max": 60, "step": 1}),
                "video_format": (["mp4", "avi", "mov", "mkv"], {"default": "mp4"}),
                "codec": (["mp4v", "XVID", "MJPG", "X264", "X265"], {"default": "X264"}),
            },
            "optional": {
                "audio": ("AUDIO",),
                "output_path": ("STRING", {"default": "video", "multiline": False, "placeholder": "留空使用默认输出路径"}),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    OUTPUT_NODE = True
    FUNCTION = "save_video"
    CATEGORY = "XnanTool/实用工具"
    
    def save_video(self, images, filename_prefix="视频", fps=25, video_format="mp4", codec="X264", audio=None, output_path=""):
        """将图像序列保存为视频文件"""
        import locale
        import sys
        import subprocess
        import tempfile
        
        # 确定输出路径
        if output_path.strip() != "":
            # 如果输出路径不是绝对路径，则将其视为相对于默认输出目录的子文件夹
            if os.path.isabs(output_path):
                full_output_dir = output_path
            else:
                full_output_dir = os.path.join(self.output_dir, output_path)
        else:
            full_output_dir = self.output_dir
        
        # 创建输出目录（如果不存在）
        if not os.path.exists(full_output_dir):
            os.makedirs(full_output_dir, exist_ok=True)
        
        # 获取图像尺寸
        img_shape = images[0].shape
        height, width = img_shape[0], img_shape[1]
        
        # 生成文件名
        counter = 0
        while True:
            # 生成文件名
            output_filename = f"{filename_prefix}_{counter:05d}.{video_format}"
            
            # 处理Windows系统的中文字符编码问题
            if sys.platform.startswith('win'):
                # 在Windows上，确保使用正确的文件名编码
                # 获取当前系统的文件系统编码
                fs_encoding = sys.getfilesystemencoding()
                if fs_encoding.lower() in ['utf-8', 'utf8']:
                    # 如果文件系统编码是UTF-8，直接使用
                    safe_filename = output_filename
                else:
                    # 否则，使用locale编码或UTF-8编码
                    try:
                        # 尝试将字符串编码为字节，然后再解码
                        safe_filename = output_filename.encode('utf-8').decode('utf-8')
                    except UnicodeEncodeError:
                        # 如果出错，使用英文替代
                        safe_filename = f"video_{counter:05d}.{video_format}"
            else:
                safe_filename = output_filename
            
            file_path = os.path.join(full_output_dir, safe_filename)
            if not os.path.exists(file_path):
                break
            counter += 1
        
        # 设置视频编码器
        # 将codec映射到OpenCV支持的四字符代码
        # OpenCV的VideoWriter_fourcc只支持特定的四字符代码
        codec_map = {
            "mp4v": "mp4v",
            "XVID": "XVIX", 
            "MJPG": "MJPG",
            "X264": "H264",  # 实际上OpenCV不直接支持H264的fourcc，可能需要使用别的方法
            "X265": "HEVC"   # 同样，OpenCV对X265的支持有限
        }
        
        # 使用原始codec值，因为某些编解码器需要特定处理
        opencv_codec = codec.lower()
        if opencv_codec == "x264":
            # 对于X264，使用mp4v作为fallback，因为OpenCV的fourcc不直接支持H264
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        elif opencv_codec == "x265":
            # 对于X265，使用mp4v作为fallback
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        elif opencv_codec == "xvid":
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        elif opencv_codec == "mjpeg" or opencv_codec == "mjpg":
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        else:
            fourcc = cv2.VideoWriter_fourcc(*opencv_codec)
        
        video_writer = cv2.VideoWriter(file_path, fourcc, fps, (width, height))
        
        # 将图像序列写入视频
        for img_tensor in images:
            # 将tensor转换为numpy数组
            img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
            
            # 如果是灰度图，转换为RGB
            if len(img_np.shape) == 3:
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
            
            video_writer.write(img_bgr)
        
        # 释放资源
        video_writer.release()
        
        # 如果提供了音频，使用FFmpeg将音频与视频合并
        if audio is not None:
            try:
                # 创建临时文件来存储合并后的视频
                temp_video_path = file_path.replace(f".{video_format}", f"_temp_with_audio.{video_format}")
                
                # 使用FFmpeg合并音频和视频
                cmd = [
                    "ffmpeg",
                    "-i", file_path,  # 输入视频
                    "-i", audio,       # 输入音频
                    "-c:v", "copy",    # 视频编码方式
                    "-c:a", "aac",     # 音频编码方式
                    "-strict", "experimental",
                    "-shortest",       # 让视频长度与最短的流（音频或视频）一样
                    "-y",              # 覆盖输出文件
                    temp_video_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # 替换原始视频文件
                    import shutil
                    shutil.move(temp_video_path, file_path)
                    message = f"视频已保存（含音频）: {file_path}"
                else:
                    # 如果FFmpeg失败，保留原始视频并发出警告
                    print(f"FFmpeg错误详情: {result.stderr}")
                    message = f"视频已保存（音频合并失败）: {file_path}\n警告: {result.stderr}"
            except subprocess.TimeoutExpired:
                message = f"视频已保存（音频合并超时）: {file_path}"
            except Exception as e:
                message = f"视频已保存（音频合并出错）: {file_path}\n错误: {str(e)}"
        else:
            message = f"视频已保存: {file_path}"
        
        return {"result": (file_path,), "ui": {"text": message}}

# 导出节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "SaveVideoNode": SaveVideoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveVideoNode": "保存视频",
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]