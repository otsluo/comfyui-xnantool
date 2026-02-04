# 🖼️ 图像处理类节点说明

本文档详细介绍了ComfyUI XnanTool插件中的图像处理类节点，这些节点提供了各种图像处理功能。

## 📋 节点列表

#### 路径图片加载节点 (LoadImagePathNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 从指定路径加载图像文件
- **输入**: 图片路径
- **输出**: 加载的图像(image)、图片路径(image_path)
- **适用场景**: 从本地文件系统加载图像进行处理

#### 图像格式转换器节点 (ImageFormatConverterNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 在不同的图像格式之间进行转换
- **输入**: 图像(images)、目标格式(format)、JPEG/WebP质量(quality)、优化PNG(optimize)
- **输出**: 转换后的图像(converted_images)
- **适用场景**: 准备适合特定用途的图像格式

#### 图像批处理节点 (BatchImageProcessorNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 对一批图像进行批量处理操作
- **输入**: 输入文件夹(input_folder)、输出格式(output_format)、质量(quality)、输出文件夹(output_folder)
- **输出**: 处理结果信息(result_info)
- **适用场景**: 同时处理多个图像以提高效率

#### 批量图像缩放（带格式转换）节点 (BatchImageResizerWithConversionNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 批量缩放图像并可选择转换格式
- **输入**: 输入文件夹(input_folder)、模式(mode)、目标尺寸(target_size)、输出文件夹(output_folder)、输出格式(output_format)、质量(quality)
- **输出**: 输出文件路径列表(output_paths)
- **适用场景**: 批量调整图像尺寸以适应特定要求

#### 批量加载图片节点 (BatchLoadImagesNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 批量加载文件夹中的图像文件
- **输入**: 模式(mode)、图片路径(image_path)、索引(index)、最大加载数量(max_load_count)
- **输出**: 图像(image)、图像文件名列表(image_filenames)、数量(count)
- **适用场景**: 需要处理大量图像的工作流

#### 批量重命名图片(MD5)节点 (BatchRenameImagesByMD5Node)
- **位置**: `XnanTool/图像处理`
- **功能**: 根据图像内容的MD5哈希值批量重命名图片文件
- **输入**: 输入目录(input_directory)、输出目录(output_directory)（可选）、覆盖已存在的文件(overwrite_existing)（可选）、文件扩展名列表(file_extensions)（可选）、删除原始文件(delete_original_files)（可选）
- **输出**: 处理结果信息(result_info)
- **适用场景**: 整理大量图像文件，避免重复文件名冲突

#### 创建图像节点 (CreateImageNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 创建指定尺寸和颜色的纯色图像
- **输入**: 宽度(width)、高度(height)、颜色(color)
- **输出**: 创建的图像(image)
- **适用场景**: 创建测试图像或占位符图像

#### 图片编码生成节点-不转化 (ImageEncodingGenerationNoConvertNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 直接从文件路径读取图片并生成唯一的UUID值和多种哈希值，不进行图像格式转换
- **输入**: 图片路径(image_path)
- **输出**: UUID(uuid)、MD5(md5)、SHA1(sha1)、SHA256(sha256)、SHA512(sha512)、图片信息(image_info)
- **适用场景**: 图像文件完整性验证和资产管理

#### 图片编码生成节点 (Imageencodinggeneration)
- **位置**: `XnanTool/图像处理`
- **功能**: 读取图片并生成唯一的UUID值和多种哈希值
- **输入**: 图像(image)
- **输出**: UUID(uuid)、MD5(md5)、SHA1(sha1)、SHA256(sha256)、SHA512(sha512)、图片信息(image_info)
- **适用场景**: 工作流中图像内容验证和缓存键生成

#### 加载图像节点节点 (LoadImageNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 加载图像文件并转换为ComfyUI可用的格式
- **输入**: 图像文件(image_file)
- **输出**: 图像(image)、图像路径(image_path)
- **适用场景**: 从预设文件夹加载图像进行处理

#### ↔长方形转换器节点 (RectangleConverter)
- **位置**: `XnanTool/图像处理`
- **功能**: 将正方形图像转换为长方形图像，支持左右和上下的扩展
- **输入**: 图像(image)、扩展方向(direction)、目标长度(target_length)、边距(margin)、填充颜色(pad_color)
- **输出**: 转换后的图像(image)、宽度(width)、高度(height)
- **适用场景**: 创建特定宽高比的图像

#### 正方形转换器节点 (SquareConverter)
- **位置**: `XnanTool/图像处理`
- **功能**: 将非正方形图像转换为正方形图像
- **输入**: 图像(image)、边距(margin)、填充颜色(pad_color)
- **输出**: 转换后的图像(image)、宽度(width)、高度(height)
- **适用场景**: 社交媒体头像制作和图像标准化处理

#### 批量图像缩放节点 (BatchImageScalerNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 批量缩放文件夹中的图像文件
- **输入**: 图像目录(image_directory)、保存目录(save_directory)、缩放因子(scale_factor)、调整尺寸模式(resize_mode)、目标宽度(target_width)、目标高度(target_height)、重采样过滤器(resampling_filter)
- **输出**: 结果信息(result_info)
- **适用场景**: 批量调整图像尺寸以适应特定要求

#### 图片合并节点 (ImageMergeNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 将多张图片合并成一张图片，支持多种合并方式：水平合并、垂直合并、网格合并，网格合并支持自定义列数
- **输入**: 合并方式(operation)、调整为相同尺寸(resize_to_same_size)、图片1-10(image1-image10)、网格列数(columns)
- **输出**: 合并后的图片(merged_image)
- **适用场景**: 将多张图像按指定布局合并成一张图像，常用于制作图像拼接、网格布局、对比图等