import random
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RandomPromptGeneratorGroupNode:
    """
    随机提示词生成器组节点
    支持多个分类的预设提示词，可随机选择指定数量的提示词
    """
    
    def __init__(self):
        # 预设的提示词分类
        self.prompt_categories = {
            "人物": [
                "人物肖像", "全身像", "半身像", "侧面像", "背影", 
                "微笑", "严肃表情", "开心", "悲伤", "愤怒", 
                "年轻女性", "成熟女性", "年轻男性", "成熟男性", "儿童",
                "老人", "精灵", "魔法师", "战士", "公主", 
                "王子", "机器人", "外星人", "天使", "恶魔"
            ],
            "场景": [
                "城市景观", "乡村风光", "海滩", "山脉", "森林",
                "沙漠", "雪景", "夜晚", "日出", "日落",
                "室内", "室外", "城堡", "宫殿", "现代建筑",
                "古代建筑", "未来都市", "废墟", "花园", "公园",
                "办公室", "咖啡厅", "餐厅", "卧室", "客厅"
            ],
            "风格": [
                "写实风格", "动漫风格", "卡通风格", "油画风格", "水彩风格",
                "素描", "像素艺术", "赛博朋克", "蒸汽朋克", "奇幻风格",
                "科幻风格", "古典艺术", "印象派", "抽象艺术", "极简主义",
                "复古风格", "未来主义", "哥特风格", "巴洛克风格", "洛可可风格"
            ],
            "光影": [
                "自然光", "柔和光线", "强烈对比光", "逆光", "侧光",
                "顶光", "背光", "霓虹灯", "烛光", "月光",
                "阳光", "阴天", "戏剧性光线", "电影级光照", "HDR效果",
                "发光效果", "光晕", "阴影", "高光", "环境光"
            ],
            "色彩": [
                "暖色调", "冷色调", "鲜艳色彩", "柔和色彩", "单色调",
                "黑白", "高对比度", "低饱和度", "彩虹色", "金色",
                "银色", "紫色", "蓝色", "绿色", "红色",
                "橙色", "黄色", "粉色", "棕色", "多彩"
            ],
            "细节": [
                "高分辨率", "细节丰富", "精致", "超现实", "梦幻",
                "唯美", "艺术感", "专业拍摄", "8K分辨率", "超精细",
                "史诗级", "电影级", "杰作", "最佳质量", "高清",
                "锐利焦点", "浅景深", "景深效果", "动态模糊", "颗粒感"
            ]
        }
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "manual_prompt": ("STRING", {
                    "label": "手动输入提示词",
                    "description": "手动输入的提示词，将添加到生成的随机提示词前面",
                    "default": "",
                    "multiline": True,
                    "dynamicPrompts": False
                }),
                "enable_person": ("BOOLEAN", {
                    "label": "启用人物分类",
                    "description": "是否启用人物分类提示词",
                    "default": True
                }),
                "person_count": ("INT", {
                    "label": "人物提示词数量",
                    "description": "人物分类中随机选择的提示词数量",
                    "default": 2,
                    "min": 0,
                    "max": 10,
                    "step": 1
                }),
                "enable_scene": ("BOOLEAN", {
                    "label": "启用场景分类",
                    "description": "是否启用场景分类提示词",
                    "default": True
                }),
                "scene_count": ("INT", {
                    "label": "场景提示词数量",
                    "description": "场景分类中随机选择的提示词数量",
                    "default": 2,
                    "min": 0,
                    "max": 10,
                    "step": 1
                }),
                "enable_style": ("BOOLEAN", {
                    "label": "启用风格分类",
                    "description": "是否启用风格分类提示词",
                    "default": True
                }),
                "style_count": ("INT", {
                    "label": "风格提示词数量",
                    "description": "风格分类中随机选择的提示词数量",
                    "default": 2,
                    "min": 0,
                    "max": 10,
                    "step": 1
                }),
                "enable_lighting": ("BOOLEAN", {
                    "label": "启用光影分类",
                    "description": "是否启用光影分类提示词",
                    "default": True
                }),
                "lighting_count": ("INT", {
                    "label": "光影提示词数量",
                    "description": "光影分类中随机选择的提示词数量",
                    "default": 2,
                    "min": 0,
                    "max": 10,
                    "step": 1
                }),
                "enable_color": ("BOOLEAN", {
                    "label": "启用色彩分类",
                    "description": "是否启用色彩分类提示词",
                    "default": True
                }),
                "color_count": ("INT", {
                    "label": "色彩提示词数量",
                    "description": "色彩分类中随机选择的提示词数量",
                    "default": 2,
                    "min": 0,
                    "max": 10,
                    "step": 1
                }),
                "enable_detail": ("BOOLEAN", {
                    "label": "启用细节分类",
                    "description": "是否启用细节分类提示词",
                    "default": True
                }),
                "detail_count": ("INT", {
                    "label": "细节提示词数量",
                    "description": "细节分类中随机选择的提示词数量",
                    "default": 2,
                    "min": 0,
                    "max": 10,
                    "step": 1
                }),
                "seed": ("INT", {
                    "label": "随机种子",
                    "description": "随机种子，相同种子会产生相同结果，不同种子产生不同结果",
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate_random_prompt"
    CATEGORY = "XnanTool/预设"

    def generate_random_prompt(self, manual_prompt, enable_person, person_count, enable_scene, scene_count, 
                              enable_style, style_count, enable_lighting, lighting_count,
                              enable_color, color_count, enable_detail, detail_count, seed):
        """
        生成随机提示词
        
        Args:
            manual_prompt (str): 手动输入的提示词
            enable_person (bool): 是否启用人物分类
            person_count (int): 人物分类中选择的提示词数量
            enable_scene (bool): 是否启用场景分类
            scene_count (int): 场景分类中选择的提示词数量
            enable_style (bool): 是否启用风格分类
            style_count (int): 风格分类中选择的提示词数量
            enable_lighting (bool): 是否启用光影分类
            lighting_count (int): 光影分类中选择的提示词数量
            enable_color (bool): 是否启用色彩分类
            color_count (int): 色彩分类中选择的提示词数量
            enable_detail (bool): 是否启用细节分类
            detail_count (int): 细节分类中选择的提示词数量
            seed (int): 随机种子
            
        Returns:
            tuple: 包含生成提示词的元组
        """
        try:
            # 使用提供的种子初始化随机数生成器
            random.seed(seed)
            
            selected_prompts = []
            
            # 根据启用状态和数量选择提示词
            if enable_person and person_count > 0:
                selected_prompts.extend(random.sample(
                    self.prompt_categories["人物"], 
                    min(person_count, len(self.prompt_categories["人物"]))
                ))
            
            if enable_scene and scene_count > 0:
                selected_prompts.extend(random.sample(
                    self.prompt_categories["场景"], 
                    min(scene_count, len(self.prompt_categories["场景"]))
                ))
            
            if enable_style and style_count > 0:
                selected_prompts.extend(random.sample(
                    self.prompt_categories["风格"], 
                    min(style_count, len(self.prompt_categories["风格"]))
                ))
            
            if enable_lighting and lighting_count > 0:
                selected_prompts.extend(random.sample(
                    self.prompt_categories["光影"], 
                    min(lighting_count, len(self.prompt_categories["光影"]))
                ))
            
            if enable_color and color_count > 0:
                selected_prompts.extend(random.sample(
                    self.prompt_categories["色彩"], 
                    min(color_count, len(self.prompt_categories["色彩"]))
                ))
            
            if enable_detail and detail_count > 0:
                selected_prompts.extend(random.sample(
                    self.prompt_categories["细节"], 
                    min(detail_count, len(self.prompt_categories["细节"]))
                ))
            
            # 打乱选中的提示词顺序
            random.shuffle(selected_prompts)
            
            # 组合成最终提示词
            random_prompt = ", ".join(selected_prompts)
            
            # 如果有手动输入的提示词，将其添加到最前面
            if manual_prompt.strip():
                final_prompt = manual_prompt.strip() + ", " + random_prompt
            else:
                final_prompt = random_prompt
            
            logger.info(f"生成随机提示词: {final_prompt}")
            return (final_prompt,)
            
        except Exception as e:
            logger.error(f"生成随机提示词时发生错误: {str(e)}")
            raise Exception(f"生成随机提示词失败: {str(e)}")


class RandomPromptGeneratorNode:
    """
    随机提示词生成器节点
    在手动输入的提示词中随机输出指定个数的提示词
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_prompts": ("STRING", {
                    "label": "输入提示词",
                    "description": "手动输入的提示词，用逗号分隔",
                    "default": "",
                    "multiline": True,
                    "dynamicPrompts": False
                }),
                "output_count": ("INT", {
                    "label": "输出个数",
                    "description": "需要随机输出的提示词个数",
                    "default": 1,
                    "min": 1,
                    "max": 50
                }),
                "separator": ("STRING", {
                    "label": "分隔符",
                    "description": "输入提示词的分隔符",
                    "default": ",",
                    "multiline": False
                }),
                "seed": ("INT", {
                    "label": "随机种子",
                    "description": "随机种子，相同种子会产生相同结果，不同种子产生不同结果",
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate_random_prompts"
    CATEGORY = "XnanTool/预设"

    def generate_random_prompts(self, input_prompts, output_count, separator, seed):
        """
        在手动输入的提示词中随机输出指定个数的提示词
        
        Args:
            input_prompts (str): 手动输入的提示词，用逗号分隔
            output_count (int): 随机输出的提示词个数
            separator (str): 输入提示词的分隔符，默认为逗号
            seed (int): 随机种子
            
        Returns:
            tuple: 包含随机选择提示词的元组
        """
        try:
            # 使用提供的种子初始化随机数生成器
            random.seed(seed)
            
            # 如果没有输入提示词，返回空字符串
            if not input_prompts.strip():
                return ("",)
            
            # 使用指定分隔符分割输入提示词
            prompts_list = [p.strip() for p in input_prompts.split(separator) if p.strip()]
            
            # 如果没有有效提示词，返回空字符串
            if not prompts_list:
                return ("",)
            
            # 随机选择指定个数的提示词
            selected_prompts = random.sample(prompts_list, min(output_count, len(prompts_list)))
            
            # 用逗号连接选中的提示词
            result = ", ".join(selected_prompts)
            
            logger.info(f"随机选择了 {len(selected_prompts)} 个提示词: {result}")
            return (result,)
            
        except Exception as e:
            logger.error(f"随机选择提示词时发生错误: {str(e)}")
            raise Exception(f"随机选择提示词失败: {str(e)}")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "RandomPromptGeneratorGroupNode": RandomPromptGeneratorGroupNode,
    "RandomPromptGeneratorNode": RandomPromptGeneratorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomPromptGeneratorGroupNode": "随机提示词生成器组",
    "RandomPromptGeneratorNode": "随机提示词生成器"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]