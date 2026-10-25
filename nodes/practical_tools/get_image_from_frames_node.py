class GetImageFromFramesNode:
    """
    从帧序列获取图像节点 - 从图像帧序列（批次）中获取指定索引的图像
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_frames": ("IMAGE", {
                    "label": "图像帧序列",
                    "description": "图像帧序列（批次格式，如从视频提取的帧）"
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
    
    def get_image(self, image_frames, index):
        """
        从图像帧序列中获取指定索引的图像
        
        Args:
            image_frames: 图像帧序列，形状为 [B, H, W, C]
            index: 要获取的索引（从0开始）
            
        Returns:
            tuple: (图像,)
        """
        # 检查输入是否为空
        if image_frames is None:
            raise ValueError("图像帧序列为空")
        
        # 确保是 4D 张量 [B, H, W, C]
        if image_frames.ndim == 3:
            # 单张图片，添加批次维度
            image_frames = image_frames.unsqueeze(0)
        
        # 获取批次大小
        batch_size = image_frames.shape[0]
        
        # 检查索引范围
        if batch_size == 0:
            raise ValueError("图像帧序列为空")
        
        if index >= batch_size:
            raise ValueError(f"索引 {index} 超出范围，帧序列长度为 {batch_size}")
        
        # 获取指定索引的图像
        # 返回形状为 [1, H, W, C] 的单张图片
        image = image_frames[index:index+1]
        
        return (image,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "GetImageFromFramesNode": GetImageFromFramesNode
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetImageFromFramesNode": "从图片帧序列获取图像"
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
