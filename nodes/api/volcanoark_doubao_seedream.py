import os
import folder_paths
import torch
import numpy as np
from PIL import Image
import io
import requests
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions


class DoubaoSeedreamTextToImageGenerationNode:
    """
    豆包Seedream文生图节点 - 使用火山引擎豆包Seedream模型生成图像
    支持单张图像生成和批量连贯图像生成
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "星际穿越，黑洞，黑洞里冲出一辆快支离破碎的复古列车，抢视觉冲击力，电影大片，末日既视感，动感，对比色，oc渲染，光线追踪，动态模糊，景深，超现实主义，深蓝，画面通过细腻的丰富的色彩层次塑造主体与场景，质感真实，暗黑风背景的光影效果营造出氛围，整体兼具艺术幻想感，夸张的广角透视效果，耀光，反射，极致的光影，强引力，吞噬",
                    "multiline": True,
                    "label": "提示词",
                    "description": "图像生成的文本提示词"
                }),
                "model_id": (["doubao-seedream-5-0-260128", "doubao-seedream-4-5-251128"], {
                    "default": "doubao-seedream-5-0-260128",
                    "label": "模型ID",
                    "description": "选择使用的豆包Seedream模型"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "password": True,
                    "label": "API密钥",
                    "description": "火山引擎方舟API密钥"
                }),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "5:4", "4:5", "9:16", "16:9", "21:9"], {
                    "default": "1:1",
                    "label": "比例",
                    "description": "生成图像的比例"
                }),
                "resolution": (["1K", "2K", "4K"], {
                    "default": "2K",
                    "label": "分辨率",
                    "description": "生成图像的分辨率"
                }),
                "mode": (["single", "batch"], {
                    "default": "single",
                    "label": "生成模式",
                    "description": "生成模式：single=单张图像，batch=批量连贯图像"
                }),
                "max_images": ("INT", {
                    "default": 15,
                    "min": 1,
                    "max": 15,
                    "step": 1,
                    "label": "图像数量",
                    "description": "生成的图像数量（批量模式下有效，1-10）"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999999999,
                    "step": 1,
                    "label": "随机种子",
                    "description": "随机种子（0为随机）"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "label": "水印",
                    "description": "是否在生成的图像上添加水印"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "status_info")
    FUNCTION = "generate_image"
    CATEGORY = "XnanTool/API/火山引擎"
    
    def generate_image(self, prompt, model_id, api_key, aspect_ratio, resolution, mode, max_images, seed, watermark):
        """
        使用豆包Seedream模型生成图像
        支持单张和批量两种模式
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("请填写火山引擎方舟API密钥")
        
        # 初始化Ark客户端
        client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key,
        )
        
        try:
            print("----- 创建图像生成请求 -----")
            
            # 根据比例和分辨率计算实际尺寸
            resolution_mapping = {
                "1K": 1024,
                "2K": 2048,
                "4K": 4096
            }
            
            aspect_ratio_mapping = {
                "1:1": (1, 1),
                "2:3": (2, 3),
                "3:2": (3, 2),
                "3:4": (3, 4),
                "4:3": (4, 3),
                "5:4": (5, 4),
                "4:5": (4, 5),
                "9:16": (9, 16),
                "16:9": (16, 9),
                "21:9": (21, 9)
            }
            
            base_size = resolution_mapping[resolution]
            ratio = aspect_ratio_mapping[aspect_ratio]
            
            # 计算实际尺寸
            if ratio[0] > ratio[1]:
                # 横屏
                width = base_size * ratio[0] // ratio[1]
                height = base_size
            else:
                # 竖屏或正方形
                width = base_size
                height = base_size * ratio[1] // ratio[0]
            
            actual_size = f"{width}x{height}"
            
            # 映射尺寸参数
            size_mapping = {
                "1024x1024": "1024x1024",
                "1024x1536": "1024x1536", 
                "1536x1024": "1536x1024",
                "2K": "2K"
            }
            
            # 存储所有生成的图像
            all_images = []
            first_image_url = ""
            
            if mode == "single":
                # 单张图像生成模式
                print("----- 单张图像生成模式 -----")
                
                images_response = client.images.generate(
                    model=model_id,
                    prompt=prompt,
                    sequential_image_generation="disabled",
                    response_format="url",
                    size=size_mapping.get(actual_size, actual_size) if actual_size != "auto" else None,
                    stream=False,
                    watermark=watermark,
                    seed=seed if seed > 0 else None
                )
                
                # 获取生成的图像URL
                image_urls = [img.url for img in images_response.data] if images_response.data else []
                first_image_url = image_urls[0] if image_urls else ""
                
                # 下载并转换图像
                print("----- 下载并转换图像 -----")
                for idx, img_url in enumerate(image_urls):
                    print(f"下载第 {idx + 1} 张图像: {img_url}")
                    response = requests.get(img_url)
                    response.raise_for_status()
                    
                    # 将图像数据转换为PIL Image
                    image_data = Image.open(io.BytesIO(response.content)).convert('RGB')
                    
                    # 转换为numpy数组
                    np_image = np.array(image_data, dtype=np.float32) / 255.0
                    
                    # 转换为torch张量 (H, W, C) -> (B, H, W, C)
                    image_tensor = torch.unsqueeze(torch.from_numpy(np_image), 0)
                    all_images.append(image_tensor)
                
                status_info = f"图像生成成功，尺寸: {actual_size}\n生成图片数量: {len(image_urls)}\n"
                for idx, img_url in enumerate(image_urls):
                    status_info += f"图片 {idx + 1} 链接: {img_url}\n"
                print(f"图像生成成功，共生成 {len(image_urls)} 张图像")
                
            else:
                # 批量图像生成模式
                print("----- 批量图像生成模式 -----")
                
                # 生成批量图像
                images_response = client.images.generate(
                    model=model_id,
                    prompt=prompt,
                    sequential_image_generation="auto",
                    sequential_image_generation_options=SequentialImageGenerationOptions(max_images=max_images),
                    response_format="url",
                    size=size_mapping.get(actual_size, actual_size) if actual_size != "auto" else None,
                    stream=True,
                    watermark=watermark,
                    seed=seed if seed > 0 else None
                )
                
                # 处理流式响应
                print("----- 处理流式响应 -----")
                image_urls = []
                for event in images_response:
                    if event is None:
                        continue
                        
                    if event.type == "image_generation.partial_failed":
                        print(f"图像生成失败: {event.error}")
                        if event.error is not None and event.error.code == "InternalServiceError":
                            break
                            
                    elif event.type == "image_generation.partial_succeeded":
                        if event.error is None and event.url:
                            print(f"收到图像: {event.url}")
                            image_urls.append(event.url)
                            
                            # 保存第一个图像的URL
                            if not first_image_url:
                                first_image_url = event.url
                            
                            # 下载并转换图像
                            try:
                                response = requests.get(event.url)
                                response.raise_for_status()
                                
                                # 将图像数据转换为PIL Image
                                image_data = Image.open(io.BytesIO(response.content)).convert('RGB')
                                
                                # 转换为numpy数组
                                np_image = np.array(image_data, dtype=np.float32) / 255.0
                                
                                # 转换为torch张量 (H, W, C) -> (B, H, W, C)
                                image_tensor = torch.unsqueeze(torch.from_numpy(np_image), 0)
                                all_images.append(image_tensor)
                            except Exception as e:
                                print(f"下载或转换图像失败: {e}")
                                
                    elif event.type == "image_generation.completed":
                        if event.error is None:
                            print("批量图像生成完成")
                            print(f"使用量: {event.usage}")
                
                status_info = f"成功生成 {len(all_images)} 张图像，尺寸: {actual_size}\n"
                for idx, img_url in enumerate(image_urls):
                    status_info += f"图片 {idx + 1} 链接: {img_url}\n"
            
            # 合并所有图像张量
            if all_images:
                images_tensor = torch.cat(all_images, dim=0)
                return (images_tensor, status_info)
            else:
                # 返回空张量
                empty_tensor = torch.zeros(1, 512, 512, 3, dtype=torch.float32)
                return (empty_tensor, "未生成任何图像")
        
        except Exception as e:
            error_msg = str(e)
            print(f"图像生成过程中出现错误: {error_msg}")
            # 返回空张量
            empty_tensor = torch.zeros(1, 512, 512, 3, dtype=torch.float32)
            return (empty_tensor, f"错误: {error_msg}")


class DoubaoSeedreamImageToImageGenerationNode:
    """
    豆包Seedream图生图节点 - 使用火山引擎豆包Seedream模型进行图像到图像生成
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "生成狗狗趴在草地上的近景画面",
                    "multiline": True,
                    "label": "提示词",
                    "description": "图像生成的文本提示词"
                }),
                "model_id": (["doubao-seedream-5-0-260128", "doubao-seedream-4-5-251128"], {
                    "default": "doubao-seedream-5-0-260128",
                    "label": "模型ID",
                    "description": "选择使用的豆包Seedream模型"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "password": True,
                    "label": "API密钥",
                    "description": "火山引擎方舟API密钥"
                }),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "5:4", "4:5", "9:16", "16:9", "21:9"], {
                    "default": "1:1",
                    "label": "比例",
                    "description": "生成图像的比例"
                }),
                "resolution": (["1K", "2K", "4K"], {
                    "default": "2K",
                    "label": "分辨率",
                    "description": "生成图像的分辨率"
                }),
                "mode": (["single", "batch"], {
                    "default": "single",
                    "label": "生成模式",
                    "description": "生成模式：single=单张图像，batch=批量连贯图像"
                }),
                "max_images": ("INT", {
                    "default": 15,
                    "min": 1,
                    "max": 15,
                    "step": 1,
                    "label": "图像数量",
                    "description": "生成的图像数量（批量模式下有效，1-10）"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999999999,
                    "step": 1,
                    "label": "随机种子",
                    "description": "随机种子（0为随机）"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "label": "水印",
                    "description": "是否在生成的图像上添加水印"
                })
            },
            "optional": {
                "image1": ("IMAGE", {
                    "label": "参考图片1",
                    "description": "作为参考的图片1"
                }),
                "image2": ("IMAGE", {
                    "label": "参考图片2",
                    "description": "作为参考的图片2"
                }),
                "image3": ("IMAGE", {
                    "label": "参考图片3",
                    "description": "作为参考的图片3"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "status_info")
    FUNCTION = "generate_image_to_image"
    CATEGORY = "XnanTool/API/火山引擎"
    
    def generate_image_to_image(self, prompt, model_id, api_key, aspect_ratio, resolution, mode, max_images, seed, watermark, image1=None, image2=None, image3=None):
        """
        使用豆包Seedream模型进行图生图
        支持单张和批量两种模式
        支持多张参考图生成单张图
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("请填写火山引擎方舟API密钥")
        
        # 收集所有提供的参考图片
        images = []
        if image1 is not None:
            images.append(image1)
        if image2 is not None:
            images.append(image2)
        if image3 is not None:
            images.append(image3)
        
        if not images:
            raise ValueError("请至少提供一张参考图片")
        
        # 将ComfyUI IMAGE格式转换为Base64编码
        print(f"----- 将ComfyUI IMAGE格式转换为Base64编码 -----")
        
        # 处理多张参考图
        import base64
        from io import BytesIO
        image_data_uris = []
        
        for idx, image in enumerate(images):
            print(f"----- 处理第 {idx + 1} 张参考图片 -----")
            
            # 确保数据类型正确
            img_tensor = image.float()
            
            # 处理batch维度
            if img_tensor.shape[0] > 1:
                img_tensor = img_tensor[0]
            
            # 调整维度顺序：[batch, height, width, channels] -> [height, width, channels]
            if len(img_tensor.shape) == 4:
                # 如果是 [batch, channels, height, width] 格式
                if img_tensor.shape[1] < img_tensor.shape[2] and img_tensor.shape[1] < img_tensor.shape[3]:
                    img_tensor = img_tensor.permute(0, 2, 3, 1)
                img_tensor = img_tensor[0]
            
            # 确保张量在CPU上并转换为numpy
            np_image = (img_tensor.clamp(0, 1).cpu().numpy() * 255).astype(np.uint8)
            
            # 转换为PIL Image
            pil_image = Image.fromarray(np_image)
            
            # 转换为Base64编码
            buffered = BytesIO()
            pil_image.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            image_data_uri = f"data:image/png;base64,{base64_image}"
            image_data_uris.append(image_data_uri)
            print(f"第 {idx + 1} 张图片已转换为Base64编码，长度: {len(base64_image)}")
        
        # 初始化Ark客户端
        client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key,
        )
        
        try:
            print("----- 创建图生图请求 -----")
            
            # 根据比例和分辨率计算实际尺寸
            resolution_mapping = {
                "1K": 1024,
                "2K": 2048,
                "4K": 4096
            }
            
            aspect_ratio_mapping = {
                "1:1": (1, 1),
                "2:3": (2, 3),
                "3:2": (3, 2),
                "3:4": (3, 4),
                "4:3": (4, 3),
                "5:4": (5, 4),
                "4:5": (4, 5),
                "9:16": (9, 16),
                "16:9": (16, 9),
                "21:9": (21, 9)
            }
            
            base_size = resolution_mapping[resolution]
            ratio = aspect_ratio_mapping[aspect_ratio]
            
            # 计算实际尺寸
            if ratio[0] > ratio[1]:
                # 横屏
                width = base_size * ratio[0] // ratio[1]
                height = base_size
            else:
                # 竖屏或正方形
                width = base_size
                height = base_size * ratio[1] // ratio[0]
            
            actual_size = f"{width}x{height}"
            
            # 映射尺寸参数
            size_mapping = {
                "1024x1024": "1024x1024",
                "1024x1536": "1024x1536", 
                "1536x1024": "1536x1024",
                "2K": "2K"
            }
            
            # 生成图像
            if mode == "single":
                # 单张图像生成模式
                print("----- 单张图像生成模式 -----")
                images_response = client.images.generate(
                    model=model_id,
                    prompt=prompt,
                    image=image_data_uris[0] if len(image_data_uris) == 1 else image_data_uris,
                    sequential_image_generation="disabled",
                    response_format="url",
                    size=size_mapping.get(actual_size, actual_size),
                    stream=False,
                    watermark=watermark,
                    seed=seed if seed > 0 else None
                )
            else:
                # 批量图像生成模式
                print("----- 批量图像生成模式 -----")
                print(f"参考图片数量: {len(image_data_uris)}")
                print(f"max_images: {max_images}")
                images_response = client.images.generate(
                    model=model_id,
                    prompt=prompt,
                    image=image_data_uris[0] if len(image_data_uris) == 1 else image_data_uris,
                    sequential_image_generation="auto",
                    sequential_image_generation_options=SequentialImageGenerationOptions(max_images=max_images),
                    response_format="url",
                    size=size_mapping.get(actual_size, actual_size),
                    stream=True,
                    watermark=watermark,
                    seed=seed if seed > 0 else None
                )
            
            # 获取生成的图像URL
            if mode == "single":
                image_urls = [img.url for img in images_response.data] if images_response.data else []
            else:
                # 批量模式需要处理流式响应
                image_urls = []
            
            # 存储所有生成的图像
            all_images = []
            
            if mode == "single":
                # 单张模式直接下载图像
                print("----- 下载并转换图像 -----")
                for idx, img_url in enumerate(image_urls):
                    print(f"下载第 {idx + 1} 张图像: {img_url}")
                    response = requests.get(img_url)
                    response.raise_for_status()
                    
                    # 将图像数据转换为PIL Image
                    image_data = Image.open(io.BytesIO(response.content)).convert('RGB')
                    
                    # 转换为numpy数组
                    np_image = np.array(image_data, dtype=np.float32) / 255.0
                    
                    # 转换为torch张量 (H, W, C) -> (B, H, W, C)
                    image_tensor = torch.unsqueeze(torch.from_numpy(np_image), 0)
                    all_images.append(image_tensor)
            else:
                # 批量模式处理流式响应
                print("----- 处理流式响应 -----")
                for event in images_response:
                    if event is None:
                        continue
                        
                    if event.type == "image_generation.partial_failed":
                        print(f"图像生成失败: {event.error}")
                        if event.error is not None and event.error.code == "InternalServiceError":
                            break
                            
                    elif event.type == "image_generation.partial_succeeded":
                        if event.error is None and event.url:
                            print(f"收到图像: {event.url}")
                            image_urls.append(event.url)
                            
                            # 下载并转换图像
                            try:
                                response = requests.get(event.url)
                                response.raise_for_status()
                                
                                # 将图像数据转换为PIL Image
                                image_data = Image.open(io.BytesIO(response.content)).convert('RGB')
                                
                                # 转换为numpy数组
                                np_image = np.array(image_data, dtype=np.float32) / 255.0
                                
                                # 转换为torch张量 (H, W, C) -> (B, H, W, C)
                                image_tensor = torch.unsqueeze(torch.from_numpy(np_image), 0)
                                all_images.append(image_tensor)
                            except Exception as e:
                                print(f"下载或转换图像失败: {e}")
                                
                    elif event.type == "image_generation.completed":
                        if event.error is None:
                            print("批量图像生成完成")
                            print(f"使用量: {event.usage}")
                
                print(f"最终接收到的图像数量: {len(image_urls)}")
            
            # 合并所有图像张量
            if all_images:
                images_tensor = torch.cat(all_images, dim=0)
                status_info = f"图生图成功，尺寸: {actual_size}\n生成图片数量: {len(image_urls)}\n"
                for idx, img_url in enumerate(image_urls):
                    status_info += f"图片 {idx + 1} 链接: {img_url}\n"
                print(f"图生图成功，共生成 {len(image_urls)} 张图像")
                return (images_tensor, status_info)
            else:
                # 返回空张量
                empty_tensor = torch.zeros(1, 512, 512, 3, dtype=torch.float32)
                return (empty_tensor, "未生成任何图像")
        
        except Exception as e:
            error_msg = str(e)
            print(f"图生图过程中出现错误: {error_msg}")
            # 返回空张量
            empty_tensor = torch.zeros(1, 512, 512, 3, dtype=torch.float32)
            return (empty_tensor, f"错误: {error_msg}")


# 导出节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "DoubaoSeedreamTextToImageGenerationNode": DoubaoSeedreamTextToImageGenerationNode,
    "DoubaoSeedreamImageToImageGenerationNode": DoubaoSeedreamImageToImageGenerationNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DoubaoSeedreamTextToImageGenerationNode": "豆包Seedream文生图",
    "DoubaoSeedreamImageToImageGenerationNode": "豆包Seedream图生图",
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]
