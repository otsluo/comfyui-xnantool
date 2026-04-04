import os
import hashlib
import shutil

class BatchRenameVideoByMD5Node:
    """
    批量重命名视频MD5节点 - 将视频文件重命名为其MD5哈希值
    
    该节点可以批量读取视频文件，计算每个视频的MD5哈希值，
    并将视频文件重命名为对应的MD5值，避免重复文件并保持文件唯一性。
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_folder": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "视频文件夹路径",
                    "description": "包含视频文件的文件夹路径"
                }),
                "output_folder": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "输出文件夹路径",
                    "description": "重命名后视频保存的文件夹路径（留空则在原文件夹）"
                }),
                "include_subfolders": ("BOOLEAN", {
                    "default": False,
                    "label": "包含子文件夹",
                    "description": "是否递归处理子文件夹中的视频文件"
                }),
            },
            "optional": {
                "overwrite_existing": ("BOOLEAN", {
                    "default": False,
                    "label": "覆盖已存在文件",
                    "description": "是否覆盖输出文件夹中已存在的同名文件"
                }),
                "delete_original_files": ("BOOLEAN", {
                    "default": False,
                    "label": "删除原始文件",
                    "description": "当输出文件夹留空或与输入文件夹相同时，是否删除重命名前的原始文件"
                }),
                "video_extensions": ("STRING", {
                    "default": "mp4,avi,mov,mkv,wmv,flv,webm",
                    "multiline": True,
                    "label": "视频扩展名",
                    "description": "需要处理的视频文件扩展名，用逗号分隔"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("info",)
    FUNCTION = "batch_rename_video_md5"
    CATEGORY = "XnanTool/媒体处理"
    DESCRIPTION = "批量重命名视频文件，使用视频内容的MD5哈希值作为新文件名，确保文件唯一性并避免重复"
    
    def calculate_md5(self, file_path):
        """
        计算文件的MD5哈希值
        
        Args:
            file_path: 文件路径
            
        Returns:
            MD5哈希值字符串
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"[BatchRenameVideoByMD5Node] 计算MD5失败: {str(e)}")
            return None
    
    def is_supported_video(self, filename, extensions):
        """
        检查文件是否为支持的视频格式
        
        Args:
            filename (str): 文件名
            extensions (list): 支持的扩展名列表
            
        Returns:
            bool: 是否为支持的视频格式
        """
        _, ext = os.path.splitext(filename.lower())
        return ext.lstrip('.') in [ext.strip().lower() for ext in extensions]
    
    def batch_rename_video_md5(self, video_folder, output_folder, include_subfolders, overwrite_existing=False, delete_original_files=False, video_extensions="mp4,avi,mov,mkv,wmv,flv,webm"):
        """
        批量重命名视频文件为MD5哈希值
        
        Args:
            video_folder: 视频文件夹路径
            output_folder: 输出文件夹路径
            include_subfolders: 是否包含子文件夹
            overwrite_existing: 是否覆盖已存在文件
            delete_original_files: 是否删除原始文件
            video_extensions: 视频扩展名，逗号分隔
            
        Returns:
            tuple: (输出文件夹路径, 信息)
        """
        try:
            # 检查输入文件夹是否存在
            if not os.path.exists(video_folder):
                return ("", f"错误：视频文件夹不存在: {video_folder}")
            
            if not os.path.isdir(video_folder):
                return ("", f"错误：输入路径不是文件夹: {video_folder}")
            
            # 如果输出文件夹为空，使用原文件夹
            if not output_folder or not output_folder.strip():
                output_folder = video_folder
            
            # 创建输出文件夹
            os.makedirs(output_folder, exist_ok=True)
            
            # 解析视频扩展名
            extensions = [ext.strip().lower() for ext in video_extensions.split(',')]
            
            # 收集所有视频文件
            video_files = []
            if include_subfolders:
                for root, dirs, files in os.walk(video_folder):
                    for file in files:
                        if self.is_supported_video(file, extensions):
                            video_files.append(os.path.join(root, file))
            else:
                for file in os.listdir(video_folder):
                    file_path = os.path.join(video_folder, file)
                    if os.path.isfile(file_path):
                        if self.is_supported_video(file, extensions):
                            video_files.append(file_path)
            
            if not video_files:
                return (output_folder, "未找到任何视频文件")
            
            # 重命名视频文件
            success_count = 0
            fail_count = 0
            skip_count = 0
            renamed_count = 0
            
            for video_path in video_files:
                try:
                    # 获取原文件名
                    original_filename = os.path.basename(video_path)
                    
                    # 计算MD5
                    md5_hash = self.calculate_md5(video_path)
                    if not md5_hash:
                        fail_count += 1
                        continue
                    
                    # 获取原文件扩展名
                    _, ext = os.path.splitext(original_filename.lower())
                    
                    # 生成新文件名
                    new_filename = f"{md5_hash}{ext}"
                    new_path = os.path.join(output_folder, new_filename)
                    
                    # 检查是否是同一个文件
                    if os.path.abspath(video_path) == os.path.abspath(new_path):
                        skip_count += 1
                        print(f"[BatchRenameVideoByMD5Node] 跳过（同一文件）: {original_filename}")
                        continue
                    
                    # 检查目标文件是否已存在
                    if os.path.exists(new_path):
                        if not overwrite_existing:
                            # 如果文件内容相同，跳过
                            existing_md5 = self.calculate_md5(new_path)
                            if existing_md5 == md5_hash:
                                skip_count += 1
                                print(f"[BatchRenameVideoByMD5Node] 跳过（文件已存在且内容相同）: {original_filename}")
                                continue
                            else:
                                skip_count += 1
                                print(f"[BatchRenameVideoByMD5Node] 跳过（文件已存在但内容不同）: {original_filename}")
                                continue
                    
                    # 复制文件到输出文件夹
                    shutil.copy2(video_path, new_path)
                    success_count += 1
                    renamed_count += 1
                    print(f"[BatchRenameVideoByMD5Node] 已重命名: {original_filename} -> {new_filename}")
                    
                    # 如果需要删除原始文件，且输出文件夹与输入文件夹相同，则删除原始文件
                    if delete_original_files and video_folder == output_folder:
                        try:
                            os.remove(video_path)
                            print(f"[BatchRenameVideoByMD5Node] 已删除原始文件: {original_filename}")
                        except Exception as e:
                            print(f"[BatchRenameVideoByMD5Node] 删除原始文件 {original_filename} 时出错: {str(e)}")
                    
                except Exception as e:
                    fail_count += 1
                    print(f"[BatchRenameVideoByMD5Node] 重命名失败: {str(e)}")
            
            # 生成信息
            info = f"批量重命名完成:\n" \
                   f"成功: {success_count} 个\n" \
                   f"失败: {fail_count} 个\n" \
                   f"跳过: {skip_count} 个\n" \
                   f"重命名: {renamed_count} 个\n" \
                   f"输出文件夹: {output_folder}"
            
            return (info,)
            
        except Exception as e:
            error_msg = f"批量重命名过程中发生错误: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return (error_msg,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "BatchRenameVideoByMD5Node": BatchRenameVideoByMD5Node,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchRenameVideoByMD5Node": "批量重命名视频(MD5)",
}
