
# 🌟 ComfyUI XnanTool 🌟

<div align="center">
  <img src="./src/logo.png" alt="XnanTool Logo" />
  <p>🚀 提升你的 ComfyUI 图像生成体验！🚀</p>
</div>

## 📝 简介

**XnanTool**初心是一个为 ComfyUI 打造的市面上插件因原作者不更，或者更新慢，导致功能不足的问题，这里提供了拓展方案。

## ✨ 功能特性

### ✨ 中文翻译优化

为了提升中文用户的使用体验，XnanTool 对所有节点的标题、描述、输入输出参数等进行了全面的中文本地化优化：

- 📘 **节点标题优化**：所有节点都有清晰易懂的中文标题，如"魔搭API文生图节点"、"YOLO检测与裁剪一体化"等
- 📝 **参数描述优化**：每个输入参数都有详细的中文说明，帮助用户快速理解参数作用
- 🎯 **功能说明优化**：每个节点都有详细的中文功能描述，解释节点的具体用途和适用场景
- 🧩 **选项标签优化**：对于下拉菜单等选项，提供了直观的中文标签，如"最高置信度"、"手动索引"等
- 📋 **输出说明优化**：每个输出端口都有明确的中文标识，便于用户识别和使用

通过这些优化，即使是初次接触 ComfyUI 的中文用户也能快速上手并高效使用 XnanTool 的各项功能。

### 🤖 modelscope-魔搭社区api在comfyui调用
- 📚 内置多种常用大模型支持
- 🔍 可视化查看和管理可用模型
- ➕ 支持添加自定义模型到预设列表
- 💾 配置自动保存，方便下次使用
- 🎨 支持LoRA 模型调用-


### 📏 预设功能：尺寸和提示词预设
- 🖼️ **智能尺寸预设**：
- 📐 **精准比例标注**：
- 💡 **提示词预设管理**：
- ⚡ **一键应用**：

### 🎯 YOLO和SAM
- 🚀 **完整集成YOLOv8系列模型支持**：
- 🚀 **支持最新的YOLO系列模型**：
- 🔍 **精确的目标检测与分类功能**：
- ✂️ **强大的图像分割能力**：
- 🤖 **YOLO与SAM模型结合，实现更精确的分割效果**：
- 🔄 **支持多种SAM模型变体（vit_h/l/b）**：
- 🧩 **与YOLO检测结合实现智能背景去除**：

### ⚙️ 智能安装与配置管理
- 🚀 一键安装脚本，简化依赖安装过程
- ✅ 自动验证功能，确保插件正确安装
- 📄 配置文件管理，保存用户偏好设置
- 🔄 支持多种安装方式（手动、ComfyUI Manager、脚本）

### 🎬 媒体处理功能
- 🎞️ 视频转GIF功能
- 🎵 视频转音频功能
- 📸 图片转视频功能

### 图片处理功能
- 🖼️ **批量图像加载**：
- 📦 **图像格式转换**：
- 📁 **批量文件夹图像格式转换**：
- 📏 **批量图像缩放（带格式转换）**：
- 🟦 **正方形转换器**：
- 🟦 **长方形转换器**：
- 🎨 **创建图像节点**：
- 🔢 **图片编码生成**：
- 🖼️ **图像加载节点**：
- 🖼️ **路径图片加载节点**：

### 🛠️ 实用工具扩展
- 🔀 **切换值节点**：


## 📥 安装方法

### 方法一：直接克隆
```bash
# 克隆仓库到 ComfyUI 的 custom_nodes 目录
git clone https://github.com/otsluo/comfyui-xnantool.git
# 安装依赖: pip install -r requirements.txt
# 重启 ComfyUI 即可使用
```
```bash
# 加速镜像
git clone https://gitcode.com/weixin_45738527/comfyui-xnantool.git
# 安装依赖: pip install -r requirements.txt
# 重启 ComfyUI 即可使用
```

### 方法二：手动安装
1. 💾 下载本项目的压缩包
2. 📂 将解压后的 `comfyui-xnantool` 文件夹复制到 ComfyUI 的 `custom_nodes` 目录中
3. 💻 安装依赖: `pip install -r requirements.txt`
4. 🔄 重启 ComfyUI 后即可在节点菜单中找到相关功能

### 方法三：使用安装脚本
1. 🚀 打开命令提示符 (CMD) 或 PowerShell
2. 📁 切换到插件目录: `例如：cd e:\git_project\comfyui-xnantool`
3. ▶️ 运行安装脚本: `python install_dependencies.py`
4. ✅ 验证安装: `python verify_installation_xnantool.py`
5. 🔄 重启 ComfyUI
<!--
### 方法四：通过 ComfyUI Manager 安装 (推荐)
1. 🧩 在 ComfyUI Manager 中搜索 `XnanTool`
2. 📦 点击安装并等待完成
3. 🔄 重启 ComfyUI
4. ✅ 安装完成后即可在节点菜单中找到相关功能
-->
## 📋 节点列表

### 📏 预设类节点

#### 🎲 随机提示词生成器组 (RandomPromptGeneratorGroupNode)
- **位置**: `XnanTool/预设`
- **功能**: 支持多个分类的预设提示词，可随机选择指定数量的提示词并组合成完整的提示词
- **输入**: 
  - 手动输入提示词(manual_prompt)：手动输入的提示词，将添加到生成的随机提示词前面
  - 启用人物分类(enable_person)：人物分类
  - 人物提示词数量(person_count)：提示词数量
  - 启用场景分类(enable_scene)：场景分类
  - 场景提示词数量(scene_count)：场提示词数量
  - 启用风格分类(enable_style)：风格分类
  - 风格提示词数量(style_count)：提示词数量
  - 启用光影分类(enable_lighting)：光影分类
  - 光影提示词数量(lighting_count)：提示词数量
  - 启用色彩分类(enable_color)：色彩分类
  - 色彩提示词数量(color_count)：提示词数量
  - 启用细节分类(enable_detail)：细节分类
  - 细节提示词数量(detail_count)：提示词数量
  - 随机种子(seed)：随机种子，相同种子会产生相同结果，不同种子产生不同结果
- **输出**: 
  - 提示词(prompt)：生成的随机提示词字符串
- **适用场景**: 需要生成包含多种元素的随机提示词组合，支持按分类控制提示词的选择

#### 🎲 随机提示词生成器 (RandomPromptGeneratorNode)
- **位置**: `XnanTool/预设`
- **功能**: 在手动输入的提示词中随机输出指定个数的提示词
- **输入**: 
  - 输入提示词(input_prompts)：手动输入的提示词，用分隔符分隔
  - 输出个数(output_count)：提示词数量
  - 分隔符(separator)：输入提示词的分隔符，默认为逗号
  - 随机种子(seed)：随机种子，相同种子会产生相同结果，不同种子产生不同结果
- **输出**: 
  - 提示词(prompt)：随机选择的提示词字符串
- **适用场景**: 需要从给定的提示词列表中随机选择指定数量的提示词

#### 📏 尺寸预设(SizeSelector)
- **位置**: `XnanTool/预设`
- **功能**: 从预设列表中选择图像尺寸
- **输入**: 预设名称
- **输出**: 宽度(width)、高度(height)
- **适用场景**: 快速选择常用的图像尺寸预设

#### 📋 图片视频提示词预设 (ImageVideoPromptSelector)
- **位置**: `XnanTool/实用工具/预设`
- **功能**: 从预设列表中选择图片和视频提示词
- **输入**: 预设名称
- **输出**: 图片提示词(image_prompt)、视频提示词(video_prompt)、预设图像(preset_image)
- **适用场景**: 快速选择常用的图片和视频提示词预设

#### 🛠️ 图片视频提示词预设管理器 (ImageVideoPromptManager)
- **位置**: `XnanTool/实用工具/预设`
- **功能**: 管理图片和视频提示词预设列表
- **输入**: 操作类型、预设名称、图片提示词、视频提示词、要删除的预设
- **输出**: 状态信息(status_message)
- **适用场景**: 添加、删除或查看图片视频提示词预设列表

###  📤 预设图像上传节点 (PresetImageUploadNode)
- **位置**: `XnanTool/实用工具/预设`
- **功能**: 为提示词预设添加图像预览
- **输入**: 预设名称、图像
- **输出**: 状态信息(status_message)
- **适用场景**: 为提示词预设添加可视化图像预览

### 🎨 魔搭API类节点

#### 🎨 魔搭API文生图节点 (modelscopeLoraTextToImageNode)
- **位置**: `XnanTool/魔搭-api`
- **功能**: 使用魔搭API的LoRA模型生成图像
- **输入**: 提示词、API Token、基础模型、LoRA模型等
- **输出**: 生成的图像(image)
- **适用场景**: 快速生成高质量的LoRA风格图像

#### 🖌️ 魔搭API图像编辑节点 (modelscopeLoraImageEditNode)
- **位置**: `XnanTool/魔搭-api`
- **功能**: 使用魔搭API的LoRA模型编辑图像
- **输入**: 图像、提示词、API Token、基础模型、LoRA模型等
- **输出**: 编辑后的图像(image)
- **适用场景**: 对现有图像进行LoRA风格编辑

#### 🤖 魔搭API-大模型选择器 (ModelscopeApiSelector)
- **位置**: `XnanTool/预设`
- **功能**: 选择魔搭API模型
- **输入**: 模型名称
- **输出**: 模型名称(model_name)
- **适用场景**: 从预设列表中选择魔搭API模型

#### 🤖 魔搭API-大模型列表管理 (ModelscopeApiManager)
- **位置**: `XnanTool/预设`
- **功能**: 管理魔搭API模型列表
- **输入**: 操作类型、模型ID、显示名称、要删除的模型等
- **输出**: 状态信息(status_message)
- **适用场景**: 添加、删除或查看魔搭API模型列表

#### 🎨 魔搭API-Lora模型选择器 (ModelscopeApiLoraSelector)
- **位置**: `XnanTool/魔搭api`
- **功能**: 从预设列表中选择魔搭API的LoRA模型
- **输入**: LoRA模型名称
- **输出**: LoRA模型名称(lora_model_name)
- **适用场景**: 快速选择常用的魔搭API LoRA模型

#### 🎨 魔搭API-Lora列表管理 (ModelscopeApiLoraManager)
- **位置**: `XnanTool/魔搭api`
- **功能**: 管理魔搭API的LoRA模型列表，支持查看、添加和删除LoRA模型
- **输入**: 操作类型、LoRA模型ID、要删除的LoRA模型等
- **输出**: 状态信息(status_message)
- **适用场景**: 添加、删除或查看魔搭API LoRA模型列表

#### 📝 魔搭API-文本生成节点 (ModelscopeApiTextGenerationNode)
- **位置**: `XnanTool/魔搭api`
- **功能**: 使用魔搭API的Qwen3-VL系列模型进行文本生成，支持对话、创作、翻译等多种文本生成任务
- **输入**: 
  - API Token(api_token)：魔搭API令牌，用于身份验证
  - 模型名称(model_name)：选择要使用的Qwen3-VL系列模型
  - 提示词(prompt)：输入的文本提示词
  - 最大令牌数(max_tokens)：生成文本的最大长度(100-4000)
  - 温度系数(temperature)：控制生成文本的随机性(0.1-2.0)
- **输出**: 生成的文本(generated_text)
- **适用场景**: 文本创作、对话生成、翻译、摘要等各类文本生成任务

#### 🎬 魔搭API-视频反推节点 (ModelscopeApiVideoCaptionNode)
- **位置**: `XnanTool/魔搭api`
- **功能**: 使用魔搭API的Qwen3-VL系列模型对视频进行反推描述，生成视频内容的文字描述
- **输入**: 
  - 视频帧(video_frames)：输入的视频帧张量
  - API Token(api_token)：魔搭API令牌，用于身份验证
  - 模型名称(model_name)：选择要使用的Qwen3-VL系列模型
  - 提示词(prompt)：用于视频描述的提示词
  - 最大令牌数(max_tokens)：生成描述文本的最大长度(100-4000)
  - 温度系数(temperature)：控制生成文本的随机性(0.1-2.0)
- **输出**: 视频描述(video_description)
- **适用场景**: 对视频内容进行自动描述，用于视频理解、标签生成等任务

#### 🖼️ 魔搭API-图片反推节点 (ModelscopeApiImageCaptionNode)
- **位置**: `XnanTool/魔搭api`
- **功能**: 使用魔搭API的Qwen3-VL系列模型对图片进行反推描述，生成图片内容的文字描述
- **输入**: 
  - 图像(image)：输入的图像张量
  - API Token(api_token)：魔搭API令牌，用于身份验证
  - 模型名称(model_name)：选择要使用的Qwen3-VL系列模型
  - 提示词(prompt)：用于图片描述的提示词
  - 最大令牌数(max_tokens)：生成描述文本的最大长度(100-4000)
  - 温度系数(temperature)：控制生成文本的随机性(0.1-2.0)
- **输出**: 图片描述(image_description)
- **适用场景**: 对图像内容进行自动描述，用于图像理解、标签生成等任务






### 🎯 YOLO类节点

#### 🎯 YOLO检测节点 (YoloDetectionNode)
- **位置**: `XnanTool/yolo和sam/yolo`
- **功能**: 使用YOLO模型对图像进行目标检测，支持置信度阈值设置和标注显示
- **输入**: YOLO模型、图像、置信度阈值、是否显示标签
- **输出**: 带标注框的图像、检测结果、检测对象数量
- **适用场景**: 图像目标检测任务，可用于识别图像中的物体并标注

#### 🎯 YOLO检测裁切节点 (YoloDetectionCropNode)
- **位置**: `XnanTool/yolo和sam/yolo`
- **功能**: 根据YOLO检测结果裁切图像，支持边距设置、方形裁切和裁切索引选择
- **输入**: 图像、检测结果、裁切索引、边距、是否裁切为正方形
- **输出**: 裁切后的图像、裁切区域数量
- **适用场景**: 根据检测结果精确裁切感兴趣的区域

#### 🎯 YOLO检测多输出裁切节点 (YoloDetectionMultiOutputCropNode)
- **位置**: `XnanTool/yolo和sam/yolo`
- **功能**: 根据YOLO检测结果裁切图像，提供5个独立图像输出端口和5个掩码输出端口
- **输入**: 图像、检测结果、边距、是否裁切为正方形
- **输出**: 5个裁切图像输出端口、5个掩码输出端口
- **适用场景**: 需要同时获取多个检测对象裁切结果的场景

#### 🎯 YOLO检测与裁剪一体化 (YoloDetectAndCropNode)
- **位置**: `XnanTool/yolo和sam/yolo`
- **功能**: 集成YOLO检测和图像裁剪功能，直接输入图像即可完成检测和裁剪，支持类别过滤、置信度阈值设置和边界填充
- **输入**: 
  - YOLO模型(YOLO_MODEL)：用于物体检测的YOLO模型
  - 图像(IMAGE)：需要处理的输入图像
  - 类别(classes)：指定要检测的类别，如 'person,dog,cat'，留空则检测所有类别

### 🖼️ 图像处理类节点

#### 🖼️ 路径图片加载节点 (LoadImagePathNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 从指定的文件路径加载图像，支持多种图像格式（jpg, jpeg, png, bmp, webp, tiff）
- **输入**: 
  - 图片路径(image_path)：图像文件的完整路径
- **输出**: 
  - 图像(image)：加载的图像张量
  - 图片路径(image_path)：图像文件的完整路径
- **适用场景**: 需要从特定文件路径加载图像的场景，适用于自动化处理或批量处理任务
  - 置信度阈值(confidence_threshold)：YOLO检测的置信度阈值(0.0-1.0)
  - 边界填充(padding)：裁剪边界填充像素数(0-100)
- **输出**: 
  - 裁剪图像(cropped_image)：根据检测结果裁剪后的图像
  - 检测结果(detection_results)：YOLO检测结果的JSON格式数据
  - 检测对象数量(detected_objects_count)：检测到的对象数量
  - 裁剪信息(crop_info)：裁剪区域的详细信息
  - 裁剪区域数量(crop_regions_count)：裁剪区域数量
  - 处理信息(info)：包含检测和裁剪详情的文本信息
- **适用场景**: 需要一步完成目标检测和图像裁剪的场景，特别适用于快速提取图像中感兴趣区域的任务

#### 🧠 YOLO模型加载器 (YoloModelLoader)
- **位置**: `XnanTool/yolo和sam/yolo`
- **功能**: 加载预设的YOLO模型，支持多种YOLOv8模型变体（检测、分割、姿态估计、分类）
- **输入**: 
  - 模型名称(model_name)：选择预设的YOLO模型名称
  - 置信度阈值(confidence_threshold)：模型检测的置信度阈值(0.1-1.0)
  - IOU阈值(iou_threshold)：非极大值抑制的IOU阈值(0.1-1.0)
  - 使用缓存(use_cache)：是否使用缓存的模型文件
  - 强制重新加载(force_reload)：是否强制重新加载模型
- **输出**: 
  - YOLO模型(YOLO_MODEL)：加载的YOLO模型对象
  - 模型信息(model_info)：包含模型详情的文本信息
- **适用场景**: 使用预设的YOLO模型进行目标检测、分割等任务

#### 🧠 YOLO模型加载器V2 (本地模型) (YoloModelLoaderV2)
- **位置**: `XnanTool/yolo和sam/yolo`
- **功能**: 从本地models/yolo目录加载YOLO模型文件，支持.pt和.onnx格式
- **输入**: 
  - 模型名称(model_name)：从本地models/yolo目录中选择模型文件
  - 置信度阈值(confidence_threshold)：模型检测的置信度阈值(0.1-1.0)
  - IOU阈值(iou_threshold)：非极大值抑制的IOU阈值(0.1-1.0)
  - 使用缓存(use_cache)：是否使用缓存的模型文件
- **输出**: 
  - YOLO模型(YOLO_MODEL)：加载的YOLO模型对象
  - 模型信息(model_info)：包含模型详情的文本信息
- **适用场景**: 使用本地存储的YOLO模型文件进行目标检测、分割等任务

#### 🧠 YOLO模型加载器(自定义路径) (YoloModelLoaderCustomPath)
- **位置**: `XnanTool/yolo和sam/yolo`
- **功能**: 从自定义路径加载YOLO模型文件，支持.pt和.onnx格式
- **输入**: 
  - 模型完整路径(model_path)：YOLO模型文件的完整路径
  - 置信度阈值(confidence_threshold)：模型检测的置信度阈值(0.1-1.0)
  - IOU阈值(iou_threshold)：非极大值抑制的IOU阈值(0.1-1.0)
  - 使用缓存(use_cache)：是否使用缓存的模型文件
- **输出**: 
  - YOLO模型(YOLO_MODEL)：加载的YOLO模型对象
  - 模型信息(model_info)：包含模型详情的文本信息
- **适用场景**: 使用指定路径的YOLO模型文件进行目标检测、分割等任务

#### 🧠 YOLO+SAM背景去除 (YoloSamBackgroundRemovalNode)
- **位置**: `XnanTool/yolo和sam/yolo+sam`
- **功能**: 使用YOLO进行物体检测，然后使用SAM进行精确分割和背景去除，支持置信度阈值、边界填充、遮罩扩张/模糊等参数设置
- **输入**: 
  - YOLO模型(YOLO_MODEL)：用于物体检测的YOLO模型
  - SAM模型(SAM_MODEL)：用于精确分割的SAM模型
  - 图像(IMAGE)：需要处理的输入图像
  - 类别(classes)：指定要检测的类别，如 'person,dog,cat'，留空则检测所有类别
  - 选择模式(selection_mode)：选择"最高置信度"或"手动索引"来选择检测对象
  - 物体索引(object_index)：手动模式下选择的物体索引
  - YOLO置信度阈值(confidence_threshold)：YOLO检测的置信度阈值(0.0-1.0)
  - 边界填充(padding)：裁剪边界填充像素数
  - 遮罩扩张(mask_dilation)：遮罩扩张像素数(可选)
  - 遮罩模糊(mask_blur)：遮罩模糊强度(可选)
- **输出**: 
  - 裁剪图像(cropped_image)：背景去除并裁剪后的图像
  - 前景遮罩(foreground_mask)：前景物体的遮罩
  - 处理信息(info)：包含检测和处理详情的文本信息
- **适用场景**: 需要精确背景去除和智能裁剪的图像处理任务，特别适用于复杂背景下的物体提取

### 🧠 SAM类节点

#### 🧠 YOLO+SAM背景去除 (YoloSamBackgroundRemovalNode)
- **位置**: `XnanTool/yolo和sam/yolo+sam`
- **功能**: 使用YOLO进行物体检测，然后使用SAM进行精确分割和背景去除，支持置信度阈值、边界填充、遮罩扩张/模糊等参数设置
- **输入**: 
  - YOLO模型(YOLO_MODEL)：用于物体检测的YOLO模型
  - SAM模型(SAM_MODEL)：用于精确分割的SAM模型
  - 图像(IMAGE)：需要处理的输入图像
  - 类别(classes)：指定要检测的类别，如 'person,dog,cat'，留空则检测所有类别
  - 选择模式(selection_mode)：选择"最高置信度"或"手动索引"来选择检测对象
  - 物体索引(object_index)：手动模式下选择的物体索引
  - YOLO置信度阈值(confidence_threshold)：YOLO检测的置信度阈值(0.0-1.0)
  - 边界填充(padding)：裁剪边界填充像素数
  - 遮罩扩张(mask_dilation)：遮罩扩张像素数(可选)
  - 遮罩模糊(mask_blur)：遮罩模糊强度(可选)
- **输出**: 
  - 裁剪图像(cropped_image)：背景去除并裁剪后的图像
  - 前景遮罩(foreground_mask)：前景物体的遮罩
  - 处理信息(info)：包含检测和处理详情的文本信息
- **适用场景**: 需要精确背景去除和智能裁剪的图像处理任务，特别适用于复杂背景下的物体提取

#### 🧠 SAM模型加载器（预设） (SamModelLoader)
- **位置**: `XnanTool/yolo和sam/sam`
- **功能**: 加载预设的SAM模型，支持vit_h、vit_l、vit_b三种模型类型
- **输入**: 
  - 模型类型(model_type)：选择预设的SAM模型类型(vit_h/vit_l/vit_b)
  - 自动下载(auto_download)：是否自动下载模型文件
  - 使用缓存(use_cache)：是否使用缓存的模型文件
- **输出**: 
  - SAM模型(SAM_MODEL)：加载的SAM模型对象
  - 模型信息(model_info)：包含模型详情的文本信息
- **适用场景**: 使用预设的SAM模型进行图像分割任务

#### 🧠 SAM模型加载器V2 (本地模型) (SamModelLoaderV2)
- **位置**: `XnanTool/yolo和sam/sam`
- **功能**: 从本地models/sam目录加载SAM模型文件(.pth格式)
- **输入**: 
  - 模型文件(model_file)：从本地models/sam目录中选择.pth模型文件
  - 使用缓存(use_cache)：是否使用缓存的模型文件
- **输出**: 
  - SAM模型(SAM_MODEL)：加载的SAM模型对象
  - 模型信息(model_info)：包含模型详情的文本信息
- **适用场景**: 使用本地存储的SAM模型文件进行图像分割任务

#### 🧠 SAM模型加载器(自定义路径) (SamModelLoaderCustomPath)
- **位置**: `XnanTool/yolo和sam/sam`
- **功能**: 从自定义路径加载SAM模型文件(.pth格式)
- **输入**: 
  - 模型完整路径(model_path)：SAM模型文件的完整路径
  - 使用缓存(use_cache)：是否使用缓存的模型文件
- **输出**: 
  - SAM模型(SAM_MODEL)：加载的SAM模型对象
  - 模型信息(model_info)：包含模型详情的文本信息
- **适用场景**: 使用指定路径的SAM模型文件进行图像分割任务

### 🎬 媒体处理类节点

#### 🎞️ 图片转GIF节点 V1 (ImagesToGifNode)
- **位置**: `XnanTool/媒体处理`
- **功能**: 将多张图片转换为GIF动画（基础版本，无过渡效果）
- **输入**: 图片、帧间隔、循环次数、缩放因子、优化GIF、调色板大小、质量等级、输出文件名（可选）
- **输出**: GIF文件路径
- **适用场景**: 需要将多张图片转换为GIF动画的场景

#### 🎞️ 图片转GIF节点 V2 (ImagesToGifNodeV2)
- **位置**: `XnanTool/媒体处理`
- **功能**: 将多张图片转换为GIF动画（增强版本，支持多种过渡效果）
- **输入**: 图片、帧间隔、循环次数、缩放因子、过渡效果、过渡帧数、优化GIF、调色板大小、质量等级、输出文件名（可选）
- **输出**: GIF文件路径
- **适用场景**: 需要将多张图片转换为带过渡效果的GIF动画的场景

#### 🎬 视频转GIF节点 (VideoToGifNode)
- **位置**: `XnanTool/媒体处理`
- **功能**: 将视频文件转换为GIF动画
- **输入**: 视频文件、持续时间、帧率、缩放因子、优化GIF、调色板大小、质量等级、输出文件名（可选）
- **输出**: GIF文件路径
- **适用场景**: 需要将视频转换为GIF动画的场景

####  视频转音频节点 (VideoToAudioNode)
- **位置**: `XnanTool/媒体处理`
- **功能**: 从视频文件中提取音频轨道并保存为音频文件
- **输入**: 视频文件、输出格式、音频质量、输出文件名（可选）
- **输出**: 音频文件路径和状态信息
- **适用场景**: 需要从视频中提取音频的场景

#### 📸 视频帧提取节点 (ExtractFrameFromVideoNode)
- **位置**: `XnanTool/媒体处理`
- **功能**: 从视频文件中提取指定帧并保存为图像文件，支持按帧号或时间点提取
- **输入**: 
  - 视频文件(video)：要处理的视频文件
  - 帧提取模式(frame_mode)：选择"按帧号"或"按时间点"提取帧
  - 帧号(frame_number)：要提取的帧号（从0开始）
  - 时间点(timestamp)：要提取的时间点（秒）
  - 输出格式(output_format)：输出图像格式（jpg/png/webp）
  - 图像质量(quality)：JPEG/WebP图像质量（1-100）
  - 输出文件名(output_filename)：自定义输出文件名（可选）
- **输出**: 
  - 图像文件路径(image_path)：提取的图像文件路径
  - 状态信息(status)：处理状态信息
- **适用场景**: 需要从视频中提取特定帧作为图像的场景，如制作视频预览图、关键帧提取等

#### 📸 批量视频帧提取节点 (BatchExtractFrameFromVideoNode)
- **位置**: `XnanTool/媒体处理`
- **功能**: 从指定文件夹中的所有视频文件提取指定帧并保存为图像文件，支持按帧号或时间点提取，支持从输入目录选择文件夹或自定义路径，支持将提取的图片导出到指定文件夹
- **输入**: 
  - 文件夹选择模式(folder_selection_mode)：选择文件夹的方式（从输入目录选择或自定义路径）
  - 视频文件夹(video_folder)：从输入目录中选择包含视频文件的文件夹
  - 自定义视频文件夹路径(custom_video_folder_path)：自定义视频文件夹的完整路径
  - 提取方式(frame_extraction_method)：选择"按帧号"或"按时间点"提取帧
  - 帧号(frame_number)：要提取的帧号（从1开始）
  - 时间戳(timestamp)：要提取的时间点（秒）
  - 输出格式(output_format)：输出图像格式（png/jpg/bmp）
  - 图片质量(image_quality)：JPEG图像质量（1-100）
  - 输出文件名前缀(output_filename_prefix)：自定义输出文件名前缀（可选）
  - 输出文件夹路径(output_folder)：自定义输出文件夹路径（可选，留空则使用默认输出目录）
- **输出**: 
  - 图像路径(image_paths)：提取的图像文件路径列表
  - 帧索引(frame_indices)：提取的帧索引列表
  - 状态信息(status_message)：处理状态信息
- **适用场景**: 需要从文件夹中所有视频批量提取特定帧作为图像的场景，如批量制作视频预览图、关键帧提取等，支持使用自定义路径访问任意位置的视频文件夹，支持将提取的图片导出到指定文件夹


### 🖼️ 图像处理类节点

#### 🟦 正方形转换器 (SquareConverter)
- **位置**: `XnanTool/Image`
- **功能**: 将图像转换为正方形，保持图像比例不变，最高尺寸为1024
- **输入**: 图像(image)、边距(margin)、填充颜色(pad_color)
- **输出**: 正方形图像(image)、宽度(width)、高度(height)
- **适用场景**: 需要将非正方形图像转换为正方形，同时保持图像内容完整

#### 🟦 长方形转换器节点 (RectangleConverter)
- **位置**: `XnanTool/实用工具/小工具`
- **功能**: 将正方形图像转换为长方形图像，支持左右和上下的扩展
- **输入**: 图像、扩展方向、目标长度、边距、填充颜色（可选）
- **输出**: 转换后的图像、宽度、高度
- **适用场景**: 需要将正方形图像转换为长方形的场景

#### 🔢 图片编码生成节点 (Imageencodinggeneration)
- **位置**: `XnanTool/图像处理`
- **功能**: 读取图片并生成唯一的UUID值和多种哈希值(MD5, SHA1, SHA256, SHA512)
- **输入**: 图像(image)
- **输出**: UUID字符串(uuid)、MD5哈希值(md5)、SHA1哈希值(sha1)、SHA256哈希值(sha256)、SHA512哈希值(sha512)、图片信息(image_info)
- **适用场景**: 需要为图像生成唯一标识符和多种哈希值的场景，可用于图像标识、校验和去重

#### 🔢 图片编码生成节点-不转化 (ImageEncodingGenerationNoConvertNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 直接从文件路径读取图片并生成唯一的UUID值和多种哈希值(MD5, SHA1, SHA256, SHA512)，不进行图像格式转换，确保哈希值与原始文件一致
- **输入**: 图片路径(image_path)
- **输出**: UUID字符串(uuid)、MD5哈希值(md5)、SHA1哈希值(sha1)、SHA256哈希值(sha256)、SHA512哈希值(sha512)、图片信息(image_info)
- **适用场景**: 需要为图像文件生成与原始文件完全一致的哈希值的场景，可用于精确的文件校验和去重

#### 🖼️ 创建图像节点 (CreateImageNode)
- **位置**: `XnanTool/实用工具/小工具`
- **功能**: 创建指定尺寸和颜色的图片
- **输入**: 宽度、高度、颜色
- **输出**: 创建的图像
- **适用场景**: 需要创建指定尺寸和颜色图像的测试场景


#### 🖼️ 图像格式转换 (ImageFormatConverterNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 将图像转换为JPEG、PNG、WEBP或BMP格式
- **输入**: 图像(images)、目标格式(format)、JPEG/WebP质量(quality)、优化PNG(optimize)
- **输出**: 转换后的图像(converted_images)
- **适用场景**: 需要将图像转换为指定格式的场景

#### 🖼️ 批量图像格式转换器 (BatchImageFormatConverterNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 批量将指定文件夹中的图像转换为JPEG、PNG、WEBP或BMP格式
- **输入**: 输入文件夹(input_folder)、输出格式(output_format)、图像质量(quality)、输出文件夹(output_folder)
- **输出**: 转换后的图像(converted_images)、文件路径列表(file_paths)
- **适用场景**: 需要批量转换文件夹中多个图像的格式，支持保持原始文件名并将输出保存到指定文件夹


#### 🖼️ 批量图像缩放（带格式转换） (BatchImageResizerWithConversionNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 批量将指定文件夹中的图像按宽度或高度进行缩放，保持图像宽高比，并支持转换图像格式
- **输入**: 输入文件夹(input_folder)、缩放模式(resize_mode)、目标尺寸(size)、输出文件夹(output_folder)、输出格式(output_format)、图像质量(quality)
- **输出**: 输出文件路径列表(output_paths)
- **适用场景**: 需要批量调整文件夹中多个图像的尺寸，支持按宽度或高度为基准进行等比缩放，并可将图像转换为指定格式（JPEG、PNG、WEBP、BMP）

#### 🖼️ 加载图像节点 (LoadImageNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 从image_video_prompt_presets_node文件夹加载图像文件并转换为ComfyUI可用的IMAGE张量和文件路径
- **输入**: 图像文件(image_file) - 从image_video_prompt_presets_node文件夹中选择的图像文件
- **输出**: 图像张量(image)、图像文件路径(image_path)
- **适用场景**: 需要从预设文件夹中加载图像文件并用于后续处理的场景


#### 🖼️ 批量加载图片节点 (BatchImageLoaderNode)
- **位置**: `XnanTool/图像处理`
- **功能**: 从指定文件夹批量加载图片，支持加载全部图片或按索引加载单张图片
- **输入**: 图片路径、加载模式、索引、最大图片数量
- **输出**: 图片(images)、文件名列表(filenames)、图片数量(count)
- **适用场景**: 需要批量加载图片进行处理的场景

#### 🖼️ 批量重命名图片(MD5) (BatchRenameImagesByMD5Node)
- **位置**: `XnanTool/图像处理`
- **功能**: 批量重命名图片文件，使用图片内容的MD5哈希值作为新文件名，确保文件唯一性并避免重复
- **输入**: 
  - 输入目录(input_directory)：包含需要重命名图片的目录路径
  - 输出目录(output_directory)：重命名后图片保存的目录路径（留空则在原目录处理）
  - 覆盖已存在文件(overwrite_existing)：是否覆盖输出目录中已存在的同名文件
  - 文件扩展名(file_extensions)：需要处理的图片文件扩展名，用逗号分隔
- **输出**: 
  - 处理信息(output_info)：处理结果信息
  - 处理文件数(processed_count)：已处理的文件数量
  - 重命名文件数(renamed_count)：已重命名的文件数量
  - 错误信息(error_info)：处理过程中出现的错误信息
- **适用场景**: 需要根据图片内容唯一性对图片文件进行重命名的场景，可有效避免重复文件并保持文件唯一性

### 🦙 Ollama类节点

#### 🦙 Ollama连接配置节点 (OllamaConnectivityRefactored)
- **位置**: `XnanTool/Ollama`
- **功能**: 测试与Ollama服务的连接状态并获取可用模型列表
- **输入**: 
  - Ollama服务地址(url)：Ollama服务的URL地址，例如 http://localhost:11434
  - 刷新(refresh)：刷新按钮，点击后重新获取模型列表
- **输出**: 
  - 连接状态(connection_status)：连接成功或失败的状态信息
  - 模型列表(models)：从Ollama服务获取的可用模型列表
- **适用场景**: 配置Ollama服务连接，验证服务状态并选择要使用的模型

#### 🦙 Ollama选项配置节点 (OllamaOptionsRefactored)
- **位置**: `XnanTool/Ollama`
- **功能**: 配置Ollama模型推理的各种参数选项
- **输入**: 
  - 启用上下文参数(enable_context_params)：是否启用上下文相关参数
  - 上下文窗口大小(num_ctx)：模型上下文窗口大小
  - 重复惩罚回溯长度(repeat_last_n)：用于重复惩罚的回溯token数量
  - 重复惩罚系数(repeat_penalty)：重复token的惩罚系数
  - 启用温度参数(enable_temperature_params)：是否启用温度相关参数
  - 温度(temperature)：控制生成文本随机性的温度参数
  - 随机种子(seed)：随机数种子，相同种子产生相同结果
  - 启用停止参数(enable_stop_params)：是否启用停止相关参数
  - 停止标记(stop)：指定生成停止的标记序列
  - 启用采样参数(enable_sampling_params)：是否启用采样相关参数
  - TFS-Z采样(tfs_z)：TFS-Z采样参数
  - 预测令牌数(num_predict)：预测生成的令牌数量
  - 启用Top-K参数(enable_top_k_params)：是否启用Top-K采样参数
  - Top-K(top_k)：Top-K采样参数
  - 启用Top-P参数(enable_top_p_params)：是否启用Top-P采样参数
  - Top-P(top_p)：Top-P采样参数
  - 启用Min-P参数(enable_min_p_params)：是否启用Min-P采样参数
  - Min-P(min_p)：Min-P采样参数
- **输出**: 
  - OLLAMA_OPTIONS：包含所有配置选项的对象
- **适用场景**: 精细调节Ollama模型推理参数，控制生成文本的质量和多样性

#### 🦙 Ollama文本生成节点 (OllamaGenerateRefactored)
- **位置**: `XnanTool/Ollama`
- **功能**: 使用Ollama模型根据提示词生成文本内容
- **输入**: 
  - Ollama服务地址(url)：Ollama服务的URL地址
  - 模型名称(model)：要使用的Ollama模型名称
  - 提示词(prompt)：输入的文本提示词
  - OLLAMA_OPTIONS：来自Ollama选项配置节点的参数选项
- **输出**: 
  - 生成的文本(response)：模型生成的文本内容
  - 完成原因(done_reason)：文本生成完成的原因
- **适用场景**: 使用Ollama模型进行文本生成任务，如文章创作、故事续写、问答等

#### 🦙 Ollama聊天节点 (OllamaChatRefactored)
- **位置**: `XnanTool/Ollama`
- **功能**: 与Ollama模型进行对话式交互
- **输入**: 
  - Ollama服务地址(url)：Ollama服务的URL地址
  - 模型名称(model)：要使用的Ollama模型名称
  - 聊天消息(messages)：对话历史消息列表
  - OLLAMA_OPTIONS：来自Ollama选项配置节点的参数选项
- **输出**: 
  - 回复消息(response)：模型回复的消息内容
  - 完成原因(done_reason)：对话完成的原因
- **适用场景**: 与Ollama模型进行多轮对话交互，构建聊天机器人等应用

### 🛠️ 实用工具类节点

#### 🛠️ 切换值节点 (ToggleValueNode)
- **位置**: `XnanTool/实用工具/小工具`
- **功能**: 可以在两个值之间切换的节点，支持多种数据类型输入（FLOAT, INT, STRING）
- **输入**: 布尔值开关(input_value)、值A(value_a)、值B(value_b)
- **输出**: 原始类型输出、字符串输出、整数输出、浮点输出
- **适用场景**: 在工作流中根据条件切换不同的值

#### 📋 查看版本节点 (VersionInfoNode)
- **位置**: `XnanTool/实用工具`
- **功能**: 显示当前插件的版本信息
- **输入**: 虚拟输入(dummy_input)
- **输出**: 版本信息(version_info)
- **适用场景**: 检查当前安装的插件版本


## ⚠️ 注意事项

## 🛠️ 常见问题解决

## 📝 版本信息
- **当前版本**: v0.6.0
- **更新日期**: 2025年11月29日
- **更新日志**: 集成Ollama大语言模型支持，新增多个Ollama相关节点，包括Ollama选项配置、连接配置、文本生成、聊天对话等功能；重构Ollama节点架构，提供更灵活的配置选项和更好的用户体验；完善插件中文翻译，为Ollama相关节点提供全面的中文本地化支持；优化节点间的数据传递和错误处理机制；修复已知问题，提升插件稳定性和性能 

## 📞 联系方式
如有任何问题或建议，欢迎联系我们！


<!--

<p align="center">
<p>up主：1527004566</p>

<img width="220px" src="./src/up主-裁切.png" align="center" alt="logo，注意这个路gitcode显示，github显示，小图，预览不显示" />
<p>交流：1046591978</p>

<img width="220px" src="./src/comfyui-xnantool-裁切.png" align="center" alt="logo，注意这个路gitcode显示，github显示，小图，预览不显示" />
</p>

-->
---

<div align="center">
  <p>💖 感谢使用XnanTool！祝您创作愉快！ 💖</p>
  <p>⭐ 如果你喜欢这个工具，请给我们一个星星支持！ ⭐</p>
</div>

### 标签
#ComfyUI #AI绘画 #图像生成 #SDXL #Qwen #LoRA #工具插件 #AI创作 #目标检测 #图像分割 #YOLO #SAM #视频处理 #图片处理 #Ollama #大语言模型 #LLM
