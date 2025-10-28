import torch
import numpy as np
from PIL import Image
import uuid
import os
import hashlib

class Imageencodinggeneration:
    """
    图片编码生成节点 - 读取图片并生成唯一的UUID值和多种哈希值(MD5, SHA1, SHA256, SHA512)
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "image_path": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("uuid", "md5", "sha1", "sha256", "sha512", "image_info")
    FUNCTION = "generate_uuid"
    CATEGORY = "XnanTool/实用工具/小工具"

    def generate_uuid(self, image, image_path=""):
        """
        读取图片并生成UUID和多种哈希值
        
        Args:
            image: 输入的图片张量
            image_path: 可选的图片文件路径
            
        Returns:
            tuple: 包含生成的UUID字符串、MD5、SHA1、SHA256、SHA512哈希值和图片信息
        """
        # 生成UUID
        generated_uuid = str(uuid.uuid4())
        
        # 计算各种哈希值
        md5_hash = self.calculate_hash(image, "MD5", image_path)
        sha1_hash = self.calculate_hash(image, "SHA1", image_path)
        sha256_hash = self.calculate_hash(image, "SHA256", image_path)
        sha512_hash = self.calculate_hash(image, "SHA512", image_path)
        
        # 获取图片信息
        if hasattr(image, 'shape'):
            image_info = f"图片尺寸: {image.shape}"
        else:
            image_info = "图片信息不可用"
            
        # 如果提供了图片路径，则获取文件信息
        if image_path and os.path.exists(image_path):
            try:
                file_size = os.path.getsize(image_path)
                file_name = os.path.basename(image_path)
                image_info = f"文件名: {file_name}, 大小: {file_size} bytes, 尺寸: {image.shape if hasattr(image, 'shape') else '未知'}"
            except Exception as e:
                image_info = f"无法获取文件信息: {str(e)}"
        
        print(f"🖼️ 读取图片并生成UUID: {generated_uuid}")
        print(f"🔍 图片MD5哈希值: {md5_hash}")
        print(f"🔍 图片SHA1哈希值: {sha1_hash}")
        print(f"🔍 图片SHA256哈希值: {sha256_hash}")
        print(f"🔍 图片SHA512哈希值: {sha512_hash}")
        print(f"📋 图片信息: {image_info}")
        
        return (generated_uuid, md5_hash, sha1_hash, sha256_hash, sha512_hash, image_info)
    
    def calculate_hash(self, image, algorithm="MD5", image_path=""):
        """
        计算图片的哈希值
        
        Args:
            image: 输入的图片张量
            algorithm: 哈希算法类型 (MD5, SHA1, SHA256, SHA512)
            image_path: 可选的图片文件路径
            
        Returns:
            str: 图片的哈希值
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
            
            # 如果提供了有效的图片路径，直接从文件计算哈希值
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    # 分块读取文件以节省内存
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)
                return hasher.hexdigest()
            
            # 如果没有有效路径，从图片张量计算哈希值
            # 将图片张量转换为字节数据
            if isinstance(image, torch.Tensor):
                # 确保数据在CPU上并转换为numpy数组
                image_data = image.cpu().numpy()
            else:
                image_data = image
            
            # 将数据展平并转换为字节
            image_bytes = image_data.tobytes()
            
            # 计算哈希值
            hasher.update(image_bytes)
            return hasher.hexdigest()
            
        except Exception as e:
            print(f"⚠️ 计算{algorithm}哈希值时出错: {str(e)}")
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
    "Imageencodinggeneration": Imageencodinggeneration
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Imageencodinggeneration": "图片编码生成节点"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']