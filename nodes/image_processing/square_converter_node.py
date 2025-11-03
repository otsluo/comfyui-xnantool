import torch
import numpy as np
from PIL import Image

class SquareConverter:
    """
    正方形转换器节点
    输入一个尺寸，例如是200x300，那么会把较短尺寸填充到与较长尺寸相等，
    图片保持不变，同时可以增加边距，使得最终尺寸的短边加边距等于长边加边距
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "margin": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000,
                    "step": 1,
                    "display": "number"
                }),
            },
            "optional": {
                "pad_color": ("STRING", {
                    "default": "#FFFFFF",
                    "multiline": False
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")
    FUNCTION = "convert_to_square"
    CATEGORY = "XnanTool/图像处理"

    def convert_to_square(self, image, margin, pad_color="#FFFFFF"):
        # 获取图像尺寸
        batch_size, height, width, channels = image.shape
        
        # 计算目标尺寸（取较大边）
        target_size = max(width, height)
        
        # 添加边距
        target_size_with_margin = target_size + 2 * margin
        
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
        
        # 如果pad_value是列表，转换为适合填充的值
        if isinstance(pad_value, list):
            # 创建新的图像张量，并用填充颜色初始化
            new_image = torch.zeros((batch_size, target_size_with_margin, target_size_with_margin, channels), 
                                   dtype=image.dtype)
            # 为每个通道分别设置值
            for i in range(channels):
                new_image[:, :, :, i] = pad_value[i]
        else:
            # 创建新的图像张量，并用填充颜色初始化
            new_image = torch.full((batch_size, target_size_with_margin, target_size_with_margin, channels), 
                                  pad_value, dtype=image.dtype)
        
        # 计算填充位置，使图像居中
        pad_height = (target_size_with_margin - height) // 2
        pad_width = (target_size_with_margin - width) // 2
        
        # 填充原始图像到中心位置
        new_image[:, pad_height:pad_height+height, pad_width:pad_width+width, :] = image
        
        # 如果选择了透明填充且图像有alpha通道，则设置alpha值
        if pad_color == "transparent" and channels >= 4:
            # 设置填充区域的alpha值为0（完全透明）
            new_image[:, :pad_height, :, 3] = 0.0  # 上方填充
            new_image[:, pad_height+height:, :, 3] = 0.0  # 下方填充
            new_image[:, pad_height:pad_height+height, :pad_width, 3] = 0.0  # 左侧填充
            new_image[:, pad_height:pad_height+height, pad_width+width:, 3] = 0.0  # 右侧填充
        
        return (new_image, target_size_with_margin, target_size_with_margin)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "SquareConverter": SquareConverter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SquareConverter": "正方形转换器"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']