import os
import zipfile
import tempfile
import shutil
from PIL import Image
import numpy as np
import torch
import torchaudio
import folder_paths


class LoadZipNode:
    """
    加载ZIP文件节点 - 从ZIP压缩包中提取文件
    支持输出图片（IMAGE类型）、文本（STRING类型）、视频音频路径（STRING类型）
    """
    
    # 文件类型分类
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
    TEXT_EXTENSIONS = {'.txt', '.json', '.csv', '.md', '.xml', '.html', '.yaml', '.yml', '.log'}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'}
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取ComfyUI默认输入文件夹路径
        input_dir = folder_paths.get_input_directory()
        
        # 获取该目录下的所有ZIP文件
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        zip_files = [f for f in files if f.lower().endswith('.zip')]
        
        # 添加空选项
        if not zip_files:
            zip_files = [""]
        if "" not in zip_files:
            zip_files.insert(0, "")
        
        return {
            "required": {
                "zip_file": (sorted(zip_files), {"zip_upload": True}),
            },
            "optional": {
                "zip_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "ZIP文件路径",
                    "description": "ZIP压缩包的完整路径（优先使用，留空则使用上方选择的文件）"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "VIDEO", "AUDIO", "STRING")
    RETURN_NAMES = ("图片列表", "文本列表", "视频列表", "音频列表", "文件列表")
    OUTPUT_IS_LIST = (True, True, True, True, False)
    FUNCTION = "load_zip"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    @classmethod
    def IS_CHANGED(cls, zip_file, zip_path=""):
        """检测ZIP文件是否变化"""
        # 获取ComfyUI默认输入文件夹路径
        input_dir = folder_paths.get_input_directory()
        
        # 确定ZIP文件路径：优先使用完整路径，否则使用选择文件名
        if zip_path and zip_path.strip():
            actual_zip_path = zip_path.strip()
        else:
            actual_zip_path = os.path.join(input_dir, zip_file)
        
        # 如果ZIP文件存在，返回其修改时间，否则返回0
        if os.path.exists(actual_zip_path):
            return os.path.getmtime(actual_zip_path)
        return 0

    @classmethod
    def VALIDATE_INPUTS(cls, zip_file):
        # 获取ComfyUI默认输入文件夹路径
        input_dir = folder_paths.get_input_directory()
        # 构建完整的ZIP文件路径
        zip_path = os.path.join(input_dir, zip_file)
        if not os.path.exists(zip_path):
            return "Invalid ZIP file: {}".format(zip_file)
        return True
    
    def load_image(self, image_path):
        """
        加载单张图片并转换为 ComfyUI IMAGE 格式
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            torch.Tensor: 图片张量 [1, H, W, C]
        """
        img = Image.open(image_path)
        
        # 转换为 RGB（如果是 RGBA 或其他模式）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 转换为 numpy 数组并归一化到 [0, 1]
        img_array = np.array(img).astype(np.float32) / 255.0
        
        # 转换为 torch tensor，形状为 [1, H, W, C]
        img_tensor = torch.from_numpy(img_array)[None,]
        
        return img_tensor
    
    def load_video(self, video_path):
        """
        加载视频文件并转换为 ComfyUI VIDEO 格式
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            VideoFromFile: ComfyUI 视频对象
        """
        try:
            from comfy_api.input_impl import VideoFromFile
            
            # 使用 ComfyUI 官方的视频加载方式
            video_obj = VideoFromFile(video_path)
            
            return video_obj
        except Exception as e:
            print(f"📦 警告：无法加载视频 {video_path} - {str(e)}")
            return None
    
    def load_audio(self, audio_path):
        """
        加载音频文件并转换为 ComfyUI AUDIO 格式
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            dict: 包含 waveform 和 sample_rate 的字典
                  waveform 形状为 [1, channels, samples]
        """
        try:
            import av
            
            # 使用 pyav 加载音频（与 load_video_node.py 一致）
            with av.open(audio_path) as container:
                audio_stream = None
                for stream in container.streams:
                    if stream.type == 'audio':
                        audio_stream = stream
                        break
                
                if audio_stream is None:
                    print(f"📦 警告：音频文件无音频流 {audio_path}")
                    return None
                
                # 收集所有音频帧
                audio_data = []
                for frame in container.decode(audio_stream):
                    audio_data.append(frame.to_ndarray())
                
                if not audio_data:
                    print(f"📦 警告：音频文件无数据 {audio_path}")
                    return None
                
                # 拼接所有音频帧
                waveform = np.concatenate(audio_data, axis=1)
                
                # 获取采样率
                sample_rate = audio_stream.rate
                
                # 转换为 [1, channels, samples] 格式
                if waveform.ndim == 1:
                    waveform = waveform.reshape(1, 1, -1)
                elif waveform.ndim == 2:
                    waveform = waveform.reshape(1, waveform.shape[0], -1)
                
                # 转换为 torch tensor
                waveform_tensor = torch.from_numpy(waveform).float()
                
                return {
                    "waveform": waveform_tensor,
                    "sample_rate": sample_rate
                }
        except Exception as e:
            print(f"📦 警告：无法加载音频 {audio_path} - {str(e)}")
            return None
    
    def load_zip(self, zip_file, zip_path=""):
        """
        加载ZIP文件并分类提取文件
        
        Args:
            zip_file: ZIP文件名（来自ComfyUI输入文件夹）
            zip_path: ZIP文件完整路径（可选，优先使用）
            
        Returns:
            tuple: (图片列表[IMAGE], 文本列表[STRING], 视频列表[VIDEO], 音频列表[AUDIO], 文件列表[STRING])
        """
        # 获取ComfyUI默认输入文件夹路径
        input_dir = folder_paths.get_input_directory()
        
        # 确定ZIP文件路径：优先使用完整路径，否则使用选择文件名
        if zip_path and zip_path.strip():
            actual_zip_path = zip_path.strip()
        else:
            actual_zip_path = os.path.join(input_dir, zip_file)
        
        # 检查ZIP文件是否存在
        if not os.path.exists(actual_zip_path):
            error_msg = f"错误：ZIP文件不存在 - {actual_zip_path}"
            print(f"📦 {error_msg}")
            empty_image = torch.zeros(1, 64, 64, 3)
            empty_video = torch.zeros(1, 64, 64, 3)
            empty_audio = {"waveform": torch.zeros(1, 2), "sample_rate": 44100}
            file_list = "文件总数: 0\n图片数量: 0\n图片名称: \n文本数量: 0\n视频数量: 0\n音频数量: 0"
            return (empty_image, error_msg, empty_video, empty_audio, file_list)
        
        if not zipfile.is_zipfile(actual_zip_path):
            error_msg = f"错误：不是有效的ZIP文件 - {actual_zip_path}"
            print(f"📦 {error_msg}")
            empty_image = torch.zeros(1, 64, 64, 3)
            empty_video = torch.zeros(1, 64, 64, 3)
            empty_audio = {"waveform": torch.zeros(1, 2), "sample_rate": 44100}
            file_list = "文件总数: 0\n图片数量: 0\n图片名称: \n文本数量: 0\n视频数量: 0\n音频数量: 0"
            return (empty_image, error_msg, empty_video, empty_audio, file_list)
        
        # 创建临时目录用于解压
        temp_dir = tempfile.mkdtemp(prefix="comfyui_zip_")
        
        try:
            image_tensors = []
            image_names = []
            text_contents = []
            text_names = []
            video_tensors = []
            video_names = []
            audio_data = []
            audio_names = []
            
            with zipfile.ZipFile(actual_zip_path, 'r') as zip_ref:
                # 遍历ZIP中的所有文件
                for file_info in zip_ref.filelist:
                    # 跳过目录
                    if file_info.is_dir():
                        continue
                    
                    # 处理文件名编码（解决中文乱码问题）
                    filename = file_info.filename
                    try:
                        # 尝试将文件名从 UTF-8 解码为 GBK（处理中文文件名乱码）
                        filename = filename.encode('cp437').decode('gbk')
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        # 如果解码失败，使用原始文件名
                        pass
                    
                    _, ext = os.path.splitext(filename.lower())
                    
                    # 根据扩展名分类
                    if ext in self.IMAGE_EXTENSIONS:
                        # 解压并加载图片
                        extracted_path = zip_ref.extract(file_info, temp_dir)
                        try:
                            img_tensor = self.load_image(extracted_path)
                            image_tensors.append(img_tensor)
                            image_names.append(filename)
                        except Exception as e:
                            print(f"📦 警告：无法加载图片 {filename} - {str(e)}")
                        
                    elif ext in self.TEXT_EXTENSIONS:
                        # 解压并读取文本文件
                        extracted_path = zip_ref.extract(file_info, temp_dir)
                        try:
                            with open(extracted_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            text_contents.append(f"{filename}\n{content}")
                            text_names.append(filename)
                        except Exception as e:
                            print(f"📦 警告：无法读取文本 {filename} - {str(e)}")
                            # 尝试其他编码
                            try:
                                with open(extracted_path, 'r', encoding='gbk') as f:
                                    content = f.read()
                                text_contents.append(f"{filename}\n{content}")
                                text_names.append(filename)
                            except Exception as e2:
                                print(f"📦 警告：无法使用GBK编码读取 {filename} - {str(e2)}")
                        
                    elif ext in self.VIDEO_EXTENSIONS:
                        # 解压并加载视频文件
                        extracted_path = zip_ref.extract(file_info, temp_dir)
                        try:
                            video_tensor = self.load_video(extracted_path)
                            if video_tensor is not None:
                                video_tensors.append(video_tensor)
                                video_names.append(filename)
                        except Exception as e:
                            print(f"📦 警告：无法加载视频 {filename} - {str(e)}")
                        
                    elif ext in self.AUDIO_EXTENSIONS:
                        # 解压并加载音频文件
                        extracted_path = zip_ref.extract(file_info, temp_dir)
                        try:
                            audio_dict = self.load_audio(extracted_path)
                            if audio_dict is not None:
                                audio_data.append(audio_dict)
                                audio_names.append(filename)
                        except Exception as e:
                            print(f"📦 警告：无法加载音频 {filename} - {str(e)}")
            
            # 构造输出（列表形式）
            # 图片：返回列表（每个图片一个张量）
            if image_tensors:
                images_output = image_tensors
            else:
                images_output = []
            
            # 文本：返回列表（每个文本文件一个字符串）
            text_output = text_contents if text_contents else []
            
            # 视频：返回列表（每个视频一个张量）
            if video_tensors:
                video_output = video_tensors
            else:
                video_output = []
            
            # 音频：返回列表（每个音频一个字典）
            if audio_data:
                audio_output = audio_data
            else:
                audio_output = []
            
            total_count = len(image_tensors) + len(text_contents) + len(video_tensors) + len(audio_data)
            
            # 构造文件列表信息
            file_list = f"文件总数: {total_count}\n"
            file_list += f"图片数量: {len(image_tensors)}\n"
            file_list += f"图片名称: {', '.join(image_names) if image_names else '无'}\n"
            file_list += f"文本数量: {len(text_contents)}\n"
            file_list += f"文本名称: {', '.join(text_names) if text_names else '无'}\n"
            file_list += f"视频数量: {len(video_tensors)}\n"
            file_list += f"视频名称: {', '.join(video_names) if video_names else '无'}\n"
            file_list += f"音频数量: {len(audio_data)}\n"
            file_list += f"音频名称: {', '.join(audio_names) if audio_names else '无'}"
            
            # 输出统计信息
            print(f"📦 已加载ZIP文件: {os.path.basename(actual_zip_path)}")
            print(f"📦 图片: {len(image_tensors)} 个")
            print(f"📦 文本: {len(text_contents)} 个")
            print(f"📦 视频: {len(video_tensors)} 个")
            print(f"📦 音频: {len(audio_data)} 个")
            print(f"📦 总计: {total_count} 个文件")
            print(f"📦 解压目录: {temp_dir}")
            
            return (images_output, text_output, video_output, audio_output, file_list)
            
        except zipfile.BadZipFile as e:
            error_msg = f"错误：ZIP文件损坏 - {str(e)}"
            print(f"📦 {error_msg}")
            empty_image = torch.zeros(1, 64, 64, 3)
            empty_video = torch.zeros(1, 64, 64, 3)
            empty_audio = {"waveform": torch.zeros(1, 2), "sample_rate": 44100}
            file_list = "文件总数: 0\n图片数量: 0\n图片名称: \n文本数量: 0\n视频数量: 0\n音频数量: 0"
            return (empty_image, error_msg, empty_video, empty_audio, file_list)
        except Exception as e:
            error_msg = f"错误：解压ZIP文件失败 - {str(e)}"
            print(f"📦 {error_msg}")
            empty_image = torch.zeros(1, 64, 64, 3)
            empty_video = torch.zeros(1, 64, 64, 3)
            empty_audio = {"waveform": torch.zeros(1, 2), "sample_rate": 44100}
            file_list = "文件总数: 0\n图片数量: 0\n图片名称: \n文本数量: 0\n视频数量: 0\n音频数量: 0"
            return (empty_image, error_msg, empty_video, empty_audio, file_list)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "LoadZipNode": LoadZipNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadZipNode": "加载ZIP文件"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
