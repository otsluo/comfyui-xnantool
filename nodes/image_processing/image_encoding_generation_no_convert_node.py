import torch
import numpy as np
from PIL import Image
import uuid
import os
import hashlib

class ImageEncodingGenerationNoConvertNode:
    """
    图片编码生成节点-不转化 - 直接从文件路径读取图片并生成唯一的UUID值和多种哈希值(MD5, SHA1, SHA256, SHA512)
    不进行图像格式转换，确保哈希值与原始文件一致
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_path": ("STRING", {
                    "label": "图片路径",
                    "description": "图片文件的完整路径",
                    "default": "",
                    "multiline": True,
                    "placeholder": "请输入图片路径",
                    "dynamicPrompts": False
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("uuid", "md5", "sha1", "sha256", "sha512", "image_info")
    FUNCTION = "generate_uuid_no_convert"
    CATEGORY = "❤️❤️❤️XnanTool/图像处理"

    def generate_uuid_no_convert(self, image_path):
        """
        直接从文件路径读取图片并生成UUID和多种哈希值，不进行图像格式转换
        
        Args:
            image_path (str): 图片文件的完整路径
            
        Returns:
            tuple: 包含生成的UUID字符串、MD5、SHA1、SHA256、SHA512哈希值和图片信息
        """
        try:
            # 检查图像文件是否存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图像文件不存在: {image_path}")
            
            # 生成UUID
            generated_uuid = str(uuid.uuid4())
            
            # 计算各种哈希值（直接从文件计算，不进行转换）
            md5_hash = self.calculate_file_hash(image_path, "MD5")
            sha1_hash = self.calculate_file_hash(image_path, "SHA1")
            sha256_hash = self.calculate_file_hash(image_path, "SHA256")
            sha512_hash = self.calculate_file_hash(image_path, "SHA512")
            
            # 获取图片信息
            try:
                image = Image.open(image_path)
                image_info = f"图片尺寸: {image.size}, 格式: {image.format}, 模式: {image.mode}"
                image.close()
            except Exception as e:
                image_info = f"无法获取图片信息: {str(e)}"
            
            print(f"🖼️ 读取图片并生成UUID: {generated_uuid}")
            print(f"🔍 图片MD5哈希值: {md5_hash}")
            print(f"🔍 图片SHA1哈希值: {sha1_hash}")
            print(f"🔍 图片SHA256哈希值: {sha256_hash}")
            print(f"🔍 图片SHA512哈希值: {sha512_hash}")
            print(f"📋 图片信息: {image_info}")
            
            return (generated_uuid, md5_hash, sha1_hash, sha256_hash, sha512_hash, image_info)
            
        except Exception as e:
            print(f"⚠️ 生成UUID和哈希值时出错: {str(e)}")
            # 返回默认值
            return (str(uuid.uuid4()), "error", "error", "error", "error", f"错误: {str(e)}")

    def calculate_file_hash(self, file_path, algorithm="MD5"):
        """
        直接从文件计算哈希值，不进行任何转换
        
        Args:
            file_path (str): 文件路径
            algorithm (str): 哈希算法类型 (MD5, SHA1, SHA256, SHA512)
            
        Returns:
            str: 文件的哈希值
        """
        try:
            # 根据算法类型创建相应的哈希对象
            if algorithm == "MD5":
                hasher = hashlib.md5()
            elif algorithm == "SHA1":
                hasher = hashlib.sha1()
            elif algorithm == "SHA256":
                hasher = hashlib.sha256()
            elif algorithm == "SHA512":
                hasher = hashlib.sha512()
            else:
                # 默认使用MD5
                hasher = hashlib.md5()
            
            # 以二进制模式打开文件并逐块读取计算哈希值
            with open(file_path, 'rb') as f:
                # 分块读取文件以处理大文件
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception as e:
            print(f"⚠️ 计算文件{algorithm}哈希值时出错: {str(e)}")
            # 返回默认值
            if algorithm == "MD5":
                return "00000000000000000000000000000000"
            elif algorithm == "SHA1":
                return "0000000000000000000000000000000000000000"
            elif algorithm == "SHA256":
                return "0000000000000000000000000000000000000000000000000000000000000000"
            elif algorithm == "SHA512":
                return "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
            else:
                return "00000000000000000000000000000000"

# 注册节点
NODE_CLASS_MAPPINGS = {
    "ImageEncodingGenerationNoConvertNode": ImageEncodingGenerationNoConvertNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageEncodingGenerationNoConvertNode": "图片编码生成-不转化"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']