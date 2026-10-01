import os
from pathlib import Path


class GetFileListNode:
    """
    获取文件名列表节点 - 获取指定目录下的文件名列表
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "目录路径",
                    "description": "要获取文件列表的目录路径"
                }),
            },
            "optional": {
                "file_extension": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "文件扩展名",
                    "description": "文件扩展名过滤（如 .png, .jpg，留空表示所有文件）"
                }),
                "recursive": ("BOOLEAN", {
                    "default": False,
                    "label": "递归子文件夹",
                    "description": "是否递归获取子文件夹中的文件"
                }),
            }
        }

    RETURN_TYPES = ("LIST", "STRING")
    RETURN_NAMES = ("文件列表", "文件信息")
    FUNCTION = "get_file_list"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def get_file_list(self, directory_path: str, file_extension: str = "", recursive: bool = False):
        """
        获取目录下的文件名列表

        Args:
            directory_path: 目录路径
            file_extension: 文件扩展名过滤（如 .png）
            recursive: 是否递归子文件夹

        Returns:
            tuple: (文件列表, 文件信息字符串)
        """
        # 检查目录是否存在
        if not directory_path or not os.path.exists(directory_path):
            error_msg = f"错误：目录不存在 - {directory_path}"
            print(f"📁 {error_msg}")
            return ([], error_msg)

        if not os.path.isdir(directory_path):
            error_msg = f"错误：路径不是目录 - {directory_path}"
            print(f"📁 {error_msg}")
            return ([], error_msg)

        # 处理扩展名
        if file_extension:
            # 确保扩展名以点开头
            if not file_extension.startswith('.'):
                file_extension = '.' + file_extension
            file_extension = file_extension.lower()

        # 收集文件
        file_list = []
        total_count = 0

        try:
            if recursive:
                # 递归遍历所有子文件夹
                for root, dirs, files in os.walk(directory_path):
                    for filename in files:
                        # 扩展名过滤
                        if file_extension:
                            if not filename.lower().endswith(file_extension):
                                continue

                        # 获取相对路径
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, directory_path)
                        file_list.append(rel_path)
                        total_count += 1
            else:
                # 只遍历当前目录
                for item in os.listdir(directory_path):
                    item_path = os.path.join(directory_path, item)

                    # 只处理文件
                    if not os.path.isfile(item_path):
                        continue

                    # 扩展名过滤
                    if file_extension:
                        if not item.lower().endswith(file_extension):
                            continue

                    file_list.append(item)
                    total_count += 1

            # 按文件名排序
            file_list.sort()

            # 生成文件信息
            ext_desc = file_extension if file_extension else "所有文件"
            recursive_desc = "（包含子文件夹）" if recursive else ""
            info_msg = f"📁 找到 {total_count} 个文件{recursive_desc}\n"
            info_msg += f"📂 目录：{directory_path}\n"
            info_msg += f"🔍 过滤：{ext_desc}\n"

            if total_count > 0:
                info_msg += f"\n文件列表："
                # 最多显示前10个文件
                show_count = min(10, len(file_list))
                for i in range(show_count):
                    info_msg += f"\n  {i + 1}. {file_list[i]}"
                if len(file_list) > show_count:
                    info_msg += f"\n  ... 还有 {len(file_list) - show_count} 个文件"

            print(f"📁 {info_msg}")
            return (file_list, info_msg)

        except Exception as e:
            error_msg = f"错误：获取文件列表失败 - {str(e)}"
            print(f"📁 {error_msg}")
            return ([], error_msg)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "GetFileListNode": GetFileListNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetFileListNode": "获取文件名列表"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
