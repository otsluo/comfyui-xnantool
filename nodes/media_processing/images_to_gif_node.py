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

class ImagesToGifNodeV2:
    """
    图片转GIF节点 V2
    将多张图片合并为GIF动画（带过渡效果）
    
    V2版本特性：
    - 支持多种过渡效果（淡入淡出、滑动、擦除等）
    - 可调节过渡帧数
    - 更精细的质量控制
    - 支持更多自定义参数
    
    质量等级说明：
    - 等级1: 最低质量，最小文件大小
    - 等级2: 低质量，较小文件大小
    - 等级3: 中等质量，平衡文件大小和质量
    - 等级4: 高质量，更好的图像质量
    - 等级5: 最高质量，最佳图像质量，支持隔行扫描
    """
    
    def __init__(self):
        """
        初始化图片转GIF节点 V2
        """
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
                "default": 0.1,
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
            "transition_effect": (["none", "crossfade", "slide_left", "slide_right", "slide_up", "slide_down", "wipe_left", "wipe_right", "wipe_up", "wipe_down"], {
                "default": "wipe_left",
                "label": "过渡效果",
                "description": "帧之间的过渡效果类型"
            }),
            "transition_frames": ("INT", {
                "default": 10,
                "min": 0,
                "max": 30,
                "step": 1,
                "display": "number",
                "label": "过渡帧数",
                "description": "过渡效果的帧数（0表示无过渡）"
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
            "quality": (["1", "2", "3", "4", "5"], {
                "default": "5",
                "label": "质量等级",
                "description": "GIF质量等级（1=最低，2=低，3=中，4=高，5=最高）"
            }),
        })
        
        return {
            "required": required_inputs,
            "optional": {
                **optional_inputs,
                "output_filename": ("STRING", {
                    "default": "图片转gif_v2.gif",
                    "multiline": False,
                    "label": "输出文件名",
                    "description": "GIF文件的输出名称"
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_path",)
    FUNCTION = "convert_images_to_gif_v2"
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
    
    def create_crossfade_frames(self, img1, img2, num_frames):
        """创建淡入淡出过渡效果的帧"""
        frames = []
        for i in range(num_frames):
            alpha = i / (num_frames - 1) if num_frames > 1 else 1
            blended = Image.blend(img1, img2, alpha)
            frames.append(blended)
        return frames
    
    def create_slide_frames(self, img1, img2, num_frames, direction):
        """创建滑动过渡效果的帧"""
        frames = []
        width, height = img1.size
        
        for i in range(num_frames):
            # 创建新图像
            new_frame = img1.copy()
            overlay = img2.copy()
            
            # 计算滑动偏移量
            progress = i / (num_frames - 1) if num_frames > 1 else 1
            
            if direction == "left":
                offset_x = int(width * progress)
                overlay = overlay.crop((0, 0, width - offset_x, height))
                new_frame.paste(overlay, (offset_x, 0))
            elif direction == "right":
                offset_x = int(width * progress)
                overlay = overlay.crop((offset_x, 0, width, height))
                new_frame.paste(overlay, (0, 0))
            elif direction == "up":
                offset_y = int(height * progress)
                overlay = overlay.crop((0, 0, width, height - offset_y))
                new_frame.paste(overlay, (0, offset_y))
            elif direction == "down":
                offset_y = int(height * progress)
                overlay = overlay.crop((0, offset_y, width, height))
                new_frame.paste(overlay, (0, 0))
                
            frames.append(new_frame)
        return frames
    
    def create_wipe_frames(self, img1, img2, num_frames, direction):
        """创建擦除过渡效果的帧"""
        frames = []
        width, height = img1.size
        
        for i in range(num_frames):
            # 创建新图像
            new_frame = img1.copy()
            overlay = img2.copy()
            
            # 计算擦除区域
            progress = i / (num_frames - 1) if num_frames > 1 else 1
            
            if direction == "left":
                wipe_width = int(width * progress)
                overlay = overlay.crop((0, 0, wipe_width, height))
                new_frame.paste(overlay, (0, 0))
            elif direction == "right":
                wipe_width = int(width * progress)
                overlay = overlay.crop((width - wipe_width, 0, width, height))
                new_frame.paste(overlay, (width - wipe_width, 0))
            elif direction == "up":
                wipe_height = int(height * progress)
                overlay = overlay.crop((0, 0, width, wipe_height))
                new_frame.paste(overlay, (0, 0))
            elif direction == "down":
                wipe_height = int(height * progress)
                overlay = overlay.crop((0, height - wipe_height, width, height))
                new_frame.paste(overlay, (0, height - wipe_height))
                
            frames.append(new_frame)
        return frames
    
    def apply_transition_effect(self, img1, img2, effect, num_frames):
        """应用过渡效果"""
        if effect == "none" or num_frames <= 0:
            return [img1]
        elif effect == "crossfade":
            return self.create_crossfade_frames(img1, img2, num_frames)
        elif effect.startswith("slide_"):
            direction = effect.split("_")[1]
            return self.create_slide_frames(img1, img2, num_frames, direction)
        elif effect.startswith("wipe_"):
            direction = effect.split("_")[1]
            return self.create_wipe_frames(img1, img2, num_frames, direction)
        else:
            return [img1]
    
    def convert_images_to_gif_v2(self, frame_duration, loop_count, resize_factor, transition_effect, transition_frames, optimize, 
                             palette_size, quality, 
                             image_1=None, image_2=None, image_3=None, image_4=None, image_5=None, 
                             image_6=None, image_7=None, image_8=None, image_9=None, image_10=None,
                             output_filename="图片转gif_v2.gif"):
        """
        将多张图片合并为GIF动画（V2版本，带过渡效果）
        
        Args:
            frame_duration (float): 每帧图片的显示时间（秒）
            loop_count (int): GIF循环播放次数（0表示无限循环）
            resize_factor (float): 图像缩放比例（0.1-1.0）
            transition_effect (str): 过渡效果类型 ("none", "crossfade", "slide_left", "slide_right", "slide_up", "slide_down", "wipe_left", "wipe_right", "wipe_up", "wipe_down")
            transition_frames (int): 过渡效果的帧数（0表示无过渡）
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
                # 应用过渡效果
                processed_frames = []
                if transition_effect != "none" and transition_frames > 0:
                    # 为每对连续帧添加过渡效果
                    for i in range(len(frames)):
                        processed_frames.append(frames[i])
                        # 如果不是最后一帧，添加过渡帧
                        if i < len(frames) - 1:
                            transition_frames_list = self.apply_transition_effect(
                                frames[i], frames[i + 1], transition_effect, transition_frames
                            )
                            # 添加过渡帧（除了第一帧，因为第一帧已经是原始帧）
                            processed_frames.extend(transition_frames_list[1:])
                else:
                    # 无过渡效果，直接使用原始帧
                    processed_frames = frames
                
                # 将palette_size从字符串转换为整数
                palette_size_int = int(palette_size)
                
                # 计算过渡帧的持续时间
                regular_frame_duration = int(frame_duration * 1000)
                transition_frame_duration = int(frame_duration * 1000 / max(transition_frames, 1)) if transition_frames > 0 else regular_frame_duration
                
                # 准备GIF保存参数
                gif_kwargs = {
                    'format': 'GIF',
                    'save_all': True,
                    'append_images': processed_frames[1:],
                    'duration': regular_frame_duration,  # 每帧持续时间（毫秒）
                    'loop': loop_count,
                    'optimize': optimize,
                    'palettesize': palette_size_int
                }
                
                # 根据质量等级设置不同的优化参数
                # 质量等级1: 最低质量，最小文件大小
                # 质量等级2: 低质量
                # 质量等级3: 中等质量
                # 质量等级4: 高质量
                # 质量等级5: 最高质量，最大文件大小
                
                if quality == "1":
                    # 最低质量设置 - 最小文件大小
                    gif_kwargs['subrectangles'] = False  # 不使用子矩形优化
                    gif_kwargs['optimize'] = True  # 优化文件大小
                    gif_kwargs['disposal'] = 2  # 处置方法：恢复到背景色
                elif quality == "2":
                    # 低质量设置 - 较小文件大小
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = True  # 优化文件大小
                    gif_kwargs['disposal'] = 2  # 处置方法：恢复到背景色
                elif quality == "3":
                    # 中等质量设置 - 平衡文件大小和质量
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = True  # 优化文件大小
                    gif_kwargs['disposal'] = 2  # 处置方法：恢复到背景色
                elif quality == "4":
                    # 高质量设置 - 更好的图像质量
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = False  # 不优化文件大小以保持质量
                    gif_kwargs['disposal'] = 1  # 处置方法：不处置
                else:  # quality == "5"
                    # 最高质量设置 - 最佳图像质量
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = False  # 不优化文件大小以保持质量
                    gif_kwargs['disposal'] = 1  # 处置方法：不处置
                    gif_kwargs['interlace'] = True  # 隔行扫描以提高显示质量
                
                # 对帧进行量化处理以应用调色板大小
                quantized_frames = []
                for i, frame in enumerate(processed_frames):
                    # 将图像转换为P模式（调色板模式）并应用指定的颜色数量
                    quantized_frame = frame.quantize(colors=palette_size_int, method=Image.MEDIANCUT)
                    quantized_frames.append(quantized_frame)
                
                # 更新GIF保存参数，确保使用量化后的帧
                gif_kwargs['append_images'] = quantized_frames[1:]  # 从第二帧开始的所有帧
                
                # 写入GIF文件
                quantized_frames[0].save(output_path, **gif_kwargs)
                
                # 记录处理后的帧数
                logger.info(f"处理后帧数: {len(processed_frames)}")
                if transition_frames > 0 and transition_effect != "none":
                    logger.info(f"过渡效果: {transition_effect}")
                    logger.info(f"过渡帧数: {transition_frames}")
            
            # 记录最终保存的文件路径
            logger.info(f"GIF已保存到: {output_path}")
            logger.info(f"原始帧数: {len(frames)}")
            logger.info(f"处理后帧数: {len(processed_frames)}")
            logger.info(f"帧间隔: {frame_duration}秒")
            logger.info(f"循环次数: {loop_count}")
            logger.info(f"调色板大小: {palette_size}")
            logger.info(f"是否优化: {optimize}")
            if transition_effect != "none" and transition_frames > 0:
                logger.info(f"过渡效果: {transition_effect}")
                logger.info(f"过渡帧数: {transition_frames}")
            
            return (output_path,)
            
        except Exception as e:
            logger.error(f"图片转GIF过程中发生错误: {str(e)}")
            raise e

class ImagesToGifNodeV1:
    """
    图片转GIF节点 V1
    将多张图片合并为GIF动画（无过渡效果）
    
    V1版本特性：
    - 基础GIF生成功能
    - 无过渡效果
    - 简化的参数设置
    
    质量等级说明：
    - 等级1: 最低质量，最小文件大小
    - 等级2: 低质量，较小文件大小
    - 等级3: 中等质量，平衡文件大小和质量
    - 等级4: 高质量，更好的图像质量
    - 等级5: 最高质量，最佳图像质量，支持隔行扫描
    """
    
    def __init__(self):
        """
        初始化图片转GIF节点 V1
        """
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # 创建10个独立的图片输入端口，但都是可选的
        required_inputs = {}
        optional_inputs = {}
        for i in range(1, 11):
            optional_inputs[f"image_{i}"] = ("IMAGE",)
        
        # 添加其他参数（去掉了过渡效果相关参数）
        required_inputs.update({
            "frame_duration": ("FLOAT", {
                "default": 1.0,
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
            "quality": (["1", "2", "3", "4", "5"], {
                "default": "5",
                "label": "质量等级",
                "description": "GIF质量等级（1=最低，2=低，3=中，4=高，5=最高）"
            }),
        })
        
        return {
            "required": required_inputs,
            "optional": {
                **optional_inputs,
                "output_filename": ("STRING", {
                    "default": "图片转gif_v1.gif",
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
                             output_filename="图片转gif_v1.gif"):
        """
        将多张图片合并为GIF动画（V1版本，无过渡效果）
        
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
            
            # 创建GIF（无过渡效果）
            if frames:
                # 将palette_size从字符串转换为整数
                palette_size_int = int(palette_size)
                
                # 计算帧的持续时间
                regular_frame_duration = int(frame_duration * 1000)
                
                # 准备GIF保存参数
                gif_kwargs = {
                    'format': 'GIF',
                    'save_all': True,
                    'append_images': frames[1:],
                    'duration': regular_frame_duration,  # 每帧持续时间（毫秒）
                    'loop': loop_count,
                    'optimize': optimize,
                    'palettesize': palette_size_int
                }
                
                # 根据质量等级设置不同的优化参数
                # 质量等级1: 最低质量，最小文件大小
                # 质量等级2: 低质量
                # 质量等级3: 中等质量
                # 质量等级4: 高质量
                # 质量等级5: 最高质量，最大文件大小
                
                if quality == "1":
                    # 最低质量设置 - 最小文件大小
                    gif_kwargs['subrectangles'] = False  # 不使用子矩形优化
                    gif_kwargs['optimize'] = True  # 优化文件大小
                    gif_kwargs['disposal'] = 2  # 处置方法：恢复到背景色
                elif quality == "2":
                    # 低质量设置 - 较小文件大小
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = True  # 优化文件大小
                    gif_kwargs['disposal'] = 2  # 处置方法：恢复到背景色
                elif quality == "3":
                    # 中等质量设置 - 平衡文件大小和质量
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = True  # 优化文件大小
                    gif_kwargs['disposal'] = 2  # 处置方法：恢复到背景色
                elif quality == "4":
                    # 高质量设置 - 更好的图像质量
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = False  # 不优化文件大小以保持质量
                    gif_kwargs['disposal'] = 1  # 处置方法：不处置
                else:  # quality == "5"
                    # 最高质量设置 - 最佳图像质量
                    gif_kwargs['subrectangles'] = True  # 使用子矩形优化
                    gif_kwargs['optimize'] = False  # 不优化文件大小以保持质量
                    gif_kwargs['disposal'] = 1  # 处置方法：不处置
                    gif_kwargs['interlace'] = True  # 隔行扫描以提高显示质量
                
                # 对帧进行量化处理以应用调色板大小
                quantized_frames = []
                for i, frame in enumerate(frames):
                    # 将图像转换为P模式（调色板模式）并应用指定的颜色数量
                    quantized_frame = frame.quantize(colors=palette_size_int, method=Image.MEDIANCUT)
                    quantized_frames.append(quantized_frame)
                
                # 更新GIF保存参数，确保使用量化后的帧
                gif_kwargs['append_images'] = quantized_frames[1:]  # 从第二帧开始的所有帧
                
                # 写入GIF文件
                quantized_frames[0].save(output_path, **gif_kwargs)
                
                # 记录帧数
                logger.info(f"处理后帧数: {len(frames)}")
            
            # 记录最终保存的文件路径
            logger.info(f"GIF已保存到: {output_path}")
            logger.info(f"帧数: {len(frames)}")
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
    "ImagesToGifNodeV2": ImagesToGifNodeV2,
    "ImagesToGifNodeV1": ImagesToGifNodeV1
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagesToGifNodeV2": "图片转GIF-V2",
    "ImagesToGifNodeV1": "图片转GIF-V1"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]