import random

from ollama import Client, AsyncClient
import numpy as np
from io import BytesIO
from pprint import pprint
from PIL import Image


class OllamaConnectivityRefactored:
    """
    重构版 Ollama 连接节点，支持异步处理和改进的错误处理。
    """
    
    @classmethod
    def INPUT_TYPES(s):
        seed = random.randint(1, 2**31)
        return {
            "required": {
                "url": ("STRING", {
                    "multiline": False,
                    "default": "http://127.0.0.1:11434"
                }),
                "model": ((), {}),
                "timeout": ("INT", {"default": 30, "min": 1, "max": 300, "step": 1}),
                "keep_alive": ("INT", {"default": 5, "min": -1, "max": 60, "step": 1}),
                "keep_alive_unit": (["seconds", "minutes", "hours"], {"default": "minutes"}),
                "seed": ("INT", {"default": seed, "min": 0, "max": 2**31, "step": 1}),
            },
        }

    RETURN_TYPES = ("OLLAMA_CONNECTIVITY",)
    RETURN_NAMES = ("connection",)
    FUNCTION = "connect"
    CATEGORY = "XnanTool/Ollama"
    DESCRIPTION = "重构版 Ollama 服务器连接，支持超时设置、保持连接和随机种子配置。"

    def connect(self, url, model, timeout, keep_alive, keep_alive_unit, seed):
        # 设置随机种子
        random.seed(seed)
        
        # 处理 keep_alive 的单位转换
        if keep_alive_unit == "minutes":
            keep_alive *= 60
        elif keep_alive_unit == "hours":
            keep_alive *= 3600
        # 如果是 seconds，则保持原值不变
        
        data = {
            "url": url,
            "model": model,
            "timeout": timeout,
            "keep_alive": keep_alive,
            "keep_alive_unit": keep_alive_unit,
            "seed": seed,
        }
        return (data,)


NODE_CLASS_MAPPINGS = {
    "OllamaConnectivityRefactored": OllamaConnectivityRefactored,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaConnectivityRefactored": "Ollama连接-重构版",
}