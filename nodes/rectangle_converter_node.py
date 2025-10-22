import torch
import numpy as np
from PIL import Image

class RectangleConverter:
    """
    长方形转换器节点
    将正方形图像转换为长方形图像，支持左右和上下的扩展，可以手动指定最终长度
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "direction": (["left_right", "top_bottom"], {
                    "default": "left_right",
                    "label": "扩展方向",
                    "description": "选择扩展方向：左右扩展或上下扩展"
                }),
                "target_length": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                    "display": "number",
                    "label": "目标长度",
                    "description": "指定长边的目标长度"
                }),
                "margin": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000,
                    "step": 1,
                    "display": "number",
                    "label": "边距",
                    "description": "在图像周围添加的额外边距"
                }),
            },
            "optional": {
                "pad_color": ("STRING", {
                    "default": "#FFFFFF",
                    "multiline": False,
                    "label": "填充颜色",
                    "description": "填充区域的颜色，支持十六进制颜色代码或'transparent'"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")
    FUNCTION = "convert_to_rectangle"
    CATEGORY = "XnanTool/实用工具/小工具"

    def convert_to_rectangle(self, image, direction, target_length, margin, pad_color="#FFFFFF"):
        # 获取图像尺寸
        batch_size, height, width, channels = image.shape
        
        # 确保目标长度不小于原图的最大边
        max_dimension = max(width, height)
        if target_length < max_dimension:
            target_length = max_dimension
        
        # 根据方向确定最终尺寸
        if direction == "left_right":
            # 左右扩展：高度保持不变，宽度扩展到目标长度
            target_width = target_length
            target_height = height
        else:  # top_bottom
            # 上下扩展：宽度保持不变，高度扩展到目标长度
            target_width = width
            target_height = target_length
        
        # 添加边距
        target_width_with_margin = target_width + 2 * margin
        target_height_with_margin = target_height + 2 * margin
        
        # 解析颜色值
        if pad_color == "transparent" and channels >= 4:
            # 对于透明填充，如果图像有alpha通道
            pad_value = [0.0, 0.0, 0.0, 0.0]  # RGBA全透明
        else:
            # 解析十六进制颜色代码
            try:
                # 移除可能存在的#前缀
                color = pad_color.lstrip('#')
                # 确保颜色代码长度为6位
                if len(color) == 6:
                    # 将十六进制转换为RGB值(0-1范围)
                    r = int(color[0:2], 16) / 255.0
                    g = int(color[2:4], 16) / 255.0
                    b = int(color[4:6], 16) / 255.0
                    pad_value = [r, g, b]
                    # 如果图像是RGBA，则添加alpha通道值(1.0表示不透明)
                    if channels == 4:
                        pad_value.append(1.0)
                else:
                    # 默认白色
                    pad_value = [1.0, 1.0, 1.0]
                    if channels == 4:
                        pad_value.append(1.0)
            except:
                # 解析失败时默认使用白色
                pad_value = [1.0, 1.0, 1.0]
                if channels == 4:
                    pad_value.append(1.0)
        
        # 创建新的图像张量，并用填充颜色初始化
        if isinstance(pad_value, list):
            # 创建新的图像张量，并用填充颜色初始化
            new_image = torch.zeros((batch_size, target_height_with_margin, target_width_with_margin, channels), 
                                   dtype=image.dtype)
            # 为每个通道分别设置值
            for i in range(channels):
                new_image[:, :, :, i] = pad_value[i]
        else:
            # 创建新的图像张量，并用填充颜色初始化
            new_image = torch.full((batch_size, target_height_with_margin, target_width_with_margin, channels), 
                                  pad_value, dtype=image.dtype)
        
        # 计算填充位置，使图像居中
        pad_height = (target_height_with_margin - height) // 2
        pad_width = (target_width_with_margin - width) // 2
        
        # 填充原始图像到中心位置
        new_image[:, pad_height:pad_height+height, pad_width:pad_width+width, :] = image
        
        # 如果选择了透明填充且图像有alpha通道，则设置alpha值
        if pad_color == "transparent" and channels >= 4:
            # 设置填充区域的alpha值为0（完全透明）
            new_image[:, :pad_height, :, 3] = 0.0  # 上方填充
            new_image[:, pad_height+height:, :, 3] = 0.0  # 下方填充
            new_image[:, pad_height:pad_height+height, :pad_width, 3] = 0.0  # 左侧填充
            new_image[:, pad_height:pad_height+height, pad_width+width:, 3] = 0.0  # 右侧填充
        
        return (new_image, target_width_with_margin, target_height_with_margin)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "RectangleConverter": RectangleConverter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RectangleConverter": "长方形转换器-【新】"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']