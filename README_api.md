# 🌐 API类节点说明

本文档详细介绍了ComfyUI XnanTool插件中的API类节点，这些节点集成了火山引擎和阿里云百炼等平台的AI能力，提供了文生图、图生图、文本生成、视觉理解等多种功能。

## 📋 节点列表

### 🎨 豆包Seedream文生图节点 (DoubaoSeedreamTextToImageGenerationNode)
- **位置**: `XnanTool/API/火山引擎`
- **功能**: 使用火山引擎豆包Seedream模型进行文生图，支持单张和批量连贯图像生成
- **输入**: 
  - 提示词(prompt)：描述要生成图像内容的文本
  - 模型ID(model_id)：选择豆包Seedream模型版本
  - API密钥(api_key)：火山引擎方舟API密钥
  - 比例(aspect_ratio)：生成图像的比例（1:1、2:3、3:2、3:4、4:3、5:4、4:5、9:16、16:9、21:9）
  - 分辨率(resolution)：生成图像的分辨率（1K、2K、4K）
  - 生成模式(mode)：生成模式（single单张，batch批量连贯）
  - 图像数量(max_images)：生成的图像数量（批量模式下，1-15）
  - 随机种子(seed)：随机种子（0为随机）
  - 水印(watermark)：是否添加水印
- **输出**: 
  - 图像(images)：生成的图像张量
  - 状态信息(status_info)：生成状态和图片链接信息
- **适用场景**: 快速生成高质量的豆包Seedream风格图像，支持批量连贯图像生成

### 🎨 豆包Seedream图生图节点 (DoubaoSeedreamImageToImageGenerationNode)
- **位置**: `XnanTool/API/火山引擎`
- **功能**: 使用火山引擎豆包Seedream模型进行图生图，支持参考图像进行风格迁移
- **输入**: 
  - 图像(image)：参考图像
  - 提示词(prompt)：描述图像编辑要求的文本
  - 模型ID(model_id)：选择豆包Seedream模型版本
  - API密钥(api_key)：火山引擎方舟API密钥
  - 比例(aspect_ratio)：生成图像的比例
  - 分辨率(resolution)：生成图像的分辨率
  - 强度(strength)：图像编辑强度（0.1-1.0）
  - 随机种子(seed)：随机种子（0为随机）
  - 水印(watermark)：是否添加水印
- **输出**: 
  - 图像(images)：编辑后的图像张量
  - 状态信息(status_info)：生成状态和图片链接信息
- **适用场景**: 基于参考图像进行风格迁移和编辑

### 🤖 百炼LLM-文本生成节点 (BailianLLMNode)
- **位置**: `XnanTool/API/阿里百炼`
- **功能**: 调用阿里云百炼大语言模型进行文本生成，支持多种模型选择
- **输入**: 
  - 提示词(prompt)：输入给大模型的提示词
  - 模型(model)：选择使用的模型（qwen3-max、qwen3.5-plus、qwen-plus、qwen-flash、deepseek-v3.2等）
  - API密钥(api_key)：阿里云百炼API密钥（可选）
  - 温度(temperature)：控制输出的随机性（0.0-1.0）
  - Top P(top_p)：累积概率阈值（0.0-1.0）
  - 最大输出长度(max_tokens)：最大输出Token数量
- **输出**: 
  - 生成文本(output_text)：大模型生成的文本内容
- **适用场景**: 文本创作、对话生成、翻译、摘要等各类文本生成任务

### 🧠 百炼VL-视觉理解节点 (BailianVLNode)
- **位置**: `XnanTool/API/阿里百炼`
- **功能**: 调用阿里云百炼视觉语言模型进行图片+文本理解
- **输入**: 
  - 提示词(prompt)：输入给大模型的提示词（可包含图片描述）
  - 图片(image)：输入的图片
  - 模型(model)：选择使用的VL模型（qwen3-vl-plus、qwen3.5-plus等）
  - API密钥(api_key)：阿里云百炼API密钥（可选）
  - 温度(temperature)：控制输出的随机性（0.0-1.0）
  - Top P(top_p)：累积概率阈值（0.0-1.0）
  - 最大输出长度(max_tokens)：最大输出Token数量
- **输出**: 
  - 理解文本(output_text)：大模型对图片的理解和描述
  - 状态信息(status_info)：处理状态信息
- **适用场景**: 图片内容理解、图像描述生成、视觉问答等任务

### 🖼️ 百炼Qwen-图片生成节点 (BailianQwenNode)
- **位置**: `XnanTool/API/阿里百炼`
- **功能**: 调用阿里云百炼图片生成模型生成图像
- **输入**: 
  - 提示词(prompt)：生成图片的提示词
  - 模型(model)：选择使用的图片生成模型（qwen-image-plus）
  - API密钥(api_key)：阿里云百炼API密钥（可选）
  - 反向提示词(negative_prompt)：不希望出现在图片中的内容
  - 图片宽度(image_width)：生成图片的宽度（256-2048像素）
  - 图片高度(image_height)：生成图片的高度（256-2048像素）
  - 采样步数(steps)：生成图片的采样步数（1-100）
  - 提示词相关性(scale)：提示词对生成图片的影响程度（1.0-20.0）
- **输出**: 
  - 图像(images)：生成的图像张量
  - 图片链接(image_urls)：生成的图片URL信息
- **适用场景**: 使用通义千问图像模型生成高质量图片

## 🛠️ API配置说明

### 火山引擎方舟API
1. 访问 [火山引擎方舟控制台](https://www.volcengine.com/product/ark)
2. 创建API密钥（Access Key ID 和 Secret Access Key）
3. 在节点中填写API密钥即可使用

### 阿里云百炼API
1. 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 创建API密钥
3. 在节点中填写API密钥即可使用

## ⚠️ 注意事项

1. 所有API节点都需要填写有效的API密钥才能使用
2. API密钥建议使用环境变量或安全的密钥管理方式
3. 不同模型可能有不同的计费标准，请参考各平台的定价说明
4. 批量生成图像时请注意控制生成数量，避免产生高额费用
5. 建议在使用前先测试单张生成，确认无误后再进行批量生成
