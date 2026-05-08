import os
import shutil
import logging
from pathlib import Path

class MoveFilesNode:
    """
    移动文件节点 - 将文件从源目录移动到目标目录
    支持文件过滤、覆盖选项和目录结构保留
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source_directory": ("STRING", {
                    "default": "",
                    "label": "源文件夹位置",
                    "description": "要移动文件的源目录路径"
                }),
                "destination_directory": ("STRING", {
                    "default": "",
                    "label": "目标文件夹位置",
                    "description": "文件移动到的目标目录路径"
                }),
            },
            "optional": {
                "file_extensions": ("STRING", {
                    "default": "*",
                    "label": "文件扩展名过滤",
                    "description": "要移动的文件扩展名，用逗号分隔（如：.jpg,.png,.txt），*表示所有文件"
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
    RETURN_NAMES = ("移动信息",)
    FUNCTION = "move_files"
    CATEGORY = "XnanTool/实用工具"
    DESCRIPTION = "将文件从源文件夹移动到目标文件夹，支持文件过滤和目录结构保留"

    def move_files(self, source_directory, destination_directory, file_extensions="*", overwrite_existing="false", preserve_structure="true"):
        """
        移动文件
        
        Args:
            source_directory: 源目录路径
            destination_directory: 目标目录路径
            file_extensions: 文件扩展名过滤器
            overwrite_existing: 是否覆盖已有文件
            preserve_structure: 是否保留目录结构
            
        Returns:
            tuple: (处理结果信息,)
        """
        moved_count = 0
        skipped_count = 0
        error_messages = []
        
        try:
            if not os.path.exists(source_directory):
                return (f"错误：源文件夹不存在: {source_directory}",)
            
            if not os.path.isdir(source_directory):
                return (f"错误：源路径不是文件夹: {source_directory}",)
            
            os.makedirs(destination_directory, exist_ok=True)
            
            if file_extensions.strip() == "*" or file_extensions.strip() == "":
                extensions = None
            else:
                extensions = [ext.strip().lower() for ext in file_extensions.split(",") if ext.strip()]
            
            source_path = Path(source_directory)
            files_to_move = []
            
            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    if extensions is not None:
                        if file_path.suffix.lower() in extensions:
                            files_to_move.append(file_path)
                    else:
                        files_to_move.append(file_path)
            
            total_files = len(files_to_move)
            for idx, file_path in enumerate(files_to_move, 1):
                try:
                    if preserve_structure == "true":
                        relative_path = file_path.relative_to(source_path)
                        dest_file_path = Path(destination_directory) / relative_path
                    else:
                        dest_file_path = Path(destination_directory) / file_path.name
                    
                    dest_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if dest_file_path.exists() and overwrite_existing == "false":
                        skipped_count += 1
                        continue
                    
                    shutil.move(str(file_path), str(dest_file_path))
                    moved_count += 1
                    
                    if idx % 10 == 0 or idx == total_files:
                        logging.info(f"移动文件进度: {idx}/{total_files} ({idx/total_files*100:.1f}%)")
                    
                except PermissionError as pe:
                    error_messages.append(f"权限不足，无法移动文件 {file_path}: {str(pe)}")
                except FileNotFoundError as fe:
                    error_messages.append(f"文件未找到 {file_path}: {str(fe)}")
                except Exception as e:
                    error_messages.append(f"移动文件失败 {file_path}: {str(e)}")
            
            result_lines = []
            result_lines.append(f"✅ 文件移动完成: 成功移动 {moved_count} 个文件, 跳过 {skipped_count} 个文件")
            result_lines.append(f"📂 源文件夹: {source_directory}")
            result_lines.append(f"📂 目标文件夹: {destination_directory}")
            
            if error_messages:
                error_info = "\n".join(error_messages[:10])
                if len(error_messages) > 10:
                    error_info += f"\n...还有 {len(error_messages) - 10} 个错误"
                result_lines.append(f"❌ 错误信息:\n{error_info}")
                
            return ("\n".join(result_lines),)
            
        except PermissionError as pe:
            return (f"❌ 权限不足，无法访问目录: {str(pe)}",)
        except Exception as e:
            return (f"❌ 移动文件过程中发生错误: {str(e)}",)


NODE_CLASS_MAPPINGS = {
    "MoveFilesNode": MoveFilesNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MoveFilesNode": "移动文件"
}
