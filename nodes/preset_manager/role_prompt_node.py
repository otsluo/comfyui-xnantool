"""
角色提示词节点
功能：扫描 role 文件夹中的角色提示词文件，提供下拉选择
"""

import os
from pathlib import Path

# 角色文件夹路径
ROLE_DIR = Path(__file__).parent / "role"


def load_role_files():
    """
    递归加载 role 文件夹中的所有文件（包括子目录）
    
    返回：
        list: 文件标识列表（相对路径，不含扩展名）
    """
    if not ROLE_DIR.exists():
        ROLE_DIR.mkdir(parents=True, exist_ok=True)
        return []
    
    files = []
    for file_path in ROLE_DIR.rglob('*'):
        if file_path.is_file() and not file_path.name.startswith('.'):
            # 获取相对于 role 目录的路径（不含扩展名）
            rel_path = file_path.relative_to(ROLE_DIR)
            # 去掉扩展名，用 / 分隔子目录
            key = str(rel_path.with_suffix('')).replace(os.sep, '/')
            files.append(key)
    
    return sorted(files)


def read_role_file(filename):
    """
    读取指定的角色文件内容（支持子目录路径）
    
    参数：
        filename: 文件标识（相对路径，不含扩展名，如 "子目录/文件名"）
    
    返回：
        str: 文件内容，如果文件不存在返回空字符串
    """
    # 尝试查找文件（支持多种扩展名）
    for ext in ['.txt', '.md', '.json']:
        file_path = ROLE_DIR / f"{filename}{ext}"
        if file_path.exists():
            return file_path.read_text(encoding='utf-8')
    
    return ""


class RolePromptNode:
    """
    角色提示词节点
    从 role 文件夹中加载角色提示词，提供下拉选择
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        """
        定义节点输入类型
        """
        role_files = load_role_files()
        
        return {
            "required": {
                "role": (role_files if role_files else [""], {
                    "default": role_files[0] if role_files else "",
                    "label": "角色"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("提示词",)
    FUNCTION = "load_role"
    CATEGORY = "❤️❤️❤️XnanTool/预设"
    
    def load_role(self, role):
        """
        加载选中的角色提示词
        
        参数：
            role: 角色名称
        
        返回：
            tuple: (提示词内容,)
        """
        if not role:
            return ("",)
        
        content = read_role_file(role)
        return (content,)


# 节点注册
NODE_CLASS_MAPPINGS = {
    "RolePromptNode": RolePromptNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RolePromptNode": "role"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
