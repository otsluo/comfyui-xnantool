# Ollama节点模块初始化文件

# 导入Ollama相关节点
from .OllamaOptionsRefactored import OllamaOptionsRefactored
from .OllamaConnectivityRefactored import OllamaConnectivityRefactored
from .OllamaGenerateRefactored import OllamaGenerateRefactored
from .OllamaChatRefactored import OllamaChatRefactored

# 定义节点映射
NODE_CLASS_MAPPINGS = {
    "OllamaOptionsRefactored": OllamaOptionsRefactored,
    "OllamaConnectivityRefactored": OllamaConnectivityRefactored,
    "OllamaGenerateRefactored": OllamaGenerateRefactored,
    "OllamaChatRefactored": OllamaChatRefactored,
}

# 定义节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaOptionsRefactored": "Ollama选项-重构版",
    "OllamaConnectivityRefactored": "Ollama连接性-重构版",
    "OllamaGenerateRefactored": "Ollama生成-重构版",
    "OllamaChatRefactored": "Ollama聊天-重构版",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']