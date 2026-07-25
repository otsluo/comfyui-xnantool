import torch
import torch.nn.functional as F


class SequenceFramesConcatNode:
    """
    序列帧拼接节点 - 将多个序列帧拼接为一个更长的序列帧
    支持10个独立的序列帧输入端口，按顺序拼接输出
    支持不同尺寸序列帧的统一处理：第一组尺寸、自定义尺寸、最大宽度和高度、最大宽度、最大高度
    """

    @classmethod
    def INPUT_TYPES(cls):
        # 创建10个独立的序列帧输入端口
        optional_inputs = {}
        for i in range(1, 11):
            optional_inputs[f"sequence_{i}"] = ("IMAGE",)

        return {
            "required": {
                "size_mode": (["第一组尺寸", "自定义尺寸", "最大宽度和高度", "最大宽度", "最大高度"], {
                    "default": "第一组尺寸",
                    "label": "尺寸模式",
                    "description": "当序列帧尺寸不一致时的处理方式"
                }),
                "custom_width": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                    "label": "自定义宽度",
                    "description": "自定义尺寸模式下的宽度"
                }),
                "custom_height": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                    "label": "自定义高度",
                    "description": "自定义尺寸模式下的高度"
                }),
            },
            "optional": optional_inputs
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("序列帧",)
    FUNCTION = "concat_sequences"
    CATEGORY = "❤️❤️❤️XnanTool/媒体处理"

    def _resize_frames(self, frames, target_height, target_width):
        """将帧序列调整到目标尺寸"""
        if frames.shape[1] != target_height or frames.shape[2] != target_width:
            frames_bchw = frames.permute(0, 3, 1, 2)
            resized = F.interpolate(frames_bchw, size=(target_height, target_width), mode='bilinear', align_corners=False)
            return resized.permute(0, 2, 3, 1)
        return frames

    def concat_sequences(self, size_mode, custom_width, custom_height,
                         sequence_1=None, sequence_2=None, sequence_3=None, sequence_4=None,
                         sequence_5=None, sequence_6=None, sequence_7=None, sequence_8=None,
                         sequence_9=None, sequence_10=None):
        """
        将多个序列帧拼接为一个更长的序列帧

        Args:
            size_mode: 尺寸模式
            custom_width: 自定义宽度
            custom_height: 自定义高度
            sequence_1 到 sequence_10: 输入的序列帧张量 (B, H, W, C)

        Returns:
            tuple: (拼接后的帧序列张量, (B, H, W, C))
        """
        # 收集所有有效的序列帧输入
        sequences_list = [sequence_1, sequence_2, sequence_3, sequence_4, sequence_5,
                          sequence_6, sequence_7, sequence_8, sequence_9, sequence_10]

        # 存储所有有效的序列帧
        valid_sequences = []
        for seq in sequences_list:
            if seq is not None and isinstance(seq, torch.Tensor):
                # 确保是4维张量 (B, H, W, C)
                if seq.dim() == 3:
                    seq = seq.unsqueeze(0)
                valid_sequences.append(seq)

        # 如果没有输入，返回空张量
        if not valid_sequences:
            empty_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            return (empty_tensor,)

        # 确定目标尺寸
        if size_mode == "第一组尺寸":
            target_height, target_width = valid_sequences[0].shape[1], valid_sequences[0].shape[2]
        elif size_mode == "自定义尺寸":
            target_width = custom_width
            target_height = custom_height
        elif size_mode == "最大宽度和高度":
            max_width = max(seq.shape[2] for seq in valid_sequences)
            max_height = max(seq.shape[1] for seq in valid_sequences)
            target_width = max_width
            target_height = max_height
        elif size_mode == "最大宽度":
            max_width = max(seq.shape[2] for seq in valid_sequences)
            # 按第一组序列的宽高比计算高度
            first_h, first_w = valid_sequences[0].shape[1], valid_sequences[0].shape[2]
            target_width = max_width
            target_height = int(first_h * (max_width / first_w))
        else:  # 最大高度
            max_height = max(seq.shape[1] for seq in valid_sequences)
            # 按第一组序列的宽高比计算宽度
            first_h, first_w = valid_sequences[0].shape[1], valid_sequences[0].shape[2]
            target_height = max_height
            target_width = int(first_w * (max_height / first_h))

        # 调整所有序列帧到目标尺寸并拼接
        resized_sequences = []
        for seq in valid_sequences:
            resized_seq = self._resize_frames(seq, target_height, target_width)
            resized_sequences.append(resized_seq)

        # 沿批次维度拼接
        result = torch.cat(resized_sequences, dim=0)

        return (result,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "SequenceFramesConcatNode": SequenceFramesConcatNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "SequenceFramesConcatNode": "序列帧拼接"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
