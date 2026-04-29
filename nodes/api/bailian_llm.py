import os
import logging
import socket
from urllib3.util import connection

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 强制使用 IPv4（解决 dashscope.aliyuncs.com 不支持 IPv6 导致的 DNS 解析失败问题）
def allowed_gai_family():
    return socket.AF_INET  # 仅使用 IPv4

connection.allowed_gai_family = allowed_gai_family

# 模型说明
MODEL_DESCRIPTIONS = {
    "qwen3-max": "通义千问3 Max（推荐）",
    "qwen3-max-2026-01-23": "通义千问3 Max 2026-01-23",
    "qwen3-max-2025-09-23": "通义千问3 Max 2025-09-23",
    "qwen3-max-preview": "通义千问3 Max 预览版",
    "qwen-max": "通义千问 Max",
    "qwen-max-latest": "通义千问 Max 最新版",
    "qwen-max-2025-01-25": "通义千问 Max 2025-01-25",
    "qwen-max-2024-09-19": "通义千问 Max 2024-09-19",
    "qwen-max-2024-04-28": "通义千问 Max 2024-04-28",
    "qwen3.5-plus": "通义千问3.5 Plus（推荐）",
    "qwen3.5-plus-2026-02-15": "通义千问3.5 Plus 2026-02-15",
    "qwen-plus": "通义千问 Plus",
    "qwen-plus-latest": "通义千问 Plus 最新版",
    "qwen-plus-2025-12-01": "通义千问 Plus 2025-12-01",
    "qwen-plus-2025-09-11": "通义千问 Plus 2025-09-11",
    "qwen-plus-2025-07-28": "通义千问 Plus 2025-07-28",
    "qwen-plus-2025-07-14": "通义千问 Plus 2025-07-14",
    "qwen-plus-2025-04-28": "通义千问 Plus 2025-04-28",
    "qwen-plus-2025-01-25": "通义千问 Plus 2025-01-25",
    "qwen-plus-2025-01-12": "通义千问 Plus 2025-01-12",
    "qwen-plus-2024-12-20": "通义千问 Plus 2024-12-20",
    "qwen-flash": "通义千问 Flash",
    "qwen-flash-latest": "通义千问 Flash 最新版",
    "qwen-flash-2025-12-01": "通义千问 Flash 2025-12-01",
    "qwen-flash-2025-09-11": "通义千问 Flash 2025-09-11",
    "qwen-flash-2025-07-28": "通义千问 Flash 2025-07-28",
    "qwen-flash-2025-07-14": "通义千问 Flash 2025-07-14",
    "qwen-flash-2025-04-28": "通义千问 Flash 2025-04-28",
    "qwen-flash-2025-01-25": "通义千问 Flash 2025-01-25",
    "qwen-flash-2025-01-12": "通义千问 Flash 2025-01-12",
    "qwen-flash-2024-12-20": "通义千问 Flash 2024-12-20",
    "qwen3-plus": "通义千问3 Plus",
    "qwen3-plus-2025-12-01": "通义千问3 Plus 2025-12-01",
    "qwen3-plus-2025-09-11": "通义千问3 Plus 2025-09-11",
    "qwen3-plus-2025-07-28": "通义千问3 Plus 2025-07-28",
    "qwen3-plus-2025-07-14": "通义千问3 Plus 2025-07-14",
    "qwen3-plus-2025-04-28": "通义千问3 Plus 2025-04-28",
    "qwen3-plus-2025-01-25": "通义千问3 Plus 2025-01-25",
    "qwen3-plus-2025-01-12": "通义千问3 Plus 2025-01-12",
    "qwen3-plus-2024-12-20": "通义千问3 Plus 2024-12-20",
    "qwen3-flash": "通义千问3 Flash",
    "qwen3-flash-2025-12-01": "通义千问3 Flash 2025-12-01",
    "qwen3-flash-2025-09-11": "通义千问3 Flash 2025-09-11",
    "qwen3-flash-2025-07-28": "通义千问3 Flash 2025-07-28",
    "qwen3-flash-2025-07-14": "通义千问3 Flash 2025-07-14",
    "qwen3-flash-2025-04-28": "通义千问3 Flash 2025-04-28",
    "qwen3-flash-2025-01-25": "通义千问3 Flash 2025-01-25",
    "qwen3-flash-2025-01-12": "通义千问3 Flash 2025-01-12",
    "qwen3-flash-2024-12-20": "通义千问3 Flash 2024-12-20",
    "qwen3.5-122b-a10b": "通义千问3.5 122B A10（高性能）",
    "deepseek-v3.2": "DeepSeek V3.2（最新，推荐）",
    "deepseek-v3.2-exp": "DeepSeek V3.2实验版",
    "deepseek-v3.1": "DeepSeek V3.1",
    "deepseek-r1": "DeepSeek R1（思考模式）",
    "deepseek-r1-0528": "DeepSeek R1 0528版（思考模式）",
    "deepseek-v3": "DeepSeek V3",
    "deepseek-r1-distill-qwen-1.5b": "DeepSeek蒸馏版1.5b",
    "deepseek-r1-distill-qwen-7b": "DeepSeek蒸馏版7b",
    "deepseek-r1-distill-qwen-14b": "DeepSeek蒸馏版14b",
    "deepseek-r1-distill-qwen-32b": "DeepSeek蒸馏版32b",
    "deepseek-r1-distill-llama-8b": "DeepSeek蒸馏版Llama 8b",
    "deepseek-r1-distill-llama-70b": "DeepSeek蒸馏版Llama 70b",
}

class BailianLLMNode:
    """
    阿里云百炼LLM节点 - 调用阿里云百炼大模型服务（直接调用模型API）
    """
    
    def __init__(self):
        self.api_key = None
    
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
                    "label": "用户提示词",
                    "description": "输入给大模型的用户提示词"
                }),
                "model": (["qwen3-max", "qwen3-max-2026-01-23", "qwen3-max-2025-09-23", "qwen3-max-preview",
                          "qwen-max", "qwen-max-latest", "qwen-max-2025-01-25", "qwen-max-2024-09-19", "qwen-max-2024-04-28",
                          "qwen3.5-plus", "qwen3.5-plus-2026-02-15",
                          "qwen-plus", "qwen-plus-latest", "qwen-plus-2025-12-01", "qwen-plus-2025-09-11", "qwen-plus-2025-07-28", "qwen-plus-2025-07-14", "qwen-plus-2025-04-28", "qwen-plus-2025-01-25", "qwen-plus-2025-01-12", "qwen-plus-2024-12-20",
                          "qwen-flash", "qwen-flash-latest", "qwen-flash-2025-12-01", "qwen-flash-2025-09-11", "qwen-flash-2025-07-28", "qwen-flash-2025-07-14", "qwen-flash-2025-04-28", "qwen-flash-2025-01-25", "qwen-flash-2025-01-12", "qwen-flash-2024-12-20",
                          "qwen3-plus", "qwen3-plus-2025-12-01", "qwen3-plus-2025-09-11", "qwen3-plus-2025-07-28", "qwen3-plus-2025-07-14", "qwen3-plus-2025-04-28", "qwen3-plus-2025-01-25", "qwen3-plus-2025-01-12", "qwen3-plus-2024-12-20",
                          "qwen3-flash", "qwen3-flash-2025-12-01", "qwen3-flash-2025-09-11", "qwen3-flash-2025-07-28", "qwen3-flash-2025-07-14", "qwen3-flash-2025-04-28", "qwen3-flash-2025-01-25", "qwen3-flash-2025-01-12", "qwen3-flash-2024-12-20",
                          "qwen3.5-122b-a10b",
                          "deepseek-v3.2", "deepseek-v3.2-exp", "deepseek-v3.1", "deepseek-r1", "deepseek-r1-0528", "deepseek-v3",
                          "deepseek-r1-distill-qwen-1.5b", "deepseek-r1-distill-qwen-7b", "deepseek-r1-distill-qwen-14b", "deepseek-r1-distill-qwen-32b", "deepseek-r1-distill-llama-8b", "deepseek-r1-distill-llama-70b"], {
                    "default": "qwen3-max",
                    "label": "模型",
                    "description": "选择要使用的模型"
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
                "enable_thinking": (["true", "false"], {
                    "default": "false",
                    "label": "思考模式",
                    "description": "仅适用于 deepseek-r1 系列模型（deepseek-r1、deepseek-r1-0528），开启思考模式可获得更长推理链"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999999999,
                    "step": 1,
                    "label": "随机种子",
                    "description": "随机种子（0为随机）"
                }),
                "endpoint": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "Endpoint URL",
                    "description": "阿里云百炼API Endpoint（留空使用默认值，SDK无需配置）"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "call_llm"
    CATEGORY = "XnanTool/API/阿里百炼"
    
    def call_llm(self, system_prompt, prompt, model, api_key=None, temperature=0.7, top_p=0.95, max_tokens=1024, enable_thinking="false", seed=0, endpoint=None):
        """
        调用阿里云百炼LLM
        
        Args:
            system_prompt: 系统提示词
            prompt: 用户提示词
            model: 模型名称
            api_key: API Key
            temperature: 温度参数
            top_p: Top P参数
            max_tokens: 最大输出长度
            enable_thinking: 是否开启思考模式
            seed: 随机种子
            endpoint: API Endpoint URL（已废弃，SDK自动使用默认值）
            
        Returns:
            tuple: (响应文本,)
        """
        try:
            # 检查提示词
            if not prompt or not prompt.strip():
                return ("错误：用户提示词不能为空",)
            
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
            
            # 根据模型选择调用方式
            # qwen3.5-122b-a10b 等新模型需要使用 compatible-mode endpoint
            new_models = [
                "qwen3.5-122b-a10b", "qwen3.5-397b-a17b", "qwen3.5-27b", "qwen3.5-35b-a3b",
                "qwen3.6-plus", "qwen3.6-plus-2026-04-02", "qwen3.5-plus", "qwen3.5-plus-2026-02-15",
                "qwen3.5-flash", "qwen3.5-flash-2026-02-23", "qwen3-max", "qwen3-max-2026-01-23",
                "qwen3-max-preview", "qwen3-flash", "qwen3-flash-2025-12-01", "qwen3-flash-2025-09-11",
                "qwen3-flash-2025-07-28", "qwen3-flash-2025-07-14", "qwen3-flash-2025-04-28",
                "qwen3-flash-2025-01-25", "qwen3-flash-2025-01-12", "qwen3-flash-2024-12-20"
            ]
            
            if model in new_models:
                # 使用 compatible-mode endpoint（OpenAI 兼容格式）
                dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
                logger.info(f"使用 compatible-mode endpoint: https://dashscope.aliyuncs.com/compatible-mode/v1")
                
                # 构建调用参数（使用 input 格式，兼容 new models）
                # 对于 compatible-mode，使用 input 格式，将 system 和 user 消息合并
                if system_prompt:
                    input_text = f"{system_prompt.strip()}\n\n{prompt.strip()}"
                else:
                    input_text = prompt.strip()
                
                params = {
                    "model": model,
                    "input": input_text
                }
                
                # 如果开启思考模式，通过 extra_body 传递（仅适用于支持的模型）
                if enable_thinking == "true":
                    params["extra_body"] = {"enable_thinking": True}
                
                try:
                    from openai import OpenAI
                    client = OpenAI(
                        api_key=api_key,
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                    )
                    response = client.responses.create(**params)
                    response_text = response.output_text
                    logger.info(f"百炼LLM调用成功")
                    return (response_text,)
                except ImportError:
                    return ("错误：请安装 openai SDK: pip install openai",)
                except Exception as e:
                    error_str = str(e)
                    error_details = f"错误类型: {type(e).__name__}\n错误信息: {error_str}"
                    
                    if hasattr(e, 'status_code'):
                        error_details += f"\n状态码: {getattr(e, 'status_code', 'N/A')}"
                    if hasattr(e, 'code'):
                        error_details += f"\n错误码: {getattr(e, 'code', 'N/A')}"
                    if hasattr(e, 'message'):
                        error_details += f"\n消息: {getattr(e, 'message', 'N/A')}"
                    if hasattr(e, 'request_id'):
                        error_details += f"\n请求ID: {getattr(e, 'request_id', 'N/A')}"
                    
                    if "FreeTierOnly" in error_str or "free tier" in error_str.lower():
                        error_msg = f"请求失败:\n错误: 免费额度已用完，请在阿里云控制台启用付费模式\n详细信息: {error_details}"
                    else:
                        error_msg = f"请求失败:\n错误: {error_details}"
                    logger.error(error_msg)
                    return (error_msg,)
            else:
                # 使用旧版 DashScope API
                dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
                logger.info(f"使用 DashScope API: https://dashscope.aliyuncs.com/api/v1")
                
                # 构建调用参数（使用 messages 格式）
                messages = [
                    {"role": "system", "content": system_prompt.strip()} if system_prompt else None,
                    {"role": "user", "content": prompt.strip()}
                ]
                messages = [m for m in messages if m is not None]
                
                params = {
                    "model": model,
                    "messages": messages,
                    "result_format": 'message',
                    "temperature": float(temperature),
                    "top_p": float(top_p),
                    "max_tokens": int(max_tokens),
                    "seed": int(seed) if seed > 0 else None
                }
                
                # 移除None值
                params = {k: v for k, v in params.items() if v is not None}
                
                # 如果开启思考模式（仅适用于deepseek-r1系列）
                if enable_thinking == "true":
                    params["enable_thinking"] = True
                
                # 调用模型
                try:
                    logger.info(f"开始调用模型: {model}")
                    logger.info(f"调用参数: {list(params.keys())}")
                    response = dashscope.Generation.call(**params)
                    
                    # 检查响应状态
                    if hasattr(response, 'status_code') and response.status_code != 200:
                        # API 调用失败，从响应中提取错误信息
                        error_msg = f"请求失败:\n状态码: {getattr(response, 'status_code', 'N/A')}\n消息: {getattr(response, 'message', 'N/A')}\n请求ID: {getattr(response, 'request_id', 'N/A')}"
                        logger.error(error_msg)
                        return (error_msg,)
                    
                    # result_format为message时，响应结构为response.output.choices[0].message.content
                    if hasattr(response, 'output') and response.output is not None:
                        if hasattr(response.output, 'choices') and len(response.output.choices) > 0:
                            response_text = response.output.choices[0].message.content
                        elif hasattr(response.output, 'text'):
                            response_text = response.output.text
                        else:
                            response_text = str(response.output)
                    else:
                        response_text = str(response)
                    logger.info(f"百炼LLM调用成功")
                    return (response_text,)
                except Exception as e:
                    error_str = str(e)
                    error_details = f"错误类型: {type(e).__name__}\n错误信息: {error_str}"
                    
                    # 检查是否是网络连接问题
                    if "getaddrinfo" in error_str or "ConnectionError" in error_str or "Failed to establish a new connection" in error_str:
                        error_details += "\n\n可能原因：\n1. 无法访问互联网或阿里云 API 服务\n2. DNS 解析失败\n3. 防火墙或代理设置阻止连接\n4. 请检查网络连接，尝试使用 VPN"
                    
                    if hasattr(e, 'status_code'):
                        error_details += f"\n状态码: {getattr(e, 'status_code', 'N/A')}"
                    if hasattr(e, 'code'):
                        error_details += f"\n错误码: {getattr(e, 'code', 'N/A')}"
                    if hasattr(e, 'message'):
                        error_details += f"\n消息: {getattr(e, 'message', 'N/A')}"
                    if hasattr(e, 'request_id'):
                        error_details += f"\n请求ID: {getattr(e, 'request_id', 'N/A')}"
                    
                    # 检查是否是配额问题
                    if "FreeTierOnly" in error_str or "free tier" in error_str.lower():
                        error_msg = f"请求失败:\n错误: 免费额度已用完，请在阿里云控制台启用付费模式\n详细信息: {error_details}"
                    else:
                        error_msg = f"请求失败:\n错误: {error_details}"
                    logger.error(error_msg)
                    return (error_msg,)
        except Exception as e:
            error_msg = f"调用百炼LLM时发生错误: {str(e)}"
            logger.error(error_msg)
            return (error_msg,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "BailianLLMNode": BailianLLMNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BailianLLMNode": "百炼LLM-文本生成",
}
