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
                "format_type": (["timestamp", "datetime", "date", "time"], {"default": "timestamp"}),
            },
            "optional": {
                "any": ("*", {}),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("time_string", "timestamp_int")
    FUNCTION = "get_current_time"
    CATEGORY = "XnanTool/实用工具"

    def get_current_time(self, format_type, any=None):
        """
        获取当前时间，返回字符串和整数格式
        """
        current_time = time.time()
        timestamp_int = int(current_time)
        
        if format_type == "timestamp":
            time_string = str(timestamp_int)
        elif format_type == "datetime":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == "date":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d')
        elif format_type == "time":
            time_string = datetime.datetime.fromtimestamp(current_time).strftime('%H:%M:%S')
        else:
            time_string = str(timestamp_int)
        
        return (time_string, timestamp_int)


NODE_CLASS_MAPPINGS = {
    "GetCurrentTimeNode": GetCurrentTimeNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GetCurrentTimeNode": "获取当前时间"
}