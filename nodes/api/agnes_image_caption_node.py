import requests
import json
import base64
import time
import numpy as np
from PIL import Image
from io import BytesIO


class AgnesImageCaptionNode:
    """
    Agnes AI 图像反推节点 - 使用视觉模型分析图像并生成描述
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {
                    "label": "图像",
                    "description": "要分析的图像"
                }),
                "prompt": ("STRING", {
                    "default": "详细描述这张图片的内容，包括主体、背景、颜色、风格等信息",
                    "multiline": True,
                    "label": "提示词",
                    "description": "用于图片描述的提示词"
                }),
                "model": (["agnes-2.0-flash", "agnes-2.5-flash", "agnes-2.5-pro-alpha"], {
                    "default": "agnes-2.0-flash",
                    "label": "模型",
                    "description": "选择要使用的视觉模型"
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
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "password": True,
                    "label": "API Key",
                    "description": "Agnes AI API Key"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("description",)
    FUNCTION = "generate_caption"
    CATEGORY = "❤️❤️❤️XnanTool/API/Agnes AI"
    DESCRIPTION = "Agnes AI 图像反推节点，使用视觉模型分析图像并生成描述。"

    def _image_to_base64(self, image_tensor):
        """
        将 ComfyUI 图像张量转换为 base64 字符串
        """
        # 将张量转换为 PIL 图像
        if len(image_tensor.shape) == 4:
            image_tensor = image_tensor.squeeze(0)
        
        if image_tensor.max() <= 1.0:
            image_np = (image_tensor.cpu().numpy() * 255).astype(np.uint8)
        else:
            image_np = image_tensor.cpu().numpy().astype(np.uint8)
        
        pil_image = Image.fromarray(image_np)
        
        # 转换为 JPEG 字节
        buffer = BytesIO()
        pil_image.save(buffer, format='JPEG', quality=85)
        img_bytes = buffer.getvalue()
        
        # 返回 base64 字符串
        return base64.b64encode(img_bytes).decode('utf-8')

    def generate_caption(self, image, prompt, model, seed, api_key=""):
        """
        调用 Agnes AI 视觉 API 生成图像描述
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("请填写 Agnes AI API Key")

        if not prompt or prompt.strip() == "":
            raise ValueError("请输入提示词")

        # 将图像转换为 base64
        image_b64 = self._image_to_base64(image)
        
        # 构造消息列表（包含图像）
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64}"
                    }
                }
            ]
        }]

        # 构造请求参数
        payload = {
            "model": model,
            "messages": messages,
        }

        # 发送请求（带重试机制）
        url = "https://apihub.agnes-ai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        max_retries = 3
        retry_delay = 5  # 秒
        
        try:
            for attempt in range(max_retries):
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=120)
                    response.raise_for_status()
                    result = response.json()
                    break
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 503 and attempt < max_retries - 1:
                        print(f"[Agnes图像反推] 服务暂时不可用，{retry_delay}秒后重试... ({attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    raise
            
            # 提取回复内容
            if "choices" in result and len(result["choices"]) > 0:
                description = result["choices"][0].get("message", {}).get("content", "")
                return (description,)
            else:
                raise ValueError(f"API 返回格式异常: {result}")

        except requests.exceptions.Timeout:
            raise Exception("请求超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"图像描述生成失败: {str(e)}")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "AgnesImageCaptionNode": AgnesImageCaptionNode,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "AgnesImageCaptionNode": "Agnes AI-图像反推",
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
