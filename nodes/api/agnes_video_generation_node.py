import requests
import time
import os
import folder_paths
import av
import numpy as np
from PIL import Image
import base64
import io


class VideoStream:
    """视频流对象 - 封装视频文件路径和元数据"""
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        self._width = None
        self._height = None
        self._has_audio = False
        self._read_metadata()

    def _read_metadata(self):
        """读取视频元数据"""
        try:
            with av.open(self.path) as container:
                for stream in container.streams:
                    if stream.type == 'video':
                        self._width = stream.width
                        self._height = stream.height
                    elif stream.type == 'audio':
                        self._has_audio = True
        except:
            self._width = 1920
            self._height = 1080

    def get_stream_source(self):
        return self.path

    def get_dimensions(self):
        """获取视频尺寸"""
        return (self._width, self._height)

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def has_audio(self):
        """检查是否包含音频"""
        return self._has_audio

    def save_to(self, output_path, format=None, codec=None, metadata=None):
        """保存视频到指定路径"""
        import shutil
        shutil.copy2(self.path, output_path)
        print(f"💾 视频已保存: {output_path}")


class AgnesVideoGenerationNode:
    """
    Agnes AI 视频生成节点 - 支持 Agnes Video V2.0 异步任务
    支持文生视频、图生视频、多图视频、关键帧动画
    """
    
    # 尺寸映射：尺寸名称 -> 基础像素值
    SIZE_MAP = {"480p": 480, "720p": 720, "1080p": 1080}
    
    # 宽高比列表
    RATIOS = ["auto", "16:9", "9:16", "1:1", "4:3", "3:4"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "提示词",
                    "description": "视频生成的文本提示词"
                }),
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "负面提示词",
                    "description": "描述不希望出现的内容（可选）"
                }),
                "mode": (["text-to-video", "image-to-video", "multi-image-video", "keyframe-animation"], {
                    "default": "text-to-video",
                    "label": "生成模式",
                    "description": "视频生成模式"
                }),
                "size": (list(cls.SIZE_MAP.keys()), {
                    "default": "720p",
                    "label": "尺寸",
                    "description": "视频尺寸"
                }),
                "ratio": (cls.RATIOS, {
                    "default": "16:9",
                    "label": "宽高比",
                    "description": "视频宽高比"
                }),
                "duration": ("FLOAT", {
                    "default": 5.0,
                    "min": 1.0,
                    "max": 30.0,
                    "step": 0.5,
                    "label": "时长(秒)",
                    "description": "视频时长（秒），将根据帧率自动计算帧数）"
                }),
                "frame_rate": ("INT", {
                    "default": 24,
                    "min": 1,
                    "max": 60,
                    "step": 1,
                    "label": "帧率",
                    "description": "视频帧率（FPS）"
                }),
                "poll_interval": ("INT", {
                    "default": 10,
                    "min": 5,
                    "max": 60,
                    "step": 1,
                    "label": "轮询间隔(秒)",
                    "description": "查询任务状态的间隔时间"
                }),
                "max_wait_time": ("INT", {
                    "default": 600,
                    "min": 60,
                    "max": 3600,
                    "step": 10,
                    "label": "最大等待时间(秒)",
                    "description": "最大等待时间，超时则放弃"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999999999,
                    "step": 1,
                    "label": "随机种子",
                    "description": "随机种子（0为随机）"
                }),
            },
            "optional": {
                "reference_image": ("IMAGE", {
                    "label": "参考图像",
                    "description": "图生视频/多图视频/关键帧动画的参考图像"
                }),
                "reference_image_2": ("IMAGE", {
                    "label": "参考图像2",
                    "description": "多图视频或关键帧动画的第二张参考图像"
                }),
                "num_inference_steps": ("INT", {
                    "default": 50,
                    "min": 10,
                    "max": 200,
                    "step": 1,
                    "label": "推理步数",
                    "description": "推理步数（可选）"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "password": True,
                    "label": "API Key",
                    "description": "Agnes AI API Key"
                }),
            }
        }

    RETURN_TYPES = ("VIDEO", "STRING", "STRING")
    RETURN_NAMES = ("video", "video_url", "task_info")
    FUNCTION = "generate_video"
    CATEGORY = "❤️❤️❤️XnanTool/API/Agnes AI"
    DESCRIPTION = "Agnes AI 视频生成节点，支持文生视频、图生视频、多图视频和关键帧动画。"

    def _resolve_size(self, size, ratio):
        """
        根据尺寸和宽高比计算实际尺寸
        """
        base = self.SIZE_MAP[size]
        
        # 根据宽高比计算尺寸
        wr, hr = map(int, ratio.split(":"))
        if wr >= hr:
            w, h = base * wr // hr, base
        else:
            w, h = base, base * hr // wr
        return max(64, w // 8 * 8), max(64, h // 8 * 8)

    def generate_video(self, prompt, api_key, mode, size, ratio, duration, frame_rate, poll_interval, max_wait_time, seed,
                       reference_image=None, reference_image_2=None, negative_prompt="", num_inference_steps=50):
        """
        调用 Agnes AI 视频生成 API（异步任务模式）
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("请填写 Agnes AI API Key")

        if not prompt or prompt.strip() == "":
            raise ValueError("请输入提示词")

        # 根据时长和帧率计算帧数（必须满足 8n+1）
        num_frames = int(duration * frame_rate)
        # 调整为最接近的 8n+1 格式
        num_frames = ((num_frames - 1) // 8) * 8 + 1
        if num_frames < 81:
            num_frames = 81
        elif num_frames > 441:
            num_frames = 441

        # 计算实际尺寸
        width, height = self._resolve_size(size, ratio)

        # 构造请求参数
        payload = {
            "model": "agnes-video-v2.0",
            "prompt": prompt.strip(),
            "width": width,
            "height": height,
            "num_frames": num_frames,
            "frame_rate": frame_rate,
        }
        if seed > 0:
            payload["seed"] = seed
        if negative_prompt and negative_prompt.strip():
            payload["negative_prompt"] = negative_prompt.strip()
        if num_inference_steps:
            payload["num_inference_steps"] = num_inference_steps

        # 根据模式处理图像
        if mode == "image-to-video" and reference_image is not None:
            # 单图生视频 - 使用 base64 格式
            img_b64 = self._image_to_base64(reference_image)
            payload["image"] = img_b64
        elif mode in ["multi-image-video", "keyframe-animation"]:
            # 多图视频或关键帧动画
            images = []
            if reference_image is not None:
                img_b64 = self._image_to_base64(reference_image)
                images.append(img_b64)
            if reference_image_2 is not None:
                img_b64_2 = self._image_to_base64(reference_image_2)
                images.append(img_b64_2)

            if images:
                payload["extra_body"] = {
                    "image": images,
                }
                if mode == "keyframe-animation":
                    payload["extra_body"]["mode"] = "keyframes"
                if mode == "multi-image-video":
                    payload["mode"] = "ti2vid"

        # 发送创建任务请求
        url = "https://apihub.agnes-ai.com/v1/videos"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            # 步骤1：创建视频任务（带重试机制）
            print(f"[Agnes视频] 正在创建视频任务...")
            max_retries = 3
            retry_delay = 5  # 秒
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=60)
                    response.raise_for_status()
                    task_result = response.json()
                    break
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 503 and attempt < max_retries - 1:
                        print(f"[Agnes视频] 服务暂时不可用，{retry_delay}秒后重试... ({attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    raise
            
            task_id = task_result.get("id")
            if not task_id:
                raise ValueError(f"创建任务失败，未返回任务ID: {task_result}")

            print(f"[Agnes视频] 任务已创建，任务ID: {task_id}")
            print(f"[Agnes视频] 任务状态: {task_result.get('status')}")

            # 步骤2：轮询查询任务状态
            video_url = None
            start_time = time.time()

            while True:
                elapsed = time.time() - start_time
                if elapsed > max_wait_time:
                    raise Exception(f"等待超时（{max_wait_time}秒），任务可能仍在队列中。任务ID: {task_id}")

                time.sleep(poll_interval)

                # 查询任务状态
                query_url = f"https://apihub.agnes-ai.com/v1/videos/{task_id}"
                query_response = requests.get(query_url, headers=headers, timeout=30)
                query_response.raise_for_status()
                status_result = query_response.json()

                status = status_result.get("status")
                progress = status_result.get("progress", 0)

                print(f"[Agnes视频] 状态: {status} | 进度: {progress}%")

                if status == "completed":
                    # 尝试多个可能的视频 URL 字段
                    video_url = (
                        status_result.get("video_url") or 
                        status_result.get("remixed_from_video_id") or
                        status_result.get("metadata", {}).get("url")
                    )
                    if not video_url:
                        raise ValueError(f"任务完成但未返回视频URL: {status_result}")
                    break
                elif status == "failed":
                    raise Exception(f"视频生成失败，任务ID: {task_id}")
                elif status == "queued":
                    print(f"[Agnes视频] 任务在队列中等待...")
                elif status == "in_progress":
                    print(f"[Agnes视频] 视频生成中... {progress}%")
                else:
                    print(f"[Agnes视频] 未知状态: {status}")

            # 步骤3：保存视频到输出目录
            print(f"[Agnes视频] 视频生成完成，正在下载并保存...")
            video_response = requests.get(video_url, timeout=300)
            video_response.raise_for_status()

            output_dir = folder_paths.get_output_directory()
            os.makedirs(output_dir, exist_ok=True)
            timestamp = int(time.time())
            video_filename = f"agnes_video_{timestamp}.mp4"
            video_path = os.path.join(output_dir, video_filename)

            with open(video_path, "wb") as f:
                f.write(video_response.content)

            # 构造任务信息
            # 计算耗时（通过 created_at 和 completed_at 时间戳）
            created_at = status_result.get('created_at', 0)
            completed_at = status_result.get('completed_at', 0)
            if created_at and completed_at:
                duration_seconds = completed_at - created_at
                duration_str = f"{duration_seconds}秒"
            else:
                duration_str = "unknown秒"
            
            task_info = (
                f"任务ID: {task_id}\n"
                f"状态: completed\n"
                f"尺寸: {status_result.get('size', 'unknown')}\n"
                f"时长: {status_result.get('seconds', 'unknown')}秒\n"
                f"耗时: {duration_str}"
            )

            return (VideoStream(video_path), video_url, task_info)

        except requests.exceptions.Timeout:
            raise Exception("请求超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"视频生成失败: {str(e)}")

    def _image_to_base64(self, image_tensor):
        """
        将 ComfyUI 图像张量转换为纯 base64 字符串
        """
        # 将张量转换为 PIL 图像
        img_tensor = image_tensor[0]
        i = 255.0 * img_tensor.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # 转换为 PNG 字节
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()

        # 返回纯 base64 字符串
        return base64.b64encode(img_bytes).decode('utf-8')


# 注册节点
NODE_CLASS_MAPPINGS = {
    "AgnesVideoGenerationNode": AgnesVideoGenerationNode,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "AgnesVideoGenerationNode": "Agnes AI-视频生成",
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
