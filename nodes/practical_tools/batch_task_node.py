"""
批量任务节点
功能：读取 Excel/CSV 表格文件，解析批量任务

表格格式（列名自定义）：
| 提示词 | 图像1 | 图像2 | 图像3 |
|--------|-------|-------|-------|
| 第一段提示词 | img1.jpg | img2.jpg | |
| 第二段提示词 | img3.jpg | | |

节点参数：
- 提示词列名：填写"提示词"
- 图片列名：填写"图像1,图像2,图像3"（用逗号分隔）
"""

import os
import json
from pathlib import Path


class BatchTaskNode:
    """批量任务节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config_file": ("STRING", {
                    "default": "",
                    "label": "表格文件路径",
                    "description": "Excel(.xlsx/.xls)或CSV文件路径"
                }),
                "column1": ("STRING", {
                    "default": "提示词",
                    "label": "列1",
                    "description": "第1列的列名"
                }),
                "column2": ("STRING", {
                    "default": "",
                    "label": "列2",
                    "description": "第2列的列名"
                }),
                "column3": ("STRING", {
                    "default": "",
                    "label": "列3",
                    "description": "第3列的列名"
                }),
                "column4": ("STRING", {
                    "default": "",
                    "label": "列4",
                    "description": "第4列的列名"
                }),
                "column5": ("STRING", {
                    "default": "",
                    "label": "列5",
                    "description": "第5列的列名"
                }),
                "column6": ("STRING", {
                    "default": "",
                    "label": "列6",
                    "description": "第6列的列名"
                }),
                "column7": ("STRING", {
                    "default": "",
                    "label": "列7",
                    "description": "第7列的列名"
                }),
                "column8": ("STRING", {
                    "default": "",
                    "label": "列8",
                    "description": "第8列的列名"
                }),
                "column9": ("STRING", {
                    "default": "",
                    "label": "列9",
                    "description": "第9列的列名"
                }),
                "column10": ("STRING", {
                    "default": "",
                    "label": "列10",
                    "description": "第10列的列名"
                }),
                "column11": ("STRING", {
                    "default": "",
                    "label": "列11",
                    "description": "第11列的列名"
                }),
                "column12": ("STRING", {
                    "default": "",
                    "label": "列12",
                    "description": "第12列的列名"
                }),
                "column13": ("STRING", {
                    "default": "",
                    "label": "列13",
                    "description": "第13列的列名"
                }),
                "column14": ("STRING", {
                    "default": "",
                    "label": "列14",
                    "description": "第14列的列名"
                }),
                "column15": ("STRING", {
                    "default": "",
                    "label": "列15",
                    "description": "第15列的列名"
                }),
                "row_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999,
                    "step": 1,
                    "label": "行号",
                    "description": "要读取的行号（0表示全部，1开始为具体行号，不含表头）"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("任务JSON",)
    FUNCTION = "load_tasks"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    
    def load_tasks(self, config_file, column1, column2, column3, column4, column5, column6, column7, column8, column9, column10, column11, column12, column13, column14, column15, row_index):
        """加载表格格式的任务配置"""
        if not config_file or not config_file.strip():
            return ("[]",)
        
        config_path = Path(config_file.strip())
        
        if not config_path.exists():
            return ("[]",)
        
        # 收集所有列名（过滤空值）
        all_columns = [column1, column2, column3, column4, column5, column6, column7, column8, column9, column10, column11, column12, column13, column14, column15]
        column_list = [col.strip() for col in all_columns if col and col.strip()]
        
        if not column_list:
            return ("[]",)
        
        try:
            ext = config_path.suffix.lower()
            
            if ext in ['.xlsx', '.xls']:
                tasks = self._load_excel(config_path, column_list, row_index)
            elif ext == '.csv':
                tasks = self._load_csv(config_path, column_list, row_index)
            else:
                return ("[]",)
            
            result_json = json.dumps(tasks, ensure_ascii=False, indent=2)
            return (result_json,)
            
        except ImportError as e:
            return ("[]",)
        except Exception as e:
            return ("[]",)
    
    def _load_excel(self, file_path, column_list, row_index):
        """加载 Excel 文件"""
        import openpyxl
        
        wb = openpyxl.load_workbook(file_path, read_only=True)
        ws = wb.active
        
        # 读取表头
        headers = []
        for cell in next(ws.iter_rows(min_row=1, max_row=1)):
            headers.append(str(cell.value).strip() if cell.value else "")
        
        # 查找所有指定列的索引
        column_indices = []
        for col_name in column_list:
            found = False
            for i, header in enumerate(headers):
                if header == col_name:
                    column_indices.append((col_name, i))
                    found = True
                    break
            if not found:
                wb.close()
                raise ValueError(f"找不到列：{col_name}，可用列：{headers}")
        
        # 读取数据行
        tasks = []
        current_row = 0
        for row in ws.iter_rows(min_row=2):
            current_row += 1
            
            # 如果指定了行号，只读取指定行
            if row_index > 0 and current_row != row_index:
                continue
            
            values = [str(cell.value).strip() if cell.value else "" for cell in row]
            
            # 检查第一列是否有值
            first_col_idx = column_indices[0][1]
            if len(values) <= first_col_idx or not values[first_col_idx]:
                continue
            
            # 用列名作为 key
            task = {}
            for col_name, col_idx in column_indices:
                if col_idx < len(values):
                    task[col_name] = values[col_idx]
                else:
                    task[col_name] = ""
            
            tasks.append(task)
            
            # 如果指定了行号，读取到后退出
            if row_index > 0:
                break
        
        wb.close()
        return tasks
    
    def _load_csv(self, file_path, column_list, row_index):
        """加载 CSV 文件"""
        import csv
        
        tasks = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # 检查所有列是否存在
            for col_name in column_list:
                if col_name not in reader.fieldnames:
                    raise ValueError(f"找不到列：{col_name}，可用列：{reader.fieldnames}")
            
            current_row = 0
            for row in reader:
                current_row += 1
                
                # 如果指定了行号，只读取指定行
                if row_index > 0 and current_row != row_index:
                    continue
                
                # 检查第一列是否有值
                first_col = column_list[0]
                first_value = row.get(first_col, '').strip()
                if not first_value:
                    continue
                
                # 用列名作为 key
                task = {}
                for col_name in column_list:
                    task[col_name] = row.get(col_name, '').strip()
                
                tasks.append(task)
                
                # 如果指定了行号，读取到后退出
                if row_index > 0:
                    break
        
        return tasks


# 节点注册
NODE_CLASS_MAPPINGS = {
    "BatchTaskNode": BatchTaskNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchTaskNode": "批量任务-BETA",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
