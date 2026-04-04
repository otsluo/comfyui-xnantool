class CounterNode:
    """
    计数器节点
    每次点击运行时数值加一
    """
    
    # 类变量，用于保存计数器状态
    _counters = {}
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "counter_id": ("STRING", {
                    "default": "default",
                    "multiline": False,
                    "placeholder": "计数器ID（不同ID独立计数）",
                    "label": "计数器ID",
                    "description": "计数器的唯一标识符，不同ID独立计数"
                }),
                "start_value": ("INT", {
                    "default": 0,
                    "min": -999999,
                    "max": 999999,
                    "step": 1,
                    "label": "起始值",
                    "description": "计数器的起始值"
                }),
                "increment": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "label": "增量",
                    "description": "每次增加的数值"
                }),
                "reset": (["否", "是"], {
                    "default": "否",
                    "label": "重置",
                    "description": "是：重置计数器为起始值；否：正常计数"
                }),
                "max_value": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10000,
                    "step": 1,
                    "label": "上限值",
                    "description": "上限值（0表示不限制）"
                }),
                "restart_on_max": (["否", "是"], {
                    "default": "否",
                    "label": "超过上限重新计数",
                    "description": "是：达到上限后重新从起始值开始计数；否：达到上限后停止计数"
                }),
                "abort_on_max": (["否", "是"], {
                    "default": "否",
                    "label": "超过上限中止运行",
                    "description": "是：达到上限后中止运行；否：按其他选项处理"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "step": 1,
                    "label": "随机种子",
                    "description": "随机种子（0表示使用系统时间）"
                }),
            },
            "optional": {
                "trigger": ("*", {
                    "label": "触发器",
                    "description": "输入任意值触发计数"
                }),
            },
        }
    
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("计数值", "信息")
    FUNCTION = "count"
    CATEGORY = "XnanTool/工具"
    
    def count(self, counter_id, reset, increment, max_value, restart_on_max, abort_on_max, seed, start_value, trigger=None):
        """
        计数器函数
        
        Args:
            counter_id: 计数器ID
            reset: 是否重置
            increment: 增量
            max_value: 上限值
            restart_on_max: 超过上限是否重新计数
            abort_on_max: 超过上限是否中止运行
            seed: 随机种子
            start_value: 起始值
            trigger: 触发器（任意输入都会触发）
            
        Returns:
            计数值: 当前计数器的值
            信息: 状态信息
        """
        # 如果需要重置
        if reset == "是":
            self._counters[counter_id] = start_value
            return (start_value, f"计数器 '{counter_id}' 已重置为 {start_value}")
        
        # 初始化计数器（如果不存在）
        if counter_id not in self._counters:
            self._counters[counter_id] = start_value
        
        # 检查是否达到上限
        if max_value > 0 and self._counters[counter_id] >= max_value:
            if abort_on_max == "是":
                print(f"\033[31m[CounterNode ERROR] 计数器 '{counter_id}' 已达到上限 {max_value}，运行已中止\033[0m")
                return (self._counters[counter_id], f"计数器 '{counter_id}' 已达到上限 {max_value}，运行已中止")
            elif restart_on_max == "是":
                print(f"\033[33m[CounterNode WARNING] 计数器 '{counter_id}' 已达到上限 {max_value}，重新开始计数\033[0m")
                self._counters[counter_id] = 0
                new_value = increment
                if max_value > 0 and new_value > max_value:
                    new_value = max_value
                self._counters[counter_id] = new_value
                return (new_value, f"计数器 '{counter_id}': {new_value}（重新开始）")
            else:
                print(f"\033[33m[CounterNode WARNING] 计数器 '{counter_id}' 已达到上限 {max_value}\033[0m")
                return (self._counters[counter_id], f"计数器 '{counter_id}' 已达到上限 {max_value}")
        
        # 增加计数
        new_value = self._counters[counter_id] + increment
        
        # 如果设置了上限，确保不超过上限
        if max_value > 0 and new_value > max_value:
            new_value = max_value
        
        self._counters[counter_id] = new_value
        current_count = new_value
        
        if max_value > 0 and current_count >= max_value:
            if abort_on_max == "是":
                print(f"\033[31m[CounterNode ERROR] 计数器 '{counter_id}': {current_count}（已达到上限 {max_value}，运行已中止）\033[0m")
                return (current_count, f"计数器 '{counter_id}': {current_count}（已达到上限 {max_value}，运行已中止）")
            elif restart_on_max == "是":
                print(f"\033[33m[CounterNode WARNING] 计数器 '{counter_id}': {current_count}（已达到上限 {max_value}，重新开始）\033[0m")
                self._counters[counter_id] = 0
                return (0, f"计数器 '{counter_id}': 0（重新开始）")
            else:
                print(f"\033[33m[CounterNode WARNING] 计数器 '{counter_id}': {current_count}（已达到上限 {max_value}）\033[0m")
                return (current_count, f"计数器 '{counter_id}': {current_count}（已达到上限 {max_value}）")
        
        return (current_count, f"计数器 '{counter_id}': {current_count}")
    
    @classmethod
    def reset_counter(cls, counter_id=None):
        """
        重置计数器（可用于外部调用）
        
        Args:
            counter_id: 计数器ID，如果为None则重置所有计数器
        """
        if counter_id is None:
            cls._counters.clear()
        elif counter_id in cls._counters:
            del cls._counters[counter_id]


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "CounterNode": CounterNode
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "CounterNode": "计数器"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
