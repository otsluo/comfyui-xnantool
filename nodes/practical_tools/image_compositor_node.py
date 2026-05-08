import torch
import numpy as np
from PIL import Image, ImageDraw
import os


class ImageCompositorNode:
    """
    图像合成节点 - 类似PS图层合成功能
    支持单图层、位置、缩放、透明度、混合模式、遮罩
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "layer_image": ("IMAGE", {
                    "label": "图层图片",
                    "description": "要合成的图层图片"
                }),
            },
            "optional": {
                "layer_mask": ("MASK", {
                    "label": "图层遮罩",
                    "description": "图层的遮罩（白色显示，黑色隐藏）"
                }),
                "layer_x": ("INT", {
                    "default": 0,
                    "min": -8192,
                    "max": 8192,
                    "step": 1,
                    "label": "X位置",
                    "description": "图层的水平位置"
                }),
                "layer_y": ("INT", {
                    "default": 0,
                    "min": -8192,
                    "max": 8192,
                    "step": 1,
                    "label": "Y位置",
                    "description": "图层的垂直位置"
                }),
                "layer_scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 10.0,
                    "step": 0.01,
                    "label": "缩放",
                    "description": "图层的缩放比例"
                }),
                "layer_opacity": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "label": "透明度",
                    "description": "图层的不透明度（1.0为完全不透明）"
                }),
                "blend_mode": (["正常", "正片叠底", "滤色", "叠加", "变亮", "变暗", "差值", "排除"], {
                    "default": "正常",
                    "label": "混合模式",
                    "description": "图层与背景的混合模式"
                }),
                "background_image": ("IMAGE", {
                    "label": "背景图片",
                    "description": "作为背景的图片"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("合成图片",)
    FUNCTION = "composite_images"
    CATEGORY = "XnanTool/实用工具"
    OUTPUT_NODE = False
    
    def composite_images(self, background_image, layer_image, layer_x, layer_y, layer_scale, layer_opacity, blend_mode, layer_mask=None):
        """
        合成图像
        
        Args:
            background_image: 背景图片
            layer_image: 图层图片
            layer_x: X位置
            layer_y: Y位置
            layer_scale: 缩放
            layer_opacity: 透明度
            blend_mode: 混合模式
            layer_mask: 图层遮罩（可选）
            
        Returns:
            tuple: (合成后的图片tensor)
        """
        # 转换背景图片
        bg_pil = self.tensor_to_pil(background_image)
        bg_width, bg_height = bg_pil.size
        
        # 创建结果图片
        result = bg_pil.convert('RGBA')
        
        # 处理图层
        result = self.apply_layer(result, layer_image, layer_x, layer_y, layer_scale, layer_opacity, blend_mode, bg_width, bg_height, layer_mask)
        
        # 转换回tensor
        result_tensor = self.pil_to_tensor(result)
        
        return (result_tensor,)
    
    def apply_layer(self, background, layer_image, x, y, scale, opacity, blend_mode, bg_width, bg_height, layer_mask=None):
        """应用单个图层到背景图片"""
        if layer_image is None:
            return background
        
        # 转换图层图片
        layer_pil = self.tensor_to_pil(layer_image).convert('RGBA')
        
        # 缩放图层
        if scale != 1.0:
            new_width = int(layer_pil.width * scale)
            new_height = int(layer_pil.height * scale)
            layer_pil = layer_pil.resize((new_width, new_height), Image.LANCZOS)
        
        # 应用遮罩
        if layer_mask is not None:
            mask_pil = self.mask_to_pil(layer_mask)
            # 调整遮罩大小以匹配图层
            mask_pil = mask_pil.resize(layer_pil.size, Image.LANCZOS)
            # 将遮罩应用到图层的alpha通道
            r, g, b, a = layer_pil.split()
            # 将遮罩转换为L模式
            mask_pil = mask_pil.convert('L')
            # 使用遮罩更新alpha通道
            a = Image.composite(a, Image.new('L', a.size, 0), mask_pil)
            layer_pil = Image.merge('RGBA', (r, g, b, a))
        
        # 调整透明度
        if opacity < 1.0:
            # 分离通道
            r, g, b, a = layer_pil.split()
            # 调整alpha通道
            a = a.point(lambda p: int(p * opacity))
            # 合并通道
            layer_pil = Image.merge('RGBA', (r, g, b, a))
        
        # 创建透明画布
        canvas = Image.new('RGBA', (bg_width, bg_height), (0, 0, 0, 0))
        canvas.paste(layer_pil, (x, y))
        
        # 应用混合模式
        if blend_mode == "正常":
            background = Image.alpha_composite(background, canvas)
        else:
            background = self.apply_blend_mode(background, canvas, blend_mode)
        
        return background
    
    def apply_blend_mode(self, background, layer, mode):
        """应用混合模式"""
        if mode == "正常":
            return Image.alpha_composite(background, layer)
        
        # 分离通道
        bg_r, bg_g, bg_b, bg_a = background.split()
        layer_r, layer_g, layer_b, layer_a = layer.split()
        
        # 转换为numpy数组进行计算
        bg_r_np = np.array(bg_r, dtype=np.float32) / 255.0
        bg_g_np = np.array(bg_g, dtype=np.float32) / 255.0
        bg_b_np = np.array(bg_b, dtype=np.float32) / 255.0
        
        layer_r_np = np.array(layer_r, dtype=np.float32) / 255.0
        layer_g_np = np.array(layer_g, dtype=np.float32) / 255.0
        layer_b_np = np.array(layer_b, dtype=np.float32) / 255.0
        
        if mode == "正片叠底":
            # Multiply: 结果 = 底色 × 混合色
            r = bg_r_np * layer_r_np
            g = bg_g_np * layer_g_np
            b = bg_b_np * layer_b_np
        elif mode == "滤色":
            # Screen: 结果 = 1 - (1-底色) × (1-混合色)
            r = 1 - (1 - bg_r_np) * (1 - layer_r_np)
            g = 1 - (1 - bg_g_np) * (1 - layer_g_np)
            b = 1 - (1 - bg_b_np) * (1 - layer_b_np)
        elif mode == "叠加":
            # Overlay: 根据底色决定使用Multiply还是Screen
            r = np.where(bg_r_np < 0.5, 2 * bg_r_np * layer_r_np, 1 - 2 * (1 - bg_r_np) * (1 - layer_r_np))
            g = np.where(bg_g_np < 0.5, 2 * bg_g_np * layer_g_np, 1 - 2 * (1 - bg_g_np) * (1 - layer_g_np))
            b = np.where(bg_b_np < 0.5, 2 * bg_b_np * layer_b_np, 1 - 2 * (1 - bg_b_np) * (1 - layer_b_np))
        elif mode == "变亮":
            # Lighten: 结果 = max(底色, 混合色)
            r = np.maximum(bg_r_np, layer_r_np)
            g = np.maximum(bg_g_np, layer_g_np)
            b = np.maximum(bg_b_np, layer_b_np)
        elif mode == "变暗":
            # Darken: 结果 = min(底色, 混合色)
            r = np.minimum(bg_r_np, layer_r_np)
            g = np.minimum(bg_g_np, layer_g_np)
            b = np.minimum(bg_b_np, layer_b_np)
        elif mode == "差值":
            # Difference: 结果 = |底色 - 混合色|
            r = np.abs(bg_r_np - layer_r_np)
            g = np.abs(bg_g_np - layer_g_np)
            b = np.abs(bg_b_np - layer_b_np)
        elif mode == "排除":
            # Exclusion: 结果 = 底色 + 混合色 - 2 × 底色 × 混合色
            r = bg_r_np + layer_r_np - 2 * bg_r_np * layer_r_np
            g = bg_g_np + layer_g_np - 2 * bg_g_np * layer_g_np
            b = bg_b_np + layer_b_np - 2 * bg_b_np * layer_b_np
        else:
            # 默认使用正常混合
            return Image.alpha_composite(background, layer)
        
        # 转换回0-255范围
        r = np.clip(r * 255, 0, 255).astype(np.uint8)
        g = np.clip(g * 255, 0, 255).astype(np.uint8)
        b = np.clip(b * 255, 0, 255).astype(np.uint8)
        
        # 合并alpha通道（使用图层的alpha）
        result = Image.merge('RGBA', (
            Image.fromarray(r),
            Image.fromarray(g),
            Image.fromarray(b),
            layer_a
        ))
        
        return Image.alpha_composite(background, result)
    
    def tensor_to_pil(self, tensor):
        """将tensor转换为PIL图片"""
        if tensor.dim() == 4:
            tensor = tensor[0]
        
        # 确保是RGB格式
        if tensor.shape[2] == 4:
            # RGBA
            img_np = (tensor.cpu().numpy() * 255).astype(np.uint8)
            return Image.fromarray(img_np, 'RGBA')
        elif tensor.shape[2] == 3:
            # RGB
            img_np = (tensor.cpu().numpy() * 255).astype(np.uint8)
            return Image.fromarray(img_np, 'RGB')
        else:
            raise ValueError(f"不支持的图片通道数: {tensor.shape[2]}")
    
    def pil_to_tensor(self, pil_image):
        """将PIL图片转换为tensor"""
        # 确保是RGBA格式
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
        
        img_np = np.array(pil_image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img_np).unsqueeze(0)
        
        return tensor
    
    def mask_to_pil(self, mask):
        """将MASK转换为PIL图片"""
        if mask.dim() == 3:
            mask = mask[0]
        
        # MASK是单通道的，值范围0-1
        mask_np = (mask.cpu().numpy() * 255).astype(np.uint8)
        return Image.fromarray(mask_np, 'L')


# 节点映射
NODE_CLASS_MAPPINGS = {
    "ImageCompositorNode": ImageCompositorNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageCompositorNode": "图像合成（图层）",
}
