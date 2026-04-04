import os
from PIL import Image
import folder_paths

class BatchFolderImageCompressorNode:
    """
    批量文件夹图片压缩节点
    支持批量压缩文件夹中的图片，调整质量和格式
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        return {
            "required": {
                "image_directory": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输入图像文件夹路径"
                }),
                "output_directory": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输出图像保存路径（留空则保存到输入目录）"
                }),
                "output_format": (["JPEG", "PNG", "WebP"], {
                    "default": "JPEG",
                    "label": "输出格式",
                    "description": "选择输出图片的格式"
                }),
                "quality": ("INT", {
                    "default": 85,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "label": "压缩质量",
                    "description": "压缩质量（1-100），数值越大质量越高，文件越大"
                }),
                "max_width": ("INT", {
                    "default": 500,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                    "label": "最大宽度",
                    "description": "最大宽度（0表示不限制）"
                }),
                "max_height": ("INT", {
                    "default": 500,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                    "label": "最大高度",
                    "description": "最大高度（0表示不限制）"
                }),
                "keep_structure": (["是", "否"], {
                    "default": "是",
                    "label": "保留原始结构",
                    "description": "是：保留子目录结构；否：所有文件输出到同一目录"
                }),
                "process_subfolders": (["是", "否"], {
                    "default": "否",
                    "label": "压缩子目录",
                    "description": "是：递归处理所有子目录；否：仅处理当前目录"
                }),
                "conflict_mode": (["覆盖", "跳过", "数字后缀", "文本后缀"], {
                    "default": "数字后缀",
                    "label": "文件冲突处理",
                    "description": "当输出文件已存在时的处理方式"
                }),
                "suffix_text": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "后缀文本（仅文本后缀模式生效）",
                    "label": "自定义后缀文本",
                    "description": "在文件名后添加的自定义文本（例如：_compressed）"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result_info",)
    FUNCTION = "compress_images"
    CATEGORY = "XnanTool/图像处理"
    
    def compress_images(self, image_directory, output_directory, output_format, quality, max_width, max_height, keep_structure, process_subfolders, conflict_mode, suffix_text):
        """
        批量压缩文件夹中的图片
        
        Args:
            image_directory: 输入图像文件夹路径
            output_directory: 输出图像保存路径
            output_format: 输出格式 (JPEG, PNG, WebP)
            quality: 压缩质量 (1-100)
            max_width: 最大宽度 (0表示不限制)
            max_height: 最大高度 (0表示不限制)
            keep_structure: 是否保留原始目录结构
            process_subfolders: 是否压缩子目录
            conflict_mode: 文件冲突处理方式（覆盖、跳过、数字后缀、文本后缀）
            suffix_text: 自定义后缀文本
            
        Returns:
            result_info: 处理结果信息
        """
        # 检查输入目录是否存在
        if not os.path.exists(image_directory):
            return (f"❌ 错误: 输入目录不存在 - {image_directory}",)
        
        if not os.path.isdir(image_directory):
            return (f"❌ 错误: 输入路径不是目录 - {image_directory}",)
        
        # 获取支持的图像格式
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.gif')
        
        # 收集所有图像文件（包括子目录）
        image_files = []
        if process_subfolders == "是":
            # 递归处理所有子目录
            for root, dirs, files in os.walk(image_directory):
                for file in files:
                    if file.lower().endswith(supported_formats):
                        full_path = os.path.join(root, file)
                        if keep_structure == "是":
                            rel_path = os.path.relpath(full_path, image_directory)
                            image_files.append((full_path, rel_path))
                        else:
                            image_files.append((full_path, os.path.basename(full_path)))
        else:
            # 只处理当前目录
            for f in os.listdir(image_directory):
                if os.path.isfile(os.path.join(image_directory, f)) and f.lower().endswith(supported_formats):
                    full_path = os.path.join(image_directory, f)
                    image_files.append((full_path, f))
        
        if not image_files:
            return (f"⚠️ 警告: 在指定目录中未找到支持的图像文件 - {image_directory}",)
        
        # 设置输出目录
        if not output_directory.strip():
            output_directory = image_directory
        elif not os.path.exists(output_directory):
            try:
                os.makedirs(output_directory)
            except Exception as e:
                return (f"❌ 错误: 无法创建输出目录 - {output_directory}, {str(e)}",)
        
        # 处理每个图像文件
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for input_path, rel_path in image_files:
            try:
                # 构建输出文件路径
                file_name, _ = os.path.splitext(os.path.basename(input_path))
                output_ext = '.' + output_format.lower()
                
                if keep_structure == "是":
                    # 保留子目录结构
                    rel_dir = os.path.dirname(rel_path)
                    if rel_dir:
                        output_subdir = os.path.join(output_directory, rel_dir)
                        if not os.path.exists(output_subdir):
                            os.makedirs(output_subdir)
                        output_path = os.path.join(output_subdir, f"{file_name}{output_ext}")
                    else:
                        output_path = os.path.join(output_directory, f"{file_name}{output_ext}")
                else:
                    # 不保留子目录结构，所有文件输出到同一目录
                    output_path = os.path.join(output_directory, f"{file_name}{output_ext}")
                
                # 处理文件冲突
                if os.path.exists(output_path):
                    if conflict_mode == "跳过":
                        skipped_count += 1
                        continue
                    elif conflict_mode == "数字后缀":
                        # 数字后缀模式
                        counter = 1
                        while os.path.exists(output_path):
                            output_path = os.path.join(output_directory, f"{file_name}_{counter:02d}{output_ext}")
                            counter += 1
                    elif conflict_mode == "文本后缀":
                        # 文本后缀模式
                        suffix = suffix_text if suffix_text else "_compressed"
                        counter = 1
                        while os.path.exists(output_path):
                            output_path = os.path.join(output_directory, f"{file_name}{suffix}_{counter:02d}{output_ext}")
                            counter += 1
                
                # 打开图像
                with Image.open(input_path) as img:
                    # 转换为RGB模式（如果需要）
                    if img.mode in ('RGBA', 'P', 'LA'):
                        # 对于有透明通道的图片，使用白色背景
                        if img.mode == 'RGBA':
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[3])
                            img = background
                        else:
                            img = img.convert('RGB')
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 调整尺寸
                    if max_width > 0 or max_height > 0:
                        original_width, original_height = img.size
                        
                        if max_width > 0 and max_height > 0:
                            # 同时限制宽高
                            new_width = min(original_width, max_width)
                            new_height = min(original_height, max_height)
                            
                            # 保持宽高比
                            width_ratio = new_width / original_width
                            height_ratio = new_height / original_height
                            ratio = min(width_ratio, height_ratio)
                            
                            new_width = int(original_width * ratio)
                            new_height = int(original_height * ratio)
                            
                            img = img.resize((new_width, new_height), Image.LANCZOS)
                        elif max_width > 0:
                            # 只限制宽度
                            if original_width > max_width:
                                ratio = max_width / original_width
                                new_height = int(original_height * ratio)
                                img = img.resize((max_width, new_height), Image.LANCZOS)
                        elif max_height > 0:
                            # 只限制高度
                            if original_height > max_height:
                                ratio = max_height / original_height
                                new_width = int(original_width * ratio)
                                img = img.resize((new_width, max_height), Image.LANCZOS)
                    
                    # 保存压缩后的图像
                    if output_format == "JPEG":
                        img.save(output_path, format='JPEG', quality=quality, optimize=True)
                    elif output_format == "WebP":
                        img.save(output_path, format='WebP', quality=quality, method=6)
                    else:  # PNG
                        # PNG不支持quality参数，使用optimize
                        img.save(output_path, format='PNG', optimize=True)
                    
                    processed_count += 1
                    
            except Exception as e:
                print(f"处理图像时出错 {input_path}: {str(e)}")
                error_count += 1
                continue
        
        # 返回处理结果信息
        subfolder_info = "（包含子目录）" if process_subfolders == "是" else "（仅当前目录）"
        structure_info = "（保留原始结构）" if keep_structure == "是" else "（所有文件输出到同一目录）"
        result = f"✅ 批量压缩完成！\n" \
                f"处理: {processed_count} 个文件\n" \
                f"跳过: {skipped_count} 个文件\n" \
                f"错误: {error_count} 个文件\n" \
                f"总文件数: {len(image_files)}\n" \
                f"范围: {subfolder_info}\n" \
                f"模式: {structure_info}\n" \
                f"保存路径: {output_directory}"
        
        return (result,)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "BatchFolderImageCompressorNode": BatchFolderImageCompressorNode
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchFolderImageCompressorNode": "批量文件夹图片压缩"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
