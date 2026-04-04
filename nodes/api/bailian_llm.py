import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    "deepseek-v3.2": "DeepSeek V3.2（最新，推荐）",
    "deepseek-v3.2-exp": "DeepSeek V3.2实验版",
    "deepseek-v3.1": "DeepSeek V3.1",
    "deepseek-r1": "DeepSeek R1（思考模式）",
    "deepseek-r1-0528": "DeepSeek R1 0528版",
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
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "提示词",
                    "description": "输入给大模型的提示词"
                }),
                "model": (["qwen3-max", "qwen3-max-2026-01-23", "qwen3-max-2025-09-23", "qwen3-max-preview",
                          "qwen-max", "qwen-max-latest", "qwen-max-2025-01-25", "qwen-max-2024-09-19", "qwen-max-2024-04-28",
                          "qwen3.5-plus", "qwen3.5-plus-2026-02-15",
                          "qwen-plus", "qwen-plus-latest", "qwen-plus-2025-12-01", "qwen-plus-2025-09-11", "qwen-plus-2025-07-28", "qwen-plus-2025-07-14", "qwen-plus-2025-04-28", "qwen-plus-2025-01-25", "qwen-plus-2025-01-12", "qwen-plus-2024-12-20",
                          "qwen-flash", "qwen-flash-latest", "qwen-flash-2025-12-01", "qwen-flash-2025-09-11", "qwen-flash-2025-07-28", "qwen-flash-2025-07-14", "qwen-flash-2025-04-28", "qwen-flash-2025-01-25", "qwen-flash-2025-01-12", "qwen-flash-2024-12-20",
                          "qwen3-plus", "qwen3-plus-2025-12-01", "qwen3-plus-2025-09-11", "qwen3-plus-2025-07-28", "qwen3-plus-2025-07-14", "qwen3-plus-2025-04-28", "qwen3-plus-2025-01-25", "qwen3-plus-2025-01-12", "qwen3-plus-2024-12-20",
                          "qwen3-flash", "qwen3-flash-2025-12-01", "qwen3-flash-2025-09-11", "qwen3-flash-2025-07-28", "qwen3-flash-2025-07-14", "qwen3-flash-2025-04-28", "qwen3-flash-2025-01-25", "qwen3-flash-2025-01-12", "qwen3-flash-2024-12-20",
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
                    "description": "仅适用于deepseek-r1系列模型，开启思考模式"
                }),
                "endpoint": ("STRING", {
                    "default": "https://dashscope.aliyuncs.com/api/v1",
                    "multiline": False,
                    "label": "Endpoint URL",
                    "description": "阿里云百炼API Endpoint（默认：https://dashscope.aliyuncs.com/api/v1）"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "call_llm"
    CATEGORY = "XnanTool/API/阿里百炼"
    
    def call_llm(self, prompt, model, api_key=None, temperature=0.7, top_p=0.95, max_tokens=1024, enable_thinking="false", endpoint="https://dashscope.aliyuncs.com/api/v1"):
        """
        调用阿里云百炼LLM
        
        Args:
            prompt: 输入提示词
            model: 模型名称
            api_key: API Key
            temperature: 温度参数
            top_p: Top P参数
            max_tokens: 最大输出长度
            enable_thinking: 是否开启思考模式
            endpoint: API Endpoint URL
            
        Returns:
            tuple: (响应文本,)
        """
        try:
            # 检查提示词
            if not prompt or not prompt.strip():
                return ("错误：提示词不能为空",)
            
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
            
            # 设置endpoint URL（根据用户输入或默认值）
            # DashScope SDK使用base_http_api_url参数
            dashscope.base_http_api_url = endpoint
            
            # 构建调用参数
            params = {
                "model": model,
                "prompt": prompt.strip(),
                "result_format": 'message',
                "temperature": float(temperature),
                "top_p": float(top_p),
                "max_tokens": int(max_tokens)
            }
            
            # 如果开启思考模式（仅适用于deepseek-r1系列）
            if enable_thinking == "true":
                params["enable_thinking"] = True
                params["incremental_output"] = True
            
            # 调用模型
            try:
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
                # 检查是否是配额问题
                if "FreeTierOnly" in error_str or "free tier" in error_str.lower():
                    error_msg = f"请求失败:\n错误: 免费额度已用完，请在阿里云控制台启用付费模式\n详细信息: {error_str}"
                else:
                    error_msg = f"请求失败:\n错误: {error_str}"
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
