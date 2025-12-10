# 🎯 YOLO和SAM类节点说明

本文档详细介绍了ComfyUI XnanTool插件中的YOLO和SAM类节点，这些节点提供了目标检测和图像分割等功能。

## 🎯 YOLO类节点

YOLO (You Only Look Once) 是一种实时目标检测系统，能够快速准确地识别图像中的多个对象。

### 📋 YOLO节点列表

#### 🔍 YOLO检测节点 (YoloDetectionNode)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 使用YOLO模型进行目标检测
- **输入**: 图像、模型、置信度阈值、IOU阈值、类别筛选等
- **输出**: 检测框坐标、类别标签、置信度分数
- **适用场景**: 快速准确的目标检测任务

#### ✂️ YOLO检测与裁剪一体化 (YoloDetectAndCropNode)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 使用YOLO模型进行目标检测并自动裁剪检测到的对象
- **输入**: 图像、模型、置信度阈值、IOU阈值、类别筛选、填充等
- **输出**: 裁剪后的图像列表、检测信息
- **适用场景**: 目标检测和裁剪的一站式解决方案

#### 🧠 YOLO模型加载器 (v8预设) (YoloModelLoader)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 加载预设的YOLO模型权重文件
- **输入**: 模型类型选择
- **输出**: 加载的模型对象
- **适用场景**: 快速加载常用的YOLO模型进行推理

#### 🧠 YOLO模型加载器V2(本地模型) (YoloModelLoaderV2)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 从本地目录加载YOLO模型权重文件
- **输入**: 模型目录路径
- **输出**: 加载的模型对象
- **适用场景**: 加载自定义训练的YOLO模型

#### 🧠 YOLO模型加载器(自定义路径) (YoloModelLoaderCustomPath)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 从自定义路径加载YOLO模型权重文件
- **输入**: 模型文件路径
- **输出**: 加载的模型对象
- **适用场景**: 加载指定路径的YOLO模型

#### ✂️ YOLO检测裁切节点 (YoloDetectionCropNode)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 根据YOLO检测结果裁切图像
- **输入**: 原始图像、检测结果、边距、方形裁切等
- **输出**: 裁切后的图像
- **适用场景**: 从复杂场景中提取特定目标

#### 🔄 YOLO检测多输出裁切节点 (YoloDetectionMultiOutputCropNode)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 根据YOLO检测结果裁切图像，并通过独立端口输出前5个对象
- **输入**: 原始图像、检测结果、边距、方形裁切等
- **输出**: 最多5个裁切后的图像（独立输出）
- **适用场景**: 需要分别处理检测到的多个对象

#### 🧹 YOLO+SAM背景去除 (YoloSamBackgroundRemovalNode)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 结合YOLO和SAM模型去除图像背景
- **输入**: 图像、YOLO模型、SAM模型、类别筛选、置信度阈值、边界填充等
- **输出**: 去除背景后的图像、裁剪信息
- **适用场景**: 精确的前景提取和背景移除

## 🧠 SAM类节点

SAM (Segment Anything Model) 是Meta开发的一种强大图像分割模型，能够在各种任务中生成高质量的分割掩码。

### 📋 SAM节点列表

#### 🧠 SAM模型加载器（预设） (SamModelLoader)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 加载预设的Segment Anything Model (SAM)权重文件
- **输入**: 模型类型选择(vit_h/vit_l/vit_b)
- **输出**: 加载的SAM模型对象
- **适用场景**: 快速加载常用的SAM模型进行图像分割

#### 🧠 SAM模型加载器V2 (本地模型) (SamModelLoaderV2)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 从本地目录加载Segment Anything Model (SAM)权重文件
- **输入**: 模型目录路径
- **输出**: 加载的SAM模型对象
- **适用场景**: 加载自定义的SAM模型

#### 🧠 SAM模型加载器(自定义路径) (SamModelLoaderCustomPath)
- **位置**: `XnanTool/Yolo和SAM`
- **功能**: 从自定义路径加载Segment Anything Model (SAM)权重文件
- **输入**: 模型文件路径
- **输出**: 加载的SAM模型对象
- **适用场景**: 加载指定路径的SAM模型