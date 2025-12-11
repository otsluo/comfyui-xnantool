import os
import hashlib
from PIL import Image
import numpy as np
import torch
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchRenameImagesByMD5Node:
    """
    批量重命名图片节点 - 基于MD5哈希值
    
    该节点可以批量读取图片文件，计算每张图片的MD5哈希值，
    并将图片文件重命名为对应的MD5值，避免重复文件并保持文件唯一性。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_directory": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "输入目录",
                    "description": "包含需要重命名图片的目录路径"
                }),
            },
            "optional": {
                "output_directory": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "输出目录",
                    "description": "重命名后图片保存的目录路径（留空则在原目录处理）"
                }),
                "overwrite_existing": ("BOOLEAN", {
                    "default": False,
                    "label": "覆盖已存在文件",
                    "description": "是否覆盖输出目录中已存在的同名文件"
                }),
                "delete_original_files": ("BOOLEAN", {
                    "default": False,
                    "label": "删除原始文件",
                    "description": "当输出目录留空或与输入目录相同时，是否删除重命名前的原始文件"
                }),
                "file_extensions": ("STRING", {
                    "default": "jpg,jpeg,png,bmp,gif,tiff,webp",
                    "multiline": True,
                    "label": "文件扩展名",
                    "description": "需要处理的图片文件扩展名，用逗号分隔"
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result_info",)
    FUNCTION = "rename_images_by_md5"
    CATEGORY = "XnanTool/图像处理"
    DESCRIPTION = "批量重命名图片文件，使用图片内容的MD5哈希值作为新文件名，确保文件唯一性并避免重复"

    def calculate_image_md5(self, image_path):
        """
        计算图片文件的MD5哈希值
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            str: 图片文件的MD5哈希值
        """
        try:
            # 以二进制方式读取文件内容并计算MD5
            with open(image_path, 'rb') as f:
                file_data = f.read()
                md5_hash = hashlib.md5(file_data).hexdigest()
                return md5_hash
        except Exception as e:
            logger.error(f"计算图片 {image_path} 的MD5时出错: {str(e)}")
            raise

    def is_supported_image(self, filename, extensions):
        """
        检查文件是否为支持的图片格式
        
        Args:
            filename (str): 文件名
            extensions (list): 支持的扩展名列表
            
        Returns:
            bool: 是否为支持的图片格式
        """
        _, ext = os.path.splitext(filename.lower())
        return ext.lstrip('.') in [ext.strip().lower() for ext in extensions]

    def rename_images_by_md5(self, input_directory, output_directory="", overwrite_existing=False, delete_original_files=False, file_extensions="jpg,jpeg,png,bmp,gif,tiff,webp"):
        """
        批量重命名图片文件为MD5哈希值
        
        Args:
            input_directory (str): 输入目录路径
            output_directory (str): 输出目录路径（可选）
            overwrite_existing (bool): 是否覆盖已存在文件
            delete_original_files (bool): 当输出目录留空或与输入目录相同时，是否删除重命名前的原始文件
            file_extensions (str): 支持的文件扩展名，逗号分隔
            
        Returns:
            tuple: (处理信息, 处理文件数, 重命名文件数, 错误信息)
        """
        # 检查输入目录是否存在
        if not os.path.exists(input_directory):
            error_msg = f"输入目录不存在: {input_directory}"
            logger.error(error_msg)
            return (error_msg, 0, 0, error_msg)
        
        if not os.path.isdir(input_directory):
            error_msg = f"输入路径不是目录: {input_directory}"
            logger.error(error_msg)
            return (error_msg, 0, 0, error_msg)
        
        # 如果未指定输出目录，则使用输入目录
        if not output_directory:
            output_directory = input_directory
        
        # 创建输出目录（如果不存在）
        if not os.path.exists(output_directory):
            try:
                os.makedirs(output_directory)
            except Exception as e:
                error_msg = f"无法创建输出目录 {output_directory}: {str(e)}"
                logger.error(error_msg)
                return (error_msg, 0, 0, error_msg)
        
        # 解析文件扩展名
        extensions = [ext.strip().lower() for ext in file_extensions.split(',')]
        
        # 获取所有支持的图片文件
        image_files = []
        for filename in os.listdir(input_directory):
            if self.is_supported_image(filename, extensions):
                image_files.append(filename)
        
        if not image_files:
            info_msg = f"在目录 {input_directory} 中未找到支持的图片文件"
            logger.info(info_msg)
            return (info_msg, 0, 0, "")
        
        processed_count = 0
        renamed_count = 0
        error_files = []
        
        # 处理每个图片文件
        for filename in image_files:
            try:
                processed_count += 1
                input_path = os.path.join(input_directory, filename)
                
                # 获取原始文件扩展名
                _, ext = os.path.splitext(filename.lower())
                
                # 计算MD5哈希值
                md5_hash = self.calculate_image_md5(input_path)
                new_filename = f"{md5_hash}{ext}"
                output_path = os.path.join(output_directory, new_filename)
                
                # 检查是否需要重命名（文件名不同）
                if new_filename != filename:
                    # 检查目标文件是否已存在
                    if os.path.exists(output_path) and not overwrite_existing:
                        logger.warning(f"文件 {new_filename} 已存在且未启用覆盖选项，跳过 {filename}")
                        continue
                    
                    # 复制文件到新名称
                    import shutil
                    shutil.copy2(input_path, output_path)
                    renamed_count += 1
                    logger.info(f"重命名文件: {filename} -> {new_filename}")
                    
                    # 如果需要删除原始文件，且输出目录与输入目录相同，则删除原始文件
                    if delete_original_files and input_directory == output_directory:
                        try:
                            os.remove(input_path)
                            logger.info(f"已删除原始文件: {filename}")
                        except Exception as e:
                            logger.warning(f"删除原始文件 {filename} 时出错: {str(e)}")
                else:
                    # 文件名已经是MD5值，无需重命名
                    if input_directory != output_directory:
                        # 如果指定了不同的输出目录，则复制文件
                        import shutil
                        shutil.copy2(input_path, output_path)
                        logger.info(f"复制文件: {filename} -> {output_directory}")
                    else:
                        logger.info(f"文件 {filename} 已经是MD5命名，无需重命名")
                        
            except Exception as e:
                error_msg = f"处理文件 {filename} 时出错: {str(e)}"
                logger.error(error_msg)
                error_files.append(f"{filename}: {str(e)}")
                continue
        
        # 生成处理结果信息
        if error_files:
            error_info = "\n".join(error_files)
        else:
            error_info = ""
        
        # 计算删除的文件数量
        deleted_count = 0
        if delete_original_files:
            # 如果删除原始文件，计算删除的数量（应该等于重命名的数量，因为只有重命名的文件才会被删除）
            deleted_count = renamed_count
        
        # 生成结构化的处理结果信息
        result_lines = []
        result_lines.append(f"处理完成: 共处理 {processed_count} 个文件，重命名 {renamed_count} 个文件")
        if delete_original_files and input_directory == output_directory:
            result_lines.append(f"删除 {deleted_count} 个原始文件")
        if error_info:
            result_lines.append(f"错误信息:\n{error_info}")
        
        result_info = "\n".join(result_lines)
        logger.info(result_info)
        
        return (result_info,)


# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "BatchRenameImagesByMD5Node": BatchRenameImagesByMD5Node
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchRenameImagesByMD5Node": "批量重命名图片(MD5)"
}

# 确保模块被正确导入
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']