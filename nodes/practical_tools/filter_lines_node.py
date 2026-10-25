import re


class FilterLinesNode:
    """
    过滤行节点 - 从多行文本中提取符合条件的行
    支持多种过滤模式：包含、不包含、精确匹配、正则表达式等
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "label": "文本",
                    "description": "要过滤的多行文本"
                }),
                "keyword": ("STRING", {
                    "default": "",
                    "label": "关键词",
                    "description": "过滤关键词或正则表达式"
                }),
                "mode": (["包含", "不包含", "精确匹配", "正则表达式", "开头匹配", "结尾匹配"], {
                    "default": "包含",
                    "label": "过滤模式",
                    "description": "选择过滤方式"
                }),
                "case_sensitive": (["false", "true"], {
                    "default": "false",
                    "label": "区分大小写",
                    "description": "是否区分大小写"
                }),
            },
            "optional": {
                "skip_count": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "label": "跳过行数",
                    "description": "跳过前N个匹配结果，从第N+1个开始输出"
                }),
                "max_lines": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "label": "最大输出行数",
                    "description": "限制输出的行数，0表示不限制"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("过滤结果", "匹配行数")
    FUNCTION = "filter_lines"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    
    def filter_lines(self, text, keyword, mode, case_sensitive, skip_count=0, max_lines=0):
        """
        过滤文本行
        
        Args:
            text: 输入的多行文本
            keyword: 过滤关键词或正则表达式
            mode: 过滤模式
            case_sensitive: 是否区分大小写
            skip_count: 跳过前N个匹配结果
            max_lines: 最大输出行数，0表示不限制
            
        Returns:
            tuple: (过滤后的文本, 匹配行数)
        """
        if not text:
            return ("", "0")
        
        lines = text.split('\n')
        matched_lines = []
        
        # 设置正则表达式标志
        flags = 0 if case_sensitive == "true" else re.IGNORECASE
        
        try:
            for line in lines:
                matched = False
                
                if mode == "包含":
                    if case_sensitive == "true":
                        matched = keyword in line
                    else:
                        matched = keyword.lower() in line.lower()
                        
                elif mode == "不包含":
                    if case_sensitive == "true":
                        matched = keyword not in line
                    else:
                        matched = keyword.lower() not in line.lower()
                        
                elif mode == "精确匹配":
                    if case_sensitive == "true":
                        matched = line.strip() == keyword.strip()
                    else:
                        matched = line.strip().lower() == keyword.strip().lower()
                        
                elif mode == "正则表达式":
                    try:
                        pattern = re.compile(keyword, flags)
                        matched = pattern.search(line) is not None
                    except re.error as e:
                        return (f"正则表达式错误: {str(e)}", "0")
                        
                elif mode == "开头匹配":
                    if case_sensitive == "true":
                        matched = line.startswith(keyword)
                    else:
                        matched = line.lower().startswith(keyword.lower())
                        
                elif mode == "结尾匹配":
                    if case_sensitive == "true":
                        matched = line.endswith(keyword)
                    else:
                        matched = line.lower().endswith(keyword.lower())
                
                if matched:
                    # 跳过前N个匹配结果
                    if skip_count > 0:
                        skip_count -= 1
                        continue

                    matched_lines.append(line)
                    # 检查是否达到最大行数限制
                    if max_lines > 0 and len(matched_lines) >= max_lines:
                        break

            result = '\n'.join(matched_lines)
            count = str(len(matched_lines))

            return (result, count)
            
        except Exception as e:
            return (f"过滤时发生错误: {str(e)}", "0")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "FilterLinesNode": FilterLinesNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "FilterLinesNode": "过滤行"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
