import os
import folder_paths
import torch
import soundfile as sf
import numpy as np

class LoadAudioPathNode:
    """
    加载音频路径节点 - 加载音频文件路径
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "音频文件路径",
                    "description": "音频文件的完整路径或相对路径"
                }),
            }
        }
    
    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "audio_path")
    FUNCTION = "load_audio"
    CATEGORY = "XnanTool/媒体处理"
    
    def load_audio(self, audio_path):
        """
        加载音频文件路径
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            tuple: (音频数据, 音频路径字符串)
        """
        try:
            if not audio_path or not audio_path.strip():
                return (None, "")
            
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                print(f"[LoadAudioPathNode] 错误：音频文件不存在: {audio_path}")
                return (None, "")
            
            # 加载音频数据
            try:
                audio_data_np, sample_rate = sf.read(audio_path)
                
                # 转换为单声道或双声道
                if len(audio_data_np.shape) > 1:
                    audio_data_np = audio_data_np.mean(axis=1)
                
                # 转换为张量
                audio_tensor = torch.from_numpy(audio_data_np).unsqueeze(0).unsqueeze(0)
                
                audio_data = {
                    "waveform": audio_tensor,
                    "sample_rate": sample_rate
                }
                
                print(f"[LoadAudioPathNode] 音频加载成功: {audio_path}, 采样率: {sample_rate}")
            except Exception as e:
                print(f"[LoadAudioPathNode] 加载音频数据失败: {str(e)}")
                return (None, "")
            
            return (audio_data, audio_path)
            
        except Exception as e:
            print(f"[LoadAudioPathNode] 加载音频时发生错误: {str(e)}")
            return (None, "")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "LoadAudioPathNode": LoadAudioPathNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadAudioPathNode": "加载音频路径",
}
