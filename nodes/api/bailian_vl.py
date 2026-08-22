import os
import logging
import base64
import requests

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 改为DEBUG级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BailianVLNode:
    """
    阿里云百炼VL节点 - 调用阿里云百炼视觉语言模型
    支持图片+文本输入
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
                    "description": "输入给大模型的提示词（可包含图片描述）"
                }),
                "image": ("IMAGE", {
                    "label": "图片",
                    "description": "输入的图片"
                }),
                "model": (["自定义", "qwen3.7-max", "qwen3.7-plus", "qwen3.7-max-preview",
                          "qwen3.7-max-2026-06-08", "qwen3.7-max-2026-05-20", "qwen3.7-max-2026-05-17",
                          "qwen3.7-plus-2026-05-26",
                          "qwen3.5-ocr",
                          "deepseek-v4-pro", "deepseek-v4-flash",
                          "kimi-k2.7-code", "glm-5.2"], {
                    "default": "qwen3.7-plus",
                    "label": "模型",
                    "description": "选择要使用的模型，选择'自定义'可手动输入模型名称"
                }),
                "custom_model": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "自定义模型",
                    "description": "当模型选择'自定义'时，在此输入模型名称"
                }),
            },
            "optional": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "API Key",
                    "description": "阿里云百炼API Key（从控制台获取）"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "label": "温度",
                    "description": "控制输出的随机性，值越大越随机"
                }),
                "top_p": ("FLOAT", {
                    "default": 0.95,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "label": "Top P",
                    "description": "累积概率阈值，控制生成的多样性"
                }),
                "max_tokens": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 65536,
                    "step": 1,
                    "label": "最大输出长度",
                    "description": "最大输出Token数量"
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
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response", "full_response")
    FUNCTION = "call_vl"
    CATEGORY = "❤️❤️❤️XnanTool/API/阿里百炼"
    
    def call_vl(self, prompt, image, model, custom_model="", api_key=None, temperature=0.7, top_p=0.95, max_tokens=1024, seed=0):
        """
        调用阿里云百炼VL模型
        
        Args:
            prompt: 输入提示词
            image: 输入图片
            model: 模型名称
            api_key: API Key
            temperature: 温度参数
            top_p: Top P参数
            max_tokens: 最大输出长度
            
        Returns:
            tuple: (响应文本,)
        """
        try:
            # 检查提示词
            if not prompt or not prompt.strip():
                return ("错误：提示词不能为空",)
            
            # 检查图片
            if image is None:
                return ("错误：图片不能为空",)
            
            # 优先使用环境变量，其次使用传入的参数
            api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
            
            # 检查必需参数
            if not api_key:
                return ("错误：API Key未配置，请传入或设置环境变量 DASHSCOPE_API_KEY",)
            
            # 尝试导入 dashscope
            try:
                import dashscope
                from http import HTTPStatus
            except ImportError:
                return ("错误：请安装 dashscope SDK: pip install dashscope",)
            
            # 设置API Key
            dashscope.api_key = api_key
            
            # 处理自定义模型
            if model == "自定义":
                if not custom_model or not custom_model.strip():
                    return ("错误：选择'自定义'模型时，必须填写自定义模型名称",)
                actual_model = custom_model.strip()
            else:
                # 提取实际模型名称（去掉中文说明部分）
                actual_model = model.split('（')[0] if '（' in model else model
            
            # 将图片转换为base64
            try:
                image_base64 = self.image_to_base64(image)
            except Exception as e:
                return (f"错误：图片转换失败: {str(e)}",)
            
            # 使用 OpenAI 兼容模式调用
            try:
                from openai import OpenAI
                
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                )
                
                # 构建消息
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            },
                            {
                                "type": "text",
                                "text": prompt.strip()
                            }
                        ]
                    }
                ]
                
                # 构建调用参数
                params = {
                    "model": actual_model,
                    "messages": messages,
                    "temperature": float(temperature),
                    "top_p": float(top_p),
                    "max_tokens": int(max_tokens),
                }
                if seed > 0:
                    params["seed"] = int(seed)
                
                # 调用模型
                response = client.chat.completions.create(**params)
                
                # 提取响应文本
                response_text = response.choices[0].message.content
                
                # 构建完整响应
                import json
                full_response = json.dumps({
                    "id": response.id,
                    "model": response.model,
                    "choices": [{
                        "index": response.choices[0].index,
                        "message": {
                            "role": response.choices[0].message.role,
                            "content": response.choices[0].message.content
                        },
                        "finish_reason": response.choices[0].finish_reason
                    }],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }, ensure_ascii=False, indent=2)
                
                logger.info(f"百炼VL调用成功")
                
                return (response_text, full_response)
                
            except ImportError:
                # 如果没有 openai 库，回退到 dashscope SDK
                pass
            
        except Exception as e:
            error_msg = f"调用百炼VL时发生错误: {str(e)}"
            logger.error(error_msg)
            return (error_msg,)
    
    def image_to_base64(self, image):
        """
        将PyTorch张量图片转换为base64字符串
        
        Args:
            image: PyTorch张量，格式为 (1, H, W, C)，值范围 [0, 1]
            
        Returns:
            str: base64编码的图片字符串
        """
        import torch
        import numpy as np
        from PIL import Image
        import io
        
        # 检查输入格式
        if isinstance(image, torch.Tensor):
            # 转换到CPU并移除batch维度
            if image.dim() == 4:
                image = image[0]
            
            # 转换到CPU并转换为numpy
            image_np = image.cpu().numpy()
            
            # 转换为uint8格式 [0, 255]
            if image_np.max() <= 1.0:
                image_np = (image_np * 255).astype(np.uint8)
            else:
                image_np = image_np.astype(np.uint8)
            
            # 转换为HWC格式
            if image_np.shape[0] == 3:  # CHW格式
                image_np = image_np.transpose(1, 2, 0)
            
            # 创建PIL图像
            if image_np.shape[2] == 1:  # 灰度图
                pil_image = Image.fromarray(image_np.squeeze(), 'L')
            elif image_np.shape[2] == 4:  # RGBA
                pil_image = Image.fromarray(image_np, 'RGBA')
            else:  # RGB
                pil_image = Image.fromarray(image_np, 'RGB')
        else:
            pil_image = image
        
        # 转换为JPEG格式
        buffered = io.BytesIO()
        pil_image.save(buffered, format="JPEG")
        
        # 编码为base64
        import base64
        return base64.b64encode(buffered.getvalue()).decode('utf-8')


# 注册节点
NODE_CLASS_MAPPINGS = {
    "BailianVLNode": BailianVLNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "BailianVLNode": "百炼VL-图像反推",
}
