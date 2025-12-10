# Ollama 类节点详细说明

Ollama 类节点集成了 Ollama 大语言模型服务，提供了连接配置、参数配置、文本生成和聊天对话等功能，支持与多种 Ollama 模型进行交互。

## 功能概述

Ollama 是一个用于运行大语言模型的工具，它简化了在本地环境中部署和使用大语言模型的过程。本插件中的 Ollama 类节点允许用户在 ComfyUI 中轻松集成和使用 Ollama 服务，从而实现文本生成、对话交互等功能。
注意：此功能依赖于：https://github.com/stavsap/comfyui-ollama插件

## 节点列表

### Ollama连接-重构版 (OllamaConnectivityRefactored)
- **位置**: `XnanTool/Ollama`
- **功能**: 测试与Ollama服务的连接状态并获取可用模型列表
- **输入**: 
  - Ollama服务地址(url)：Ollama服务的URL地址，例如 http://localhost:11434
  - 刷新(refresh)：刷新按钮，点击后重新获取模型列表
- **输出**: 
  - 连接状态(connection_status)：连接成功或失败的状态信息
  - 模型列表(models)：从Ollama服务获取的可用模型列表
- **适用场景**: 配置Ollama服务连接，验证服务状态并选择要使用的模型

### Ollama选项-重构版 (OllamaOptionsRefactored)
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

### Ollama生成-重构版 (OllamaGenerateRefactored)
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

### Ollama聊天-重构版 (OllamaChatRefactored)
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

## 使用指南

1. 在使用 Ollama 类节点之前，请确保已在本地环境中安装并启动了 Ollama 服务。
2. 使用 Ollama 连接配置节点测试与 Ollama 服务的连接，并获取可用模型列表。
3. 根据需要使用 Ollama 选项配置节点设置模型推理参数。
4. 将配置好的参数连接到 Ollama 文本生成节点或 Ollama 聊天节点，以执行相应的任务。

## 故障排除

如果遇到连接问题，请检查以下几点：
- Ollama 服务是否正在运行
- 服务地址是否正确
- 防火墙设置是否阻止了连接