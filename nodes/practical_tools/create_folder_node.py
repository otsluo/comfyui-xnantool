import os

class CreateFolderNode:
    """
    创建文件夹节点 - 批量创建文件夹
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "基础路径",
                    "description": "文件夹创建的基础目录路径"
                }),
                "folder_names": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "文件夹路径",
                    "description": "要创建的文件夹路径列表，每行一个路径（支持多级目录）"
                }),
                "exist_ok": (["true", "false"], {
                    "default": "true",
                    "label": "已存在时",
                    "description": "如果目标文件夹已存在：\n  true = 忽略并继续\n  false = 报错停止"
                })
            },
            "optional": {
                "usage_notes": ("STRING", {
                    "default": "批量创建文件夹节点\n支持创建单级或多级目录结构\n适用于批量生成文件夹结构\n\n使用示例：\n基础路径: D:\\666\n文件夹路径:\n  111\n  222\n  111\\sub1\n  222\\sub2\\sub3\n\n结果：\n  D:\\666\\111\n  D:\\666\\222\n  D:\\666\\111\\sub1\n  D:\\666\\222\\sub2\\sub3",
                    "multiline": True
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("status", "info")
    FUNCTION = "create_folders"
    CATEGORY = "XnanTool/实用工具"
    
    def create_folders(self, base_path, folder_names, exist_ok, usage_notes=None):
        """
        批量创建文件夹
        
        Args:
            base_path: 文件夹创建的基础目录路径
            folder_names: 要创建的文件夹路径列表（每行一个，支持多级目录）
            exist_ok: 如果文件夹已存在是否忽略错误
            usage_notes: 使用说明（可选）
            
        Returns:
            tuple: (状态, 信息)
        """
        try:
            # 检查基础路径是否为空
            if not base_path or not base_path.strip():
                return ("error", "错误：基础路径不能为空")
            
            # 检查文件夹路径是否为空
            if not folder_names or not folder_names.strip():
                return ("error", "错误：文件夹路径不能为空")
            
            # 创建成功的文件夹数量
            success_count = 0
            # 已存在的文件夹数量
            exist_count = 0
            # 失败的文件夹数量
            error_count = 0
            # 错误信息列表
            error_messages = []
            
            # 处理基础路径，确保路径格式正确
            base_path = os.path.normpath(base_path)
            
            # 检查基础路径是否存在
            if not os.path.exists(base_path):
                try:
                    os.makedirs(base_path, exist_ok=True)
                except Exception as e:
                    return ("error", f"错误：无法创建基础路径: {str(e)}")
            
            # 分割文件夹路径
            folder_list = [path.strip() for path in folder_names.split('\n') if path.strip()]
            
            # 如果没有有效的文件夹路径
            if not folder_list:
                return ("error", "错误：没有有效的文件夹路径")
            
            # 遍历并创建每个文件夹
            for folder_path in folder_list:
                # 组合完整路径
                full_path = os.path.join(base_path, folder_path)
                
                try:
                    # 检查路径是否已存在
                    if os.path.exists(full_path):
                        if os.path.isdir(full_path):
                            if exist_ok == "true":
                                exist_count += 1
                                continue
                            else:
                                error_count += 1
                                error_messages.append(f"路径已存在: {folder_path}")
                                continue
                        else:
                            error_count += 1
                            error_messages.append(f"路径已存在但不是文件夹: {folder_path}")
                            continue
                    
                    # 创建文件夹（包括所有必要的父文件夹）
                    os.makedirs(full_path, exist_ok=True)
                    success_count += 1
                    
                except PermissionError as pe:
                    error_count += 1
                    error_messages.append(f"权限不足，无法创建路径 {folder_path}: {str(pe)}")
                except Exception as e:
                    error_count += 1
                    error_messages.append(f"创建路径 {folder_path} 时发生错误: {str(e)}")
            
            # 构建返回信息
            info_lines = [
                f"基础路径: {base_path}",
                f"成功创建: {success_count} 个",
                f"已存在: {exist_count} 个",
                f"失败: {error_count} 个"
            ]
            
            if error_messages:
                info_lines.append("")
                info_lines.append("错误详情:")
                for msg in error_messages:
                    info_lines.append(f"  - {msg}")
            
            info = "\n".join(info_lines)
            
            if error_count > 0:
                return ("partial", info)
            else:
                return ("success", info)
            
        except Exception as e:
            return ("error", f"创建文件夹时发生错误: {str(e)}")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "CreateFolderNode": CreateFolderNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CreateFolderNode": "创建文件夹",
}
