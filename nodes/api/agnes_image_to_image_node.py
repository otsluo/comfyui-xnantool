import requests
import io
import base64
import numpy as np
from PIL import Image
import torch


class AgnesImageToImageNode:
    """
    Agnes AI 图生图节点 - 支持 Agnes Image 2.0 Flash 和 2.1 Flash 模型
    """
    
    # 尺寸映射：尺寸名称 -> 基础像素值
    SIZE_MAP = {"1K": 1024, "2K": 2048, "4K": 4096}
    
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
                    "description": "图像生成的文本提示词（有图片输入时可为空）"
                }),
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "负面提示词",
                    "description": "描述不希望出现的内容（可选）"
                }),
                "model": (["agnes-image-2.0-flash", "agnes-image-2.1-flash"], {
                    "default": "agnes-image-2.1-flash",
                    "label": "模型",
                    "description": "选择要使用的图像模型"
                }),
                "size": (list(cls.SIZE_MAP.keys()), {
                    "default": "1K",
                    "label": "尺寸",
                    "description": "生成图像的尺寸（1K=1024px, 2K=2048px, 4K=4096px）"
                }),
                "ratio": (cls.RATIOS, {
                    "default": "auto",
                    "label": "宽高比",
                    "description": "生成图像的宽高比（auto 时根据输入图像自动计算）"
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
                    "label": "参考图像1",
                    "description": "作为参考的输入图像（支持IMAGE类型）"
                }),
                "reference_image_2": ("IMAGE", {
                    "label": "参考图像2",
                    "description": "第二张参考图像（可选）"
                }),
                "reference_image_3": ("IMAGE", {
                    "label": "参考图像3",
                    "description": "第三张参考图像（可选）"
                }),
                "reference_image_4": ("IMAGE", {
                    "label": "参考图像4",
                    "description": "第四张参考图像（可选）"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "password": True,
                    "label": "Agnes API Key",
                    "description": "Agnes AI API Key"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "status_info")
    FUNCTION = "generate_image"
    CATEGORY = "❤️❤️❤️XnanTool/API/Agnes AI"
    DESCRIPTION = "Agnes AI 图生图节点，支持 Agnes Image 2.0 Flash 和 2.1 Flash 模型。"

    def _image_to_base64(self, image_tensor):
        """
        将 ComfyUI 图像张量转换为纯 base64 字符串（不含 data URI 前缀）
        """
        # 将张量转换为 PIL 图像
        img_tensor = image_tensor[0]
        i = 255.0 * img_tensor.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # 转换为 PNG 字节
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()

        # 返回纯 base64 字符串（参考项目格式）
        return base64.b64encode(img_bytes).decode('utf-8')

    def _resolve_size(self, size, ratio, img_shape=None):
        """
        根据尺寸和宽高比计算实际尺寸
        参考: ComfyUI-Agnes-AI/agnes_api.py 中的 resolve_size 函数
        """
        base = self.SIZE_MAP[size]
        
        # auto 模式：根据输入图像尺寸计算
        if ratio == "auto" and img_shape is not None:
            _, h, w, _ = img_shape
            if w >= h:
                out_w, out_h = base * w // h, base
            else:
                out_w, out_h = base, base * h // w
            return f"{max(64, out_w // 8 * 8)}x{max(64, out_h // 8 * 8)}"
        
        # auto 模式但没有输入图像，默认 1:1
        if ratio == "auto":
            ratio = "1:1"
        
        # 根据宽高比计算尺寸
        wr, hr = map(int, ratio.split(":"))
        if wr >= hr:
            w, h = base * wr // hr, base
        else:
            w, h = base, base * hr // wr
        return f"{max(64, w // 8 * 8)}x{max(64, h // 8 * 8)}"

    def generate_image(self, prompt, negative_prompt, model, size, ratio, seed,
                       reference_image=None, reference_image_2=None,
                       reference_image_3=None, reference_image_4=None,
                       api_key=""):
        """
        调用 Agnes AI 图生图 API
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("请填写 Agnes AI API Key")

        # 收集所有图像引用
        image_refs = []
        first_image_shape = None

        # 使用 IMAGE 类型（转换为纯 base64）
        for ref in (reference_image, reference_image_2, reference_image_3, reference_image_4):
            if ref is not None:
                if first_image_shape is None:
                    first_image_shape = ref.shape
                image_refs.append(self._image_to_base64(ref))

        if not image_refs:
            raise ValueError("请至少提供一张参考图像")

        # 有图片输入时提示词可为空，使用默认提示词
        final_prompt = prompt.strip() if prompt and prompt.strip() else \
            "Merge these images into one cohesive composition"

        # 计算实际尺寸
        size = self._resolve_size(size, ratio, first_image_shape)

        # 构造请求参数
        payload = {
            "model": model,
            "prompt": final_prompt,
            "size": size,
        }
        if seed > 0:
            payload["seed"] = seed
        if negative_prompt and negative_prompt.strip():
            payload["negative_prompt"] = negative_prompt.strip()

        # 添加图像到 extra_body 中（使用 b64_json 格式，参考项目一致）
        payload["extra_body"] = {
            "image": image_refs,
            "response_format": "b64_json"
        }

        # 发送请求
        url = "https://apihub.agnes-ai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()

            # 提取生成的图像
            if "data" in result and len(result["data"]) > 0:
                image_data = result["data"][0]

                if "b64_json" in image_data:
                    # 返回 base64 格式，直接解码
                    img_bytes = base64.b64decode(image_data["b64_json"])
                    img = Image.open(io.BytesIO(img_bytes))
                elif "url" in image_data:
                    # 返回 URL 格式，下载图像
                    img_response = requests.get(image_data["url"], timeout=120)
                    img_response.raise_for_status()
                    img = Image.open(io.BytesIO(img_response.content))
                else:
                    raise ValueError(f"API 返回格式异常: {result}")

                # 将图像转换为 ComfyUI 格式
                img = img.convert("RGB")
                img_array = np.array(img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_array).unsqueeze(0)

                status_info = f"图像生成成功 | 模型: {model} | 尺寸: {size} | 输入图像数: {len(image_refs)}"
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
    "AgnesImageToImageNode": AgnesImageToImageNode,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "AgnesImageToImageNode": "Agnes AI-图生图",
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
