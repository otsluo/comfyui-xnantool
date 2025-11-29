import random
from pprint import pprint


class OllamaOptionsRefactored:
    """
    重构版的 Ollama 选项节点，具有以下改进：
    1. 更清晰的参数组织和分组
    2. 增强的参数说明和工具提示
    3. 改进的默认值设置
    4. 更好的可维护性和扩展性
    """
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        seed = random.randint(1, 2 ** 31)
        return {
            "required": {
                # Mirostat 采样参数
                "enable_mirostat": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用 Mirostat 采样。Mirostat 是一种在文本生成过程中主动维持生成文本质量在期望范围内的算法。"
                }),
                "mirostat": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 2, 
                    "step": 1, 
                    "tooltip": "Mirostat 采样模式 (0 = 禁用, 1 = Mirostat 1, 2 = Mirostat 2.0)"
                }),

                "enable_mirostat_eta": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用 Mirostat ETA 参数"
                }),
                "mirostat_eta": ("FLOAT", {
                    "default": 0.1, 
                    "min": 0, 
                    "step": 0.1, 
                    "tooltip": "Mirostat 的学习率参数，影响算法对生成文本反馈的响应速度。"
                }),

                "enable_mirostat_tau": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用 Mirostat TAU 参数"
                }),
                "mirostat_tau": ("FLOAT", {
                    "default": 5.0, 
                    "min": 0, 
                    "step": 0.1, 
                    "tooltip": "Mirostat 的目标熵参数，控制生成文本中连贯性与多样性的平衡。"
                }),

                # 上下文和重复参数
                "enable_num_ctx": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用上下文长度设置"
                }),
                "num_ctx": ("INT", {
                    "default": 2048, 
                    "min": 0, 
                    "max": 2 ** 31, 
                    "step": 1, 
                    "tooltip": "设置用于生成下一个标记的上下文窗口大小。"
                }),

                "enable_repeat_last_n": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用重复惩罚回溯长度设置"
                }),
                "repeat_last_n": ("INT", {
                    "default": 64, 
                    "min": 0, 
                    "max": 2 ** 31, 
                    "step": 1, 
                    "tooltip": "考虑应用重复惩罚的最后 n 个标记数量。"
                }),

                "enable_repeat_penalty": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用重复惩罚因子设置"
                }),
                "repeat_penalty": ("FLOAT", {
                    "default": 1.1, 
                    "min": 0, 
                    "step": 0.1, 
                    "tooltip": "重复标记的惩罚因子。大于 1.0 的值会抑制重复生成。"
                }),

                # 温度和随机性参数
                "enable_temperature": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用温度系数设置"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.8, 
                    "min": 0, 
                    "step": 0.1, 
                    "tooltip": "控制生成随机性的温度参数。较低的值使输出更确定性，较高的值使其更具随机性。"
                }),

                "enable_seed": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用随机种子设置"
                }),
                "seed": ("INT", {
                    "default": seed, 
                    "min": -1, 
                    "max": 2 ** 31, 
                    "step": 1, 
                    "tooltip": "随机数生成器种子 (-1 表示随机)"
                }),

                # 停止和采样参数
                "enable_stop": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用停止词设置"
                }),
                "stop": ("STRING", {
                    "default": "", 
                    "multiline": False, 
                    "tooltip": "定义生成何时停止的标记序列，多个标记用逗号分隔。"
                }),

                "enable_tfs_z": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用 Tail Free Sampling 参数"
                }),
                "tfs_z": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0, 
                    "step": 0.1, 
                    "tooltip": "Tail Free Sampling 参数。"
                }),

                # 预测长度参数
                "enable_num_predict": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用最大预测词数设置"
                }),
                "num_predict": ("INT", {
                    "default": 128, 
                    "min": -1, 
                    "max": 2 ** 31, 
                    "step": 1, 
                    "tooltip": "模型将生成的最大标记数 (-1 表示无限)。"
                }),

                # Top-K 和 Top-P 采样参数
                "enable_top_k": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用 Top-K 采样设置"
                }),
                "top_k": ("INT", {
                    "default": 40, 
                    "min": 0, 
                    "max": 2 ** 31, 
                    "step": 1, 
                    "tooltip": "保留用于采样的最高概率标记数。"
                }),

                "enable_top_p": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用 Top-P 采样设置"
                }),
                "top_p": ("FLOAT", {
                    "default": 0.9, 
                    "min": 0, 
                    "step": 0.1, 
                    "tooltip": "累积概率阈值，用于核采样。"
                }),

                # Min-P 采样参数
                "enable_min_p": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否启用 Min-P 采样设置"
                }),
                "min_p": ("FLOAT", {
                    "default": 0.0, 
                    "min": 0, 
                    "step": 0.01, 
                    "tooltip": "最小概率阈值，用于减少极端低概率标记的影响。"
                }),
                
                # 调试选项
                "debug": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用",
                    "label_off": "禁用",
                    "tooltip": "是否打印选项配置到控制台用于调试。"
                }),
            }
        }

    RETURN_TYPES = ("OLLAMA_OPTIONS",)
    RETURN_NAMES = ("options",)
    FUNCTION = "ollama_options"
    CATEGORY = "XnanTool/Ollama"
    DESCRIPTION = "重构版的 Ollama 推理配置选项。提供更多高级参数控制模型生成行为。"

    def ollama_options(self, **kwargs):
        """
        处理 Ollama 选项配置
        
        Args:
            **kwargs: 所有输入参数
            
        Returns:
            tuple: 包含选项配置的元组
        """
        if kwargs.get('debug', False):
            print("--- Ollama 选项重构版配置 ---")
            pprint(kwargs)
            print("----------------------------------------")

        # 返回所有参数，由其他节点过滤启用的选项
        return (kwargs,)


# 节点映射配置
NODE_CLASS_MAPPINGS = {
    "OllamaOptionsRefactored": OllamaOptionsRefactored,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaOptionsRefactored": "Ollama选项-重构版",
}