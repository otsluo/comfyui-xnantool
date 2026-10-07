import time
import datetime

class GetCurrentTimeNode:
    """
    获取当前时间节点 - 获取当前时间戳，输出字符串和整数格式
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "format_type": (["时间戳", "日期时间", "日期", "年月", "月日", "年", "月", "日", "时间"], {"default": "时间戳"}),
            },
            "optional": {
                "input_value": ("*", {}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("time_string",)
    FUNCTION = "get_current_time"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def get_current_time(self, format_type, input_value=None):
        """
        获取当前时间，返回字符串格式
        """
        current_time = time.time()
        timestamp_int = int(current_time)

        if format_type == "时间戳":
            time_string = str(timestamp_int)
        elif format_type == "日期时间":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == "日期":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d')
        elif format_type == "年月":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m')
        elif format_type == "月日":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%m-%d')
        elif format_type == "年":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%Y')
        elif format_type == "月":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%m')
        elif format_type == "日":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%d')
        elif format_type == "时间":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%H:%M:%S')
        else:
            time_string = str(timestamp_int)

        return (time_string,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "GetCurrentTimeNode": GetCurrentTimeNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetCurrentTimeNode": "获取时间"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']