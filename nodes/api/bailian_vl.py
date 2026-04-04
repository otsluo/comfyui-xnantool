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

# 模型说明
MODEL_DESCRIPTIONS = {
    "qwen3.5-plus": "通义千问3.5 Plus（推荐）",
    "qwen3.5-plus-2026-02-15": "通义千问3.5 Plus 2026-02-15",
    "qwen3.5-flash": "通义千问3.5 Flash",
    "qwen3.5-flash-2026-02-23": "通义千问3.5 Flash 2026-02-23",
    "qwen3.5-35b-a3b": "通义千问3.5 35B-A3B",
    "qwen3.5-27b": "通义千问3.5 27B",
    "qwen3.5-122b-a10b": "通义千问3.5 122B-A10B",
    "qwen3.5-397b-a17b": "通义千问3.5 397B-A17B（推荐）",
    "qwen3-vl-plus": "通义千问3 VL Plus（推荐）",
    "qwen3-vl-plus-2025-12-19": "通义千问3 VL Plus 2025-12-19",
    "qwen3-vl-plus-2025-09-23": "通义千问3 VL Plus 2025-09-23",
    "qwen3-vl-flash": "通义千问3 VL Flash",
    "qwen3-vl-flash-2026-01-22": "通义千问3 VL Flash 2026-01-22",
    "qwen3-vl-flash-2025-10-15": "通义千问3 VL Flash 2025-10-15",
    "qwen3-vl-30b-a3b-thinking": "通义千问3 VL 30B-A3B 思考模式",
}

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
                "model": (["qwen3.5-plus", "qwen3.5-plus-2026-02-15", 
                          "qwen3.5-flash", "qwen3.5-flash-2026-02-23",
                          "qwen3.5-35b-a3b", "qwen3.5-27b", "qwen3.5-122b-a10b", "qwen3.5-397b-a17b",
                          "qwen3-vl-plus", "qwen3-vl-plus-2025-12-19", "qwen3-vl-plus-2025-09-23",
                          "qwen3-vl-flash", "qwen3-vl-flash-2026-01-22", "qwen3-vl-flash-2025-10-15",
                          "qwen3-vl-30b-a3b-thinking"], {
                    "default": "qwen3-vl-plus",
                    "label": "模型",
                    "description": "选择要使用的VL模型"
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
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response", "full_response")
    FUNCTION = "call_vl"
    CATEGORY = "XnanTool/API/阿里百炼"
    
    def call_vl(self, prompt, image, model, api_key=None, temperature=0.7, top_p=0.95, max_tokens=1024):
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
            
            # 将图片转换为base64
            try:
                image_base64 = self.image_to_base64(image)
            except Exception as e:
                return (f"错误：图片转换失败: {str(e)}",)
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": f"data:image/jpeg;base64,{image_base64}"},
                        {"text": prompt.strip()}
                    ]
                }
            ]
            
            # 构建调用参数
            params = {
                "model": model,
                "messages": messages,
                "result_format": "message",
                "temperature": float(temperature),
                "top_p": float(top_p),
                "max_tokens": int(max_tokens)
            }
            
            # 调用VL模型
            response = dashscope.MultiModalConversation.call(**params)
            
            # 调试信息
            logger.debug(f"响应对象类型: {type(response)}")
            logger.debug(f"响应对象内容: {response}")
            logger.debug(f"响应对象属性: {dir(response)}")
            
            # 检查响应状态
            if response.status_code != HTTPStatus.OK:
                error_msg = f"请求失败:\n状态码: {response.status_code}\n消息: {response.message}\n请求ID: {response.request_id}"
                logger.error(error_msg)
                return (error_msg,)
            
            # 调试输出内容
            logger.debug(f"response.output类型: {type(response.output)}")
            logger.debug(f"response.output: {response.output}")
            
            if hasattr(response.output, 'choices') and response.output.choices:
                logger.debug(f"response.output.choices[0]类型: {type(response.output.choices[0])}")
                logger.debug(f"response.output.choices[0]: {response.output.choices[0]}")
                
                if hasattr(response.output.choices[0], 'message'):
                    logger.debug(f"response.output.choices[0].message类型: {type(response.output.choices[0].message)}")
                    logger.debug(f"response.output.choices[0].message: {response.output.choices[0].message}")
                    
                    if hasattr(response.output.choices[0].message, 'content'):
                        logger.debug(f"response.output.choices[0].message.content类型: {type(response.output.choices[0].message.content)}")
                        logger.debug(f"response.output.choices[0].message.content: {response.output.choices[0].message.content}")
            
            # 返回响应
            response_text = response.output.choices[0].message.content
            
            # 如果content是列表，取第一个元素
            if isinstance(response_text, list):
                if len(response_text) > 0:
                    response_text = response_text[0]
                else:
                    return ("错误：响应内容为空",)
            
            # 如果content是字典，提取text字段
            if isinstance(response_text, dict):
                if "text" in response_text:
                    response_text = response_text["text"]
                else:
                    response_text = str(response_text)
            
            # 转换为字符串
            if not isinstance(response_text, str):
                response_text = str(response_text)
            
            # 获取完整响应（JSON格式）
            import json
            full_response = json.dumps({
                "output": {
                    "choices": [{
                        "finish_reason": getattr(response.output.choices[0], 'finish_reason', 'N/A'),
                        "message": {
                            "role": getattr(response.output.choices[0].message, 'role', 'N/A'),
                            "content": str(response.output.choices[0].message.content)
                        }
                    }]
                },
                "usage": {
                    "output_tokens": getattr(response.usage, 'output_tokens', 'N/A') if hasattr(response, 'usage') else 'N/A',
                    "input_tokens": getattr(response.usage, 'input_tokens', 'N/A') if hasattr(response, 'usage') else 'N/A',
                    "image_tokens": getattr(response.usage, 'image_tokens', 'N/A') if hasattr(response, 'usage') else 'N/A'
                },
                "request_id": getattr(response, 'request_id', 'N/A') if hasattr(response, 'request_id') else 'N/A'
            }, ensure_ascii=False, indent=2)
            
            logger.info(f"百炼VL调用成功")
            
            return (response_text, full_response)
            
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

NODE_DISPLAY_NAME_MAPPINGS = {
    "BailianVLNode": "百炼VL-视觉理解",
}
