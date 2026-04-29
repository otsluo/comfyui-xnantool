import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import glob
import folder_paths


class CoverTextGeneratorNode:
    """
    封面文字生成器节点 - 生成透明底文字图片
    支持文字位置选择、角度微调、字体选择、描边效果
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "封面文字",
                    "multiline": True,
                    "label": "文字内容",
                    "description": "要显示的文字内容"
                }),
                "width": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                    "label": "图片宽度",
                    "description": "输出图片的宽度"
                }),
                "height": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 8192,
                    "step": 1,
                    "label": "图片高度",
                    "description": "输出图片的高度"
                }),
                "position": (["左上", "中上", "右上", "左中", "居中", "右中", "左下", "中下", "右下"], {
                    "default": "居中",
                    "label": "文字位置",
                    "description": "文字在图片中的位置"
                }),
                "alignment": (["左对齐", "居中对齐", "右对齐"], {
                    "default": "居中对齐",
                    "label": "对齐方式",
                    "description": "多行文字的对齐方式"
                }),
                "font_name": (cls._get_system_fonts(), {
                    "default": "微软雅黑",
                    "label": "字体选择",
                    "description": "选择系统字体"
                }),
                "font_size": ("INT", {
                    "default": 72,
                    "min": 1,
                    "max": 500,
                    "step": 1,
                    "label": "字体大小",
                    "description": "文字的字体大小"
                }),
                "rotation": ("INT", {
                    "default": 0,
                    "min": -180,
                    "max": 180,
                    "step": 1,
                    "label": "旋转角度",
                    "description": "文字的旋转角度（-180到180）"
                }),
                "text_color": ("STRING", {
                    "default": "#FFFFFF",
                    "multiline": False,
                    "label": "文字颜色",
                    "description": "文字的颜色（十六进制）"
                }),
                "stroke_color": ("STRING", {
                    "default": "#000000",
                    "multiline": False,
                    "label": "描边颜色",
                    "description": "文字描边的颜色（十六进制）"
                }),
                "stroke_width": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "label": "描边大小",
                    "description": "文字描边的宽度（0表示不描边）"
                }),
                "stroke_style": (["外描边", "发光效果"], {
                    "default": "外描边",
                    "label": "描边样式",
                    "description": "文字描边的样式"
                }),
            },
            "optional": {
                "font_file": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "自定义字体路径",
                    "description": "自定义字体文件路径（.ttf或.otf，优先使用此路径）"
                }),
                "offset_x": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1,
                    "label": "水平偏移",
                    "description": "文字的水平偏移量（像素）"
                }),
                "offset_y": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1,
                    "label": "垂直偏移",
                    "description": "文字的垂直偏移量（像素）"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_cover_image"
    CATEGORY = "XnanTool/实用工具"
    OUTPUT_NODE = False
    
    @classmethod
    def _get_system_fonts(cls):
        """获取ComfyUI的models/fonts目录下的字体列表"""
        font_list = ["默认字体"]
        
        # 使用folder_paths获取ComfyUI的models目录
        try:
            models_dir = folder_paths.get_folder_paths("custom_nodes")[0] if folder_paths.get_folder_paths("custom_nodes") else ""
            if models_dir:
                comfyui_dir = os.path.dirname(os.path.dirname(models_dir))
                fonts_dir = os.path.join(comfyui_dir, "models", "fonts")
            else:
                fonts_dir = None
        except:
            fonts_dir = None
        
        if not fonts_dir or not os.path.exists(fonts_dir):
            # 备用方案：从当前文件路径向上推导
            comfyui_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            fonts_dir = os.path.join(comfyui_dir, "models", "fonts")
        
        # 字体文件名到文件路径的映射
        font_file_mapping = {}
        
        try:
            if os.path.exists(fonts_dir):
                font_files = glob.glob(os.path.join(fonts_dir, "*.ttf")) + \
                            glob.glob(os.path.join(fonts_dir, "*.ttc")) + \
                            glob.glob(os.path.join(fonts_dir, "*.otf"))
                
                for font_file in font_files:
                    font_filename = os.path.splitext(os.path.basename(font_file))[0]
                    
                    if font_filename not in font_list:
                        font_list.append(font_filename)
                    font_file_mapping[font_filename] = font_file
        
        except Exception as e:
            print(f"⚠️ 获取字体失败: {e}")
        
        # 存储字体映射供后续使用
        cls._font_file_mapping = font_file_mapping
        
        return sorted(font_list, key=lambda x: (x == "默认字体", x))
    
    def generate_cover_image(self, text, width, height, position, alignment, font_name="默认字体", font_size=48, rotation=0, 
                            text_color="#FFFFFF", stroke_color="#000000", stroke_width=0, stroke_style="外描边", font_file="", offset_x=0, offset_y=0):
        """
        生成透明底文字图片
        
        Args:
            text: 文字内容
            width: 图片宽度
            height: 图片高度
            position: 文字位置
            alignment: 对齐方式
            font_name: 字体名称
            font_size: 字体大小
            rotation: 旋转角度
            text_color: 文字颜色
            stroke_color: 描边颜色
            stroke_width: 描边宽度
            stroke_style: 描边样式
            font_file: 自定义字体文件路径
            offset_x: 水平偏移
            offset_y: 垂直偏移
            
        Returns:
            tuple: (图片tensor)
        """
        if not text or not text.strip():
            # 返回空透明图片
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            return (self._pil_to_tensor(image),)
        
        # 解析颜色值
        text_rgb = self._parse_color(text_color)
        stroke_rgb = self._parse_color(stroke_color)
        
        # 创建透明背景图片
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 加载字体
        font = self._load_font(font_name, font_file, font_size)
        
        # 处理多行文字
        lines = text.split('\n')
        
        # 计算文字位置
        x, y = self._calculate_position(lines, width, height, position, alignment, font, offset_x, offset_y)
        
        # 绘制文字
        if rotation == 0:
            # 不需要旋转，直接绘制
            line_height = self._get_line_height(font)
            current_y = y
            
            for line in lines:
                # 根据对齐方式计算x坐标
                line_x = self._calculate_line_x(line, x, width, alignment, font)
                
                self._draw_text_with_stroke(draw, line_x, current_y, line, text_rgb, stroke_rgb, stroke_width, stroke_style, font)
                
                current_y += line_height
        else:
            # 需要旋转，创建临时图片进行旋转
            # 先获取所有行的尺寸
            line_height = self._get_line_height(font)
            total_height = line_height * len(lines)
            
            # 获取最宽行的宽度
            max_width = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                max_width = max(max_width, line_width)
            
            # 创建足够大的临时图片
            padding = max(max_width, total_height) // 2 + 10 + stroke_width * 2
            temp_size = int(max(max_width, total_height) * 1.5) + padding * 2
            temp_image = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_image)
            
            # 在临时图片中心绘制多行文字
            current_y = (temp_size - total_height) // 2
            
            for line in lines:
                # 根据对齐方式计算x坐标
                line_x = self._calculate_line_x(line, (temp_size - max_width) // 2, temp_size, alignment, font)
                
                self._draw_text_with_stroke(temp_draw, line_x, current_y, line, text_rgb, stroke_rgb, stroke_width, stroke_style, font)
                
                current_y += line_height
            
            # 旋转
            rotated_image = temp_image.rotate(-rotation, resample=Image.BICUBIC, expand=True)
            
            # 粘贴到主图片
            paste_x = int(x - rotated_image.width // 2 + max_width // 2)
            paste_y = int(y - rotated_image.height // 2 + total_height // 2)
            
            image.paste(rotated_image, (paste_x, paste_y), rotated_image)
        
        print(f"🎨 生成封面文字图片: {width}x{height}, 位置: {position}, 字体: {font_name}, 字体大小: {font_size}, 旋转: {rotation}°, 描边: {stroke_width}px")
        
        return (self._pil_to_tensor(image),)
    
    def _parse_color(self, color_str):
        """解析颜色字符串为RGBA元组"""
        if color_str.startswith('#'):
            hex_color = color_str.lstrip('#')
            if len(hex_color) == 6:
                r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            elif len(hex_color) == 3:
                r, g, b = tuple(int(hex_color[i:i+1]*2, 16) for i in (0, 1, 2))
            else:
                r, g, b = 255, 255, 255
        else:
            r, g, b = 255, 255, 255
        
        return (r, g, b, 255)
    
    def _load_font(self, font_name, font_file, font_size):
        """加载字体文件"""
        # 优先使用自定义字体路径
        if font_file and os.path.exists(font_file):
            try:
                return ImageFont.truetype(font_file, font_size)
            except Exception as e:
                print(f"⚠️ 自定义字体加载失败: {e}")
        
        # 使用字体文件映射（从fonts目录）
        if hasattr(self, '_font_file_mapping') and font_name in self._font_file_mapping:
            font_path = self._font_file_mapping[font_name]
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except Exception as e:
                    print(f"⚠️ 字体加载失败: {e}")
        
        # 使用默认字体
        print(f"⚠️ 使用默认字体，可能不支持中文")
        return ImageFont.load_default()
    
    def _draw_text_with_stroke(self, draw, x, y, text, text_rgb, stroke_rgb, stroke_width, stroke_style, font):
        """根据描边样式绘制文字"""
        if stroke_width == 0:
            # 不描边
            draw.text((x, y), text, fill=text_rgb, font=font)
            return
        
        if stroke_style == "外描边":
            # 外描边：描边只在文字外部
            # 先绘制描边
            draw.text((x, y), text, fill=stroke_rgb, font=font, stroke_width=stroke_width, stroke_fill=stroke_rgb)
            # 再绘制文字覆盖内部
            draw.text((x, y), text, fill=text_rgb, font=font)
        
        elif stroke_style == "发光效果":
            # 发光效果：多层渐变描边
            for i in range(stroke_width * 2, 0, -1):
                alpha = int(255 * (1 - i / (stroke_width * 2)))
                glow_color = (stroke_rgb[0], stroke_rgb[1], stroke_rgb[2], alpha)
                draw.text((x, y), text, fill=glow_color, font=font, stroke_width=i, stroke_fill=glow_color)
            draw.text((x, y), text, fill=text_rgb, font=font)
    
    def _get_line_height(self, font):
        """获取行高"""
        temp_image = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_image)
        bbox = temp_draw.textbbox((0, 0), "测试", font=font)
        return int((bbox[3] - bbox[1]) * 1.2)  # 1.2倍行距
    
    def _calculate_line_x(self, line, base_x, width, alignment, font):
        """根据对齐方式计算行的x坐标"""
        bbox = ImageDraw.Draw(Image.new('RGBA', (1, 1), (0, 0, 0, 0))).textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        
        if alignment == "左对齐":
            return base_x
        elif alignment == "右对齐":
            return base_x + (width - base_x * 2 - line_width) if base_x > 0 else width - line_width - 20
        else:  # 居中对齐
            return base_x
    
    def _calculate_position(self, lines, width, height, position, alignment, font, offset_x, offset_y):
        """计算文字位置"""
        # 获取所有行的尺寸
        line_height = self._get_line_height(font)
        total_height = line_height * len(lines)
        
        # 获取最宽行的宽度
        max_width = 0
        for line in lines:
            bbox = ImageDraw.Draw(Image.new('RGBA', (1, 1), (0, 0, 0, 0))).textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            max_width = max(max_width, line_width)
        
        # 计算基础位置
        if "左" in position:
            x = 20
        elif "右" in position:
            x = width - max_width - 20
        else:  # 中
            x = (width - max_width) // 2
        
        if "上" in position:
            y = 20
        elif "下" in position:
            y = height - total_height - 20
        else:  # 中
            y = (height - total_height) // 2
        
        # 应用偏移
        x += offset_x
        y += offset_y
        
        return x, y
    
    def _pil_to_tensor(self, pil_image):
        """将PIL图片转换为ComfyUI的tensor格式"""
        # 保留RGBA通道（如果有的话）
        if pil_image.mode == 'RGBA':
            image_np = np.array(pil_image).astype(np.float32) / 255.0
        elif pil_image.mode == 'RGB':
            image_np = np.array(pil_image).astype(np.float32) / 255.0
        else:
            image_np = np.array(pil_image.convert('RGB')).astype(np.float32) / 255.0
        
        # 转换为tensor格式 (H, W, C) -> (1, H, W, C)
        image_tensor = torch.from_numpy(image_np)[None,]
        
        return image_tensor


# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "CoverTextGeneratorNode": CoverTextGeneratorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CoverTextGeneratorNode": "封面文字生成器",
}
