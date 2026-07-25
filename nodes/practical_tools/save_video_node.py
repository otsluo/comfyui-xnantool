import folder_paths
import os
import av
import numpy as np
import torch
from datetime import datetime
import uuid
import platform
import random
import string
from fractions import Fraction

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
                "output_path": ("STRING", {"default": "video", "multiline": False, "placeholder": "留空使用默认输出路径"}),
                "filename_prefix": ("STRING", {"default": "视频"}),
                "fps": (["自动", 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 25, 30, 48, 50, 60], {"default": "自动"}),
                "video_format": (["mp4", "avi", "mov", "mkv"], {"default": "mp4"}),
                "codec": (["自动", "libx264", "libx265", "mpeg4", "vp9"], {"default": "自动"}),
                "preset": (["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"], {"default": "fast"}),
                "crf": (["自动", 0, 5, 10, 15, 18, 20, 23, 25, 28, 30, 35, 40, 45, 51], {"default": "自动"}),
                "audio_sample_rate": (["自动", 8000, 16000, 22050, 32000, 44100, 48000, 96000], {"default": "自动"}),
                "audio_bitrate": (["自动", "64k", "128k", "192k", "256k", "320k"], {"default": "自动"}),
            },
            "optional": {
                "images": ("IMAGE",),
                "video": ("VIDEO",),
                "audio": ("AUDIO",),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("保存信息",)
    OUTPUT_NODE = True
    FUNCTION = "save_video"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    
    def save_video(self, filename_prefix="视频", fps="自动", video_format="mp4", codec="自动", preset="fast", crf="自动", audio_sample_rate="自动", audio_bitrate="自动", images=None, video=None, audio=None, output_path=""):
        """将图像序列保存为视频文件"""
        import sys
        
        # 检查是否至少有一个输入
        if images is None and video is None:
            return {"result": ("",), "ui": {"text": "错误: 请至少提供图像序列或视频输入"}}
        
        # 解析路径中的变量
        output_path = self._parse_path_variables(output_path)
        filename_prefix = self._parse_path_variables(filename_prefix)
        
        # 确定输出路径
        if output_path.strip() != "":
            if os.path.isabs(output_path):
                full_output_dir = output_path
            else:
                full_output_dir = os.path.join(self.output_dir, output_path)
        else:
            full_output_dir = self.output_dir
        
        # 创建输出目录（如果不存在）
        if not os.path.exists(full_output_dir):
            os.makedirs(full_output_dir, exist_ok=True)
        
        # 处理输入源
        image_list = None
        width = None
        height = None
        video_fps = None
        original_video_path = None
        
        if images is not None:
            # 使用图像序列
            if len(images) == 0:
                return {"result": ("",), "ui": {"text": "错误: 图像序列为空"}}
            img_shape = images[0].shape
            height, width = img_shape[0], img_shape[1]
            image_list = images
            print(f"🎬 使用图像序列: {len(images)} 张, 尺寸: {width}x{height}")
        elif video is not None:
            # 使用视频输入
            print(f"🎬 视频输入类型: {type(video)}")
            
            # 获取视频文件路径
            video_path = None
            if hasattr(video, 'get_stream_source'):
                try:
                    stream_source = video.get_stream_source()
                    if stream_source and isinstance(stream_source, str):
                        video_path = stream_source
                        print(f"🎬 通过 get_stream_source 获取路径: {video_path}")
                except Exception as e:
                    print(f"🎬 get_stream_source 失败: {e}")
            
            if not video_path and hasattr(video, '_VideoFromFile__file'):
                file_obj = getattr(video, '_VideoFromFile__file')
                if hasattr(file_obj, 'name'):
                    video_path = file_obj.name
                elif isinstance(file_obj, str):
                    video_path = file_obj
                print(f"🎬 通过 __file 获取路径: {video_path}")
            
            if video_path and os.path.exists(video_path):
                original_video_path = video_path
                print(f"🎬 视频路径: {video_path}")
                
                # 使用 av 库读取视频
                with av.open(video_path) as container:
                    video_stream = container.streams.video[0]
                    width = video_stream.width
                    height = video_stream.height
                    video_fps = float(video_stream.base_rate)
                    total_frames = video_stream.frames
                    
                    print(f"🎬 视频信息: {total_frames}帧, {video_fps}fps, {width}x{height}")
                    
                    # 自动帧率：使用视频原始帧率
                    if fps == "自动":
                        fps = video_fps
                        print(f"🎬 使用视频原始帧率: {fps} fps")
                    
                    # 读取所有帧
                    image_list = []
                    for frame in container.decode(video=0):
                        # 转换为 RGB numpy 数组
                        img_rgb = frame.to_ndarray(format='rgb24')
                        # 转换为 tensor
                        frame_tensor = torch.from_numpy(img_rgb.astype(np.float32) / 255.0).unsqueeze(0)
                        image_list.append(frame_tensor)
                    
                    print(f"🎬 成功读取 {len(image_list)} 帧")
                    
            elif video_path:
                return {"result": ("",), "ui": {"text": f"错误: 视频文件不存在: {video_path}"}}
            else:
                return {"result": ("",), "ui": {"text": "错误: 无法从视频输入中获取文件路径"}}
        else:
            return {"result": ("",), "ui": {"text": "错误: 请至少提供图像序列或视频输入"}}
        
        # 检查image_list
        if image_list is None or len(image_list) == 0:
            return {"result": ("",), "ui": {"text": "错误: 没有可用的图像数据"}}
        
        # 自动帧率
        if fps == "自动":
            fps = max(1, min(len(image_list), 30))
            print(f"🎬 自动帧率: {fps} fps")
        
        print(f"🎬 最终处理: {len(image_list)} 帧, 尺寸: {width}x{height}")
        
        # 生成文件名
        counter = 1
        while True:
            output_filename = f"{filename_prefix}_{counter:05d}.{video_format}"
            
            if sys.platform.startswith('win'):
                fs_encoding = sys.getfilesystemencoding()
                if fs_encoding.lower() in ['utf-8', 'utf8']:
                    safe_filename = output_filename
                else:
                    try:
                        safe_filename = output_filename.encode('utf-8').decode('utf-8')
                    except UnicodeEncodeError:
                        safe_filename = f"video_{counter:05d}.{video_format}"
            else:
                safe_filename = output_filename
            
            file_path = os.path.join(full_output_dir, safe_filename)
            if not os.path.exists(file_path):
                break
            counter += 1
        
        # 自动编码器
        if codec == "自动":
            codec_map = {
                "mp4": "libx264",
                "avi": "mpeg4",
                "mov": "libx264",
                "mkv": "libx264"
            }
            codec = codec_map.get(video_format, "libx264")
            print(f"🎬 自动编码器: {codec}")
        
        # 使用 av 库编码视频（与 ComfyUI 官方一致）
        print(f"🎬 使用 av 库编码: {codec}, 帧率: {fps}, 尺寸: {width}x{height}")
        
        container = av.open(file_path, mode='w')
        
        # 创建视频流
        stream = container.add_stream(codec, rate=Fraction(round(fps * 1000), 1000))
        stream.width = width
        stream.height = height
        stream.pix_fmt = "yuv420p"
        
        # 设置编码参数
        if crf == "自动":
            crf_value = 23
        else:
            crf_value = int(crf)
        
        if codec in ["libx264", "libx265", "h264"]:
            stream.options = {'preset': preset, 'crf': str(crf_value)}
            print(f"🎬 编码参数: preset={preset}, crf={crf_value}")
        
        # 写入帧
        frame_count = 0
        for img_tensor in image_list:
            # 将tensor转换为 numpy 数组
            img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
            
            # 去掉batch维度
            if len(img_np.shape) == 4:
                img_np = img_np[0]
            elif len(img_np.shape) == 3 and img_np.shape[0] == 1:
                img_np = img_np[0]
            
            # 确保是3通道图像
            if len(img_np.shape) == 2:
                img_rgb = np.stack([img_np] * 3, axis=-1)
            elif img_np.shape[2] == 4:
                img_rgb = img_np[:, :, :3]
            else:
                img_rgb = img_np
            
            # 检查尺寸
            if img_rgb.shape[1] != width or img_rgb.shape[0] != height:
                import cv2
                img_rgb = cv2.resize(img_rgb, (width, height))
            
            # 创建 VideoFrame
            frame = av.VideoFrame.from_ndarray(img_rgb, format='rgb24')
            
            # 编码并写入
            for packet in stream.encode(frame):
                container.mux(packet)
            
            frame_count += 1
            if frame_count % 50 == 0:
                print(f"🎬 已写入 {frame_count}/{len(image_list)} 帧")
        
        # 刷新编码器缓冲区
        for packet in stream.encode():
            container.mux(packet)
        
        container.close()
        print(f"🎬 视频编码完成: {frame_count} 帧")
        
        # 处理音频合并
        audio_source = None
        audio_type = None
        
        if audio is not None:
            audio_source = audio
            audio_type = "外部音频"
        elif original_video_path and os.path.exists(original_video_path):
            # 检查原始视频是否有音频
            try:
                with av.open(original_video_path) as src_container:
                    audio_streams = [s for s in src_container.streams if s.type == 'audio']
                    if audio_streams:
                        audio_source = original_video_path
                        audio_type = "原始视频音频"
                        print(f"🎬 检测到原始视频有音频流")
            except Exception as e:
                print(f"🎬 检查音频流失败: {e}")
        
        if audio_source:
            try:
                temp_video_path = file_path.replace(f".{video_format}", f"_temp_with_audio.{video_format}")
                
                if audio_type == "原始视频音频":
                    # 从原始视频复制音频流
                    with av.open(original_video_path) as src_container:
                        audio_streams = [s for s in src_container.streams if s.type == 'audio']
                        
                        if audio_streams:
                            out_container = av.open(temp_video_path, mode='w', options={'movflags': 'use_metadata_tags'})
                            
                            out_video = out_container.add_stream('h264', rate=Fraction(round(fps * 1000), 1000))
                            out_video.width = width
                            out_video.height = height
                            out_video.pix_fmt = 'yuv420p'
                            
                            if crf == "自动":
                                crf_value = 23
                            else:
                                crf_value = int(crf)
                            out_video.options = {'preset': preset, 'crf': str(crf_value)}
                            
                            audio_stream = audio_streams[0]
                            out_audio = out_container.add_stream_from_template(template=audio_stream)
                            
                            for img_tensor in image_list:
                                img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
                                if len(img_np.shape) == 4:
                                    img_np = img_np[0]
                                elif len(img_np.shape) == 3 and img_np.shape[0] == 1:
                                    img_np = img_np[0]
                                
                                if len(img_np.shape) == 2:
                                    img_rgb = np.stack([img_np] * 3, axis=-1)
                                elif img_np.shape[2] == 4:
                                    img_rgb = img_np[:, :, :3]
                                else:
                                    img_rgb = img_np
                                
                                if img_rgb.shape[1] != width or img_rgb.shape[0] != height:
                                    import cv2
                                    img_rgb = cv2.resize(img_rgb, (width, height))
                                
                                frame = av.VideoFrame.from_ndarray(img_rgb, format='rgb24')
                                for packet in out_video.encode(frame):
                                    out_container.mux(packet)
                            
                            for packet in out_video.encode():
                                out_container.mux(packet)
                            
                            for packet in src_container.demux(audio_stream):
                                if packet.dts is None:
                                    continue
                                packet.stream = out_audio
                                out_container.mux(packet)
                            
                            out_container.close()
                            
                            import shutil
                            shutil.move(temp_video_path, file_path)
                            message = f"视频已保存（含{audio_type}）: {file_path}"
                            print(f"🎬 {message}")
                        else:
                            message = f"视频已保存: {file_path}"
                elif audio_type == "外部音频":
                    # 处理外部音频输入（waveform + sample_rate）
                    import math
                    
                    waveform = audio_source.get('waveform', None)
                    sample_rate = audio_source.get('sample_rate', None)
                    
                    if waveform is not None and sample_rate is not None:
                        # 确定输出采样率
                        if audio_sample_rate == "自动":
                            output_sample_rate = sample_rate
                        else:
                            output_sample_rate = int(audio_sample_rate)
                        
                        print(f"🎬 外部音频: 原始采样率={sample_rate}, 输出采样率={output_sample_rate}")
                        
                        # 如果需要重采样
                        if output_sample_rate != sample_rate:
                            try:
                                import torchaudio
                                waveform = torchaudio.functional.resample(waveform, sample_rate, output_sample_rate)
                                print(f"🎬 音频重采样完成: {sample_rate} -> {output_sample_rate}")
                            except ImportError:
                                print(f"🎬 警告: torchaudio 不可用，使用原始采样率 {sample_rate}")
                                output_sample_rate = sample_rate
                        else:
                            output_sample_rate = sample_rate
                        
                        out_container = av.open(temp_video_path, mode='w', options={'movflags': 'use_metadata_tags'})
                        
                        out_video = out_container.add_stream('h264', rate=Fraction(round(fps * 1000), 1000))
                        out_video.width = width
                        out_video.height = height
                        out_video.pix_fmt = 'yuv420p'
                        
                        if crf == "自动":
                            crf_value = 23
                        else:
                            crf_value = int(crf)
                        out_video.options = {'preset': preset, 'crf': str(crf_value)}
                        
                        # 创建音频流
                        audio_channels = waveform.shape[1] if len(waveform.shape) > 1 else 1
                        layout = 'mono' if audio_channels == 1 else 'stereo'
                        out_audio = out_container.add_stream('aac', rate=output_sample_rate, layout=layout)
                        
                        # 设置音频比特率
                        if audio_bitrate == "自动":
                            out_audio.bit_rate = 128000
                        else:
                            out_audio.bit_rate = int(audio_bitrate.replace('k', '000'))
                        print(f"🎬 音频比特率: {out_audio.bit_rate // 1000}k")
                        
                        # 写入视频帧
                        for img_tensor in image_list:
                            img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
                            if len(img_np.shape) == 4:
                                img_np = img_np[0]
                            elif len(img_np.shape) == 3 and img_np.shape[0] == 1:
                                img_np = img_np[0]
                            
                            if len(img_np.shape) == 2:
                                img_rgb = np.stack([img_np] * 3, axis=-1)
                            elif img_np.shape[2] == 4:
                                img_rgb = img_np[:, :, :3]
                            else:
                                img_rgb = img_np
                            
                            if img_rgb.shape[1] != width or img_rgb.shape[0] != height:
                                import cv2
                                img_rgb = cv2.resize(img_rgb, (width, height))
                            
                            frame = av.VideoFrame.from_ndarray(img_rgb, format='rgb24')
                            for packet in out_video.encode(frame):
                                out_container.mux(packet)
                        
                        for packet in out_video.encode():
                            out_container.mux(packet)
                        
                        # 写入音频
                        # waveform shape: [batch, channels, samples]
                        # 取第一个batch
                        if len(waveform.shape) == 3:
                            waveform = waveform[0]
                        
                        # 计算视频总时长（秒）
                        video_duration = len(image_list) / fps
                        print(f"🎬 视频时长: {video_duration:.2f}秒")
                        
                        # 计算音频总样本数
                        audio_samples = waveform.shape[-1]
                        audio_duration = audio_samples / output_sample_rate
                        print(f"🎬 音频时长: {audio_duration:.2f}秒")
                        
                        # 如果音频超过视频长度，裁剪音频
                        if audio_duration > video_duration:
                            max_samples = int(video_duration * output_sample_rate)
                            waveform = waveform[:, :max_samples]
                            print(f"🎬 裁剪音频到视频长度: {max_samples} 样本")
                        
                        # 转换为 numpy
                        waveform_np = waveform.float().cpu().contiguous().numpy()
                        
                        # 创建音频帧
                        audio_frame = av.AudioFrame.from_ndarray(waveform_np, format='fltp', layout=layout)
                        audio_frame.sample_rate = output_sample_rate
                        audio_frame.pts = 0
                        
                        for packet in out_audio.encode(audio_frame):
                            out_container.mux(packet)
                        
                        # 刷新音频编码器
                        for packet in out_audio.encode():
                            out_container.mux(packet)
                        
                        out_container.close()
                        
                        import shutil
                        shutil.move(temp_video_path, file_path)
                        message = f"视频已保存（含{audio_type}）: {file_path}"
                        print(f"🎬 {message}")
                    else:
                        message = f"视频已保存（音频数据无效）: {file_path}"
                        print(f"🎬 {message}")
                else:
                    message = f"视频已保存: {file_path}"
            except Exception as e:
                import traceback
                message = f"视频已保存（音频合并出错）: {file_path}\n错误: {str(e)}"
                print(f"🎬 {message}")
                print(f"🎬 错误详情: {traceback.format_exc()}")
        else:
            message = f"视频已保存: {file_path}"
        
        with av.open(file_path) as container:
            video_stream = None
            audio_stream = None
            
            for stream in container.streams:
                if stream.type == 'video' and video_stream is None:
                    video_stream = stream
                elif stream.type == 'audio' and audio_stream is None:
                    audio_stream = stream
            
            if video_stream:
                width = video_stream.width
                height = video_stream.height
                fps = float(video_stream.average_rate)
                
                frame_count = 0
                for frame in container.decode(video_stream):
                    frame_count += 1
                
                duration = frame_count / fps if fps > 0 else 0
                
                has_audio = "是" if audio_stream else "否"
                audio_info = ""
                if audio_stream:
                    audio_bitrate_display = ""
                    if audio_stream.bit_rate:
                        audio_bitrate_display = f", 比特率={audio_stream.bit_rate // 1000}k"
                    audio_info = f", 采样率={audio_stream.rate}Hz, 声道={audio_stream.channels}{audio_bitrate_display}"
                
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                filename = os.path.basename(file_path)
                
                # 获取编码参数
                crf_display = f"{crf_value}" if crf != "自动" else "自动(23)"
                
                info_text = (
                    f"✅ {message}\n\n"
                    f"📄 文件名: {filename}\n"
                    f"📐 尺寸: {width}x{height}\n"
                    f"🎞️ 帧率: {fps:.2f} fps\n"
                    f"🖼️ 帧数: {frame_count}\n"
                    f"⏱️ 时长: {duration:.2f} 秒\n"
                    f"🔊 音频: {has_audio}{audio_info}\n"
                    f"💾 大小: {file_size:.2f} MB\n"
                    f"🎬 编码: {codec}\n"
                    f"📊 CRF质量: {crf_display}\n"
                    f"⚡ 编码预设: {preset}"
                )
            else:
                info_text = f"✅ {message}\n\n⚠️ 视频中无视频流"
        
        file_dir = os.path.dirname(file_path)
        try:
            rel_path = os.path.relpath(file_dir, self.output_dir)
        except ValueError:
            rel_path = file_dir
        
        result = {
            "filename": os.path.basename(file_path),
            "subfolder": rel_path,
            "type": "output"
        }
        
        print(f"🎬 {message}")
        print(f"📊 视频信息:\n{info_text}")
        
        return {
            "result": (info_text,), 
            "ui": {
                "text": info_text,
                "images": [result], 
                "animated": (True,)
            }
        }
    
    def _parse_path_variables(self, path):
        """解析路径中的日期变量"""
        if not path:
            return path
        
        now = datetime.now()
        
        variables = {
            '%date:yyyyMMdd%': now.strftime('%Y%m%d'),
            '%date:yyyy-MM-dd%': now.strftime('%Y-%m-%d'),
            '%date:yyyy/MM/dd%': now.strftime('%Y/%m/%d'),
            '%date:yyMMdd%': now.strftime('%y%m%d'),
            '%date:MMdd%': now.strftime('%m%d'),
            '%date:MM-dd%': now.strftime('%m-%d'),
            '%date:hhmm%': now.strftime('%H%M'),
            '%date:hh-mm%': now.strftime('%H-%M'),
            '%date:yyyyMMddHHmmss%': now.strftime('%Y%m%d%H%M%S'),
            '%date:yyyy-MM-dd HH:mm:ss%': now.strftime('%Y-%m-%d %H:%M:%S'),
            '%time:HHmmss%': now.strftime('%H%M%S'),
            '%time:HH-mm-ss%': now.strftime('%H-%M-%S'),
            '%time:HHmm%': now.strftime('%H%M'),
            '%time:HH-mm%': now.strftime('%H-%M'),
            '%time:HHmmssfff%': now.strftime('%H%M%S') + f'{now.microsecond // 1000:03d}',
            '%year%': now.strftime('%Y'),
            '%month%': now.strftime('%m'),
            '%day%': now.strftime('%d'),
            '%hour%': now.strftime('%H'),
            '%minute%': now.strftime('%M'),
            '%second%': now.strftime('%S'),
            '%millisecond%': str(now.microsecond // 1000).zfill(3),
            '%weekday:name%': now.strftime('%A'),
            '%weekday:name:cn%': ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][now.weekday()],
            '%weekday:num%': str(now.weekday() + 1),
            '%week:num%': str(now.isocalendar()[1]).zfill(2),
            '%yearweek%': now.strftime('%Y') + str(now.isocalendar()[1]).zfill(2),
            '%yearday%': str(now.timetuple().tm_yday).zfill(3),
            '%timestamp%': str(int(now.timestamp())),
            '%timestamp:ms%': str(int(now.timestamp() * 1000)),
            '%random:4%': ''.join(random.choices(string.digits, k=4)),
            '%random:6%': ''.join(random.choices(string.digits, k=6)),
            '%random:8%': ''.join(random.choices(string.digits, k=8)),
            '%random:letter:4%': ''.join(random.choices(string.ascii_lowercase, k=4)),
            '%random:letter:6%': ''.join(random.choices(string.ascii_lowercase, k=6)),
            '%random:alnum:6%': ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
            '%random:alnum:8%': ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)),
            '%uuid%': str(uuid.uuid4()),
            '%uuid:short%': str(uuid.uuid4())[:8],
            '%computer%': platform.node(),
            '%user%': platform.user() if hasattr(platform, 'user') else os.environ.get('USERNAME', os.environ.get('USER', 'unknown')),
        }
        
        for var, value in variables.items():
            path = path.replace(var, value)
        
        return path

# 注册节点
NODE_CLASS_MAPPINGS = {
    "SaveVideoNode": SaveVideoNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveVideoNode": "保存视频"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
