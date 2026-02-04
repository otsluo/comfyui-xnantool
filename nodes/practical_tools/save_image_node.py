import os
import folder_paths
from PIL import Image
import numpy as np
import torch

class SaveImageNode:
    """
    保存图片节点 - 将图像保存到指定路径
    """
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "file_path": ("STRING", {"default": ""}),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "folder_separator": ("STRING", {"default": "_"}),
                "num_padding_digits": ("INT", {"default": 3, "min": 1, "max": 10, "step": 1}),
                "extension": (["png", "jpg", "jpeg", "gif", "webp", "bmp"],),
                "quality": ("INT", {"default": 100, "min": 1, "max": 100, "step": 1}),
            },
            "hidden": {
                "prompt": "PROMPT", 
                "extra_pnginfo": "EXTRA_PNGINFO",
                "save_workflow": ("BOOLEAN", {"default": False})
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "save_result")
    OUTPUT_NODE = True
    FUNCTION = "save_images"
    CATEGORY = "XnanTool/实用工具"

    def save_images(self, images, file_path, filename_prefix="ComfyUI", folder_separator="_", num_padding_digits=3, extension="png", quality=100, prompt=None, extra_pnginfo=None, save_workflow=False):
        """
        保存图片到指定路径
        """
        # 确保输出目录存在
        full_output_dir = os.path.join(self.output_dir, file_path)
        if not os.path.exists(full_output_dir):
            os.makedirs(full_output_dir, exist_ok=True)
        
        results = []
        for idx, image in enumerate(images):
            # 转换图像格式
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # 生成文件名
            if filename_prefix and filename_prefix.strip():  # 检查文件名前缀是否为空或只包含空白字符
                if len(images) > 1:
                    filename = f"{filename_prefix}{folder_separator}{idx:0{num_padding_digits}d}.{extension}"
                else:
                    filename = f"{filename_prefix}.{extension}"
            else:  # 如果文件名前缀为空或只包含空白字符，使用默认前缀
                if len(images) > 1:
                    filename = f"ComfyUI{folder_separator}{idx:0{num_padding_digits}d}.{extension}"
                else:
                    filename = f"ComfyUI.{extension}"
            
            # 处理文件存在的情况 - 默认追加数值
            file_path_full = os.path.join(full_output_dir, filename)
            original_file_path_full = file_path_full
            counter = 1
            name, ext = os.path.splitext(filename)
            while os.path.exists(file_path_full):
                new_filename = f"{name}_{counter:0{num_padding_digits}d}{ext}"
                file_path_full = os.path.join(full_output_dir, new_filename)
                counter += 1
            
            # 保存图片
            try:
                if extension.lower() in ["jpg", "jpeg"]:
                    img = img.convert("RGB")  # JPEG不支持透明通道
                    if save_workflow:
                        # 保留工作流信息
                        exif_data = self._get_workflow_exif_data(prompt, extra_pnginfo)
                        if exif_data:
                            img.save(file_path_full, format=extension.upper(), quality=quality, exif=exif_data)
                        else:
                            img.save(file_path_full, format=extension.upper(), quality=quality)
                    else:
                        # 不保留工作流信息
                        img.save(file_path_full, format=extension.upper(), quality=quality)
                elif extension.lower() == "webp":
                    if save_workflow:
                        # 保留工作流信息
                        exif_data = self._get_workflow_exif_data(prompt, extra_pnginfo)
                        if exif_data:
                            img.save(file_path_full, format=extension.upper(), quality=quality, exif=exif_data)
                        else:
                            img.save(file_path_full, format=extension.upper(), quality=quality)
                    else:
                        # 不保留工作流信息
                        img.save(file_path_full, format=extension.upper(), quality=quality)
                elif extension.lower() == "png":
                    if save_workflow:
                        # 保留工作流信息
                        pnginfo_data = self._get_workflow_exif_data(prompt, extra_pnginfo)
                        if pnginfo_data:
                            img.save(file_path_full, format=extension.upper(), pnginfo=pnginfo_data)
                        else:
                            img.save(file_path_full, format=extension.upper())
                    else:
                        # 不保留工作流信息
                        img.save(file_path_full, format=extension.upper())
                else:
                    if save_workflow:
                        # 保留工作流信息
                        pnginfo_data = self._get_workflow_exif_data(prompt, extra_pnginfo)
                        if pnginfo_data:
                            img.save(file_path_full, format=extension.upper(), pnginfo=pnginfo_data)
                        else:
                            img.save(file_path_full, format=extension.upper())
                    else:
                        # 不保留工作流信息
                        img.save(file_path_full, format=extension.upper())
                
                results.append({
                    "filename": os.path.basename(file_path_full),
                    "subfolder": file_path,
                    "type": self.type
                })
                    
            except Exception as e:
                return {"ui": {"status": f"保存失败: {str(e)}"}, "result": (f"保存失败: {str(e)}",)}

        return {"ui": {"status": f"成功保存 {len(images)} 张图片"}, "result": (images, f"成功保存 {len(images)} 张图片到 {full_output_dir}")}

    @staticmethod
    def _get_workflow_exif_data(prompt, extra_pnginfo):
        """
        生成工作流EXIF/PNGINFO数据
        """
        from PIL.PngImagePlugin import PngInfo
        import json
        
        metadata = PngInfo()
        
        # 添加prompt信息
        if prompt:
            metadata.add_text("prompt", json.dumps(prompt))
        
        # 添加extra_pnginfo信息
        if extra_pnginfo:
            for x in extra_pnginfo:
                metadata.add_text(x, json.dumps(extra_pnginfo[x]))
        
        return metadata


NODE_CLASS_MAPPINGS = {
    "SaveImageNode": SaveImageNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageNode": "保存图片"
}