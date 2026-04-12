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

# 支持的图像编辑模型列表
SUPPORTED_IMAGE_EDIT_MODELS = [
    ("Qwen/Qwen-Image-Edit", "Qwen-Image-Edit"),
    ("Qwen/Qwen-Image-Edit-2509", "Qwen-Image-Edit-2509"),
    ("Qwen/Qwen-Image-Edit-2511", "Qwen-Image-Edit-2511"),
    ("runwayml/stable-diffusion-inpainting", "SD Inpainting"),
]

class modelscopeLoraImageEditNode:
    """支持多种基础模型的图像编辑节点，包含LoRA支持"""
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        saved_token = load_api_token()
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "修改图片中的内容",
                    "label": "编辑提示词",
                    "description": "描述您想要如何编辑图像",
                    "placeholder": "描述您想要如何编辑图像"
                }),
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "负面提示词",
                    "placeholder": "描述您不想在编辑后图像中出现的内容"
                }),
                "base_model": ("STRING", {
                    "default": SUPPORTED_IMAGE_EDIT_MODELS[2][0],
                    "options": [model[0] for model in SUPPORTED_IMAGE_EDIT_MODELS],
                    "labels": {model[0]: model[1] for model in SUPPORTED_IMAGE_EDIT_MODELS},
                    "label": "基础模型"
                }),
                "lora_model": ("STRING", {
                    "default": "",
                    "label": "LoRA模型"
                }),
                "lora_weight": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "label": "LoRA权重"
                }),
                "use_custom_size": ("BOOLEAN", {
                    "default": False,
                    "label": "使用自定义尺寸",
                    "description": "开启时使用自定义宽度和高度，关闭时自动获取输入图像尺寸"
                }),
                "width": ("INT", {
                    "default": 928,
                    "min": 64,
                    "max": 2048,
                    "step": 8,
                    "label": "宽度"
                }),
                "height": ("INT", {
                    "default": 1664,
                    "min": 64,
                    "max": 2048,
                    "step": 8,
                    "label": "高度"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 20251003,
                    "label": "随机种子"
                }),
                "steps": ("INT", {
                    "default": 30,
                    "min": 1,
                    "max": 100,
                    "label": "采样步数"
                }),
                "guidance": ("FLOAT", {
                    "default": 3.5,
                    "min": 1.5,
                    "max": 20.0,
                    "step": 0.1,
                    "label": "引导系数"
                }),
            },
            "optional": {
                "api_token": ("STRING", {
                    "default": saved_token,
                    "placeholder": "请输入您的魔搭API Token",
                    "label": "API令牌"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("edited_image", "image_edit_models")
    FUNCTION = "edit_with_lora"
    CATEGORY = "XnanTool/魔搭api"
    
    def edit_with_lora(self, image, prompt, negative_prompt, base_model, lora_model, lora_weight, use_custom_size, width, height, seed, steps, guidance, api_token="", generate_control="fixed"):
        
        # 准备图像编辑模型列表字符串
        image_edit_models_str = "\n".join([f"{name} ({model_id})" for model_id, name in SUPPORTED_IMAGE_EDIT_MODELS])
        
        # 验证API Token
        if not api_token or api_token.strip() == "" or api_token.strip() == "api_token":
            raise Exception("请输入有效的API Token（当前配置无效）")
        
        try:
            # 准备通用请求头
            common_headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json',
            }
            
            # 准备图像数据
            print("📤 准备图像数据...")
            if len(image.shape) == 4:
                img = image[0]
            else:
                img = image
            
            # 根据use_custom_size决定使用自定义尺寸还是图像原始尺寸
            if use_custom_size:
                img_width = width
                img_height = height
            else:
                img_height, img_width = img.shape[:2]
                img_width = (img_width // 8) * 8
                img_height = (img_height // 8) * 8
            
            pil_image = Image.fromarray((img.cpu().numpy() * 255).astype(np.uint8))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 保存到临时文件
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            pil_image.save(temp_file.name, format='JPEG', quality=95)
            temp_file.close()
            
            # 读取为 base64
            with open(temp_file.name, 'rb') as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # 准备请求数据
            payload = {
                'model': base_model,
                'prompt': prompt,
                'image_url': [f"data:image/jpeg;base64,{img_base64}"],
                'size': f"{img_width}x{img_height}",
                'steps': steps,
                'guidance_scale': guidance,
                'seed': seed if seed != -1 else -1,
                'generate_control': generate_control
            }
            
            # 添加LoRA参数
            if lora_model and lora_model.strip() != "":
                payload['loras'] = {lora_model: lora_weight}
            
            # 添加负向提示词
            if negative_prompt.strip():
                payload['negative_prompt'] = negative_prompt
            
            # 调试信息
            print(f"📤 请求参数: {payload}")
            
            model_display_name = next((model[1] for model in SUPPORTED_IMAGE_EDIT_MODELS if model[0] == base_model), base_model)
            print(f"🔧 使用基础模型: {model_display_name} ({base_model})")
            print(f"🧩 使用LoRA模型: {lora_model}")
            print(f"⚖️ LoRA权重: {lora_weight}")
            
            # 发送请求
            print("📤 正在提交LoRA图像编辑任务...")
            url = 'https://api-inference.modelscope.cn/v1/images/generations'
            
            submission_response = requests.post(
                url,
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
                timeout=60
            )
            
            print(f"📤 请求响应状态码: {submission_response.status_code}")
            print(f"📤 请求响应内容: {submission_response.text}")
            
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
            result_image_url = None
            if 'task_id' in submission_json:
                task_id = submission_json['task_id']
                print(f"🕒 已提交任务，任务ID: {task_id}，开始轮询...")
                poll_start = time.time()
                max_wait_seconds = 720
                
                while True:
                    # 查询任务状态
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
                        
                        result_image_url = data["output_images"][0]
                        print("✅ 任务完成，开始下载编辑后的图片...")
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
            
            # 下载编辑后的图片
            img_response = requests.get(result_image_url, timeout=30)
            if img_response.status_code != 200:
                raise Exception(f"图片下载失败: {img_response.status_code}")
            
            # 处理图片
            pil_image = Image.open(BytesIO(img_response.content))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 转换为ComfyUI需要的格式
            image_np = np.array(pil_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]
            
            print("🎉 图片编辑完成！")
            return (image_tensor, image_edit_models_str)
            
        except Exception as e:
            print(f"魔搭API-LoRA图像编辑调用失败: {str(e)}")
            raise
        finally:
            # 清理临时文件
            if 'temp_file' in locals() and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "modelscopeLoraImageEditNode": modelscopeLoraImageEditNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "modelscopeLoraImageEditNode": "魔搭API-图像编辑"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
