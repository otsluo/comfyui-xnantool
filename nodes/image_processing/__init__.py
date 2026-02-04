# 图像处理节点模块初始化文件

# 导入图像处理相关节点
from .load_image_node import LoadImageNode
from .load_image_path_node import LoadImagePathNode
from .batch_load_images_node import BatchLoadImagesNode
from .image_format_converter_node import ImageFormatConverterNode
from .batch_image_format_converter_node import BatchImageFormatConverterNode
from .Image_encoding_generation_node import Imageencodinggeneration
from .image_encoding_generation_no_convert_node import ImageEncodingGenerationNoConvertNode
from .batch_image_resizer_with_conversion_node import BatchImageResizerWithConversionNode
from .square_converter_node import SquareConverter
from .rectangle_converter_node import RectangleConverter
from .create_image_node import CreateImageNode
from .batch_rename_images_by_md5_node import BatchRenameImagesByMD5Node
from .batch_image_scaler_node import BatchImageScalerNode
from .image_merge_node import ImageMergeNode



# 定义节点映射
NODE_CLASS_MAPPINGS = {
    "LoadImageNode": LoadImageNode,
    "LoadImagePathNode": LoadImagePathNode,
    "BatchLoadImagesNode": BatchLoadImagesNode,
    "ImageFormatConverterNode": ImageFormatConverterNode,
    "BatchImageFormatConverterNode": BatchImageFormatConverterNode,
    "Imageencodinggeneration": Imageencodinggeneration,
    "ImageEncodingGenerationNoConvertNode": ImageEncodingGenerationNoConvertNode,
    "BatchImageResizerWithConversionNode": BatchImageResizerWithConversionNode,
    "SquareConverter": SquareConverter,
    "RectangleConverter": RectangleConverter,
    "CreateImageNode": CreateImageNode,
    "BatchRenameImagesByMD5Node": BatchRenameImagesByMD5Node,
    "BatchImageScalerNode": BatchImageScalerNode,
    "ImageMergeNode": ImageMergeNode,
}

# 定义节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageNode": "加载图像-【Beta】",
    "LoadImagePathNode": "路径图片加载",
    "BatchLoadImagesNode": "批量加载图片",
    "ImageFormatConverterNode": "图像格式转换器",
    "BatchImageFormatConverterNode": "批量图像格式转换器",
    "Imageencodinggeneration": "图片编码生成",
    "ImageEncodingGenerationNoConvertNode": "图片编码生成-不转化",
    "BatchImageResizerWithConversionNode": "批量图像缩放（带格式转换）",
    "SquareConverter": "正方形转换器",
    "RectangleConverter": "长方形转换器",
    "CreateImageNode": "创建图像",
    "BatchRenameImagesByMD5Node": "批量重命名图片(MD5)",
    "BatchImageScalerNode": "批量图像缩放",
    "ImageMergeNode": "图片合并",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']