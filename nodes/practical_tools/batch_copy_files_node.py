import os
import shutil
import logging
from pathlib import Path

class BatchCopyFilesNode:
    """
    批量复制文件节点 - 支持将指定目录中的文件批量复制到目标目录
    支持文件过滤、覆盖选项和进度反馈
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source_directory": ("STRING", {
                    "default": "",
                    "label": "源目录路径",
                    "description": "要复制文件的源目录路径"
                }),
                "destination_directory": ("STRING", {
                    "default": "",
                    "label": "目标目录路径",
                    "description": "文件复制到的目标目录路径"
                }),
                "file_extensions": ("STRING", {
                    "default": "*",
                    "label": "文件扩展名过滤",
                    "description": "要复制的文件扩展名，用逗号分隔（如：.jpg,.png,.txt），*表示所有文件"
                }),
                "overwrite_existing": (["true", "false"], {
                    "default": "false",
                    "label": "覆盖已有文件",
                    "description": "是否覆盖目标目录中已存在的同名文件"
                }),
                "preserve_structure": (["true", "false"], {
                    "default": "true",
                    "label": "保留目录结构",
                    "description": "是否保留源目录的子目录结构"
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result_info",)
    FUNCTION = "copy_files"
    CATEGORY = "XnanTool/实用工具"

    def copy_files(self, source_directory, destination_directory, file_extensions, overwrite_existing, preserve_structure):
        """
        批量复制文件
        
        Args:
            source_directory: 源目录路径
            destination_directory: 目标目录路径
            file_extensions: 文件扩展名过滤器
            overwrite_existing: 是否覆盖已有文件
            preserve_structure: 是否保留目录结构
            
        Returns:
            tuple: (处理结果信息,)
        """
        # 初始化统计变量
        copied_count = 0
        skipped_count = 0
        error_messages = []
        
        try:
            # 检查源目录是否存在
            if not os.path.exists(source_directory):
                error_msg = f"源目录不存在: {source_directory}"
                return (error_msg, copied_count, skipped_count, error_msg)
            
            # 检查源目录是否为目录
            if not os.path.isdir(source_directory):
                error_msg = f"源路径不是目录: {source_directory}"
                return (error_msg, copied_count, skipped_count, error_msg)
            
            # 创建目标目录（如果不存在）
            os.makedirs(destination_directory, exist_ok=True)
            
            # 解析文件扩展名过滤器
            if file_extensions.strip() == "*" or file_extensions.strip() == "":
                extensions = None  # 不过滤文件类型
            else:
                extensions = [ext.strip().lower() for ext in file_extensions.split(",") if ext.strip()]
            
            # 获取源目录中的所有文件
            source_path = Path(source_directory)
            files_to_copy = []
            
            # 遍历源目录中的所有文件
            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    # 如果指定了文件扩展名过滤器，则检查文件扩展名
                    if extensions is not None:
                        if file_path.suffix.lower() in extensions:
                            files_to_copy.append(file_path)
                    else:
                        files_to_copy.append(file_path)
            
            # 复制文件
            total_files = len(files_to_copy)
            for idx, file_path in enumerate(files_to_copy, 1):
                try:
                    # 计算目标文件路径
                    if preserve_structure == "true":
                        # 保留目录结构
                        relative_path = file_path.relative_to(source_path)
                        dest_file_path = Path(destination_directory) / relative_path
                    else:
                        # 不保留目录结构，所有文件放到同一目录
                        dest_file_path = Path(destination_directory) / file_path.name
                    
                    # 创建目标文件的目录（如果不存在）
                    dest_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 检查目标文件是否已存在
                    if dest_file_path.exists() and overwrite_existing == "false":
                        skipped_count += 1
                        continue
                    
                    # 复制文件
                    shutil.copy2(file_path, dest_file_path)
                    copied_count += 1
                    
                    # 进度日志
                    if idx % 10 == 0 or idx == total_files:
                        logging.info(f"批量复制进度: {idx}/{total_files} ({idx/total_files*100:.1f}%)")
                    
                except PermissionError as pe:
                    error_msg = f"权限不足，无法复制文件 {file_path}: {str(pe)}"
                    error_messages.append(error_msg)
                except FileNotFoundError as fe:
                    error_msg = f"文件未找到 {file_path}: {str(fe)}"
                    error_messages.append(error_msg)
                except Exception as e:
                    error_msg = f"复制文件失败 {file_path}: {str(e)}"
                    error_messages.append(error_msg)
            
            # 构造结构化的结果信息
            result_lines = []
            result_lines.append(f"批量复制完成: 成功复制 {copied_count} 个文件, 跳过 {skipped_count} 个文件")
            
            if error_messages:
                error_info = "\n".join(error_messages[:10])  # 只返回前10个错误信息，避免过长
                if len(error_messages) > 10:
                    error_info += f"\n...还有 {len(error_messages) - 10} 个错误"
                result_lines.append(f"错误信息:\n{error_info}")
                
            result_info = "\n".join(result_lines)
                
            return (result_info,)
            
        except PermissionError as pe:
            error_msg = f"权限不足，无法访问目录: {str(pe)}"
            return (error_msg, copied_count, skipped_count, error_msg)
        except Exception as e:
            error_msg = f"批量复制过程中发生错误: {str(e)}"
            return (error_msg, copied_count, skipped_count, error_msg)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "BatchCopyFilesNode": BatchCopyFilesNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchCopyFilesNode": "批量复制文件"
}