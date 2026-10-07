import os


class LoadTextFileNode:
    """
    加载文本文件节点 - 从指定路径加载文本文件内容

    编码格式说明：
    - utf-8: 通用编码（默认）
    - gbk: 中文Windows
    - gb2312: 简体中文
    - gb18030: 中文国家标准
    - big5: 繁体中文
    - latin-1: 西欧语言
    - ascii: 英文
    - utf-16: Unicode
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "文件路径",
                    "description": "要加载的文本文件的完整路径"
                }),
            },
            "optional": {
                "encoding": (["utf-8", "gbk", "gb2312", "gb18030", "big5", "latin-1", "ascii", "utf-16"], {
                    "default": "utf-8",
                    "label": "编码格式",
                    "description": "文件编码格式"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("文本内容",)
    FUNCTION = "load_text_file"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def load_text_file(self, file_path, encoding="utf-8"):
        """
        加载文本文件内容

        Args:
            file_path: 文件路径
            encoding: 文件编码格式

        Returns:
            tuple: (文本内容,)
        """
        # 检查文件路径是否为空
        if not file_path or not file_path.strip():
            error_msg = "错误：文件路径不能为空"
            print(f"📄 {error_msg}")
            return (error_msg,)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            error_msg = f"错误：文件不存在 - {file_path}"
            print(f"📄 {error_msg}")
            return (error_msg,)

        # 检查是否为文件
        if not os.path.isfile(file_path):
            error_msg = f"错误：路径不是文件 - {file_path}"
            print(f"📄 {error_msg}")
            return (error_msg,)

        try:
            # 读取文件内容
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            # 输出文件信息
            file_size = os.path.getsize(file_path)
            line_count = content.count('\n') + 1
            print(f"📄 已加载文本文件: {os.path.basename(file_path)}")
            print(f"📄 文件大小: {file_size} 字节")
            print(f"📄 行数: {line_count}")

            return (content,)

        except UnicodeDecodeError as e:
            error_msg = f"错误：文件编码错误 - {str(e)}\n请尝试其他编码格式（如 gbk, gb2312）"
            print(f"📄 {error_msg}")
            return (error_msg,)
        except Exception as e:
            error_msg = f"错误：读取文件失败 - {str(e)}"
            print(f"📄 {error_msg}")
            return (error_msg,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "LoadTextFileNode": LoadTextFileNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadTextFileNode": "加载文本文件"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
