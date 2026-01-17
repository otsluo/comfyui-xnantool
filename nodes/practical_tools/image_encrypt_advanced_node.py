import torch
import numpy as np
from PIL import Image
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class ImageEncryptNodeAdvanced:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "password": ("STRING", {
                    "multiline": False,
                    "default": "default_password"
                }),
                "encryption_method": (["AES-CFB"],)
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "encrypt_image_advanced"
    CATEGORY = "image/encryption"

    def encrypt_image_advanced(self, image, password, encryption_method):
        # 将tensor转换为numpy数组
        image_np = image.cpu().numpy()
        
        # 将图像数据转换为字节
        image_bytes = (image_np * 255).astype(np.uint8)
        
        # 使用密码生成密钥
        key = self._generate_key(password)
        
        if encryption_method == "AES-CFB":
            encrypted_bytes = self._encrypt_data_cfb(image_bytes.tobytes(), key)
            
        # 将加密后的字节转换回图像格式
        encrypted_array = np.frombuffer(encrypted_bytes, dtype=np.uint8)
        result = self._bytes_to_image(encrypted_array, image_np.shape)
            
        # 转换回tensor
        result_tensor = torch.from_numpy(result).float() / 255.0
        return (result_tensor,)

    def _generate_key(self, password):
        """使用SHA-256哈希函数从密码生成32字节密钥"""
        return hashlib.sha256(password.encode()).digest()

    def _encrypt_data_cfb(self, data, key):
        """使用AES-CFB加密数据"""
        # 生成随机IV
        iv = os.urandom(16)
        
        # 创建加密器
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # 加密数据
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # 返回IV和密文的组合
        return iv + ciphertext

    def _bytes_to_image(self, data, shape):
        """将字节数据转换为图像数组"""
        # 如果数据长度不匹配，进行截断或填充
        expected_size = np.prod(shape)
        if len(data) > expected_size:
            data = data[:expected_size]
        elif len(data) < expected_size:
            # 用零填充
            padding = np.zeros(expected_size - len(data), dtype=np.uint8)
            data = np.concatenate([data, padding])
            
        return data.reshape(shape)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "ImageEncryptNodeAdvanced": ImageEncryptNodeAdvanced,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageEncryptNodeAdvanced": "AES-CFB高级图像加密",
}