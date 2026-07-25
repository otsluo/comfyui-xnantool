# 实用工具节点模块初始化文件
# 自动合并所有子模块的节点映射

import os
import importlib

# 获取当前目录路径
current_dir = os.path.dirname(__file__)

# 初始化合并字典
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# 遍历当前目录下所有Python文件（排除__init__.py）
for filename in os.listdir(current_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = filename[:-3]  # 移除.py后缀
        
        try:
            # 动态导入模块
            module = importlib.import_module(f'.{module_name}', package=__name__)
            
            # 合并节点映射
            if hasattr(module, 'NODE_CLASS_MAPPINGS'):
                NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
            
            if hasattr(module, 'NODE_DISPLAY_NAME_MAPPINGS'):
                NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
        except Exception as e:
            print(f'警告: 加载模块 {module_name} 失败 - {e}')

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
