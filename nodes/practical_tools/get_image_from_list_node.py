class GetImageFromListNode:
    """
    从列表获取图像节点 - 从图像列表中获取指定索引的图像
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_list": ("IMAGE", {
                    "label": "图像列表",
                    "description": "图像列表（来自加载ZIP等节点）"
                }),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "label": "索引",
                    "description": "要获取的图像索引（从0开始）"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("图像",)
    FUNCTION = "get_image"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    INPUT_IS_LIST = True
    
    def get_image(self, image_list, index):
        """
        从图像列表中获取指定索引的图像
        
        Args:
            image_list: 图像列表（会被包装成列表的列表）
            index: 要获取的索引（会被包装成列表）
            
        Returns:
            tuple: (图像,)
        """
        # 处理列表输入
        # image_list 会被包装成 [[image1, image2, ...]]
        # index 会被包装成 [index_value]
        if isinstance(image_list, list) and len(image_list) > 0:
            if isinstance(image_list[0], list):
                images = image_list[0]
            else:
                images = image_list
        else:
            images = image_list
        
        # 提取索引值
        if isinstance(index, list) and len(index) > 0:
            index_value = index[0]
        else:
            index_value = index
        
        # 确保 images 是列表
        if not isinstance(images, list):
            images = [images]
        
        # 检查索引范围
        if len(images) == 0:
            raise ValueError("图像列表为空")
        
        if index_value >= len(images):
            raise ValueError(f"索引 {index_value} 超出范围，列表长度为 {len(images)}")
        
        # 获取指定索引的图像
        image = images[index_value]
        
        return (image,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "GetImageFromListNode": GetImageFromListNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetImageFromListNode": "从图片列表获取图像"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
