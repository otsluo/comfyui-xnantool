import os
import logging
import base64
import io

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模型说明
MODEL_DESCRIPTIONS = {
    "wan2.6-t2v": "万相2.6 文生视频（推荐，有声视频）",
    "wan2.6-t2v-us": "万相2.6 文生视频（美国）",
    "wan2.5-t2v-preview": "万相2.5 文生视频预览版（有声视频）",
    "wan2.2-t2v-plus": "万相2.2 文生视频 plus（无声视频）",
    "wan2.1-t2v-turbo": "万相2.1 文生视频 turbo（无声视频）",
    "wan2.1-t2v-plus": "万相2.1 文生视频 plus（无声视频）",
    "wan2.6-i2v": "万相2.6 图生视频（推荐，有声视频）",
    "wan2.6-i2v-flash": "万相2.6 图生视频 flash（有声视频）",
    "wan2.6-i2v-us": "万相2.6 图生视频（美国）",
    "wan2.5-i2v-preview": "万相2.5 图生视频预览版（有声视频）",
    "wan2.2-i2v-flash": "万相2.2 图生视频 flash（无声视频）",
    "wan2.2-i2v-plus": "万相2.2 图生视频 plus（无声视频）",
    "wan2.1-i2v-plus": "万相2.1 图生视频 plus（无声视频）",
    "wan2.1-i2v-turbo": "万相2.1 图生视频 turbo（无声视频）",
    "wan2.2-kf2v-flash": "万相2.2 首尾帧生视频 flash（无声视频）",
    "wan2.1-kf2v-plus": "万相2.1 首尾帧生视频 plus（无声视频）",
    "wan2.6-r2v": "万相2.6 参考生视频（有声视频）",
    "wan2.6-r2v-flash": "万相2.6 参考生视频 flash（有声视频）",
    "wan2.1-vace-plus": "万相2.1 通用视频编辑 plus（无声视频）",
}

class BailianWanNode:
    """
    阿里云百炼Wan节点 - 调用阿里云百炼视频生成模型
    支持文生视频、图生视频、参考生视频、视频编辑等多种视频生成任务
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
                    "description": "生成视频的提示词"
                }),
                "model": (["wan2.6-t2v", "wan2.6-t2v-us", "wan2.5-t2v-preview", "wan2.2-t2v-plus", 
                          "wan2.1-t2v-turbo", "wan2.1-t2v-plus",
                          "wan2.6-i2v", "wan2.6-i2v-flash", "wan2.6-i2v-us", "wan2.5-i2v-preview",
                          "wan2.2-i2v-flash", "wan2.2-i2v-plus", "wan2.1-i2v-plus", "wan2.1-i2v-turbo",
                          "wan2.2-kf2v-flash", "wan2.1-kf2v-plus",
                          "wan2.6-r2v", "wan2.6-r2v-flash",
                          "wan2.1-vace-plus"], {
                    "default": "wan2.6-t2v",
                    "label": "模型",
                    "description": "选择要使用的视频生成模型"
                }),
            },
            "optional": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "API Key",
                    "description": "阿里云百炼API Key（从控制台获取）"
                }),
                "image": ("IMAGE", {
                    "label": "首帧图像",
                    "description": "图生视频时的首帧图像（可选）"
                }),
                "end_image": ("IMAGE", {
                    "label": "尾帧图像",
                    "description": "首尾帧生视频时的尾帧图像（可选）"
                }),
                "video": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "参考视频URL",
                    "description": "参考生视频时的参考视频URL（可选）"
                }),
                "audio": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "音频URL",
                    "description": "有声视频的音频URL（可选）"
                }),
                "video_duration": ("INT", {
                    "default": 5,
                    "min": 2,
                    "max": 15,
                    "step": 1,
                    "label": "视频时长",
                    "description": "生成视频的时长（秒），范围2-15秒"
                }),
                "resolution": (["480P", "720P", "1080P"], {
                    "default": "1080P",
                    "label": "分辨率",
                    "description": "生成视频的分辨率"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate_video"
    CATEGORY = "XnanTool/API/阿里百炼"
    
    def generate_video(self, prompt, model, api_key=None, image=None, end_image=None, 
                      video="", audio="", video_duration=5, resolution="1080P"):
        """
        调用阿里云百炼视频生成模型
        
        Args:
            prompt: 生成视频的提示词
            model: 模型名称
            api_key: API Key
            image: 首帧图像
            end_image: 尾帧图像
            video: 参考视频URL
            audio: 音频URL
            video_duration: 视频时长
            resolution: 分辨率
            
        Returns:
            tuple: (视频URL, 任务ID)
        """
        try:
            # 检查提示词
            if not prompt or not prompt.strip():
                return ("错误：提示词不能为空", "")
            
            # 优先使用环境变量，其次使用传入的参数
            api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
            
            # 检查必需参数
            if not api_key:
                return ("错误：API Key未配置，请传入或设置环境变量 DASHSCOPE_API_KEY", "")
            
            # 尝试导入 dashscope
            try:
                import dashscope
                from http import HTTPStatus
            except ImportError:
                return ("错误：请安装 dashscope SDK: pip install dashscope", "")
            
            # 设置API Key
            dashscope.api_key = api_key
            
            # 构建调用参数
            params = {
                "model": model,
                "input": {
                    "prompt": prompt.strip()
                },
                "parameters": {
                    "duration": int(video_duration),
                    "resolution": resolution
                }
            }
            
            # 根据模型类型添加不同的输入参数
            model_lower = model.lower()
            
            # 图生视频模型
            if any(x in model_lower for x in ["i2v", "kf2v"]):
                if image is not None:
                    # 将 ComfyUI 的 Tensor 转换为 Base64
                    base64_data = tensor_to_base64(image)
                    if base64_data:
                        params["input"]["first_frame"] = base64_data
                        logger.info(f"图生视频模型，已添加首帧图像（Base64编码）")
                    else:
                        logger.warning("图生视频模型，首帧图像转换失败")
                else:
                    logger.warning("图生视频模型需要提供首帧图像")
                    logger.info(f"图生视频模型，跳过首帧图像")
            
            # 首尾帧生视频模型
            if "kf2v" in model_lower:
                if end_image is not None:
                    # 将 ComfyUI 的 Tensor 转换为 Base64
                    base64_data = tensor_to_base64(end_image)
                    if base64_data:
                        params["input"]["last_frame"] = base64_data
                        logger.info(f"首尾帧生视频模型，已添加尾帧图像（Base64编码）")
                    else:
                        logger.warning("首尾帧生视频模型，尾帧图像转换失败")
                else:
                    logger.warning("首尾帧生视频模型需要提供尾帧图像")
                    logger.info(f"首尾帧生视频模型，跳过尾帧图像")
            
            # 参考生视频模型
            if "r2v" in model_lower:
                if video:
                    params["input"]["video"] = video
                    logger.info(f"参考生视频模型，已添加参考视频")
                else:
                    return ("错误：参考生视频模型需要提供参考视频URL", "")
            
            # 有声视频模型：仅 wan2.6 和 wan2.5 的 t2v/i2v 支持音频
            if ("2.6" in model_lower or "2.5" in model_lower) and any(x in model_lower for x in ["t2v", "i2v"]):
                if audio:
                    params["input"]["audio"] = audio
                    logger.info(f"有声视频模型，已添加音频")
            
            # 调用视频生成模型（视频生成需要异步调用）
            try:
                import requests
                
                # 构建请求URL
                api_url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis'
                
                # 构建请求头，必须包含 X-DashScope-Async: enable
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "X-DashScope-Async": "enable"
                }
                
                # 构建请求体
                payload = {
                    "model": model,
                    "input": params["input"],
                    "parameters": params["parameters"]
                }
                
                # 发送异步请求
                response = requests.post(api_url, headers=headers, json=payload)
                
                # 检查响应
                if response.status_code != 200:
                    error_msg = f"请求失败:\n状态码: {response.status_code}\n消息: {response.text}"
                    logger.error(error_msg)
                    return (error_msg, "")
                
                # 解析响应
                result = response.json()
                
                # 获取任务ID
                task_id = result.get("output", {}).get("task_id", "")
                
                logger.info(f"百炼Wan视频生成任务已提交，任务ID: {task_id}")
                
                # 返回任务ID和状态
                task_status = result.get("output", {}).get("task_status", "UNKNOWN")
                return (f"任务已提交，任务ID: {task_id}，状态: {task_status}", task_id)
                
            except Exception as e:
                error_msg = f"请求失败:\n错误: {str(e)}\n提示：视频生成模型需要异步调用"
                logger.error(error_msg)
                return (error_msg, "")
            
        except Exception as e:
            error_msg = f"调用百炼Wan视频生成时发生错误: {str(e)}"
            logger.error(error_msg)
            return (error_msg, "")


def tensor_to_base64(tensor):
    """
    将 ComfyUI 的 IMAGE Tensor 转换为 Base64 格式
    
    Args:
        tensor: IMAGE Tensor (形状: [B, H, W, C], 值范围: 0-1)
        
    Returns:
        str: Base64 格式的图片数据 (data:image/png;base64,...)
    """
    try:
        import torch
        from PIL import Image
        
        # 如果是 batch，只取第一张
        if len(tensor.shape) == 4:
            tensor = tensor[0]
        
        # 将 tensor 从 [H, W, C] 转换为 [C, H, W]
        if tensor.shape[2] == 3:
            tensor = tensor.permute(2, 0, 1)
        
        # 将值从 [0, 1] 转换为 [0, 255]
        tensor = (tensor * 255).clamp(0, 255).to(torch.uint8)
        
        # 转换为 numpy
        np_img = tensor.permute(1, 2, 0).cpu().numpy()
        
        # 转换为 PIL Image
        image = Image.fromarray(np_img, mode='RGB')
        
        # 保存到内存缓冲区
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        
        # 转换为 Base64
        base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{base64_data}"
        
    except Exception as e:
        logger.error(f"Tensor 转 Base64 失败: {str(e)}")
        return None


class BailianWanQueryNode:
    """
    阿里云百炼Wan查询节点 - 查询视频生成任务状态
    """
    
    def __init__(self):
        self.api_key = None
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "task_id": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "任务ID",
                    "description": "要查询的任务ID"
                }),
            },
            "optional": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "API Key",
                    "description": "阿里云百炼API Key（从控制台获取）"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("task_status", "video_url", "error_msg", "task_id", "all_info")
    FUNCTION = "query_task"
    CATEGORY = "XnanTool/API/阿里百炼"
    
    def query_task(self, task_id, api_key=None):
        """
        查询视频生成任务状态
        
        Args:
            task_id: 任务ID
            api_key: API Key
            
        Returns:
            tuple: (任务状态, 视频URL, 错误信息, 任务ID, 完整信息JSON)
        """
        try:
            # 检查任务ID
            if not task_id:
                return ("", "", "错误：任务ID不能为空", "", "")
            
            # 优先使用环境变量，其次使用传入的参数
            api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
            
            # 检查必需参数
            if not api_key:
                return ("", "", "错误：API Key未配置，请传入或设置环境变量 DASHSCOPE_API_KEY", "", "")
            
            # 查询任务状态
            try:
                import requests
                import json
                
                # 构建请求URL
                api_url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
                
                # 构建请求头
                headers = {
                    "Authorization": f"Bearer {api_key}"
                }
                
                # 发送GET请求
                response = requests.get(api_url, headers=headers)
                
                # 检查响应
                if response.status_code != 200:
                    error_msg = f"查询失败:\n状态码: {response.status_code}\n消息: {response.text}"
                    logger.error(error_msg)
                    return ("", "", error_msg, "", "")
                
                # 解析响应
                result = response.json()
                
                # 获取任务状态
                task_status = result.get("output", {}).get("task_status", "UNKNOWN")
                
                # 从 raw_response.output 中获取 video_url
                video_url = result.get("output", {}).get("video_url", "")
                if not video_url:
                    video_url = result.get("output", {}).get("output_video_url", "")
                
                error_code = result.get("output", {}).get("code", "")
                error_msg = result.get("output", {}).get("message", "")
                
                # 获取更多详细信息
                submit_time = result.get("output", {}).get("submit_time", "")
                scheduled_time = result.get("output", {}).get("scheduled_time", "")
                end_time = result.get("output", {}).get("end_time", "")
                usage = result.get("output", {}).get("usage", {})
                request_id = result.get("request_id", "")
                
                # 构建完整信息JSON
                all_info = {
                    "task_id": task_id,
                    "task_status": task_status,
                    "video_url": video_url,
                    "error_code": error_code,
                    "error_message": error_msg,
                    "submit_time": submit_time,
                    "scheduled_time": scheduled_time,
                    "end_time": end_time,
                    "usage": usage,
                    "request_id": request_id,
                    "raw_response": result
                }
                all_info_json = json.dumps(all_info, ensure_ascii=False, indent=2)
                
                logger.info(f"任务状态: {task_status}")
                
                if task_status == "SUCCEEDED":
                    logger.info(f"视频生成成功，URL: {video_url}")
                    return (task_status, video_url, "", task_id, all_info_json)
                elif task_status in ["FAILED", "CANCELED"]:
                    logger.error(f"任务失败: {error_msg} (错误码: {error_code})")
                    return (task_status, "", f"错误码: {error_code}, 消息: {error_msg}", task_id, all_info_json)
                else:
                    # 任务仍在进行中
                    return (task_status, "", "", task_id, all_info_json)
                
            except Exception as e:
                error_msg = f"查询任务失败: {str(e)}"
                logger.error(error_msg)
                return ("", "", error_msg, "", "")
            
        except Exception as e:
            error_msg = f"查询百炼Wan任务时发生错误: {str(e)}"
            logger.error(error_msg)
            return ("", "", error_msg, "", "")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "BailianWanNode": BailianWanNode,
    "BailianWanQueryNode": BailianWanQueryNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BailianWanNode": "百炼Wan-视频生成",
    "BailianWanQueryNode": "百炼Wan-查询任务-测试图参",
}
