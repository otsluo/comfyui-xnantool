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

# 支持的视频反推模型列表
SUPPORTED_VIDEO_CAPTION_MODELS = [
    ("Qwen/Qwen3-VL-235B-A22B-Instruct", "Qwen3-VL 235B A22B Instruct"),
    ("Qwen/Qwen2-VL-72B-Instruct", "Qwen2-VL 72B Instruct"),
    ("Qwen/Qwen2-VL-7B-Instruct", "Qwen2-VL 7B Instruct"),
    ("Qwen/Qwen-VL-Chat", "Qwen-VL Chat"),
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

class ModelscopeApiVideoCaptionNode:
    """魔搭API视频反推节点 - 用于从视频生成描述文本"""
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
                    "default": "请详细描述这个视频的内容，包括场景、动作、主体、背景等信息",
                    "label": "提示词",
                    "description": "用于视频描述的提示词",
                    "multiline": True
                }),
                "video_frames": ("IMAGE",),
                "model_name": ("STRING", {
                    "default": "Qwen/Qwen3-VL-235B-A22B-Instruct",
                    "options": [model[0] for model in SUPPORTED_VIDEO_CAPTION_MODELS],
                    "labels": {model[0]: model[1] for model in SUPPORTED_VIDEO_CAPTION_MODELS},
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
    RETURN_NAMES = ("视频描述",)
    FUNCTION = "generate_caption"
    CATEGORY = "XnanTool/魔搭api"
    
    def generate_caption(self, prompt, video_frames, model_name, max_tokens, temperature, seed, api_token):
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
            print(f"🔍 开始生成视频描述...")
            print(f"📝 提示词: {prompt}")
            print(f"🤖 模型: {model_name}")
            print(f"🔑 使用API Token: {token[:10]}...")
            
            # 转换视频帧为base64格式列表
            if isinstance(video_frames, torch.Tensor):
                # 处理视频帧张量 (batch of images)
                print(f"🔍 输入张量形状: {video_frames.shape}, 数据类型: {video_frames.dtype}")
                frame_count = video_frames.shape[0]
                print(f"🎞️ 视频帧数量: {frame_count}")
                
                # 构建消息体，包含所有视频帧
                content = [{
                    'type': 'text',
                    'text': prompt,
                }]
                
                # 添加所有视频帧
                for i in range(frame_count):
                    frame_tensor = video_frames[i:i+1]  # 取单帧
                    print(f"🖼️ 处理第 {i+1}/{frame_count} 帧，形状: {frame_tensor.shape}")
                    try:
                        frame_url = tensor_to_base64_url(frame_tensor)
                        content.append({
                            'type': 'image_url',
                            'image_url': {
                                'url': frame_url,
                            },
                        })
                        print(f"✅ 第 {i+1} 帧转换成功")
                    except Exception as e:
                        print(f"❌ 第 {i+1} 帧转换失败: {e}")
                        raise Exception(f"视频帧 {i+1} 转换失败: {str(e)}")
                
                messages = [{
                    'role': 'user',
                    'content': content,
                }]
            else:
                # 如果不是张量，尝试直接处理
                messages = [{
                    'role': 'user',
                    'content': [{
                        'type': 'text',
                        'text': prompt,
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
            error_msg = f"视频描述生成失败: {str(e)}"
            print(f"❌ {error_msg}")
            return (error_msg,)

# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "ModelscopeApiVideoCaptionNode": ModelscopeApiVideoCaptionNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ModelscopeApiVideoCaptionNode": "魔搭API-视频反推",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']