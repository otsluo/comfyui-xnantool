import os
import cv2
import numpy as np
import torch
import folder_paths
import tempfile
import soundfile as sf

class ImagesToVideoNode:
    """
    图片转视频节点 - 将图片拉长成视频（重复图片帧）
    支持添加背景音乐
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "duration": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 60,
                    "step": 1,
                    "label": "时长(秒)",
                    "description": "视频时长（秒）"
                }),
                "fps": ("INT", {
                    "default": 30,
                    "min": 1,
                    "max": 60,
                    "step": 1,
                    "label": "帧率",
                    "description": "视频帧率（1-60帧/秒）"
                }),
                "output_resolution": (["original", "custom", "320x240", "640x480", "1280x720", "1920x1080", "2560x1440", "3840x2160"], {
                    "default": "original",
                    "label": "输出分辨率",
                    "description": "输出视频的分辨率（选择custom可自定义宽高）"
                }),
                "custom_width": ("INT", {
                    "default": 1920,
                    "min": 1,
                    "max": 7680,
                    "step": 1,
                    "label": "自定义宽度"
                }),
                "custom_height": ("INT", {
                    "default": 1080,
                    "min": 1,
                    "max": 4320,
                    "step": 1,
                    "label": "自定义高度"
                }),
                "output_filename": ("STRING", {
                    "default": "图片转视频",
                    "multiline": False,
                    "label": "输出文件名",
                    "description": "视频文件的输出名称（不含扩展名）"
                }),
                "output_path": ("STRING", {
                    "default": "video",
                    "multiline": False,
                    "label": "输出路径",
                    "description": "视频文件的输出目录（默认为video文件夹）"
                }),
                "conflict_mode": (["覆盖", "跳过", "数字后缀"], {
                    "default": "数字后缀",
                    "label": "文件名冲突处理",
                    "description": "当文件名已存在时的处理方式：覆盖、跳过或添加数字后缀"
                }),
                "pad_width": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 6,
                    "step": 1,
                    "label": "数字位数",
                    "description": "数字后缀的填充位数（例如：2位则显示为01, 02, 03）"
                }),
                "separator": ("STRING", {
                    "default": "_",
                    "multiline": False,
                    "label": "分隔符",
                    "description": "文件名和数字之间的分隔符（默认下划线_）"
                }),
            },
            "optional": {
                "image": ("IMAGE",),
                "image_frames": ("IMAGE",),
                "audio": ("AUDIO",),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("output_path", "info")
    FUNCTION = "convert_image_to_video"
    CATEGORY = "XnanTool/媒体处理"
    
    def convert_image_to_video(self, duration, fps, output_resolution, custom_width, custom_height, output_filename, output_path, conflict_mode="数字后缀", pad_width=2, separator="_", image=None, image_frames=None, audio=None):
        """
        将图片拉长成视频（支持单张图片或图片帧序列）
        
        Args:
            duration: 视频时长（秒）
            fps: 视频帧率
            output_resolution: 输出分辨率
            custom_width: 自定义宽度
            custom_height: 自定义高度
            output_filename: 输出文件名
            output_path: 输出路径
            conflict_mode: 文件名冲突处理方式（覆盖、跳过、数字后缀）
            pad_width: 数字后缀的填充位数
            separator: 文件名和数字之间的分隔符
            image: 单张输入图片（可选，与image_frames二选一）
            image_frames: 图片帧序列（可选，与image二选一）
            audio: 音频输入（可选）
            
        Returns:
            tuple: (输出文件路径, 信息)
        """
        try:
            # 检查是否提供了图片输入
            if image is None and image_frames is None:
                return ("", "错误：必须提供图片或图片帧序列")
            
            # 确定使用哪种输入
            if image is not None and image_frames is not None:
                print(f"[ImagesToVideoNode] 同时提供了image和image_frames，优先使用image_frames")
                use_image = False
            elif image is not None:
                print(f"[ImagesToVideoNode] 使用单张图片输入")
                use_image = True
            else:
                print(f"[ImagesToVideoNode] 使用图片帧序列输入")
                use_image = False
            
            image_input = image if use_image else image_frames
            # 获取输出目录
            output_dir = folder_paths.get_output_directory()
            
            # 处理输出路径
            if output_path and output_path.strip():
                output_dir_full = os.path.join(output_dir, output_path.strip())
            else:
                output_dir_full = os.path.join(output_dir, "video")
            
            # 构建输出文件路径
            if not output_filename.lower().endswith('.mp4'):
                output_filename += '.mp4'
            
            output_path_full = os.path.join(output_dir_full, output_filename)
            
            # 处理文件名冲突
            if conflict_mode == "跳过":
                if os.path.exists(output_path_full):
                    print(f"[ImagesToVideoNode] 检测到同名文件，已跳过: {os.path.basename(output_path_full)}")
                    return (output_path_full, f"文件已存在，已跳过: {output_path_full}")
            elif conflict_mode == "数字后缀":
                import re
                base_name, ext = os.path.splitext(output_filename)
                
                # 确保输出目录存在以便检查文件
                os.makedirs(output_dir_full, exist_ok=True)
                
                # 查找已存在的文件，找到最大的数字后缀
                counter = 1
                try:
                    files = os.listdir(output_dir_full)
                    max_counter = 0
                    
                    # 使用正则表达式匹配类似 "filename_01.ext" 的模式
                    pattern = re.compile(
                        re.escape(base_name) + 
                        re.escape(separator) + 
                        r'(\d{' + str(pad_width) + r'})' + 
                        re.escape(ext) + r'$'
                    )
                    
                    print(f"[ImagesToVideoNode] 当前目录: {output_dir_full}")
                    print(f"[ImagesToVideoNode] 基础文件名: {base_name}, 扩展名: {ext}, 分隔符: {separator}, 位数: {pad_width}")
                    print(f"[ImagesToVideoNode] 匹配模式: {pattern.pattern}")
                    print(f"[ImagesToVideoNode] 目录中的文件: {files}")
                    
                    for file in files:
                        match = pattern.match(file)
                        if match:
                            num = int(match.group(1))
                            print(f"[ImagesToVideoNode] 匹配文件: {file}, 数字: {num}")
                            max_counter = max(max_counter, num)
                        else:
                            print(f"[ImagesToVideoNode] 未匹配: {file}")
                    
                    print(f"[ImagesToVideoNode] 最大数字后缀: {max_counter}, 下一个计数器: {counter}")
                    counter = max_counter + 1
                except Exception as e:
                    print(f"[ImagesToVideoNode] 检查文件冲突时出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    counter = 1
                
                # 构建初始路径
                output_path_full = os.path.join(output_dir_full, output_filename)
                original_output_path = output_path_full
                
                # 如果文件已存在，使用计数器生成新文件名
                if os.path.exists(output_path_full):
                    while os.path.exists(output_path_full):
                        new_filename = f"{base_name}{separator}{str(counter).zfill(pad_width)}{ext}"
                        output_path_full = os.path.join(output_dir_full, new_filename)
                        counter += 1
                    
                    if original_output_path != output_path_full:
                        print(f"[ImagesToVideoNode] 检测到同名文件，已自动重命名为: {os.path.basename(output_path_full)}")
            # 如果是"覆盖"模式，直接使用原文件路径，会覆盖现有文件
            
            # 处理输入图片
            if use_image:
                # 处理单张图片
                if isinstance(image, torch.Tensor):
                    if image.dim() == 4:
                        # 批量图片，取第一张
                        image = image[0]
                    
                    if image.dim() == 3:
                        # 转换为numpy数组
                        image_np = image.cpu().numpy()
                        image_np = (image_np * 255).astype(np.uint8)
                        height, width, channels = image_np.shape
                        print(f"[ImagesToVideoNode] 原始图片尺寸: {width}x{height}, 通道数: {channels}")
                    else:
                        return ("", "错误：图片格式不正确")
                else:
                    return ("", "错误：输入不是有效的图片")
            else:
                # 处理图片帧序列
                if isinstance(image_frames, torch.Tensor):
                    if image_frames.dim() == 4:
                        # 图片帧序列 [B, H, W, C]
                        batch_size, height, width, channels = image_frames.shape
                        print(f"[ImagesToVideoNode] 图片帧序列数量: {batch_size}, 尺寸: {width}x{height}, 通道数: {channels}")
                        # 转换为numpy数组
                        image_frames_np = image_frames.cpu().numpy()
                        image_frames_np = (image_frames_np * 255).astype(np.uint8)
                    else:
                        return ("", "错误：图片帧序列格式不正确")
                else:
                    return ("", "错误：输入不是有效的图片帧序列")
            
            # 确定输出尺寸
            if output_resolution == "original":
                new_width = width
                new_height = height
            elif output_resolution == "custom":
                new_width = custom_width
                new_height = custom_height
            else:
                res_parts = output_resolution.split('x')
                new_width = int(res_parts[0])
                new_height = int(res_parts[1])
            
            print(f"[ImagesToVideoNode] 输出尺寸: {new_width}x{new_height}")
            print(f"[ImagesToVideoNode] 最终输出路径: {output_path_full}")
            
            # 创建视频写入对象
            # 使用 mp4v 编码器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path_full, fourcc, fps, (new_width, new_height))
            
            if not out.isOpened():
                return ("", "错误：无法创建视频文件")
            
            # 计算总帧数
            total_frames = duration * fps
            
            print(f"[ImagesToVideoNode] 总帧数: {total_frames}")
            
            if use_image:
                # 单张图片模式：重复使用同一张图片
                # 将图片调整到目标尺寸并写入
                for frame_idx in range(total_frames):
                    # 调整图片大小
                    if new_width != width or new_height != height:
                        frame = cv2.resize(image_np, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
                    else:
                        frame = image_np.copy()
                    
                    # OpenCV 使用 BGR 格式，需要转换
                    if frame.shape[2] == 3:
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    out.write(frame)
            else:
                # 图片帧序列模式：使用提供的帧序列
                # 如果帧序列数量不足，重复最后一帧
                # 如果帧序列数量过多，只使用前N帧
                actual_frame_count = min(batch_size, total_frames)
                print(f"[ImagesToVideoNode] 实际使用帧数: {actual_frame_count}")
                
                for frame_idx in range(actual_frame_count):
                    frame = image_frames_np[frame_idx]
                    
                    # 调整图片大小
                    if new_width != width or new_height != height:
                        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
                    
                    # OpenCV 使用 BGR 格式，需要转换
                    if frame.shape[2] == 3:
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    out.write(frame)
                
                # 如果帧序列不足，用最后一帧填充剩余帧
                if batch_size < total_frames:
                    remaining_frames = total_frames - batch_size
                    print(f"[ImagesToVideoNode] 帧序列不足，用最后一帧填充 {remaining_frames} 帧")
                    last_frame = image_frames_np[-1]
                    if new_width != width or new_height != height:
                        last_frame = cv2.resize(last_frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
                    if last_frame.shape[2] == 3:
                        last_frame = cv2.cvtColor(last_frame, cv2.COLOR_RGB2BGR)
                    
                    for _ in range(remaining_frames):
                        out.write(last_frame)
            
            out.release()
            print(f"[ImagesToVideoNode] 视频写入完成")
            
            # 如果有音频输入，合并音频
            if audio is not None:
                print(f"[ImagesToVideoNode] 开始合并音频")
                print(f"[ImagesToVideoNode] 音频数据类型: {type(audio)}")
                if isinstance(audio, dict):
                    print(f"[ImagesToVideoNode] 音频数据键: {audio.keys()}")
                    if 'waveform' in audio:
                        print(f"[ImagesToVideoNode] 音频波形形状: {audio['waveform'].shape}")
                    if 'sample_rate' in audio:
                        print(f"[ImagesToVideoNode] 音频采样率: {audio['sample_rate']}")
                output_path_with_audio = self.merge_audio_to_video(output_path_full, audio)
                if output_path_with_audio:
                    output_path_full = output_path_with_audio
                    print(f"[ImagesToVideoNode] 音频合并成功，最终输出: {output_path_full}")
                else:
                    print(f"[ImagesToVideoNode] 音频合并失败，视频将不含音频")
                    print(f"[ImagesToVideoNode] 原始视频路径: {output_path_full}")
            else:
                print(f"[ImagesToVideoNode] 未检测到音频输入，跳过音频合并")
            
            # 生成信息
            if use_image:
                info = f"图片转视频完成: {output_path_full}\n" \
                       f"原始尺寸: {width}x{height}, 输出尺寸: {new_width}x{new_height}\n" \
                       f"时长: {duration}秒, 帧率: {fps}fps, 总帧数: {total_frames}"
            else:
                info = f"图片帧序列转视频完成: {output_path_full}\n" \
                       f"帧序列数量: {batch_size}, 尺寸: {width}x{height}, 输出尺寸: {new_width}x{new_height}\n" \
                       f"时长: {duration}秒, 帧率: {fps}fps, 实际使用帧数: {actual_frame_count}"
            
            return (output_path_full, info)
            
        except Exception as e:
            error_msg = f"图片转视频过程中发生错误: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return ("", error_msg)
    
    def merge_audio_to_video(self, video_path, audio_data):
        """
        使用 FFmpeg 合并音频到视频
        
        Args:
            video_path: 视频文件路径
            audio_data: 音频数据（字典，包含 waveform 和 sample_rate）
            
        Returns:
            合并后的视频文件路径
        """
        print(f"[ImagesToVideoNode] 开始音频合并流程")
        print(f"[ImagesToVideoNode] 输入视频路径: {video_path}")
        print(f"[ImagesToVideoNode] 音频数据类型: {type(audio_data)}")
        
        try:
            import subprocess
            import shutil
            
            # 检查是否是字典格式的音频数据
            if isinstance(audio_data, dict):
                waveform = audio_data.get('waveform', None)
                sample_rate = audio_data.get('sample_rate', None)
                
                print(f"[ImagesToVideoNode] 音频数据格式: 字典")
                print(f"[ImagesToVideoNode] waveform 是否存在: {waveform is not None}")
                print(f"[ImagesToVideoNode] sample_rate 是否存在: {sample_rate is not None}")
                
                if waveform is None or sample_rate is None:
                    print(f"[ImagesToVideoNode] 音频数据格式不正确 - waveform: {waveform}, sample_rate: {sample_rate}")
                    return None
                
                # 将音频张量保存为临时 WAV 文件
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                    temp_audio_path = temp_audio.name
                
                print(f"[ImagesToVideoNode] 临时音频文件路径: {temp_audio_path}")
                
                # 转换音频数据为 numpy 数组
                print(f"[ImagesToVideoNode] 音频波形形状: {waveform.shape}")
                audio_np = waveform.squeeze().cpu().numpy()
                print(f"[ImagesToVideoNode] 转换后 numpy 数组形状: {audio_np.shape}")
                
                # 保存为 WAV 文件
                sf.write(temp_audio_path, audio_np.T, sample_rate)
                print(f"[ImagesToVideoNode] 临时音频文件保存成功: {temp_audio_path}")
            else:
                # 如果是字符串，直接使用
                print(f"[ImagesToVideoNode] 音频数据格式: 字符串路径")
                temp_audio_path = audio_data
                print(f"[ImagesToVideoNode] 音频文件路径: {temp_audio_path}")
            
            # 创建临时文件来存储合并后的视频
            base_name, ext = os.path.splitext(video_path)
            temp_video_path = f"{base_name}_temp_with_audio.mp4"
            print(f"[ImagesToVideoNode] 临时视频文件路径: {temp_video_path}")
            
            # 检查输入文件是否存在
            if not os.path.exists(video_path):
                print(f"[ImagesToVideoNode] 错误：视频文件不存在: {video_path}")
                return None
            if not os.path.exists(temp_audio_path):
                print(f"[ImagesToVideoNode] 错误：音频文件不存在: {temp_audio_path}")
                return None
            
            print(f"[ImagesToVideoNode] 视频文件大小: {os.path.getsize(video_path)} 字节")
            print(f"[ImagesToVideoNode] 音频文件大小: {os.path.getsize(temp_audio_path)} 字节")
            
            # 构建 FFmpeg 命令
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-i", temp_audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                "-shortest",
                "-y",
                temp_video_path
            ]
            
            print(f"[ImagesToVideoNode] FFmpeg 命令: {' '.join(cmd)}")
            
            # 执行 FFmpeg 命令
            print(f"[ImagesToVideoNode] 开始执行 FFmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            print(f"[ImagesToVideoNode] FFmpeg 执行完成")
            print(f"[ImagesToVideoNode] 返回码: {result.returncode}")
            if result.stdout:
                print(f"[ImagesToVideoNode] FFmpeg 标准输出: {result.stdout}")
            if result.stderr:
                print(f"[ImagesToVideoNode] FFmpeg 错误输出: {result.stderr}")
            
            # 清理临时音频文件
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                print(f"[ImagesToVideoNode] 已删除临时音频文件: {temp_audio_path}")
            
            if result.returncode != 0:
                print(f"[ImagesToVideoNode] FFmpeg 合并音频失败")
                print(f"[ImagesToVideoNode] 返回码: {result.returncode}")
                print(f"[ImagesToVideoNode] 错误信息: {result.stderr}")
                # 如果失败，删除临时文件
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
                    print(f"[ImagesToVideoNode] 已删除临时视频文件: {temp_video_path}")
                return None
            
            # 合并成功，替换原始视频文件
            print(f"[ImagesToVideoNode] FFmpeg 合并音频成功")
            print(f"[ImagesToVideoNode] 移动临时文件到: {video_path}")
            shutil.move(temp_video_path, video_path)
            print(f"[ImagesToVideoNode] 音频合并成功: {video_path}")
            return video_path
            
        except FileNotFoundError as e:
            print(f"[ImagesToVideoNode] FFmpeg 未找到，跳过音频合并")
            print(f"[ImagesToVideoNode] 错误: {str(e)}")
            return None
        except subprocess.TimeoutExpired:
            print(f"[ImagesToVideoNode] FFmpeg 合并音频超时")
            return None
        except Exception as e:
            print(f"[ImagesToVideoNode] 合并音频时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


# 注册节点
NODE_CLASS_MAPPINGS = {
    "ImagesToVideoNode": ImagesToVideoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagesToVideoNode": "图片转视频",
}
