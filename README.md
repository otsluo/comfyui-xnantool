


          
# 🌟 ComfyUI XnanTool 🌟

<div align="center">
  <img src="./src/logo.png" alt="XnanTool Logo" />
  <p>🚀 提升你的 ComfyUI 图像生成体验！🚀</p>
</div>

## 📝 简介

**XnanTool**是一个为 ComfyUI 打造的市面上插件因原作者不更，或者更新慢，导致功能不足的问题，这里提供了拓展方案。

## ✨ 功能特性

### 🤖 modelscope-魔搭社区api在comfyui调用
- 📚 内置多种常用大模型支持
- 🔍 可视化查看和管理可用模型
- ➕ 支持添加自定义模型到预设列表
- 💾 配置自动保存，方便下次使用

### 🎨 支持LoRA 模型调用- 
- 🚀 支持多种基础模型的文生图功能
- 🎭 集成 LoRA 模型加载和权重调整，无需下载
- 🌐 通过魔搭 API 调用模型，参数灵活自定义
- 🎯 精准控制生成效果，满足个性化需求

### 📏 尺寸预设功能
- 🖼️ 提供 AI 生图常用尺寸的快速选择
- 📐 支持多种模型的推荐尺寸（SD 1.5、SDXL、Qwen-Image、Flux等）
- 📊 每个尺寸都标注了精确的比例信息
- ⚡ 一键应用，省去手动计算烦恼

### 🎯 YOLO目标检测与分割
- 🚀 完整集成YOLOv8系列模型支持
- 🔍 精确的目标检测与分类功能
- ✂️ 强大的图像分割能力
- 🤖 YOLO与SAM模型结合，实现更精确的分割效果

### 🧠 SAM智能分割功能
- 🎯 精确的图像分割能力
- 🔄 支持多种SAM模型变体（vit_h/l/b）
- 🧩 与YOLO检测结合实现智能背景去除

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



## 📋 节点列表

### 📏 尺寸预设-【新】 (SizeSelector)
- **位置**: `XnanTool/预设`
- **功能**: 从预设列表中选择图像尺寸
- **输入**: 预设名称
- **输出**: 宽度(width)、高度(height)
- **适用场景**: 快速选择常用的图像尺寸预设

### 🎨 魔搭API文生图节点 (modelscopeLoraTextToImageNode)
- **位置**: `XnanTool/modelscope-api`
- **功能**: 使用魔搭API的LoRA模型生成图像
- **输入**: 提示词、API Token、基础模型、LoRA模型等
- **输出**: 生成的图像(image)
- **适用场景**: 快速生成高质量的LoRA风格图像

### 🖌️ 魔搭API图像编辑节点 (modelscopeLoraImageEditNode)
- **位置**: `XnanTool/modelscope-api`
- **功能**: 使用魔搭API的LoRA模型编辑图像
- **输入**: 图像、提示词、API Token、基础模型、LoRA模型等
- **输出**: 编辑后的图像(image)
- **适用场景**: 对现有图像进行LoRA风格编辑

### 🚀 YOLO模型加载器 (v8预设)-【新】 (YoloModelLoader)
- **位置**: `XnanTool/YOLO`
- **功能**: 加载和配置YOLO目标检测模型
- **输入**: 模型名称、置信度阈值、IOU阈值、使用缓存选项等
- **输出**: YOLO模型(YOLO_MODEL)、模型信息(model_info)
- **适用场景**: 为检测任务准备YOLO模型

### 🚀 YOLO模型加载器V2(本地模型)-【新】 (YoloModelLoaderV2)
- **位置**: `XnanTool/YOLO`
- **功能**: 加载本地YOLO模型文件
- **输入**: 本地模型、置信度阈值、IOU阈值、使用缓存选项等
- **输出**: YOLO模型(YOLO_MODEL)、模型信息(model_info)
- **适用场景**: 使用本地存储的YOLO模型文件

### 🚀 YOLO模型加载器(自定义路径)-【新】 (YoloModelLoaderCustomPath)
- **位置**: `XnanTool/YOLO`
- **功能**: 从自定义路径加载YOLO模型
- **输入**: 模型完整路径、置信度阈值、IOU阈值、使用缓存选项等
- **输出**: YOLO模型(YOLO_MODEL)、模型信息(model_info)
- **适用场景**: 使用指定路径的YOLO模型文件

### 🎯 YOLO检测与裁剪一体化-【新】 (YoloDetectAndCropNode)
- **位置**: `XnanTool/YOLO`
- **功能**: 执行YOLO检测并裁剪图像
- **输入**: YOLO模型、图像、类别、置信度阈值、边界填充
- **输出**: 裁剪后的图像、检测结果、检测对象数量、裁剪信息、裁剪区域数量
- **适用场景**: 目标检测后自动裁剪感兴趣区域

### 🟦 正方形转换器-【新】 (SquareConverter)
- **位置**: `XnanTool/Image`
- **功能**: 将图像转换为正方形，保持图像比例不变
- **输入**: 图像(image)、边距(margin)、填充颜色(pad_color)
- **输出**: 正方形图像(image)、宽度(width)、高度(height)
- **适用场景**: 需要将非正方形图像转换为正方形，同时保持图像内容完整

### 🧠 SAM模型加载器（预设）-【新】 (SamModelLoader)
- **位置**: `XnanTool/SAM`
- **功能**: 加载预设的SAM模型
- **输入**: 模型类型、自动下载、使用缓存选项等
- **输出**: SAM模型(SAM_MODEL)、模型信息(model_info)
- **适用场景**: 使用预设的SAM模型进行图像分割

### 🧠 SAM模型加载器V2 (本地模型) -【新】(SamModelLoaderV2)
- **位置**: `XnanTool/SAM`
- **功能**: 加载本地SAM模型文件
- **输入**: 模型文件、使用缓存选项等
- **输出**: SAM模型(SAM_MODEL)、模型信息(model_info)
- **适用场景**: 使用本地存储的SAM模型文件

### 🧠 SAM模型加载器(自定义路径)-【新】 (SamModelLoaderCustomPath)
- **位置**: `XnanTool/SAM`
- **功能**: 从自定义路径加载SAM模型
- **输入**: 模型完整路径、使用缓存选项等
- **输出**: SAM模型(SAM_MODEL)、模型信息(model_info)
- **适用场景**: 使用指定路径的SAM模型文件

### 🤖 魔搭API模型选择器 (ModelscopeApiSelector)
- **位置**: `XnanTool/预设`
- **功能**: 选择魔搭API模型
- **输入**: 模型名称
- **输出**: 模型名称(model_name)
- **适用场景**: 从预设列表中选择魔搭API模型

### 🤖 魔搭API列表管理 (ModelscopeApiManager)
- **位置**: `XnanTool/预设`
- **功能**: 管理魔搭API模型列表
- **输入**: 操作类型、模型ID、显示名称、要删除的模型等
- **输出**: 状态信息(status_message)
- **适用场景**: 添加、删除或查看魔搭API模型列表

### 🧠 YOLO+SAM背景去除-【新】 (YoloSamBackgroundRemovalNode)
- **位置**: `XnanTool/SAM`
- **功能**: 使用YOLO目标检测和SAM分割技术进行精确的背景去除和裁剪
- **输入**: YOLO模型、SAM模型、图像、检测类别、选择模式等
- **输出**: 裁剪图像、前景遮罩、处理信息
- **适用场景**: 需要精确背景去除和智能裁剪的图像处理任务

## 📖 使用指南

### 📏 尺寸选择器使用
1. 在节点菜单中找到 `XnanTool/预设` -> `尺寸预设-【新】`
2. 选择需要的尺寸预设（如 SDXL 正方形、横屏等）
3. 将输出的宽度和高度连接到其他需要尺寸参数的节点
4. 完成！🎉

### 🎨 魔搭API文生图使用
1. 🔑 获取魔搭 API Token
2. 📝 在节点中输入提示词、API Token、选择基础模型和 LoRA 模型
3. ⚙️ 调整其他可选参数（负面提示词、尺寸、种子、步数、引导系数、LoRA 权重等）
4. ▶️ 执行节点生成图像
5. 🎉 欣赏你的创作！

### 🚀 YOLO目标检测使用
1. 在节点菜单中找到 `XnanTool/YOLO` 目录
2. 根据需要选择合适的模型加载器：
   - `YOLO模型加载器 (v8预设)-【新】`：使用预设的YOLOv8模型
   - `YOLO模型加载器V2(本地模型)-【新】`：使用本地存储的YOLO模型文件
   - `YOLO模型加载器(自定义路径)-【新】`：使用指定路径的YOLO模型文件
3. 配置模型参数（置信度阈值、IOU阈值等）
4. 将加载的模型连接到 `YOLO检测与裁剪一体化-【新】` 节点
5. 连接输入图像并配置检测参数
6. 执行节点进行目标检测和图像裁剪

### 🧠 SAM模型使用
1. 在节点菜单中找到 `XnanTool/SAM` 目录
2. 根据需要选择合适的模型加载器：
   - `SAM模型加载器（预设）`：使用预设的SAM模型
   - `SAM模型加载器V2 (本地模型)`：使用本地存储的SAM模型文件
   - `SAM模型加载器(自定义路径)`：使用指定路径的SAM模型文件
3. 配置模型参数（自动下载、使用缓存等）
4. 加载模型后可用于图像分割任务

### 🤖 魔搭API模型管理使用
1. 在节点菜单中找到 `XnanTool/预设` -> `魔搭API列表管理`
2. 选择操作类型：
   - `list`：查看当前所有可用模型
   - `add`：添加新的魔搭API模型到预设列表中
   - `delete`：删除已有的魔搭API模型
3. 根据操作类型填写相应的参数
4. 执行节点查看操作结果
5. 注意：添加或删除模型后需重启ComfyUI才能在选择器中看到变化

## 🧰 支持的模型

### 内置支持的基础模型
- 🔮 **Qwen-Image**
- ⚡ **FLUX.1-schnell**
- 🚀 **FLUX.1-Krea-dev**
- 🎨 **SDXL 1.0**
- 🌟 **Segmind-Vega**
- 🖌️ **Qwen-Image-Edit**
- ✨ **SDXL Refiner**
- 🔧 **SD Inpainting**

### 支持的YOLO模型
- **YOLOv8n** (轻量型)
- **YOLOv8s** (小型)
- **YOLOv8m** (中型)
- **YOLOv8l** (大型)
- **YOLOv8x** (超大型)
- 支持自定义YOLO模型添加

### 尺寸预设列表
#### 🎯 SD 1.5 推荐尺寸
- `512x512` (1:1) - 基础正方形
- `512x768` (2:3) - 竖屏比例
- `768x512` (3:2) - 横屏比例
- `768x768` (1:1) - 大正方形

#### 🚀 SDXL 推荐尺寸
- `1024x1024` (1:1) - 标准正方形
- `1152x896` (4:3) - 经典竖屏
- `896x1152` (3:4) - 经典横屏

#### 🎨 Qwen-Image 推荐尺寸
- `1328x1328` (1:1) - 优化正方形
- `1664x928` (16:9) - 宽屏横屏
- `928x1664` (9:16) - 宽屏竖屏
- `1472x1140` (4:3) - 经典横屏
- `1140x1472` (3:4) - 经典竖屏
- `1584x1056` (3:2) - 电影横屏
- `1056x1584` (2:3) - 电影竖屏

#### ⚡ Flux 推荐尺寸
- `2048x2048` (1:1) - 超高清正方形

## ⚙️ 配置文件
- `config.json` - 存储默认参数配置
- `model_presets.json` - 存储模型预设列表
- `.modelscope_api_token` - 存储 API 令牌（可选）

## ⚠️ 注意事项
1. ⚠️ 添加新模型后需要重启 ComfyUI 才能在选择器中看到
2. 🔑 使用 LoRA 功能需要有效的魔搭 API Token
3. 📋 模型 ID 格式为：`用户名/模型名`（如：`Qwen/Qwen-Image`）
4. 🌐 生成图像时可能受网络状况影响，请确保网络连接稳定
5. 💡 如有问题，请检查日志文件获取详细信息

## 🛠️ 常见问题解决


## 📝 版本信息
- **当前版本**: v0.0.2
- **更新日期**: 2025年10月13日

## 🚀 更新日志

- **v0.0.2** - 功能拓展版本
  - ✅ 完整集成YOLOv8系列目标检测模型
  - ✅ 添加YOLO模型加载器节点 (YoloModelLoader, YoloModelLoaderV2, YoloModelLoaderCustomPath)
  - ✅ 添加YOLO检测与裁剪一体化节点 (YoloDetectAndCropNode)
  - ✅ 完整集成SAM模型支持
  - ✅ 添加SAM模型加载器节点 (SamModelLoader, SamModelLoaderV2)
  - ✅ 添加SAM模型加载器(自定义路径)节点
  - ✅ 添加YOLO+SAM背景去除节点
  - ✅ 完善YOLO和SAM相关节点的使用文档和示例
  - ✅ 优化项目结构，节点分类更清晰
  - ✅ 添加魔搭API模型管理节点 (ModelscopeApiManager)
  - ✅ 增强正方形转换器功能，支持自定义填充颜色

- **v0.0.1** - 初始版本发布
  - ✅ 尺寸选择器节点
  - ✅ LoRA 文生图节点
  - ✅ LoRA 图像编辑节点
  - ✅ 支持多种模型和尺寸预设


## 📞 联系方式
如有任何问题或建议，欢迎联系我们！

---

<div align="center">
  <p>💖 感谢使用XnanTool！祝您创作愉快！ 💖</p>
  <p>⭐ 如果你喜欢这个工具，请给我们一个星星支持！ ⭐</p>
</div>

### 标签
#ComfyUI #AI绘画 #图像生成 #SDXL #Qwen #LoRA #工具插件 #AI创作 #目标检测 #图像分割 #YOLO
        