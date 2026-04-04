import os
import numpy as np
import torchaudio
from .. import NODE_CLASS_MAPPINGS as PRIMITIVE_TOOLS_NODE_CLASS_MAPPINGS


class SaveAudioNode:
    """
    保存音频节点 - 将音频数据保存为文件
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"label": "音频数据"}),
                "filename_prefix": ("STRING", {"default": "audio", "multiline": False, "label": "文件名前缀"}),
                "output_dir": ("STRING", {"default": "", "multiline": False, "label": "输出目录"}),
                "format": (["wav", "mp3", "flac", "ogg", "m4a"], {"default": "wav", "label": "音频格式"}),
                "sample_rate": ("INT", {"default": 44100, "min": 8000, "max": 192000, "step": 1000, "label": "采样率"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_path",)
    FUNCTION = "save_audio"
    CATEGORY = "XnanTool/音频处理"
    
    def save_audio(self, audio, filename_prefix, output_dir, format, sample_rate):
        """
        保存音频数据到文件
        
        Args:
            audio: 音频数据张量
            filename_prefix: 文件名前缀
            output_dir: 输出目录路径
            format: 音频格式
            sample_rate: 采样率
            
        Returns:
            tuple: (输出文件路径,)
        """
        try:
            # 处理输出目录
            if not output_dir or not output_dir.strip():
                output_dir = "output/audio"
            
            output_dir = os.path.abspath(output_dir)
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.{format}"
            output_path = os.path.join(output_dir, filename)
            
            # 处理音频数据
            if isinstance(audio, np.ndarray):
                audio_tensor = torch.from_numpy(audio)
            elif isinstance(audio, torch.Tensor):
                audio_tensor = audio
            else:
                raise ValueError(f"不支持的音频数据类型: {type(audio)}")
            
            # 确保张量是正确的形状 (batch, channels, frames)
            if audio_tensor.dim() == 1:
                audio_tensor = audio_tensor.unsqueeze(0).unsqueeze(0)
            elif audio_tensor.dim() == 2:
                if audio_tensor.shape[0] > audio_tensor.shape[1]:
                    audio_tensor = audio_tensor.unsqueeze(0)
                else:
                    audio_tensor = audio_tensor.unsqueeze(0).transpose(1, 2)
            
            # 转换为单声道或立体声
            if audio_tensor.dim() == 3:
                if audio_tensor.shape[1] > 2:
                    audio_tensor = audio_tensor[:, :2, :]
            
            # 保存音频文件
            audio_tensor = audio_tensor.squeeze(0)
            
            if format.lower() == "wav":
                torchaudio.save(output_path, audio_tensor, sample_rate, encoding="PCM_S")
            elif format.lower() == "mp3":
                torchaudio.save(output_path, audio_tensor, sample_rate)
            elif format.lower() == "flac":
                torchaudio.save(output_path, audio_tensor, sample_rate)
            elif format.lower() == "ogg":
                torchaudio.save(output_path, audio_tensor, sample_rate)
            elif format.lower() == "m4a":
                torchaudio.save(output_path, audio_tensor, sample_rate)
            
            print(f"[SaveAudioNode] 音频已保存: {output_path}")
            
            return (output_path,)
            
        except Exception as e:
            print(f"[SaveAudioNode] 保存音频时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return ("",)


NODE_CLASS_MAPPINGS = {
    "SaveAudioNode": SaveAudioNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveAudioNode": "保存音频"
}
