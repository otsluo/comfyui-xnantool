import os
import re
import json


class SensitiveWordFilterNode:
    """
    违禁词过滤节点 - 过滤和替换文本中的违禁词
    支持自定义违禁词列表、替换策略和日志输出
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "输入文本",
                    "description": "需要过滤的文本内容"
                }),
                "filter_mode": (["替换为星号", "替换为指定文本", "删除违禁词", "仅标记不修改"], {
                    "default": "替换为星号",
                    "label": "过滤模式",
                    "description": "选择违禁词的处理方式"
                }),
                "replacement_text": ("STRING", {
                    "default": "***",
                    "multiline": False,
                    "label": "替换文本",
                    "description": "当选择'替换为指定文本'时使用的替换内容"
                }),
                "match_mode": (["精确匹配", "模糊匹配", "正则匹配"], {
                    "default": "模糊匹配",
                    "label": "匹配模式",
                    "description": "选择违禁词的匹配方式"
                }),
                "case_sensitive": (["否", "是"], {
                    "default": "否",
                    "label": "区分大小写",
                    "description": "是否区分英文字母大小写"
                }),
            },
            "optional": {
                "custom_words": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "label": "自定义违禁词",
                    "description": "自定义违禁词列表（用逗号、分号或换行分隔）"
                }),
                "regex_patterns": ("STRING", {
                    "default": "正常写法：【过滤文字】\n中间有数字：【过】\\d*【滤】\n中间有字母：【过】[a-zA-Z]*【滤】\n中间有符号：【过】[^\\w]*【滤】\n中间有空格：【过】\\s*【滤】\n重复字符：【过】+【滤】+\n混合插入：【过】[^【过】]*【滤】\n后字重复：【过】[^【过】]*【滤】+\n前字重复：【过】+[^【滤】]*【滤】\n全部：【过】+[^【过】]*【滤】+",
                    "multiline": True,
                    "label": "正则表达式",
                    "description": "自定义正则表达式匹配规则（每行一个）"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("filtered_text", "filter_report", "found_count")
    FUNCTION = "filter_sensitive_words"
    CATEGORY = "XnanTool/实用工具"
    
    def filter_sensitive_words(self, input_text, filter_mode, replacement_text, match_mode, case_sensitive,
                               custom_words="", regex_patterns=""):
        """
        过滤文本中的违禁词
        
        Args:
            input_text: 输入文本
            filter_mode: 过滤模式
            replacement_text: 替换文本
            match_mode: 匹配模式
            case_sensitive: 是否区分大小写
            custom_words: 自定义违禁词
            regex_patterns: 正则表达式
            
        Returns:
            tuple: (过滤后文本, 过滤报告, 发现数量)
        """
        if not input_text or not input_text.strip():
            return ("", "输入文本为空", 0)
        
        # 解析自定义违禁词
        sensitive_words = []
        if custom_words and custom_words.strip():
            words = re.split(r'[,，;；\n]+', custom_words.strip())
            sensitive_words = [w.strip() for w in words if w.strip()]
        
        # 解析正则表达式
        custom_regex = []
        if regex_patterns and regex_patterns.strip():
            custom_regex = [line.strip() for line in regex_patterns.strip().split('\n') if line.strip()]
        
        # 初始化统计
        found_words = []
        filtered_text = input_text
        count = 0
        
        # 根据匹配模式处理
        if match_mode == "精确匹配":
            for word in sensitive_words:
                if not case_sensitive:
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                else:
                    pattern = re.compile(re.escape(word))
                
                matches = pattern.findall(filtered_text)
                if matches:
                    count += len(matches)
                    found_words.extend(matches)
                    
                    if filter_mode == "替换为星号":
                        replacement = '*' * len(word)
                        filtered_text = pattern.sub(replacement, filtered_text)
                    elif filter_mode == "替换为指定文本":
                        filtered_text = pattern.sub(replacement_text, filtered_text)
                    elif filter_mode == "删除违禁词":
                        filtered_text = pattern.sub('', filtered_text)
        
        elif match_mode == "模糊匹配":
            for word in sensitive_words:
                if not case_sensitive:
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                else:
                    pattern = re.compile(re.escape(word))
                
                matches = pattern.findall(filtered_text)
                if matches:
                    count += len(matches)
                    found_words.extend(matches)
                    
                    if filter_mode == "替换为星号":
                        replacement = '*' * len(word)
                        filtered_text = pattern.sub(replacement, filtered_text)
                    elif filter_mode == "替换为指定文本":
                        filtered_text = pattern.sub(replacement_text, filtered_text)
                    elif filter_mode == "删除违禁词":
                        filtered_text = pattern.sub('', filtered_text)
        
        elif match_mode == "正则匹配":
            all_patterns = custom_regex
            if not all_patterns:
                return (input_text, "未提供正则表达式", 0)
            
            for pattern_str in all_patterns:
                try:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    pattern = re.compile(pattern_str, flags)
                    
                    matches = pattern.findall(filtered_text)
                    if matches:
                        count += len(matches)
                        found_words.extend(matches)
                        
                        if filter_mode == "替换为星号":
                            filtered_text = pattern.sub('***', filtered_text)
                        elif filter_mode == "替换为指定文本":
                            filtered_text = pattern.sub(replacement_text, filtered_text)
                        elif filter_mode == "删除违禁词":
                            filtered_text = pattern.sub('', filtered_text)
                except re.error as e:
                    return (input_text, f"正则表达式错误: {str(e)}", 0)
        
        # 生成过滤报告
        if count > 0:
            unique_words = list(set(found_words))
            report = f"发现 {count} 处违禁内容\n"
            report += f"违禁词列表: {', '.join(unique_words[:20])}"
            if len(unique_words) > 20:
                report += f" 等{len(unique_words)}个"
        else:
            report = "未发现违禁内容"
        
        return (filtered_text, report, count)


# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "SensitiveWordFilterNode": SensitiveWordFilterNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SensitiveWordFilterNode": "违禁词过滤",
}
