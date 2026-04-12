import requests
import json
import os
import time

# 检查openai库是否可用
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 支持的文本生成模型列表
SUPPORTED_TEXT_GENERATION_MODELS = [
    ("Qwen/Qwen3-VL-235B-A22B-Instruct", "Qwen3-VL 235B A22B Instruct"),
]

def load_api_token():
    return ""

def save_api_token(token):
    return True

class ModelscopeApiTextGenerationNode:
    """魔搭API文本生成节点 - 用于生成文本内容"""
    def __init__(self):
        pass
    
    def parse_api_token(self, token_input):
        """解析输入的单个API Token"""
        if not token_input or token_input.strip() == "":
            # 尝试加载保存的token
            saved_token = load_api_token()
            if saved_token:
                return saved_token
            return ""
        
        # 返回单个Token
        return token_input.strip()
    
    @classmethod
    def INPUT_TYPES(cls):
        if not OPENAI_AVAILABLE:
            return {
                "required": {
                    "error_message": ("STRING", {
                        "default": "请先安装openai库: pip install openai",
                        "multiline": True
                    }),
                }
            }
        saved_token = load_api_token()
        return {
            "required": {
                "system_prompt": ("STRING", {
                    "default": "",
                    "label": "系统提示词",
                    "description": "系统级别的提示词，用于设定AI的行为",
                    "multiline": True
                }),
                "prompt": ("STRING", {
                    "default": "",
                    "label": "提示词",
                    "description": "用于文本生成的提示词",
                    "multiline": True
                }),
                "model_name": ("STRING", {
                    "default": "Qwen/Qwen3-VL-235B-A22B-Instruct",
                    "options": [model[0] for model in SUPPORTED_TEXT_GENERATION_MODELS],
                    "labels": {model[0]: model[1] for model in SUPPORTED_TEXT_GENERATION_MODELS},
                    "label": "模型名称"
                }),
                "max_tokens": ("INT", {
                    "default": 1000,
                    "min": 100,
                    "max": 4000,
                    "label": "最大令牌数",
                    "description": "生成文本的最大长度"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.1,
                    "label": "温度系数",
                    "description": "控制生成文本的随机性"
                }),
                "top_p": ("FLOAT", {
                    "default": 0.9,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.1,
                    "label": "Top P",
                    "description": "控制生成文本的多样性"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "label": "随机种子"
                }),
                "api_token": ("STRING", {
                    "default": saved_token,
                    "label": "API Token",
                    "description": "modelscope API 令牌",
                    "placeholder": "请输入您的 modelscope API Token",
                    "multiline": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("生成文本",)
    FUNCTION = "generate_text"
    CATEGORY = "XnanTool/魔搭api"
    
    def generate_text(self, system_prompt, prompt, model_name, max_tokens, temperature, top_p, seed, api_token):
        if not OPENAI_AVAILABLE:
            return ("请先安装openai库: pip install openai",)
        
        # 解析单个API Token
        token = self.parse_api_token(api_token)
        if not token:
            raise Exception("请输入有效的API Token")
        
        # 保存新Token（如果有变化）
        saved_token = load_api_token()
        if api_token.strip() != saved_token:
            if save_api_token(token):
                print("✅ API Token已自动保存")
            else:
                print("⚠️ API Token保存失败，但不影响当前使用")
        
        try:
            print(f"📝 开始生成文本...")
            print(f"🔤 提示词: {prompt}")
            print(f"🤖 模型: {model_name}")
            print(f"🔑 使用API Token: {token[:10]}...")
            
            try:
                print(f"🔄 使用API Token进行调用...")
                
                # 初始化OpenAI客户端
                client = OpenAI(
                    base_url='https://api-inference.modelscope.cn/v1',
                    api_key=token
                )
                
                # 构建消息体
                messages = []
                if system_prompt.strip():
                    messages.append({
                        'role': 'system',
                        'content': system_prompt,
                    })
                
                messages.append({
                    'role': 'user',
                    'content': prompt,
                })
                
                # 调用API（使用选中的模型）
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    seed=seed if seed >= 0 else None,
                    stream=False
                )
                
                # 检查响应是否有效
                if not response or not response.choices or len(response.choices) == 0:
                    raise Exception("API返回空响应，可能是模型调用失败")
                
                # 成功获取结果
                generated_text = response.choices[0].message.content
                print(f"✅ API调用成功!")
                print(f"📄 结果预览: {generated_text[:100]}...")
                return (generated_text,)
                
            except Exception as e:
                error_msg = f"API调用失败: {str(e)}"
                print(f"❌ {error_msg}")
                if 'response' in locals():
                    print(f"🔍 响应详情: {response}")
                return (error_msg,)
            
        except Exception as e:
            error_msg = f"文本生成失败: {str(e)}"
            print(f"❌ {error_msg}")
            return (error_msg,)

# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "ModelscopeApiTextGenerationNode": ModelscopeApiTextGenerationNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ModelscopeApiTextGenerationNode": "魔搭API-文本生成",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']