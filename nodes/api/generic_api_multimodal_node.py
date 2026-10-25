import os
import logging
import json
import requests
import socket
import base64
import numpy as np
from urllib3.util import connection
from PIL import Image
import io

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 强制使用 IPv4（解决某些域名不支持 IPv6 导致的 DNS 解析失败问题）
def allowed_gai_family():
    return socket.AF_INET  # 仅使用 IPv4

connection.allowed_gai_family = allowed_gai_family

class GenericAPIMultimodalNode:
    """
    通用多模态API调用节点 - 支持文本、图片、视频、音频和上下文对话
    兼容OpenAI多模态API格式（如GPT-4V、GPT-4o等）
    """
    
    def __init__(self):
        self.conversation_history = []
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "系统提示词",
                    "description": "系统提示词，用于设定模型的角色和行为规范"
                }),
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "提示词",
                    "description": "输入给模型的文本提示词"
                }),
                "model": ("STRING", {
                    "default": "gpt-4o",
                    "multiline": False,
                    "label": "模型名称",
                    "description": "要调用的模型名称（如gpt-4o、gpt-4-vision-preview等）"
                }),
            },
            "optional": {
                "image1": ("IMAGE", {
                    "label": "图片1",
                    "description": "输入的第1张图片（可选）"
                }),
                "image2": ("IMAGE", {
                    "label": "图片2",
                    "description": "输入的第2张图片（可选）"
                }),
                "image3": ("IMAGE", {
                    "label": "图片3",
                    "description": "输入的第3张图片（可选）"
                }),
                "image4": ("IMAGE", {
                    "label": "图片4",
                    "description": "输入的第4张图片（可选）"
                }),
                "image5": ("IMAGE", {
                    "label": "图片5",
                    "description": "输入的第5张图片（可选）"
                }),
                "image6": ("IMAGE", {
                    "label": "图片6",
                    "description": "输入的第6张图片（可选）"
                }),
                "image7": ("IMAGE", {
                    "label": "图片7",
                    "description": "输入的第7张图片（可选）"
                }),
                "image8": ("IMAGE", {
                    "label": "图片8",
                    "description": "输入的第8张图片（可选）"
                }),
                "image9": ("IMAGE", {
                    "label": "图片9",
                    "description": "输入的第9张图片（可选）"
                }),
                "video": ("VIDEO", {
                    "label": "视频",
                    "description": "输入的视频（可选）"
                }),
                "audio": ("AUDIO", {
                    "label": "音频",
                    "description": "输入的音频（可选）"
                }),
                "conversation_history": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "对话历史",
                    "description": "之前的对话历史（JSON格式，用于上下文对话）"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "label": "温度",
                    "description": "控制输出的随机性，值越大越随机（0-2）"
                }),
                "top_p": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "label": "Top P",
                    "description": "累积概率阈值，控制生成的多样性（0-1）"
                }),
                "max_tokens": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 128000,
                    "step": 1,
                    "label": "最大输出长度",
                    "description": "最大输出Token数量"
                }),
                "presence_penalty": ("FLOAT", {
                    "default": 0.0,
                    "min": -2.0,
                    "max": 2.0,
                    "step": 0.1,
                    "label": "存在惩罚",
                    "description": "控制模型重复使用相同内容的程度（-2到2）"
                }),
                "frequency_penalty": ("FLOAT", {
                    "default": 0.0,
                    "min": -2.0,
                    "max": 2.0,
                    "step": 0.1,
                    "label": "频率惩罚",
                    "description": "控制模型重复使用相同词汇的程度（-2到2）"
                }),
                "extra_params": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "额外参数",
                    "description": "额外的API参数（JSON格式），会合并到请求中"
                }),
                "max_conversation_rounds": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "label": "最大对话轮数",
                    "description": "自动保存的最大对话轮数（1轮=1次用户提问+1次AI回复）"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999999999,
                    "step": 1,
                    "label": "随机种子",
                    "description": "随机种子（0为随机）"
                }),
                "api_url": ("STRING", {
                    "default": "https://api.openai.com/v1/chat/completions",
                    "multiline": False,
                    "label": "API地址",
                    "description": "API的完整URL地址（OpenAI兼容格式）"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "API密钥",
                    "description": "API认证密钥"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("response", "conversation_history", "raw_response")
    FUNCTION = "call_multimodal_api"
    CATEGORY = "❤️❤️❤️XnanTool/API/通用API"
    
    def image_to_base64(self, image_tensor):
        """
        将ComfyUI的IMAGE张量转换为base64编码
        
        Args:
            image_tensor: ComfyUI的IMAGE张量 [B, H, W, C]
            
        Returns:
            str: base64编码的图片字符串
        """
        try:
            # 转换为numpy数组
            if isinstance(image_tensor, np.ndarray):
                image_np = image_tensor
            else:
                image_np = image_tensor.cpu().numpy()
            
            # 处理批次维度
            if image_np.ndim == 4:
                image_np = image_np[0]  # 取第一张图片
            
            # 确保值在0-255范围内
            if image_np.max() <= 1.0:
                image_np = (image_np * 255).astype(np.uint8)
            else:
                image_np = image_np.astype(np.uint8)
            
            # 转换为PIL Image
            if image_np.shape[-1] == 1:
                # 灰度图
                pil_image = Image.fromarray(image_np.squeeze(-1), mode='L')
            elif image_np.shape[-1] == 3:
                # RGB图
                pil_image = Image.fromarray(image_np, mode='RGB')
            elif image_np.shape[-1] == 4:
                # RGBA图
                pil_image = Image.fromarray(image_np, mode='RGBA')
            else:
                raise ValueError(f"不支持的图像通道数: {image_np.shape[-1]}")
            
            # 转换为base64
            buffered = io.BytesIO()
            pil_image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return img_base64
            
        except Exception as e:
            logger.error(f"图片转base64失败: {str(e)}")
            return None
    
    def video_to_base64(self, video):
        """
        将视频转换为base64编码
        
        Args:
            video: 视频对象（VideoStream或VideoFromFile）
            
        Returns:
            str: base64编码的视频字符串
        """
        try:
            # 获取视频文件路径
            video_path = None
            if hasattr(video, 'get_stream_source'):
                video_path = video.get_stream_source()
            elif hasattr(video, 'path'):
                video_path = video.path
            else:
                logger.error("无法获取视频路径")
                return None
            
            if not video_path or not os.path.exists(video_path):
                logger.error(f"视频文件不存在: {video_path}")
                return None
            
            # 读取视频文件并转换为base64
            with open(video_path, 'rb') as f:
                video_data = f.read()
                video_base64 = base64.b64encode(video_data).decode('utf-8')
            
            logger.info(f"视频转base64成功，大小: {len(video_base64)} 字符")
            return video_base64
            
        except Exception as e:
            logger.error(f"视频转base64失败: {str(e)}")
            return None
    
    def audio_to_base64(self, audio):
        """
        将音频转换为base64编码
        
        Args:
            audio: 音频对象（AudioStream）
            
        Returns:
            str: base64编码的音频字符串
        """
        try:
            # 获取音频文件路径
            audio_path = None
            if hasattr(audio, 'get_stream_source'):
                audio_path = audio.get_stream_source()
            elif hasattr(audio, 'path'):
                audio_path = audio.path
            else:
                logger.error("无法获取音频路径")
                return None
            
            if not audio_path or not os.path.exists(audio_path):
                logger.error(f"音频文件不存在: {audio_path}")
                return None
            
            # 读取音频文件并转换为base64
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            logger.info(f"音频转base64成功，大小: {len(audio_base64)} 字符")
            return audio_base64
            
        except Exception as e:
            logger.error(f"音频转base64失败: {str(e)}")
            return None
    
    def call_multimodal_api(self, system_prompt, prompt, model,
                           image1=None, image2=None, image3=None, image4=None,
                           image5=None, image6=None, image7=None, image8=None, image9=None,
                           video=None, audio=None,
                           conversation_history="",
                           temperature=0.7, top_p=1.0, max_tokens=1024,
                           presence_penalty=0.0, frequency_penalty=0.0,
                           extra_params="", seed=0,
                           api_url="https://api.openai.com/v1/chat/completions",
                           api_key="", max_conversation_rounds=10):
        """
        调用多模态API
        
        Args:
            system_prompt: 系统提示词
            prompt: 文本提示词
            model: 模型名称
            images: 图片输入（可选）
            video: 视频输入（可选）
            audio: 音频输入（可选）
            conversation_history: 对话历史（JSON格式）
            temperature: 温度参数
            top_p: Top P参数
            max_tokens: 最大输出长度
            presence_penalty: 存在惩罚
            frequency_penalty: 频率惩罚
            extra_params: 额外的JSON参数
            seed: 随机种子
            api_url: API地址
            api_key: API密钥
            
        Returns:
            tuple: (响应文本, 对话历史, 原始响应JSON)
        """
        try:
            # 检查必需参数
            if not api_url:
                return ("错误：API地址不能为空", "", "")
            
            if not api_key:
                return ("错误：API密钥不能为空", "", "")
            
            if not prompt or not prompt.strip():
                return ("错误：提示词不能为空", "", "")
            
            # 自动补全URL路径
            api_url = api_url.strip()
            if not api_url.endswith('/chat/completions') and not api_url.endswith('/completions'):
                if api_url.endswith('/v1') or api_url.endswith('/v1/'):
                    api_url = api_url.rstrip('/') + '/chat/completions'
                    logger.info(f"自动补全API地址: {api_url}")
            
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # 构建消息内容
            message_content = []
            
            # 添加文本
            if prompt and prompt.strip():
                message_content.append({
                    "type": "text",
                    "text": prompt.strip()
                })
            
            # 添加图片
            image_inputs = [image1, image2, image3, image4, image5, image6, image7, image8, image9]
            image_count = 0
            for i, img in enumerate(image_inputs, 1):
                if img is not None:
                    logger.info(f"处理图片{i}输入...")
                    # 处理单张图片
                    if img.ndim == 3:
                        # 单张图片 [H, W, C]
                        img = img.unsqueeze(0)
                    
                    # 处理批次中的每张图片
                    for j in range(img.shape[0]):
                        img_base64 = self.image_to_base64(img[j:j+1])
                        if img_base64:
                            message_content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            })
                            image_count += 1
                            logger.info(f"已添加图片{i}的第{j+1}张")
            
            if image_count > 0:
                logger.info(f"总共添加了{image_count}张图片")
            
            # 添加视频（如果支持）
            if video is not None:
                logger.info("处理视频输入...")
                video_base64 = self.video_to_base64(video)
                if video_base64:
                    message_content.append({
                        "type": "video_url",
                        "video_url": {
                            "url": f"data:video/mp4;base64,{video_base64}"
                        }
                    })
                    logger.info("已添加视频")
                else:
                    logger.warning("视频处理失败")
            
            # 添加音频（如果支持）
            if audio is not None:
                logger.info("处理音频输入...")
                audio_base64 = self.audio_to_base64(audio)
                if audio_base64:
                    message_content.append({
                        "type": "audio_url",
                        "audio_url": {
                            "url": f"data:audio/mp3;base64,{audio_base64}"
                        }
                    })
                    logger.info("已添加音频")
                else:
                    logger.warning("音频处理失败")
            
            # 构建消息列表
            messages = []
            
            # 加载对话历史
            if conversation_history and conversation_history.strip():
                try:
                    history = json.loads(conversation_history.strip())
                    messages.extend(history)
                    logger.info(f"已加载 {len(history)} 条对话历史")
                except json.JSONDecodeError as e:
                    logger.warning(f"对话历史JSON解析失败: {str(e)}，将忽略历史")
            
            # 添加系统提示词
            if system_prompt and system_prompt.strip():
                messages.insert(0, {
                    "role": "system",
                    "content": system_prompt.strip()
                })
            
            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": message_content
            })
            
            # 构建请求体
            payload = {
                "model": model,
                "messages": messages,
                "temperature": float(temperature),
                "top_p": float(top_p),
                "max_tokens": int(max_tokens),
                "presence_penalty": float(presence_penalty),
                "frequency_penalty": float(frequency_penalty)
            }
            
            # 添加随机种子
            if seed > 0:
                payload["seed"] = int(seed)
            
            # 合并额外参数
            if extra_params and extra_params.strip():
                try:
                    extra_dict = json.loads(extra_params.strip())
                    payload.update(extra_dict)
                    logger.info(f"已合并额外参数: {list(extra_dict.keys())}")
                except json.JSONDecodeError as e:
                    logger.warning(f"额外参数JSON解析失败: {str(e)}")
            
            # 发送请求
            logger.info(f"正在调用多模态API: {api_url}")
            logger.info(f"使用模型: {model}")
            logger.info(f"消息数量: {len(messages)}")
            
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"API请求失败:\n状态码: {response.status_code}\n响应内容: {response.text[:500]}"
                logger.error(error_msg)
                
                if response.status_code == 404:
                    error_msg += "\n\n可能原因：\n1. API地址不正确\n2. 模型名称在该服务中不存在\n3. 模型不支持多模态输入"
                elif response.status_code == 401:
                    error_msg += "\n\n可能原因：\n1. API密钥错误或已过期\n2. 密钥格式不正确"
                elif response.status_code == 403:
                    error_msg += "\n\n可能原因：\n1. 账户余额不足\n2. 没有权限访问该模型"
                
                return (error_msg, conversation_history, response.text)
            
            # 检查响应内容
            if not response.text or response.text.strip() == "":
                error_msg = "API返回空响应"
                logger.error(error_msg)
                return (error_msg, conversation_history, "")
            
            # 解析响应
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:
                error_msg = f"API响应JSON解析失败:\n错误: {str(e)}\n响应内容: {response.text[:500]}"
                logger.error(error_msg)
                return (error_msg, conversation_history, response.text)
            
            raw_response = json.dumps(response_json, indent=2, ensure_ascii=False)
            
            # 检查错误
            if "error" in response_json:
                error_info = response_json["error"]
                error_msg = f"API返回错误:\n"
                if isinstance(error_info, dict):
                    error_msg += f"类型: {error_info.get('type', 'N/A')}\n"
                    error_msg += f"消息: {error_info.get('message', 'N/A')}\n"
                    error_msg += f"代码: {error_info.get('code', 'N/A')}"
                else:
                    error_msg += str(error_info)
                logger.error(error_msg)
                return (error_msg, conversation_history, raw_response)
            
            # 提取响应文本
            if "choices" in response_json and len(response_json["choices"]) > 0:
                choice = response_json["choices"][0]
                if "message" in choice:
                    response_text = choice["message"].get("content", "")
                elif "text" in choice:
                    response_text = choice["text"]
                else:
                    response_text = str(choice)
            elif "output" in response_json:
                response_text = response_json["output"]
            elif "text" in response_json:
                response_text = response_json["text"]
            else:
                response_text = raw_response
            
            # 更新对话历史
            messages.append({
                "role": "assistant",
                "content": response_text
            })
            
            # 保存对话历史（根据用户设置的轮数）
            # 1轮 = 1条用户消息 + 1条AI回复 = 2条消息
            max_messages = max_conversation_rounds * 2
            if len(messages) > max_messages:
                messages = messages[-max_messages:]
            
            new_history = json.dumps(messages, ensure_ascii=False, indent=2)
            
            logger.info(f"多模态API调用成功，已保存最近 {max_conversation_rounds} 轮对话")
            return (response_text, new_history, raw_response)
            
        except requests.exceptions.Timeout:
            error_msg = "API请求超时（120秒）"
            logger.error(error_msg)
            return (error_msg, conversation_history, "")
        except requests.exceptions.ConnectionError as e:
            error_msg = f"API连接失败:\n错误: {str(e)}"
            logger.error(error_msg)
            return (error_msg, conversation_history, "")
        except requests.exceptions.RequestException as e:
            error_msg = f"API请求异常: {str(e)}"
            logger.error(error_msg)
            return (error_msg, conversation_history, "")
        except Exception as e:
            error_msg = f"调用API时发生错误: {str(e)}"
            logger.error(error_msg)
            import traceback
            traceback.print_exc()
            return (error_msg, conversation_history, "")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "GenericAPIMultimodalNode": GenericAPIMultimodalNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "GenericAPIMultimodalNode": "通用API-多模态-beta"
}

# 导出映射
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
