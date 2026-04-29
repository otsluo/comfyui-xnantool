import time
import folder_paths
from volcenginesdkarkruntime import Ark


class DoubaoSeedanceVideoGenerationNode:
    """
    豆包Seedance视频生成节点 - 使用火山引擎豆包Seedance模型生成视频
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "无人机以极快速度穿越复杂障碍或自然奇观，带来沉浸式飞行体验 --duration 5 --camerafixed false --watermark true",
                    "multiline": True,
                    "label": "提示词",
                    "description": "视频生成的文本提示词"
                }),
                "model_id": (["doubao-seedance-1-5-pro-251215", "doubao-seedance-1-0-pro-250528"], {
                    "default": "doubao-seedance-1-5-pro-251215",
                    "label": "模型ID",
                    "description": "选择使用的豆包Seedance模型"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "password": True,
                    "label": "API密钥",
                    "description": "火山引擎方舟API密钥"
                }),
                "enable_image_to_video": ("BOOLEAN", {
                    "default": False,
                    "label": "启用图片转视频",
                    "description": "是否使用图片作为视频生成的首帧"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999999999,
                    "step": 1,
                    "label": "随机种子",
                    "description": "随机种子（0为随机）"
                })
            },
            "optional": {
                "image_url": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "图片URL",
                    "description": "首帧图片URL（当启用图片转视频时有效）",
                    "forceInput": True
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id", "status_info")
    FUNCTION = "generate_video"
    CATEGORY = "XnanTool/API/火山引擎"
    
    def generate_video(self, prompt, model_id, api_key, enable_image_to_video, seed=0, image_url=None):
        """
        使用豆包Seedance模型生成视频
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("请填写火山引擎方舟API密钥")
        
        # 初始化Ark客户端
        client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key,
        )
        
        try:
            print("----- 创建视频生成请求 -----")
            
            # 构建内容列表
            content = [{
                "type": "text",
                "text": prompt
            }]
            
            # 如果启用了图片转视频且提供了图片URL，则添加图片内容
            if enable_image_to_video and image_url and image_url.strip():
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url.strip()
                    }
                })
            
            # 创建视频生成任务
            create_kwargs = {
                "model": model_id,
                "content": content
            }
            
            # 添加随机种子（0表示随机）
            if seed > 0:
                create_kwargs["seed"] = int(seed)
            
            create_result = client.content_generation.tasks.create(**create_kwargs)
            
            task_id = create_result.id
            print(f"任务ID: {task_id}")
            
            # 轮询查询任务状态
            print("----- 轮询查询任务状态 -----")
            while True:
                get_result = client.content_generation.tasks.get(task_id=task_id)
                status = get_result.status
                
                if status == "succeeded":
                    print("----- 任务成功 -----")
                    video_url = get_result.content.get("video_url", "") if hasattr(get_result, 'content') and get_result.content else ""
                    status_info = f"任务成功，状态: {status}, 视频URL: {video_url}"
                    return (video_url, task_id, status_info)
                elif status == "failed":
                    print("----- 任务失败 -----")
                    error_msg = getattr(get_result, 'error', '未知错误')
                    status_info = f"任务失败，状态: {status}, 错误: {error_msg}"
                    return ("", task_id, status_info)
                else:
                    print(f"当前状态: {status}, 3秒后重试...")
                    time.sleep(3)
        
        except Exception as e:
            error_msg = str(e)
            print(f"视频生成过程中出现错误: {error_msg}")
            return ("", "", f"错误: {error_msg}")


# 导出节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "DoubaoSeedanceVideoGenerationNode": DoubaoSeedanceVideoGenerationNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DoubaoSeedanceVideoGenerationNode": "豆包Seedance视频生成",
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]