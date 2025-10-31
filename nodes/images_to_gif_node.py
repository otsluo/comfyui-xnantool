import torch
import numpy as np
from PIL import Image
import imageio
import os
import logging
import folder_paths
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImagesToGifNode:
    """
    图片转GIF节点
    将多张图片合并为GIF动画
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # 创建10个独立的图片输入端口，但都是可选的
        required_inputs = {}
        optional_inputs = {}
        for i in range(1, 11):
            optional_inputs[f"image_{i}"] = ("IMAGE",)
        
        # 添加其他参数
        required_inputs.update({
            "frame_duration": ("FLOAT", {
                "default": 0.5,
                "min": 0.1,
                "max": 10.0,
                "step": 0.1,
                "display": "number",
                "label": "帧间隔",
                "description": "每帧图片的显示时间（秒）"
            }),
            "loop_count": ("INT", {
                "default": 0,
                "min": 0,
                "max": 100,
                "step": 1,
                "display": "number",
                "label": "循环次数",
                "description": "GIF循环播放次数（0表示无限循环）"
            }),
            "resize_factor": ("FLOAT", {
                "default": 1.0,
                "min": 0.1,
                "max": 1.0,
                "step": 0.1,
                "display": "slider",
                "label": "缩放因子",
                "description": "图像缩放比例（0.1-1.0）"
            }),
            "optimize": ("BOOLEAN", {
                "default": True,
                "label": "优化GIF",
                "description": "是否优化GIF文件大小"
            }),
            "palette_size": (["2", "4", "8", "16", "32", "64", "128", "256"], {
                "default": "256",
                "label": "调色板大小",
                "description": "GIF的颜色数量"
            }),
            "quality": (["1", "2", "3"], {
                "default": "2",
                "label": "质量等级",
                "description": "GIF质量等级（1=低，2=中，3=高）"
            }),
        })
        
        return {
            "required": required_inputs,
            "optional": {
                **optional_inputs,
                "output_filename": ("STRING", {
                    "default": "图片转gif.gif",
                    "multiline": False,
                    "label": "输出文件名",
                    "description": "GIF文件的输出名称"
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_path",)
    FUNCTION = "convert_images_to_gif"
    CATEGORY = "XnanTool/媒体处理"
    
    def tensor_to_numpy(self, tensor):
        """将tensor格式转换为numpy数组 (B,H,W,C) -> (H,W,C) RGB"""
        # 确保tensor在CPU上并转换为numpy
        tensor = tensor.cpu()
        # 转换为numpy并调整维度顺序 (H,W,C)
        numpy_image = tensor.numpy()
        # 转换范围从[0,1]到[0,255]
        numpy_image = (numpy_image * 255).astype(np.uint8)
        return numpy_image
    
    def numpy_to_pil(self, numpy_image):
        """将numpy数组转换为PIL图像"""
        return Image.fromarray(numpy_image)
    
    def convert_images_to_gif(self, frame_duration, loop_count, resize_factor, optimize, 
                             palette_size, quality, 
                             image_1=None, image_2=None, image_3=None, image_4=None, image_5=None, 
                             image_6=None, image_7=None, image_8=None, image_9=None, image_10=None,
                             output_filename="图片转gif.gif"):
        """
        将多张图片合并为GIF动画
        
        Args:
            frame_duration (float): 每帧图片的显示时间（秒）
            loop_count (int): GIF循环播放次数（0表示无限循环）
            resize_factor (float): 图像缩放比例（0.1-1.0）
            optimize (bool): 是否优化GIF文件大小
            palette_size (str): GIF使用的颜色数量（"2"-"256"）
            quality (str): GIF质量等级（"1"=低，"2"=中，"3"=高）
            image_1 to image_10 (torch.Tensor, optional): 输入的图片张量 (B, H, W, C) 或单张图片 (H, W, C)
            output_filename (str): GIF文件的输出名称
            
        Returns:
            tuple: 包含输出文件路径的元组
        """
        try:
            # 获取输出目录
            output_dir = folder_paths.get_output_directory()
            
            # 构建输出文件路径并处理文件名冲突
            if not output_filename.lower().endswith('.gif'):
                output_filename += '.gif'
            
            # 处理文件名冲突，自动添加序号
            base_name, ext = os.path.splitext(output_filename)
            output_path = os.path.join(output_dir, output_filename)
            counter = 1
            original_output_path = output_path
            while os.path.exists(output_path):
                new_filename = f"{base_name}_{counter}{ext}"
                output_path = os.path.join(output_dir, new_filename)
                counter += 1
            
            # 如果文件被重命名，记录日志
            if original_output_path != output_path:
                logger.info(f"检测到同名文件，已自动重命名为: {os.path.basename(output_path)}")
            
            # 收集帧数据
            frames = []
            
            # 处理所有10个输入图片
            images_list = [image_1, image_2, image_3, image_4, image_5, 
                          image_6, image_7, image_8, image_9, image_10]
            
            for img in images_list:
                # 跳过未连接的输入
                if img is not None:
                    # 处理单张图片或批量图片
                    if isinstance(img, torch.Tensor):
                        # 如果是单张图片 (H, W, C)
                        if img.dim() == 3:
                            numpy_image = self.tensor_to_numpy(img)
                            pil_image = self.numpy_to_pil(numpy_image)
                            
                            # 调整图像大小
                            if resize_factor != 1.0:
                                width, height = pil_image.size
                                new_width = int(width * resize_factor)
                                new_height = int(height * resize_factor)
                                pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                            
                            frames.append(pil_image)
                        # 如果是批量图片 (B, H, W, C)
                        elif img.dim() == 4:
                            for i in range(img.shape[0]):
                                numpy_image = self.tensor_to_numpy(img[i])
                                pil_image = self.numpy_to_pil(numpy_image)
                                
                                # 调整图像大小
                                if resize_factor != 1.0:
                                    width, height = pil_image.size
                                    new_width = int(width * resize_factor)
                                    new_height = int(height * resize_factor)
                                    pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                                
                                frames.append(pil_image)
            
            # 创建GIF
            if frames:
                # 将palette_size从字符串转换为整数
                palette_size_int = int(palette_size)
                
                # 准备GIF保存参数
                gif_kwargs = {
                    'format': 'GIF',
                    'save_all': True,
                    'append_images': frames[1:],
                    'duration': int(frame_duration * 1000),  # 每帧持续时间（毫秒）
                    'loop': loop_count,
                    'optimize': optimize,
                    'palettesize': palette_size_int
                }
                
                # 添加质量参数映射
                quality_map = {
                    "1": False,  # 不使用子矩形
                    "2": True,   # 使用子矩形
                    "3": True    # 使用子矩形
                }
                
                # 根据质量等级设置子矩形参数
                if quality_map.get(quality, True):
                    gif_kwargs['subrectangles'] = True
                
                # 写入GIF文件
                frames[0].save(output_path, **gif_kwargs)
            
            # 记录最终保存的文件路径
            logger.info(f"GIF已保存到: {output_path}")
            logger.info(f"总帧数: {len(frames)}")
            logger.info(f"帧间隔: {frame_duration}秒")
            logger.info(f"循环次数: {loop_count}")
            logger.info(f"调色板大小: {palette_size}")
            logger.info(f"是否优化: {optimize}")
            
            return (output_path,)
            
        except Exception as e:
            logger.error(f"图片转GIF过程中发生错误: {str(e)}")
            raise e

# 注册节点
NODE_CLASS_MAPPINGS = {
    "ImagesToGifNode": ImagesToGifNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagesToGifNode": "图片转GIF节点"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]