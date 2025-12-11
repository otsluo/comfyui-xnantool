# 🎨 魔搭API类节点说明

本文档详细介绍了ComfyUI XnanTool插件中的魔搭API类节点，这些节点允许您使用魔搭(ModelScope)平台的API进行图像生成、文本生成、图像描述等任务。

## 🛠️ 配置文件说明

从插件 v0.6.5 版本开始，魔搭API节点不再依赖外部配置文件。所有配置均已硬编码到节点中，简化了使用流程。

如果您是从旧版本升级的用户，可以安全地删除以下文件：
- `modelscope_config.json` - 旧版配置文件（已不再使用）
- `tokens` - 旧版API令牌存储文件（已不再使用）

API令牌现在会直接保存在插件内部，无需额外配置文件。

## 📋 节点列表

#### 🎨 魔搭API文生图节点 (modelscopeLoraTextToImageNode)
- **位置**: `XnanTool/魔搭-api`
- **功能**: 使用魔搭API的LoRA模型生成图像
- **输入**: 
  - 提示词(prompt)：描述要生成图像内容的文本
  - API Token(api_token)：魔搭API访问令牌
  - 基础模型(base_model)：用于生成的基础模型名称
  - LoRA模型(lora_model)：可选的LoRA模型名称
  - 宽度(width)：生成图像的宽度(默认1024)
  - 高度(height)：生成图像的高度(默认1024)
  - 指导权重(guidance_scale)：控制生成质量的参数(默认7.5)
  - 推理步数(num_inference_steps)：生成过程的迭代次数(默认50)
- **输出**: 生成的图像(image)
- **适用场景**: 快速生成高质量的LoRA风格图像

#### 🖌️ 魔搭API图像编辑节点 (modelscopeLoraImageEditNode)
- **位置**: `XnanTool/魔搭-api`
- **功能**: 使用魔搭API的LoRA模型编辑图像
- **输入**: 
  - 图像(image)：需要编辑的输入图像
  - 提示词(prompt)：描述图像编辑要求的文本
  - API Token(api_token)：魔搭API访问令牌
  - 基础模型(base_model)：用于编辑的基础模型名称
  - LoRA模型(lora_model)：可选的LoRA模型名称
  - 指导权重(guidance_scale)：控制编辑质量的参数(默认7.5)
  - 强度(strength)：编辑强度，值越大变化越明显(默认0.8)
  - 推理步数(num_inference_steps)：编辑过程的迭代次数(默认50)
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
