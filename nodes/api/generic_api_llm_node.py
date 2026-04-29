import os
import logging
import json
import requests
import socket
from urllib3.util import connection

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 强制使用 IPv4（解决某些域名不支持 IPv6 导致的 DNS 解析失败问题）
def allowed_gai_family():
    return socket.AF_INET  # 仅使用 IPv4

connection.allowed_gai_family = allowed_gai_family

class GenericAPILLMNode:
    """
    通用LLM API调用节点 - 支持调用任何OpenAI兼容的大语言模型API服务
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
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
                "model": ("STRING", {
                    "default": "gpt-3.5-turbo",
                    "multiline": False,
                    "label": "模型名称",
                    "description": "要调用的模型名称"
                }),
                "system_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "系统提示词",
                    "description": "系统提示词，用于设定模型的角色和行为规范"
                }),
                "user_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "用户提示词",
                    "description": "输入给模型的用户提示词"
                }),
            },
            "optional": {
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
    RETURN_NAMES = ("response", "raw_response")
    FUNCTION = "call_llm_api"
    CATEGORY = "XnanTool/API/LLM"
    
    def call_llm_api(self, api_url, api_key, model, system_prompt, user_prompt, 
                 temperature=0.7, top_p=1.0, max_tokens=1024, 
                 presence_penalty=0.0, frequency_penalty=0.0, extra_params="", seed=0):
        """
        调用大语言模型API
        
        Args:
            api_url: API的完整URL
            api_key: API密钥
            model: 模型名称
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数
            top_p: Top P参数
            max_tokens: 最大输出长度
            presence_penalty: 存在惩罚
            frequency_penalty: 频率惩罚
            extra_params: 额外的JSON参数
            seed: 随机种子
            
        Returns:
            tuple: (响应文本, 原始响应JSON)
        """
        try:
            # 检查必需参数
            if not api_url:
                return ("错误：API地址不能为空", "")
            
            if not api_key:
                return ("错误：API密钥不能为空", "")
            
            if not user_prompt or not user_prompt.strip():
                return ("错误：用户提示词不能为空", "")
            
            # 自动补全URL路径（如果用户只输入了基础URL）
            api_url = api_url.strip()
            if not api_url.endswith('/chat/completions') and not api_url.endswith('/completions'):
                # 检查是否是常见的基础URL格式
                if api_url.endswith('/v1') or api_url.endswith('/v1/'):
                    api_url = api_url.rstrip('/') + '/chat/completions'
                    logger.info(f"自动补全API地址: {api_url}")
            
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # 构建消息列表
            messages = []
            if system_prompt and system_prompt.strip():
                messages.append({
                    "role": "system",
                    "content": system_prompt.strip()
                })
            
            messages.append({
                "role": "user",
                "content": user_prompt.strip()
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
            
            # 添加随机种子（0表示随机）
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
            logger.info(f"正在调用API: {api_url}")
            logger.info(f"使用模型: {model}")
            logger.info(f"请求参数: {json.dumps(payload, ensure_ascii=False)[:500]}...")
            
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
                
                # 提供常见错误的原因分析
                if response.status_code == 404:
                    error_msg += "\n\n可能原因：\n1. API地址不正确（需要包含完整路径，如 /v1/chat/completions）\n2. 模型名称在该服务中不存在\n3. 请检查API文档确认正确的端点地址"
                elif response.status_code == 401:
                    error_msg += "\n\n可能原因：\n1. API密钥错误或已过期\n2. 密钥格式不正确"
                elif response.status_code == 403:
                    error_msg += "\n\n可能原因：\n1. 账户余额不足或免费额度已用完\n2. 没有权限访问该模型"
                
                return (error_msg, response.text)
            
            # 检查响应内容是否为空
            if not response.text or response.text.strip() == "":
                error_msg = "API返回空响应，请检查：\n1. API地址是否正确（需要包含完整路径）\n2. 模型名称是否正确"
                logger.error(error_msg)
                return (error_msg, "")
            
            # 解析响应
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:
                error_msg = f"API响应JSON解析失败:\n错误: {str(e)}\n响应内容: {response.text[:500]}\n\n可能原因：\n1. API地址不正确\n2. 返回的不是JSON格式数据"
                logger.error(error_msg)
                return (error_msg, response.text)
            
            raw_response = json.dumps(response_json, indent=2, ensure_ascii=False)
            
            # 检查是否有错误信息
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
                return (error_msg, raw_response)
            
            # 提取响应文本（OpenAI兼容格式）
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
            
            logger.info(f"API调用成功")
            return (response_text, raw_response)
            
        except requests.exceptions.Timeout:
            error_msg = "API请求超时（120秒），请检查网络连接或增加超时时间"
            logger.error(error_msg)
            return (error_msg, "")
        except requests.exceptions.ConnectionError as e:
            error_msg = f"API连接失败:\n错误: {str(e)}\n\n可能原因：\n1. 无法访问API服务\n2. DNS解析失败\n3. 防火墙或代理设置阻止连接"
            logger.error(error_msg)
            return (error_msg, "")
        except requests.exceptions.RequestException as e:
            error_msg = f"API请求异常: {str(e)}"
            logger.error(error_msg)
            return (error_msg, "")
        except Exception as e:
            error_msg = f"调用API时发生错误: {str(e)}"
            logger.error(error_msg)
            return (error_msg, "")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "GenericAPILLMNode": GenericAPILLMNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GenericAPILLMNode": "通用LLM API调用"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
