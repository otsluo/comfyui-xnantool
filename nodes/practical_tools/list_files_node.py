import os

class ListFilesNode:
    """
    列出文件节点 - 读取输入文件夹并输出该文件夹下的所有文件名称列表
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
                    "description": "多个文件名称之间的分隔符"
                }),
                "file_extensions": ("STRING", {
                    "default": "",
                    "label": "文件扩展名过滤",
                    "description": "要过滤的文件扩展名（多个用逗号分隔，留空则列出所有文件）"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("file_list", "count",)
    FUNCTION = "list_files"
    CATEGORY = "XnanTool/实用工具"

    def list_files(self, input_directory, recursive, separator, file_extensions):
        """
        列出文件夹中的所有文件
        
        Args:
            input_directory: 输入文件夹路径
            recursive: 是否递归搜索
            separator: 文件名称分隔符
            file_extensions: 文件扩展名过滤（逗号分隔）
            
        Returns:
            tuple: (文件列表字符串, 文件数量)
        """
        file_names = []
        
        try:
            # 检查输入目录是否存在
            if not os.path.exists(input_directory):
                error_msg = f"输入文件夹不存在: {input_directory}"
                return (error_msg, "0")
            
            # 检查输入路径是否为目录
            if not os.path.isdir(input_directory):
                error_msg = f"输入路径不是文件夹: {input_directory}"
                return (error_msg, "0")
            
            # 解析文件扩展名过滤器
            extensions_filter = []
            if file_extensions and file_extensions.strip():
                extensions_filter = [ext.strip().lower() for ext in file_extensions.split(',')]
            
            # 获取文件列表
            if recursive == "true":
                # 递归搜索所有子文件夹
                for root, dirs, files in os.walk(input_directory):
                    for filename in files:
                        # 检查扩展名过滤
                        if extensions_filter:
                            _, ext = os.path.splitext(filename.lower())
                            if ext.lstrip('.') not in extensions_filter:
                                continue
                        
                        # 计算相对路径
                        relative_path = os.path.relpath(os.path.join(root, filename), input_directory)
                        file_names.append(relative_path)
            else:
                # 只搜索当前目录
                for item in os.listdir(input_directory):
                    item_path = os.path.join(input_directory, item)
                    if os.path.isfile(item_path):
                        # 检查扩展名过滤
                        if extensions_filter:
                            _, ext = os.path.splitext(item.lower())
                            if ext.lstrip('.') not in extensions_filter:
                                continue
                        
                        file_names.append(item)
            
            # 构造文件列表字符串
            if file_names:
                # 将字面的 \n 转换为实际的换行符
                actual_separator = separator.replace("\\n", "\n").replace("\\t", "\t")
                file_list_str = actual_separator.join(file_names)
            else:
                file_list_str = ""
            
            # 获取文件数量
            file_count = str(len(file_names))
            
            return (file_list_str, file_count)
            
        except PermissionError as pe:
            error_msg = f"权限不足，无法访问文件夹: {str(pe)}"
            return (error_msg, "0")
        except Exception as e:
            error_msg = f"列出文件时发生错误: {str(e)}"
            return (error_msg, "0")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "ListFilesNode": ListFilesNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ListFilesNode": "列出文件"
}
