import requests
import base64
import io
import numpy as np
from PIL import Image
import torch


class AgnesTextToImageNode:
    """
    Agnes AI 文生图节点 - 支持 Agnes Image 2.0 Flash 和 2.1 Flash 模型
    """
    
    # 尺寸映射：尺寸名称 -> 基础像素值
    SIZE_MAP = {"自定义": 0, "1K": 1024, "2K": 2048, "4K": 4096}
    
    # 宽高比列表
    RATIOS = ["auto", "1:1", "2:3", "3:4", "4:5", "9:16", "9:21", "3:2", "4:3", "5:4", "16:9", "21:9"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "提示词",
                    "description": "图像生成的文本提示词"
                }),
                "model": (["agnes-image-2.0-flash", "agnes-image-2.1-flash"], {
                    "default": "agnes-image-2.1-flash",
                    "label": "模型",
                    "description": "选择要使用的图像模型"
                }),
                "ratio": (cls.RATIOS, {
                    "default": "1:1",
                    "label": "宽高比",
                    "description": "图像宽高比"
                }),
                "size": (list(cls.SIZE_MAP.keys()), {
                    "default": "1K",
                    "label": "尺寸",
                    "description": "基础尺寸档位"
                }),
                "custom_width": ("INT", {
                    "default": 1024,
                    "min": 256,
                    "max": 4096,
                    "step": 8,
                    "label": "自定义宽度",
                    "description": "自定义图像宽度（仅当尺寸选择'自定义'时生效）"
                }),
                "custom_height": ("INT", {
                    "default": 1024,
                    "min": 256,
                    "max": 4096,
                    "step": 8,
                    "label": "自定义高度",
                    "description": "自定义图像高度（仅当尺寸选择'自定义'时生效）"
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

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "status_info")
    FUNCTION = "generate_image"
    CATEGORY = "❤️❤️❤️XnanTool/API/Agnes AI"
    DESCRIPTION = "Agnes AI 文生图节点，支持 Agnes Image 2.0 Flash 和 2.1 Flash 模型。"

    def _resolve_size(self, size, ratio, custom_width, custom_height):
        """
        根据尺寸和宽高比计算实际尺寸
        """
        # 如果选择自定义，直接使用自定义宽高
        if size == "自定义":
            return max(64, custom_width // 8 * 8), max(64, custom_height // 8 * 8)
        
        base = self.SIZE_MAP[size]
        
        # 根据宽高比计算尺寸
        wr, hr = map(int, ratio.split(":"))
        if wr >= hr:
            w, h = base * wr // hr, base
        else:
            w, h = base, base * hr // wr
        return max(64, w // 8 * 8), max(64, h // 8 * 8)

    def generate_image(self, prompt, model, ratio, size, custom_width, custom_height, seed, api_key=""):
        """
        调用 Agnes AI 文生图 API
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("请填写 Agnes AI API Key")

        if not prompt or prompt.strip() == "":
            raise ValueError("请输入提示词")

        # 计算实际尺寸
        width, height = self._resolve_size(size, ratio, custom_width, custom_height)

        # 构造请求参数
        payload = {
            "model": model,
            "prompt": prompt,
            "size": f"{width}x{height}",
        }

        # 发送请求
        url = "https://apihub.agnes-ai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            result = response.json()

            # 提取生成的图像
            if "data" in result and len(result["data"]) > 0:
                image_data = result["data"][0]

                # API 返回 URL 格式
                if "url" in image_data:
                    # 下载图像
                    img_response = requests.get(image_data["url"], timeout=60)
                    img_response.raise_for_status()
                    img_bytes = img_response.content
                else:
                    raise ValueError(f"API 返回格式异常: {result}")

                # 将图像转换为 ComfyUI 格式
                img = Image.open(io.BytesIO(img_bytes))
                img = img.convert("RGB")
                img_array = np.array(img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_array).unsqueeze(0)

                status_info = f"图像生成成功 | 模型: {model} | 尺寸: {size}"
                return (img_tensor, status_info)
            else:
                raise ValueError(f"API 返回格式异常: {result}")

        except requests.exceptions.Timeout:
            raise Exception("请求超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"图像生成失败: {str(e)}")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "AgnesTextToImageNode": AgnesTextToImageNode,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "AgnesTextToImageNode": "Agnes AI-文生图",
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
