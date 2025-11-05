import sys
import os

# 获取插件根目录
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class VersionInfoNode:
    """
    版本信息查看节点
    用于显示当前插件的版本信息
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dummy_input": ("STRING", {"default": "version_check", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("version_info",)
    FUNCTION = "get_version_info"
    CATEGORY = "XnanTool/实用工具"
    OUTPUT_NODE = True

    def get_version_info(self, dummy_input):
        """
        获取并返回插件版本信息
        """
        # 从 __init__.py 文件中读取版本信息
        version_file_path = os.path.join(PLUGIN_ROOT, "__init__.py")
        
        version = "Unknown"
        if os.path.exists(version_file_path):
            with open(version_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("__version__"):
                        # 提取版本号，例如：__version__ = "0.4.0"
                        version = line.split("=")[1].strip().strip('"').strip("'")
                        break
        
        version_info = f"XnanTool 插件版本: {version}"
        return (version_info,)


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "VersionInfoNode": VersionInfoNode
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "VersionInfoNode": "应用查看版本"
}