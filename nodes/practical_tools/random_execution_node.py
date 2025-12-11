import random
import torch

class RandomExecutionNode:
    """
    随机执行节点 - 支持随机、固定、顺序循环等多种执行模式的节点
    根据实际连接的端口数量执行相应数量的操作
    支持多种数据类型输入（FLOAT, INT, STRING等）
    在顺序循环模式下，会依次执行所有输入，执行到底后重新从头开始执行
    """
    
    def __init__(self):
        # 用于跟踪顺序执行模式的当前位置
        self.sequential_position = 0
        # 用于跟踪上一次执行的seed，防止重复执行时位置不更新
        self.last_seed = None
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["random", "fixed", "sequential"], {
                    "default": "random",
                    "label": "执行模式",
                    "description": "选择执行模式：random(随机), fixed(固定), sequential(顺序循环)"
                }),
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "label": "随机种子",
                    "description": "用于随机模式的种子值"
                }),
                "position": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 1000,
                    "label": "位置编号",
                    "description": "用于fixed模式的位置编号"
                }),
            },
            "optional": {
                "input_1": ("*", {"label": "输入1"}),
                "input_2": ("*", {"label": "输入2"}),
                "input_3": ("*", {"label": "输入3"}),
                "input_4": ("*", {"label": "输入4"}),
                "input_5": ("*", {"label": "输入5"}),
            }
        }

    RETURN_TYPES = ("*", "STRING", "INT", "FLOAT", "INT")
    RETURN_NAMES = ("原始类型输出", "字符串输出", "整数输出", "浮点输出", "选中索引")
    FUNCTION = "execute"
    CATEGORY = "XnanTool/实用工具"

    def execute(self, mode, seed, position, input_1=None, input_2=None, input_3=None, input_4=None, input_5=None):
        """
        根据指定模式在提供的输入值中选择一个输出
        
        Args:
            mode: 执行模式 ("random", "fixed", "sequential")
                - random: 随机选择一个连接的输入进行输出
                - fixed: 根据position参数选择固定的输入进行输出（position从1开始，超出输入数量时会循环）
                - sequential: 自动顺序循环选择输入进行输出（执行到底后会重新从头开始执行，不依赖position参数）
            seed: 随机种子，用于随机模式和sequential模式的状态检测
            position: 位置编号，仅用于fixed模式（从1开始计数，循环执行）
            input_1~input_5: 可选的输入值
            
        Returns:
            tuple: 包含所选值的不同类型表示和选中索引
        """
        # 收集所有非空输入，保持顺序
        inputs = [input_1, input_2, input_3, input_4, input_5]
        valid_inputs = [inp for inp in inputs if inp is not None]
        
        # 如果没有有效输入，返回默认值
        if not valid_inputs:
            selected_value = None
            selected_index = -1
        else:
            # 根据模式选择执行方式
            if mode == "random":
                # 随机模式 - 使用局部随机数生成器避免影响全局状态
                rng = random.Random(seed)
                selected_index = rng.randint(0, len(valid_inputs) - 1)
                selected_value = valid_inputs[selected_index]
                # 重置顺序执行位置
                self.sequential_position = 0
                self.last_seed = None
            elif mode == "fixed":
                # 固定模式，使用指定位置（从1开始，循环）
                selected_index = (position - 1) % len(valid_inputs)
                selected_value = valid_inputs[selected_index]
                # 重置顺序执行位置
                self.sequential_position = 0
                self.last_seed = None
            elif mode == "sequential":
                # 顺序模式，使用内部计数器实现真正的循环执行
                # 检查是否是新的执行（通过seed变化判断）
                if self.last_seed != seed:
                    # 新的执行，更新位置并重置seed记录
                    self.sequential_position = (self.sequential_position + 1) % len(valid_inputs)
                    self.last_seed = seed
                # 使用当前顺序位置选择输入
                selected_index = self.sequential_position
                selected_value = valid_inputs[selected_index]
            else:
                # 默认使用随机模式 - 使用局部随机数生成器避免影响全局状态
                rng = random.Random(seed)
                selected_index = rng.randint(0, len(valid_inputs) - 1)
                selected_value = valid_inputs[selected_index]
                # 重置顺序执行位置
                self.sequential_position = 0
                self.last_seed = None
        
        # 保持原始类型输出
        original_output = selected_value
        
        # 转换为字符串输出
        if selected_value is None:
            string_output = ""
        elif isinstance(selected_value, (int, float)):
            string_output = str(selected_value)
        elif isinstance(selected_value, str):
            string_output = selected_value
        else:
            # 对于其他类型，尝试转换为字符串
            try:
                string_output = str(selected_value)
            except:
                string_output = "无法转换为字符串"
        
        # 转换为整数输出
        try:
            if selected_value is None:
                int_output = 0
            elif isinstance(selected_value, str):
                # 如果是字符串，尝试解析为数字
                int_output = int(float(selected_value)) if selected_value.replace('.', '', 1).isdigit() or (selected_value.startswith('-') and selected_value[1:].replace('.', '', 1).isdigit()) else len(selected_value)
            else:
                int_output = int(selected_value)
        except:
            int_output = 0
            
        # 转换为浮点输出
        try:
            if selected_value is None:
                float_output = 0.0
            elif isinstance(selected_value, str):
                # 如果是字符串，尝试解析为数字
                float_output = float(selected_value) if selected_value.replace('.', '', 1).replace('-', '', 1).isdigit() else float(len(selected_value))
            else:
                float_output = float(selected_value)
        except:
            float_output = 0.0
        
        return (original_output, string_output, int_output, float_output, selected_index)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "RandomExecutionNode": RandomExecutionNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomExecutionNode": "随机执行"
}