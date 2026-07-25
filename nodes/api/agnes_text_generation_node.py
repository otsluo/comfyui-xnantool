import requests
import json


class AgnesTextGenerationNode:
    """
    Agnes AI 文本生成节点 - 支持 Agnes 1.5 Flash 和 2.0 Flash 模型
    """

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
                    "description": "输入给模型的提示词"
                }),
                "model": (["agnes-1.5-flash", "agnes-2.0-flash", "agnes-2.5-flash", "agnes-2.5-pro-alpha"], {
                    "default": "agnes-2.5-flash",
                    "label": "模型",
                    "description": "选择要使用的文本模型"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "label": "温度",
                    "description": "控制输出的随机性，值越大越随机"
                }),
                "max_tokens": ("INT", {
                    "default": 4096,
                    "min": 1,
                    "max": 65536,
                    "step": 1,
                    "label": "最大输出长度",
                    "description": "最大输出Token数量"
                }),
                "top_p": ("FLOAT", {
                    "default": 0.95,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "label": "Top P",
                    "description": "累积概率阈值，控制生成的多样性"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999999999,
                    "step": 1,
                    "label": "随机种子",
                    "description": "随机种子（0为随机）"
                }),
            },
            "optional": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "password": True,
                    "label": "API Key",
                    "description": "Agnes AI API Key"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "generate_text"
    CATEGORY = "❤️❤️❤️XnanTool/API/Agnes AI"
    DESCRIPTION = "Agnes AI 文本生成节点，支持 Agnes 1.5 Flash 和 2.0 Flash 模型。"

    def generate_text(self, system_prompt, prompt, model, api_key, temperature, max_tokens, top_p, seed):
        """
        调用 Agnes AI 文本生成 API
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("请填写 Agnes AI API Key")

        if not prompt or prompt.strip() == "":
            raise ValueError("请输入提示词")

        # 构造消息列表
        messages = []
        if system_prompt and system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # 构造请求参数
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }
        if seed > 0:
            payload["seed"] = seed

        # 发送请求
        url = "https://apihub.agnes-ai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()

            # 提取回复内容
            if "choices" in result and len(result["choices"]) > 0:
                text_output = result["choices"][0].get("message", {}).get("content", "")
                return (text_output,)
            else:
                raise ValueError(f"API 返回格式异常: {result}")

        except requests.exceptions.Timeout:
            raise Exception("请求超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"文本生成失败: {str(e)}")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "AgnesTextGenerationNode": AgnesTextGenerationNode,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "AgnesTextGenerationNode": "Agnes AI-文本生成",
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
