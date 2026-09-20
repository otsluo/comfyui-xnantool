"""
批量任务解析节点
功能：解析批量任务节点输出的JSON，自动提取单条任务的所有字段值
"""

import json


class BatchTaskParserNode:
    """批量任务解析节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "task_json": ("STRING", {
                    "default": "[]",
                    "label": "任务JSON",
                    "description": "批量任务节点输出的任务JSON"
                }),
            },
        }
    
    # 最多支持15个输出端口
    MAX_OUTPUTS = 15
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("值1", "值2", "值3", "值4", "值5", "值6", "值7", "值8", "值9", "值10", "值11", "值12", "值13", "值14", "值15")
    FUNCTION = "parse_task"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    
    def parse_task(self, task_json):
        """解析单条任务，自动提取所有字段值"""
        empty_result = ("", "", "", "", "", "", "", "", "", "", "", "", "", "", "")
        
        try:
            tasks = json.loads(task_json)
        except json.JSONDecodeError:
            return empty_result
        
        if not isinstance(tasks, list) or len(tasks) == 0:
            return empty_result
        
        # 取第一条任务
        task = tasks[0]
        
        # 自动提取所有字段（按JSON中的顺序）
        values = []
        for key in task.keys():
            values.append(str(task[key]) if task[key] is not None else "")
        
        # 填充到 MAX_OUTPUTS 个
        while len(values) < self.MAX_OUTPUTS:
            values.append("")
        
        return (values[0], values[1], values[2], values[3], values[4],
                values[5], values[6], values[7], values[8], values[9],
                values[10], values[11], values[12], values[13], values[14])


# 节点注册
NODE_CLASS_MAPPINGS = {
    "BatchTaskParserNode": BatchTaskParserNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchTaskParserNode": "批量任务解析-BETA",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
