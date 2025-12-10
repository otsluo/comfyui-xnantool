# 预设管理类节点模块说明

本模块提供了一系列用于管理和使用预设的节点，包括尺寸预设、提示词预设和随机提示词生成等功能。这些节点可以帮助用户快速选择常用的图像尺寸、提示词组合，提高工作效率。

## 节点列表

### 1. 尺寸预设节点 (SizeSelector)
- **位置**: `XnanTool/预设`
- **功能**: 提供常用图像尺寸的快速选择，支持SD 1.5、SDXL、Flux和Qwen-Image等模型的推荐尺寸
- **输入参数**:
  - `size_preset` (STRING): 尺寸预设选项，包括各种常用尺寸及其标签
- **输出参数**:
  - `width` (INT): 图像宽度
  - `height` (INT): 图像高度
- **适用场景**: 当需要快速选择标准图像尺寸时使用，特别适用于不同生成模型的推荐尺寸

### 2. 图片视频提示词预设节点 (ImageVideoPromptSelector)
- **位置**: `XnanTool/预设`
- **功能**: 提供图片和视频提示词预设的选择功能
- **输入参数**:
  - `prompt_preset` (STRING): 提示词预设选项，从配置文件中加载
- **输出参数**:
  - `image_prompt` (STRING): 图片提示词
  - `video_prompt` (STRING): 视频提示词
  - `preset_image` (IMAGE): 预设对应的图像预览
- **适用场景**: 当需要使用预定义的提示词组合时，可以快速选择并应用

### 3. 图片视频提示词预设管理器节点 (ImageVideoPromptManager)
- **位置**: `XnanTool/预设`
- **功能**: 用于管理图片和视频提示词预设，支持列出、添加和删除操作
- **输入参数**:
  - `action` (STRING): 操作类型，可选"list"、"add"、"delete"
  - `preset_name` (STRING, 可选): 要添加的预设名称（仅在添加操作时使用）
  - `image_prompt` (STRING, 可选): 图片提示词（仅在添加操作时使用）
  - `video_prompt` (STRING, 可选): 视频提示词（仅在添加操作时使用）
  - `preset_to_delete` (STRING, 可选): 要删除的预设名称（仅在删除操作时使用）
- **输出参数**:
  - `status_message` (STRING): 操作状态消息
- **适用场景**: 当需要管理提示词预设库时使用，可以动态添加或删除预设

### 4. 预设图像上传节点 (PresetImageUploadNode)
- **位置**: `XnanTool/预设`
- **功能**: 用于为预设添加图像预览
- **输入参数**:
  - `preset_name` (STRING): 预设名称
  - `image` (IMAGE): 要保存为预览的图像
- **输出参数**:
  - 无
- **适用场景**: 当需要为提示词预设添加可视化图像预览时使用

### 5. 随机提示词生成器组节点 (RandomPromptGeneratorGroupNode)
- **位置**: `XnanTool/预设`
- **功能**: 支持多个分类的预设提示词，可随机选择指定数量的提示词
- **输入参数**:
  - `manual_prompt` (STRING): 手动输入的提示词，将添加到生成的随机提示词前面
  - `enable_person` (BOOLEAN): 是否启用人物分类
  - `person_count` (INT): 人物分类中随机选择的提示词数量
  - `enable_scene` (BOOLEAN): 是否启用场景分类
  - `scene_count` (INT): 场景分类中随机选择的提示词数量
  - `enable_style` (BOOLEAN): 是否启用风格分类
  - `style_count` (INT): 风格分类中随机选择的提示词数量
  - `enable_lighting` (BOOLEAN): 是否启用光影分类
  - `lighting_count` (INT): 光影分类中随机选择的提示词数量
  - `enable_color` (BOOLEAN): 是否启用色彩分类
  - `color_count` (INT): 色彩分类中随机选择的提示词数量
  - `enable_detail` (BOOLEAN): 是否启用细节分类
  - `detail_count` (INT): 细节分类中随机选择的提示词数量
  - `seed` (INT): 随机种子
- **输出参数**:
  - `prompt` (STRING): 生成的随机提示词
- **适用场景**: 当需要生成多样化的提示词组合时使用，可以根据不同分类随机选择提示词

### 6. 随机提示词生成器节点 (RandomPromptGeneratorNode)
- **位置**: `XnanTool/预设`
- **功能**: 在手动输入的提示词中随机输出指定个数的提示词
- **输入参数**:
  - `input_prompts` (STRING): 手动输入的提示词，用逗号分隔
  - `output_count` (INT): 需要随机输出的提示词个数
  - `separator` (STRING): 输入提示词的分隔符，默认为逗号
  - `seed` (INT): 随机种子
- **输出参数**:
  - `prompt` (STRING): 随机选择的提示词
- **适用场景**: 当需要从自定义提示词库中随机选择特定数量的提示词时使用