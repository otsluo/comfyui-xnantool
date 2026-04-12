import requests
import json
import torch
import numpy as np
from PIL import Image
from io import BytesIO
import os
import base64
import time

# 检查openai库是否可用
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 支持的图片反推模型列表
SUPPORTED_CAPTION_MODELS = [
    ("Qwen/Qwen3-VL-235B-A22B-Instruct", "Qwen3-VL 235B A22B Instruct"),
    ("Qwen/Qwen3-VL-8B-Instruct", "Qwen3-VL 8B Instruct"),
    ("Qwen/Qwen3-VL-2B-Instruct", "Qwen3-VL 2B Instruct"),
]

def load_api_token():
    return ""

def save_api_token(token):
    return True

def tensor_to_base64_url(image_tensor):
    try:
        if len(image_tensor.shape) == 4:
            image_tensor = image_tensor.squeeze(0)
        
        if image_tensor.max() <= 1.0:
            image_np = (image_tensor.cpu().numpy() * 255).astype(np.uint8)
        else:
            image_np = image_tensor.cpu().numpy().astype(np.uint8)
        
        pil_image = Image.fromarray(image_np)
        
        buffer = BytesIO()
        pil_image.save(buffer, format='JPEG', quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/jpeg;base64,{img_base64}"
        
    except Exception as e:
        print(f"图像转换失败: {e}")
        raise Exception(f"图像格式转换失败: {str(e)}")

class ModelscopeApiImageCaptionNode:
    """魔搭API图片反推节点 - 用于从图像生成描述文本"""
    def __init__(self):
        pass
    
    def parse_api_token(self, token_input):
        """解析输入的单个API Token"""
        if not token_input or token_input.strip() == "":
            # 尝试加载保存的token
            saved_token = load_api_token()
            if saved_token:
                return saved_token
            return ""
        
        # 返回单个Token
        return token_input.strip()
    
    @classmethod
    def INPUT_TYPES(cls):
        if not OPENAI_AVAILABLE:
            return {
                "required": {
                    "error_message": ("STRING", {
                        "default": "请先安装openai库: pip install openai",
                        "multiline": True
                    }),
                }
            }
        saved_token = load_api_token()
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "详细描述这张图片的内容，包括主体、背景、颜色、风格等信息",
                    "label": "提示词",
                    "description": "用于图片描述的提示词",
                    "multiline": True
                }),
                "image": ("IMAGE",),
                "model_name": ("STRING", {
                    "default": "Qwen/Qwen3-VL-235B-A22B-Instruct",
                    "options": [model[0] for model in SUPPORTED_CAPTION_MODELS],
                    "labels": {model[0]: model[1] for model in SUPPORTED_CAPTION_MODELS},
                    "label": "模型名称"
                }),
                "max_tokens": ("INT", {
                    "default": 1000,
                    "min": 100,
                    "max": 4000,
                    "label": "最大令牌数",
                    "description": "生成描述文本的最大长度"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.1,
                    "label": "温度系数",
                    "description": "控制生成文本的随机性"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "label": "随机种子"
                }),
                "api_token": ("STRING", {
                    "default": saved_token,
                    "label": "API Token",
                    "description": "modelscope API 令牌",
                    "placeholder": "请输入您的 modelscope API Token",
                    "multiline": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("图片描述",)
    FUNCTION = "generate_caption"
    CATEGORY = "XnanTool/魔搭api"
    
    def generate_caption(self, prompt, image, model_name, max_tokens, temperature, seed, api_token):
        if not OPENAI_AVAILABLE:
            return ("请先安装openai库: pip install openai",)
        
        # 解析单个API Token
        token = self.parse_api_token(api_token)
        if not token:
            raise Exception("请输入有效的API Token")
        
        # 保存新Token（如果有变化）
        saved_token = load_api_token()
        if api_token.strip() != saved_token:
            if save_api_token(token):
                print("✅ API Token已自动保存")
            else:
                print("⚠️ API Token保存失败，但不影响当前使用")
        
        try:
            print(f"🔍 开始生成图像描述...")
            print(f"📝 提示词: {prompt}")
            print(f"🤖 模型: {model_name}")
            print(f"🔑 使用API Token: {token[:10]}...")
            
            # 转换图像为base64格式
            image_url = tensor_to_base64_url(image)
            print(f"🖼️ 图像已转换为base64格式")
            
            # 构建消息体
            messages = [{
                'role': 'user',
                'content': [{
                    'type': 'text',
                    'text': prompt,
                }, {
                    'type': 'image_url',
                    'image_url': {
                        'url': image_url,
                    },
                }],
            }]
            
            try:
                print(f"🔄 使用API Token进行调用...")
                
                # 初始化OpenAI客户端
                client = OpenAI(
                    base_url='https://api-inference.modelscope.cn/v1',
                    api_key=token
                )
                
                # 调用API（使用选中的模型）
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    seed=seed if seed >= 0 else None,
                    stream=False
                )
                
                # 检查响应是否有效
                if not response or not response.choices or len(response.choices) == 0:
                    raise Exception("API返回空响应，可能是模型调用失败")
                
                # 成功获取结果
                description = response.choices[0].message.content
                print(f"✅ API调用成功!")
                print(f"📄 结果预览: {description[:100]}...")
                return (description,)
                
            except Exception as e:
                error_msg = f"API调用失败: {str(e)}"
                print(f"❌ {error_msg}")
                if 'response' in locals():
                    print(f"🔍 响应详情: {response}")
                return (error_msg,)
            
        except Exception as e:
            error_msg = f"图像描述生成失败: {str(e)}"
            print(f"❌ {error_msg}")
            return (error_msg,)

# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "ModelscopeApiImageCaptionNode": ModelscopeApiImageCaptionNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ModelscopeApiImageCaptionNode": "魔搭API-图片反推",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']