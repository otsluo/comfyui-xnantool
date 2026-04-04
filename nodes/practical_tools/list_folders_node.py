import os

class ListFoldersNode:
    """
    列出文件夹节点 - 读取输入文件夹并输出该文件夹下的所有文件夹名称列表
    支持过滤选项和递归搜索
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_directory": ("STRING", {
                    "default": "",
                    "label": "输入文件夹路径",
                    "description": "要读取的文件夹路径"
                }),
                "recursive": (["false", "true"], {
                    "default": "false",
                    "label": "递归搜索",
                    "description": "是否递归搜索子文件夹"
                }),
                "separator": ("STRING", {
                    "default": "\n",
                    "label": "分隔符",
                    "description": "多个文件夹名称之间的分隔符"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("folder_list", "count",)
    FUNCTION = "list_folders"
    CATEGORY = "XnanTool/实用工具"

    def list_folders(self, input_directory, recursive, separator):
        """
        列出文件夹中的所有文件夹
        
        Args:
            input_directory: 输入文件夹路径
            recursive: 是否递归搜索
            separator: 文件夹名称分隔符
            
        Returns:
            tuple: (文件夹列表字符串, 文件夹数量)
        """
        folder_names = []
        
        try:
            # 检查输入目录是否存在
            if not os.path.exists(input_directory):
                error_msg = f"输入文件夹不存在: {input_directory}"
                return (error_msg, "0")
            
            # 检查输入路径是否为目录
            if not os.path.isdir(input_directory):
                error_msg = f"输入路径不是文件夹: {input_directory}"
                return (error_msg, "0")
            
            # 获取文件夹列表
            if recursive == "true":
                # 递归搜索所有子文件夹
                for root, dirs, files in os.walk(input_directory):
                    for dir_name in dirs:
                        # 计算相对路径
                        relative_path = os.path.relpath(os.path.join(root, dir_name), input_directory)
                        folder_names.append(relative_path)
            else:
                # 只搜索当前目录
                for item in os.listdir(input_directory):
                    item_path = os.path.join(input_directory, item)
                    if os.path.isdir(item_path):
                        folder_names.append(item)
            
            # 构造文件夹列表字符串
            if folder_names:
                # 将字面的 \n 转换为实际的换行符
                actual_separator = separator.replace("\\n", "\n").replace("\\t", "\t")
                folder_list_str = actual_separator.join(folder_names)
            else:
                folder_list_str = ""
            
            # 获取文件夹数量
            folder_count = str(len(folder_names))
            
            return (folder_list_str, folder_count)
            
        except PermissionError as pe:
            error_msg = f"权限不足，无法访问文件夹: {str(pe)}"
            return (error_msg, "0")
        except Exception as e:
            error_msg = f"列出文件夹时发生错误: {str(e)}"
            return (error_msg, "0")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "ListFoldersNode": ListFoldersNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ListFoldersNode": "列出文件夹"
}
