class CountTriggerNode:
    """
    计数触发节点 - 累积指定次数后才输出一次
    支持设置起始值、增量和上限
    输出值从起始值开始，每次触发后按增量增加
    """

    def __init__(self):
        self.count = None
        self.output_value = None
        self.last_params = None  # 保存上次的参数值，用于检测参数变化
        self.last_seed = None  # 保存上次的种子值，用于检测种子变化

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trigger_count": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 999999,
                    "step": 1,
                    "label": "触发计数",
                    "description": "累积多少次触发后输出一次（核心功能）"
                }),
                "start_value": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "label": "起始值",
                    "description": "第一次触发时输出的值"
                }),
                "increment": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 999999,
                    "step": 1,
                    "label": "增量",
                    "description": "每次触发后输出值增加的量"
                }),
                "max_value": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "label": "上限",
                    "description": "输出值的上限，达到后不再增加，0表示不限制"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999999,
                    "step": 1,
                    "label": "种子",
                    "description": "修改种子值会触发节点重新执行并计数"
                }),
            },
            "optional": {
                "trigger_signal": ("*", {
                    "label": "触发",
                    "description": "接收到输入时计数+1，用于外部触发"
                }),
            }
        }

    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("输出值", "当前计数", "状态")
    FUNCTION = "trigger"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    OUTPUT_NODE = True

    def trigger(self, trigger_count, start_value, increment, max_value, seed, trigger_signal=None):
        """
        计数触发

        Args:
            trigger_count: 触发计数阈值（核心）
            start_value: 起始值（第一次触发时输出）
            increment: 增量（每次触发后输出值增加的量）
            max_value: 上限值（0表示不限制）
            seed: 种子值（修改种子值会触发节点重新执行并计数）
            trigger_signal: 触发信号（外部输入，接收到信号时计数）
        """
        # 初始化计数器和输出值（首次执行）
        if self.count is None:
            self.count = 0
            self.output_value = start_value
            self.last_params = (start_value, increment, max_value, trigger_count)
            self.last_seed = seed

        # 检测参数变化，如果参数改变则重置
        current_params = (start_value, increment, max_value, trigger_count)
        if self.last_params != current_params:
            self.count = 0
            self.output_value = start_value
            self.last_params = current_params

        # 判断是否需要计数
        # 如果没有接入触发器，则每次执行都计数（种子变化用于触发节点重新执行）
        # 如果接入了触发器，则只在接收到触发信号时计数
        if trigger_signal is None:
            # 没有触发器，每次执行都计数
            self.count += 1
        elif trigger_signal is not None:
            # 有触发器，接收到信号时计数
            self.count += 1

        # 判断是否触发输出
        should_trigger = False
        trigger_reason = ""

        # 条件1：达到触发计数的倍数（每N次触发一次）
        if self.count > 0 and self.count % trigger_count == 0:
            should_trigger = True
            trigger_reason = f"第{self.count}次触发（每{trigger_count}次）"

        # 条件2：达到上限（如果设置了上限）
        if max_value > 0 and self.output_value >= max_value:
            should_trigger = True
            trigger_reason = f"输出值达到上限({max_value})"

        if should_trigger:
            # 达到触发计数，先输出当前值
            current_output = self.output_value
            status = f"触发！{trigger_reason}，输出值：{current_output}"

            # 然后更新值供下次使用
            self.output_value += increment

            # 如果设置了上限，确保输出值不超过上限
            if max_value > 0 and self.output_value > max_value:
                self.output_value = max_value

            return (current_output, self.count, status)
        else:
            # 未达到触发条件，输出当前值
            limit_info = f"，上限：{max_value}" if max_value > 0 else ""
            status = f"第{self.count}次，下次触发输出值：{self.output_value}{limit_info}"
            return (self.output_value, self.count, status)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "CountTriggerNode": CountTriggerNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "CountTriggerNode": "计数触发"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
