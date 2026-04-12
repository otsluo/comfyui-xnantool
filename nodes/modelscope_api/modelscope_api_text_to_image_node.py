import requests
import json
import time
import torch
import numpy as np
from PIL import Image
from io import BytesIO
import os
import base64
import tempfile
import random


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

# 支持的文生图模型列表
SUPPORTED_TEXT_TO_IMAGE_MODELS = [
    ("black-forest-labs/FLUX.1-schnell", "FLUX.1-schnell"),
    ("black-forest-labs/FLUX.1-dev", "FLUX.1-dev"),
    ("black-forest-labs/FLUX.1-Krea-dev", "FLUX.1-Krea-dev"),
    ("black-forest-labs/FLUX.1-Kontext", "FLUX.1-Kontext"),
    ("black-forest-labs/FLUX.2-klein-9B", "FLUX.2-klein-9B"),
    ("black-forest-labs/FLUX.2-dev", "FLUX.2-dev"),
    ("Qwen/Qwen-Image", "Qwen-Image"),
    ("Tencent-Hunyuan/HunyuanImage-2.1", "HunyuanImage-2.1"),
    ("Tencent-Hunyuan/HunyuanImage-3.0", "HunyuanImage-3.0"),
    ("Qwen/Qwen-Image-2512", "Qwen-Image-2512"),
    ("stabilityai/stable-diffusion-xl-base-1.0", "SDXL 1.0"),
    ("stabilityai/stable-diffusion-xl-refiner-1.0", "SDXL Refiner"),
    ("stabilityai/stable-diffusion-3-medium-diffusers", "SD3 Medium"),
    ("Tongyi-MAI/Z-Image-Turbo", "Z-Image-Turbo"),
    ("segmind/Segmind-Vega", "Segmind-Vega"),
]

class modelscopeLoraTextToImageNode:
    """支持多种基础模型的文生图节点，包含LoRA支持和批次生成功能"""
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        saved_token = load_api_token()
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Career line,with prominent breasts,A very realistic style,high definition photography style,a young woman,long black hair,holding a badminton shuttlecock,standing,outdoors.",
                    "label": "提示词",
                    "description": "描述您想要生成的图像内容",
                    "placeholder": "描述您想要生成的图像内容"
                }),
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "负面提示词",
                    "placeholder": "描述您不想在图像中出现的内容"
                }),
                "base_model": ("STRING", {
                    "default": SUPPORTED_TEXT_TO_IMAGE_MODELS[9][0],
                    "options": [model[0] for model in SUPPORTED_TEXT_TO_IMAGE_MODELS],
                    "labels": {model[0]: model[1] for model in SUPPORTED_TEXT_TO_IMAGE_MODELS},
                    "label": "基础模型"
                }),
                "lora_model": ("STRING", {
                    "default": "qiyuanai/TikTok_Xiaohongshu_career_line_beauty_v2",
                    "label": "LoRA模型"
                }),
                "lora_weight": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "label": "LoRA权重"
                }),
                "width": ("INT", {
                    "default": 928,
                    "min": 64,
                    "max": 2048,
                    "step": 64,
                    "label": "宽度"
                }),
                "height": ("INT", {
                    "default": 1664,
                    "min": 64,
                    "max": 2048,
                    "step": 64,
                    "label": "高度"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "label": "随机种子"
                }),
                "steps": ("INT", {
                    "default": 30,
                    "min": 1,
                    "max": 100,
                    "label": "采样步数"
                }),
                "guidance": ("FLOAT", {
                    "default": 7.5,
                    "min": 1.5,
                    "max": 20.0,
                    "step": 0.1,
                    "label": "引导系数"
                }),
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 8,
                    "label": "批次大小",
                    "description": "一次生成的图片数量"
                }),
            },
            "optional": {
                "api_token": ("STRING", {
                    "default": saved_token,
                    "label": "API Token",
                    "description": "modelscope API 令牌，用于调用服务",
                    "placeholder": "请输入您的 modelscope API Token"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "text_to_image_models")
    FUNCTION = "generate_with_lora"
    CATEGORY = "XnanTool/魔搭api"
    
    def generate_with_lora(self, prompt, negative_prompt, base_model, lora_model, lora_weight, width, height, seed, steps, guidance, batch_size, api_token="", generate_control="fixed"):
        
        # 准备文生图模型列表字符串
        text_to_image_models_str = "\n".join([f"{name} ({model_id})" for model_id, name in SUPPORTED_TEXT_TO_IMAGE_MODELS])
        
        # 验证API Token
        if not api_token or api_token.strip() == "" or api_token.strip() == "api_token":
            raise Exception("请输入有效的API Token（当前配置无效）")
        
        try:
            # 为每个批次生成使用不同的种子
            base_seed = seed if seed != -1 else random.randint(0, 20251003)
            
            # 存储所有生成的图像
            image_tensors = []
            
            # 为每个批次生成图像
            for i in range(batch_size):
                current_seed = base_seed + i if seed != -1 else random.randint(0, 20251003)
                
                # 准备API请求参数
                url = 'https://api-inference.modelscope.cn/v1/images/generations'
                
                # 基础payload
                payload = {
                    'model': base_model,  # 使用用户选择的基础模型
                    'prompt': prompt,
                    'size': f"{width}x{height}",
                    'steps': steps,
                    'guidance_scale': guidance,
                    'generate_control': generate_control,
                    'seed': current_seed
                }
                
                # 修复LoRA参数格式 - 按照官方文档要求
                if lora_model and lora_model.strip() != "":
                    # 单个LoRA模型格式：{"model_id": weight}
                    payload['loras'] = {lora_model: lora_weight}
                
                # 添加可选参数
                if negative_prompt.strip():
                    payload['negative_prompt'] = negative_prompt
                
                # 准备请求头 - 统一格式
                common_headers = {
                    'Authorization': f'Bearer {api_token}',
                    'Content-Type': 'application/json',
                }
                
                headers = {** common_headers, "X-ModelScope-Async-Mode": "true"}
                
                # 发送请求
                print(f"📤 正在提交第 {i+1}/{batch_size} 个LoRA图像生成任务，种子: {current_seed}")
                submission_response = requests.post(
                    url,
                    data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                    headers=headers,
                    timeout=60
                )
                
                # 处理请求响应
                if submission_response.status_code != 200:
                    error_detail = submission_response.text
                    print(f"❌ API请求失败详情:")
                    print(f"   状态码: {submission_response.status_code}")
                    print(f"   响应内容: {error_detail}")
                    try:
                        error_json = submission_response.json()
                        if "errors" in error_json:
                            error_message = error_json["errors"].get("message", "未知错误")
                            error_code = error_json["errors"].get("code", "未知错误码")
                            raise Exception(f"API请求失败 [{submission_response.status_code}]: {error_code} - {error_message}")
                    except:
                        pass
                    raise Exception(f"API请求失败: {submission_response.status_code}, {error_detail}")
                
                submission_json = submission_response.json()
                
                # 处理异步任务
                image_url = None
                if 'task_id' in submission_json:
                    task_id = submission_json['task_id']
                    print(f"🕒 已提交第 {i+1} 个任务，任务ID: {task_id}，开始轮询...")
                    poll_start = time.time()
                    max_wait_seconds = 720
                    
                    while True:
                        # 查询任务状态 - 修复请求头格式
                        task_resp = requests.get(
                            f"https://api-inference.modelscope.cn/v1/tasks/{task_id}",
                            headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
                            timeout=120
                        )
                        
                        if task_resp.status_code != 200:
                            raise Exception(f"任务查询失败: {task_resp.status_code}, {task_resp.text}")
                        
                        data = task_resp.json()
                        task_status = data.get("task_status")
                        
                        if task_status == "SUCCEED":
                            if not data.get("output_images") or len(data["output_images"]) == 0:
                                raise Exception("任务成功但未返回图片URL")
                            
                            image_url = data["output_images"][0]
                            print(f"✅ 第 {i+1} 个任务完成，开始下载图片...")
                            
                            # 下载图片
                            img_response = requests.get(image_url, timeout=30)
                            if img_response.status_code != 200:
                                raise Exception(f"图片下载失败: {img_response.status_code}")
                            
                            # 处理图片
                            pil_image = Image.open(BytesIO(img_response.content))
                            if pil_image.mode != 'RGB':
                                pil_image = pil_image.convert('RGB')
                            
                            # 转换为ComfyUI需要的格式
                            image_np = np.array(pil_image).astype(np.float32) / 255.0
                            image_tensor = torch.from_numpy(image_np)[None,]
                            
                            # 添加到图像列表
                            image_tensors.append(image_tensor)
                            break
                            
                        elif task_status == "FAILED":
                            error_message = data.get("errors", {}).get("message", "未知错误")
                            error_code = data.get("errors", {}).get("code", "未知错误码")
                            raise Exception(f"任务失败: 错误码 {error_code}, 错误信息: {error_message}")
                            
                        # 检查超时
                        if time.time() - poll_start > max_wait_seconds:
                            raise Exception("任务轮询超时，请稍后重试或降低并发")
                            
                        # 未完成，继续轮询
                        time.sleep(5)
                else:
                    raise Exception(f"未识别的API返回格式: {submission_json}")
            
            # 合并所有图像张量
            if len(image_tensors) > 0:
                final_tensor = torch.cat(image_tensors, dim=0)
                print(f"🎉 批次图片生成完成！共生成 {len(image_tensors)} 张图片")
                return (final_tensor, text_to_image_models_str)
            else:
                raise Exception("未生成任何图片")
        
        except Exception as e:
            print(f"魔搭API-LoRA调用失败: {str(e)}")
            # 创建一个红色错误图像作为回退
            error_image = Image.new('RGB', (width, height), color='red')
            error_np = np.array(error_image).astype(np.float32) / 255.0
            error_tensor = torch.from_numpy(error_np)[None,]
            # 如果是批次生成，复制图像以匹配批次大小
            if batch_size > 1:
                error_tensor = error_tensor.repeat(batch_size, 1, 1, 1)
            return (error_tensor, text_to_image_models_str)

# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "modelscopeLoraTextToImageNode": modelscopeLoraTextToImageNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "modelscopeLoraTextToImageNode": "魔搭API-文生图"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
