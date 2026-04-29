import os
import logging
import requests
import io
import base64

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模型说明
MODEL_DESCRIPTIONS = {
    "qwen-image-plus": "通义千问图像plus",
    "qwen-image-plus-2026-01-09": "通义千问图像plus 2026-01-09",
}

class BailianQwenNode:
    """
    阿里云百炼Qwen节点 - 调用阿里云百炼图片生成模型
    """
    
    def __init__(self):
        self.api_key = None
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "提示词",
                    "description": "生成图片的提示词"
                }),
                "model": (["qwen-image-plus", "qwen-image-plus-2026-01-09"], {
                    "default": "qwen-image-plus",
                    "label": "模型",
                    "description": "选择要使用的图片生成模型"
                }),
            },
            "optional": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "API Key",
                    "description": "阿里云百炼API Key（从控制台获取）"
                }),
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "反向提示词",
                    "description": "不希望出现在图片中的内容"
                }),
                "image_width": ("INT", {
                    "default": 1024,
                    "min": 256,
                    "max": 2048,
                    "step": 64,
                    "label": "图片宽度",
                    "description": "生成图片的宽度（像素）"
                }),
                "image_height": ("INT", {
                    "default": 1024,
                    "min": 256,
                    "max": 2048,
                    "step": 64,
                    "label": "图片高度",
                    "description": "生成图片的高度（像素）"
                }),
                "steps": ("INT", {
                    "default": 30,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "label": "采样步数",
                    "description": "生成图片的采样步数"
                }),
                "scale": ("FLOAT", {
                    "default": 7.5,
                    "min": 1.0,
                    "max": 20.0,
                    "step": 0.5,
                    "label": "提示词相关性",
                    "description": "提示词对生成图片的影响程度"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999999999,
                    "step": 1,
                    "label": "随机种子",
                    "description": "随机种子（0为随机）"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "image_urls")
    FUNCTION = "generate_image"
    CATEGORY = "XnanTool/API/阿里百炼"
    
    def generate_image(self, prompt, model, api_key=None, negative_prompt="", image_width=1024, image_height=1024, steps=30, scale=7.5, seed=0):
        """
        调用阿里云百炼图片生成模型
        
        Args:
            prompt: 提示词
            model: 模型名称
            api_key: API Key
            negative_prompt: 反向提示词
            image_width: 图片宽度
            image_height: 图片高度
            steps: 采样步数
            scale: 提示词相关性
            
        Returns:
            tuple: (图片列表, 图片URL列表)
        """
        try:
            # 检查提示词
            if not prompt or not prompt.strip():
                return (None, "错误：提示词不能为空")
            
            # 优先使用环境变量，其次使用传入的参数
            api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
            
            # 检查必需参数
            if not api_key:
                return (None, "错误：API Key未配置，请传入或设置环境变量 DASHSCOPE_API_KEY")
            
            # 尝试导入 dashscope
            try:
                import dashscope
                from http import HTTPStatus
            except ImportError:
                return (None, "错误：请安装 dashscope SDK: pip install dashscope")
            
            # 设置API Key
            dashscope.api_key = api_key
            # 设置 endpoint URL
            dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
            
            # 构建调用参数
            params = {
                "model": model,
                "prompt": prompt.strip(),
                "negative_prompt": negative_prompt.strip() if negative_prompt else " ",
                "n": 1,
                "size": f"{int(image_width)}*{int(image_height)}",
                "prompt_extend": True,
                "watermark": False,
                "seed": int(seed) if seed > 0 else None
            }
            
            # 移除None值
            params = {k: v for k, v in params.items() if v is not None}
            
            # 调用图片生成模型
            response = dashscope.ImageSynthesis.call(**params)
            
            # 检查响应状态
            if response.status_code != HTTPStatus.OK:
                error_msg = f"请求失败:\n状态码: {response.status_code}\n消息: {response.message}\n请求ID: {response.request_id}"
                logger.error(error_msg)
                return (None, error_msg)
            
            # 获取生成的图片
            image_urls = []
            images = []
            
            logger.debug(f"response.output: {response.output}")
            logger.debug(f"response.output类型: {type(response.output)}")
            
            if hasattr(response.output, 'results'):
                logger.debug(f"response.output.results: {response.output.results}")
                logger.debug(f"response.output.results类型: {type(response.output.results)}")
                logger.debug(f"response.output.results长度: {len(response.output.results) if response.output.results else 0}")
                
                if response.output.results:
                    import torch
                    import numpy as np
                    from PIL import Image
                    
                    for idx, result in enumerate(response.output.results):
                        logger.debug(f"result {idx}: {result}")
                        logger.debug(f"result类型: {type(result)}")
                        
                        if hasattr(result, 'url'):
                            image_urls.append(result.url)
                            logger.debug(f"图片URL: {result.url}")
                            # 下载图片
                            try:
                                img_response = requests.get(result.url)
                                logger.debug(f"下载状态码: {img_response.status_code}")
                                if img_response.status_code == 200:
                                    # 将图片转换为PIL图像
                                    pil_image = Image.open(io.BytesIO(img_response.content))
                                    logger.debug(f"PIL图片模式: {pil_image.mode}, 大小: {pil_image.size}")
                                    # 转换为RGB模式
                                    if pil_image.mode != 'RGB':
                                        pil_image = pil_image.convert('RGB')
                                    # 转换为numpy数组
                                    img_np = np.array(pil_image).astype(np.float32) / 255.0
                                    logger.debug(f"numpy数组形状: {img_np.shape}")
                                    # 转换为torch张量 (H, W, C) -> (C, H, W)
                                    img_tensor = torch.from_numpy(img_np).unsqueeze(0)
                                    logger.debug(f"torch张量形状: {img_tensor.shape}")
                                    images.append(img_tensor)
                                else:
                                    logger.error(f"下载图片失败，状态码: {img_response.status_code}")
                            except Exception as e:
                                logger.error(f"下载图片失败: {str(e)}")
                        else:
                            logger.warning(f"result 没有 url 属性")
                else:
                    logger.warning(f"response.output.results 为空")
            else:
                logger.warning(f"response.output 没有 results 属性")
            
            logger.debug(f"images列表长度: {len(images)}")
            
            # 如果没有成功下载图片，返回错误
            if not images:
                return (None, "错误：无法下载生成的图片")
            
            # 返回图片张量列表和URL列表
            logger.info(f"百炼图片生成调用成功")
            
            return (torch.cat(images, dim=0), ", ".join(image_urls))
            
        except Exception as e:
            error_msg = f"调用百炼图片生成时发生错误: {str(e)}"
            logger.error(error_msg)
            return (None, error_msg)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "BailianQwenNode": BailianQwenNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BailianQwenNode": "百炼Qwen-图片生成",
}
