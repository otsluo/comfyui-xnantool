# YOLO和SAM节点模块初始化文件

# 导入YOLO相关节点
from .yolo_detection_node import YoloDetectionNode
from .yolo_detect_and_crop_node import YoloDetectAndCropNode
from .yolo_detection_crop_node import YoloDetectionCropNode
from .yolo_detection_multi_output_crop_node import YoloDetectionMultiOutputCropNode
from .yolo_modelloader_nodes import YoloModelLoader, YoloModelLoaderV2, YoloModelLoaderCustomPath
from .yolo_sam_background_removal_node import YoloSamBackgroundRemovalNode

# 导入SAM相关节点
from .sam_modelloader_nodes import SamModelLoader, SamModelLoaderV2, SamModelLoaderCustomPath

# 定义节点映射
NODE_CLASS_MAPPINGS = {
    "YoloDetectionNode": YoloDetectionNode,
    "YoloDetectAndCropNode": YoloDetectAndCropNode,
    "YoloDetectionCropNode": YoloDetectionCropNode,
    "YoloDetectionMultiOutputCropNode": YoloDetectionMultiOutputCropNode,
    "YoloModelLoader": YoloModelLoader,
    "YoloModelLoaderV2": YoloModelLoaderV2,
    "YoloModelLoaderCustomPath": YoloModelLoaderCustomPath,
    "YoloSamBackgroundRemovalNode": YoloSamBackgroundRemovalNode,
    "SamModelLoader": SamModelLoader,
    "SamModelLoaderV2": SamModelLoaderV2,
    "SamModelLoaderCustomPath": SamModelLoaderCustomPath,
}

# 定义节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "YoloDetectionNode": "YOLO检测节点",
    "YoloDetectAndCropNode": "YOLO检测与裁剪一体化",
    "YoloDetectionCropNode": "YOLO检测裁切节点",
    "YoloDetectionMultiOutputCropNode": "YOLO检测多输出裁切节点",
    "YoloModelLoader": "YOLO模型加载器 (v8预设)",
    "YoloModelLoaderV2": "YOLO模型加载器V2(本地模型)",
    "YoloModelLoaderCustomPath": "YOLO模型加载器(自定义路径)",
    "YoloSamBackgroundRemovalNode": "YOLO+SAM背景去除",
    "SamModelLoader": "SAM模型加载器（预设）",
    "SamModelLoaderV2": "SAM模型加载器V2 (本地模型)",
    "SamModelLoaderCustomPath": "SAM模型加载器(自定义路径)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']