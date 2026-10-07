import re


class TextProcessorNode:
    """
    文本处理节点 - 对文本进行各种处理
    支持：不改变、取数字、取字母、转大写、转小写、取中文、去标点、去换行、去空格、去格式、统计字数、统计字符
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "文本",
                    "description": "要处理的文本"
                }),
                "mode": (["不改变", "取数字", "取字母", "转大写", "转小写", "取中文", "去标点", "去换行", "去空行", "去空格", "去双引号", "去前后双引号", "去格式", "统计字数", "统计字符", "反转文本"], {
                    "default": "不改变",
                    "label": "处理模式",
                    "description": "选择文本处理方式"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("处理结果",)
    FUNCTION = "process_text"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"

    def process_text(self, text, mode):
        """
        根据模式处理文本

        Args:
            text: 输入的文本
            mode: 处理模式

        Returns:
            tuple: (处理结果,)
        """
        if text is None:
            text = ""

        result = text

        if mode == "不改变":
            result = text

        elif mode == "取数字":
            result = re.sub(r'[^\d]', '', text)

        elif mode == "取字母":
            result = re.sub(r'[^a-zA-Z]', '', text)

        elif mode == "转大写":
            result = text.upper()

        elif mode == "转小写":
            result = text.lower()

        elif mode == "取中文":
            result = re.sub(r'[^\u4e00-\u9fff]', '', text)

        elif mode == "去标点":
            # 去除中英文标点
            result = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
            result = re.sub(r'[\u3000-\u303f\uff00-\uffef]', '', result)

        elif mode == "去换行":
            result = text.replace('\r\n', '').replace('\n', '').replace('\r', '')

        elif mode == "去空行":
            # 去除空行，保留有内容的行
            lines = text.splitlines()
            non_empty_lines = [line for line in lines if line.strip()]
            result = '\n'.join(non_empty_lines)

        elif mode == "去空格":
            # 只去除普通空格字符
            result = text.replace(' ', '')

        elif mode == "去双引号":
            # 去除全部双引号（包括中英文双引号）
            result = text.replace('"', '').replace('"', '').replace('"', '')

        elif mode == "去前后双引号":
            # 只去除文本首尾的双引号
            result = text.strip('"').strip('"').strip('"')

        elif mode == "去格式":
            # 去除特殊字符、格式符号、换行和空格
            result = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
            result = re.sub(r'[`~!@#$%^&*()_+<>?:"{},.\/;\'\\[\]]', '', result)
            result = re.sub(r'[\s]+', '', result)

        elif mode == "统计字数":
            # 只统计总字符数
            result = str(len(text))

        elif mode == "统计字符":
            # 统计各种字符数量
            original_length = len(text)
            chinese_count = len(re.findall(r'[\u4e00-\u9fff]', text))
            english_count = len(re.findall(r'[a-zA-Z]', text))
            digit_count = len(re.findall(r'\d', text))
            space_count = len(re.findall(r'\s', text))
            punctuation_count = original_length - chinese_count - english_count - digit_count - space_count

            result = (
                f"总字符数：{original_length}\n"
                f"中文字符：{chinese_count}\n"
                f"英文字母：{english_count}\n"
                f"数字：{digit_count}\n"
                f"空格：{space_count}\n"
                f"标点符号：{punctuation_count}"
            )

        elif mode == "反转文本":
            # 将文本倒序排列
            result = text[::-1]

        return (result,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "TextProcessorNode": TextProcessorNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "TextProcessorNode": "文本处理"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
