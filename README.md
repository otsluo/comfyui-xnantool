


          
# 🌟 comfyui-xnantool🌟

## ✨ 功能特性

### 🤖 modelscope-魔搭社区api在comfyui调用
- 📚 支持多种常用大模型
- 🔧 配置自动保存，方便下次使用

### 🎨 LoRA 模型调用
- 🚀 支持多种基础模型的文生图功能
- 🎭 集成 LoRA 模型加载和权重调整，无需下载
- 🌐 通过魔搭 API 调用模型，参数灵活自定义
- 🎯 精准控制生成效果，满足个性化需求

## 📥 安装方法

### 方法一：直接克隆
```bash
# 克隆仓库到 ComfyUI 的 custom_nodes 目录
git clone https://github.com/otsluo/comfyui-xnantool.git
# 重启 ComfyUI 即可使用
```
```bash
# 加速镜像
git clone https://gitcode.com/weixin_45738527/comfyui-xnantool.git
# 重启 ComfyUI 即可使用
```

### 方法二：手动安装
1. 💾 下载本项目的压缩包
2. 📂 将解压后的 `comfyui-xnantool` 文件夹复制到 ComfyUI 的 `custom_nodes` 目录中
3. 🔄 重启 ComfyUI 后即可在节点菜单中找到相关功能

## 📋 节点列表

### 🎨 文生图节点 (modelscopeLoraTextToImageNode)
- **位置**: `modelscope_api`
- **功能**: 通过魔搭 API 调用支持 LoRA 的文生图模型
- **输入**: 提示词、API 令牌、基础模型、LoRA 模型等
- **输出**: 生成的图像(image)
- **适用场景**: 快速生成带有 LoRA 风格的图像

### 🎨 图像编辑节点 (modelscopeLoraImageEditNode)
- **位置**: `modelscope_api`
- **功能**: 通过魔搭 API 调用支持 LoRA 的图像编辑模型
- **输入**: 图像、编辑提示词、API 令牌、基础模型、LoRA 模型等
- **输出**: 编辑后的图像(edited_image)
- **适用场景**: 编辑现有图像并应用LoRA风格，实现图像内容修改和风格转换

## 📖 使用指南

### 🎨 文生图节点使用
1. 🔑 获取魔搭 API Token
2. 📝 在节点中输入提示词、API Token、选择基础模型和 LoRA 模型
3. ⚙️ 调整其他可选参数（负面提示词、尺寸、种子、步数、引导系数、LoRA 权重等）
4. ▶️ 执行节点生成图像
5. 🎉 欣赏你的创作！

### 🎨 图像编辑节点使用
1. 🔑 获取魔搭 API Token
2. 📝 连接要编辑的图像，输入编辑提示词、API Token、选择基础模型和 LoRA 模型
3. ⚙️ 调整其他可选参数（负面提示词、尺寸、种子、步数、引导系数、LoRA 权重等）
4. ▶️ 执行节点编辑图像
5. 🎉 查看编辑后的图像！

## 🧰 支持的模型

### 内置支持的基础模型

#### 文生图模型
- 🔮 **Qwen-Image**
- ⚡ **FLUX.1-schnell**
- 🚀 **SD3 Medium**
- 🌟 **Segmind-Vega**
- 🎨 **SDXL 1.0**

#### 图像编辑模型
- 🖌️ **Qwen-Image-Edit**
- ✨ **SDXL Refiner**
- 🔧 **SD Inpainting**

## ⚙️ 配置文件
- `config.json` - 存储默认参数配置
- `.modelscope_api_token` - 存储 API 令牌（可选）

## ⚠️ 注意事项
1. 🔑 使用功能需要有效的魔搭 API Token
2. 📋 模型 ID 格式为：`用户名/模型名`（如：`Qwen/Qwen-Image`）
3. 🌐 生成图像时可能受网络状况影响，请确保网络连接稳定
4. 💡 如有问题，请检查日志文件获取详细信息

## 📝 版本信息
- **当前版本**: v0.0.1

## 📞 联系方式
如有任何问题或建议，欢迎联系我们！

---

<div align="center">
  <p>💖 感谢使用小南工具箱！祝您创作愉快！ 💖</p>
  <p>⭐ 如果你喜欢这个工具，请给我们一个星星支持！ ⭐</p>
</div>

### 标签
#ComfyUI #AI绘画 #图像生成 #SDXL #Qwen #LoRA #工具插件 #AI创作
        