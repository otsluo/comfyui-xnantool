# API相关节点模块初始化文件

# 导入API相关节点
from .volcanoark_doubao_seedream import DoubaoSeedreamTextToImageGenerationNode
from .volcanoark_doubao_seedream import DoubaoSeedreamImageToImageGenerationNode
# from .volcanoark_doubao_seedance import DoubaoSeedanceVideoGenerationNode  # 暂时禁用，待后续更新
from .bailian_llm import BailianLLMNode
from .bailian_vl import BailianVLNode
from .bailian_qwen import BailianQwenNode
from .generic_api_llm_node import GenericAPILLMNode
# from .bailian_tts import BailianTTSSNode  # 暂时禁用，待后续更新
# from .bailian_wan import BailianWanNode, BailianWanQueryNode  # 暂时禁用，待后续更新

# 定义节点映射
NODE_CLASS_MAPPINGS = {
    "DoubaoSeedreamTextToImageGenerationNode": DoubaoSeedreamTextToImageGenerationNode,
    "DoubaoSeedreamImageToImageGenerationNode": DoubaoSeedreamImageToImageGenerationNode,
    # "DoubaoSeedanceVideoGenerationNode": DoubaoSeedanceVideoGenerationNode,  # 暂时禁用，待后续更新
    "BailianLLMNode": BailianLLMNode,
    "BailianVLNode": BailianVLNode,
    "BailianQwenNode": BailianQwenNode,
    "GenericAPILLMNode": GenericAPILLMNode,
    # "BailianTTSSNode": BailianTTSSNode,  # 暂时禁用，待后续更新
    # "BailianWanNode": BailianWanNode,  # 暂时禁用，待后续更新
    # "BailianWanQueryNode": BailianWanQueryNode,  # 暂时禁用，待后续更新
}

# 定义节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "DoubaoSeedreamTextToImageGenerationNode": "豆包Seedream文生图",
    "DoubaoSeedreamImageToImageGenerationNode": "豆包Seedream图生图",
    # "DoubaoSeedanceVideoGenerationNode": "豆包Seedance视频生成",  # 暂时禁用，待后续更新
    "BailianLLMNode": "百炼LLM-文本生成",
    "BailianVLNode": "百炼VL-视觉理解",
    "BailianQwenNode": "百炼Qwen-图片生成",
    "GenericAPILLMNode": "通用LLM API调用",
    # "BailianTTSSNode": "百炼TTS-语音合成",  # 暂时禁用，待后续更新
    # "BailianWanNode": "百炼Wan-视频生成",  # 暂时禁用，待后续更新
    # "BailianWanQueryNode": "百炼Wan-查询任务",  # 暂时禁用，待后续更新
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
