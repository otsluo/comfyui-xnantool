import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image


class ImagesToSequenceFramesNode:
    """
    图片合成序列帧节点 - 将多张图片合成为图像帧序列
    支持10个独立的图片输入端口，输出IMAGE类型的帧序列
    支持不同尺寸图片的统一处理：第一张尺寸、自定义尺寸、最大宽度和高度、最大宽度、最大高度
    """

    @classmethod
    def INPUT_TYPES(cls):
        # 创建10个独立的图片输入端口
        optional_inputs = {}
        for i in range(1, 11):
            optional_inputs[f"image_{i}"] = ("IMAGE",)

        return {
            "required": {
                "size_mode": (["第一张尺寸", "自定义尺寸", "最大宽度和高度", "最大宽度", "最大高度"], {
                    "default": "第一张尺寸",
                    "label": "尺寸模式",
                    "description": "当图片尺寸不一致时的处理方式"
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
    FUNCTION = "merge_to_sequence"
    CATEGORY = "❤️❤️❤️XnanTool/媒体处理"

    def merge_to_sequence(self, size_mode, custom_width, custom_height,
                          image_1=None, image_2=None, image_3=None, image_4=None,
                          image_5=None, image_6=None, image_7=None, image_8=None,
                          image_9=None, image_10=None):
        """
        将多张图片合成为图像帧序列

        Args:
            size_mode: 尺寸模式（第一张尺寸、自定义尺寸、最大尺寸）
            custom_width: 自定义宽度
            custom_height: 自定义高度
            image_1 到 image_10: 输入的图片张量，每个可以是 (H, W, C) 或 (B, H, W, C)

        Returns:
            tuple: (帧序列张量, (B, H, W, C))
        """
        # 收集所有有效的图片输入
        images_list = [image_1, image_2, image_3, image_4, image_5,
                       image_6, image_7, image_8, image_9, image_10]

        # 存储所有帧
        frames = []

        for img in images_list:
            if img is not None and isinstance(img, torch.Tensor):
                # 处理单张图片 (H, W, C)
                if img.dim() == 3:
                    frames.append(img.unsqueeze(0))
                # 处理批量图片 (B, H, W, C)
                elif img.dim() == 4:
                    frames.append(img)

        # 如果没有输入图片，返回空张量
        if not frames:
            empty_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            return (empty_tensor,)

        # 确定目标尺寸
        if size_mode == "第一张尺寸":
            # 使用第一张图片的尺寸
            target_height, target_width = frames[0].shape[1], frames[0].shape[2]
            # 将所有帧调整到目标尺寸
            resized_frames = []
            for frame in frames:
                # 检查是否需要调整尺寸
                if frame.shape[1] != target_height or frame.shape[2] != target_width:
                    # ComfyUI的IMAGE格式是 (B, H, W, C)，需要转换为 (B, C, H, W) 进行插值
                    frame_bchw = frame.permute(0, 3, 1, 2)
                    # 使用双线性插值调整尺寸
                    resized = F.interpolate(frame_bchw, size=(target_height, target_width), mode='bilinear', align_corners=False)
                    # 转换回 (B, H, W, C) 格式
                    resized_bhwc = resized.permute(0, 2, 3, 1)
                    resized_frames.append(resized_bhwc)
                else:
                    resized_frames.append(frame)
        elif size_mode == "自定义尺寸":
            # 使用自定义尺寸
            target_width = custom_width
            target_height = custom_height
            # 将所有帧调整到目标尺寸
            resized_frames = []
            for frame in frames:
                # 检查是否需要调整尺寸
                if frame.shape[1] != target_height or frame.shape[2] != target_width:
                    # ComfyUI的IMAGE格式是 (B, H, W, C)，需要转换为 (B, C, H, W) 进行插值
                    frame_bchw = frame.permute(0, 3, 1, 2)
                    # 使用双线性插值调整尺寸
                    resized = F.interpolate(frame_bchw, size=(target_height, target_width), mode='bilinear', align_corners=False)
                    # 转换回 (B, H, W, C) 格式
                    resized_bhwc = resized.permute(0, 2, 3, 1)
                    resized_frames.append(resized_bhwc)
                else:
                    resized_frames.append(frame)
        elif size_mode == "最大宽度和高度":
            # 找出所有图片中的最大宽度和最大高度，分别作为目标
            max_width = max(frame.shape[2] for frame in frames)
            max_height = max(frame.shape[1] for frame in frames)
            target_width = max_width
            target_height = max_height
            # 将所有帧调整到目标尺寸
            resized_frames = []
            for frame in frames:
                # 检查是否需要调整尺寸
                if frame.shape[1] != target_height or frame.shape[2] != target_width:
                    # ComfyUI的IMAGE格式是 (B, H, W, C)，需要转换为 (B, C, H, W) 进行插值
                    frame_bchw = frame.permute(0, 3, 1, 2)
                    # 使用双线性插值调整尺寸
                    resized = F.interpolate(frame_bchw, size=(target_height, target_width), mode='bilinear', align_corners=False)
                    # 转换回 (B, H, W, C) 格式
                    resized_bhwc = resized.permute(0, 2, 3, 1)
                    resized_frames.append(resized_bhwc)
                else:
                    resized_frames.append(frame)
        elif size_mode == "最大宽度":
            # 找出所有图片中的最大宽度，按宽度比例缩放高度
            max_width = max(frame.shape[2] for frame in frames)
            target_width = max_width
            # 将所有帧调整到目标宽度，高度按比例缩放
            resized_frames = []
            for frame in frames:
                current_height, current_width = frame.shape[1], frame.shape[2]
                if current_width != target_width:
                    # 计算缩放比例
                    scale = target_width / current_width
                    target_height = int(current_height * scale)
                    # ComfyUI的IMAGE格式是 (B, H, W, C)，需要转换为 (B, C, H, W) 进行插值
                    frame_bchw = frame.permute(0, 3, 1, 2)
                    # 使用双线性插值调整尺寸
                    resized = F.interpolate(frame_bchw, size=(target_height, target_width), mode='bilinear', align_corners=False)
                    # 转换回 (B, H, W, C) 格式
                    resized_bhwc = resized.permute(0, 2, 3, 1)
                    resized_frames.append(resized_bhwc)
                else:
                    resized_frames.append(frame)
        else:  # 最大高度
            # 找出所有图片中的最大高度，按高度比例缩放宽度
            max_height = max(frame.shape[1] for frame in frames)
            target_height = max_height
            # 将所有帧调整到目标高度，宽度按比例缩放
            resized_frames = []
            for frame in frames:
                current_height, current_width = frame.shape[1], frame.shape[2]
                if current_height != target_height:
                    # 计算缩放比例
                    scale = target_height / current_height
                    target_width = int(current_width * scale)
                    # ComfyUI的IMAGE格式是 (B, H, W, C)，需要转换为 (B, C, H, W) 进行插值
                    frame_bchw = frame.permute(0, 3, 1, 2)
                    # 使用双线性插值调整尺寸
                    resized = F.interpolate(frame_bchw, size=(target_height, target_width), mode='bilinear', align_corners=False)
                    # 转换回 (B, H, W, C) 格式
                    resized_bhwc = resized.permute(0, 2, 3, 1)
                    resized_frames.append(resized_bhwc)
                else:
                    resized_frames.append(frame)

        # 将所有帧拼接成一个批次
        result = torch.cat(resized_frames, dim=0)

        return (result,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "ImagesToSequenceFramesNode": ImagesToSequenceFramesNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagesToSequenceFramesNode": "图片合成序列帧"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
