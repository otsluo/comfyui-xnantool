# 🌟 ComfyUI XnanTool 🌟

<div align="center">
  <img src="./src/logo.png" alt="XnanTool Logo" />
  <p>🚀 提升你的 ComfyUI 图像生成体验！🚀</p>
</div>

## 📝 简介

**XnanTool**初心是一个为 ComfyUI 打造的市面上插件因原作者不更，或者更新慢，导致功能不足的问题，这里提供了拓展方案。

## ✨ 功能特性

### 1、✨ 中文翻译优化

为了提升中文用户的使用体验，XnanTool 对所有节点的标题、描述、输入输出参数等进行了全面的中文本地化优化：

- 📘 **节点标题优化**
- 📝 **参数描述优化**
- 🎯 **功能说明优化**
- 🧩 **选项标签优化**
- 📋 **输出说明优化**

通过这些优化，即使是初次接触 ComfyUI 的中文用户也能快速上手并高效使用 XnanTool 的各项功能。

### 2、🤖 modelscope-魔搭社区api在comfyui调用

### 3、📏 预设功能：尺寸和提示词预设

### 4、🎯 YOLO和SAM功能

### 5、⚙️ 智能安装与配置管理

### 6、🎬 媒体处理功能

### 7、🖼️ 图片处理功能

### 8、🛠️ 实用工具扩展

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

### 🎨 魔搭API类节点
魔搭API类节点集成了阿里云魔搭平台的强大AI能力，提供了文生图、图像编辑、文本生成、视频反推、图片反推等多种功能。

有关魔搭API类节点的详细信息，请参阅 [魔搭API类节点说明](README_modelscope_api.md)。

### 🎯 YOLO类节点
YOLO类节点集成了先进的YOLOv8系列目标检测模型，提供了目标检测、图像裁切等功能，支持精确的目标识别和处理。

有关YOLO类节点的详细信息，请参阅 [YOLO和SAM类节点说明](README_yolo_and_sam.md)。

### 🖼️ 图像处理类节点
图像处理类节点提供了丰富的图像处理功能，包括图像加载、格式转换、尺寸调整等，满足各种图像处理需求。

有关图像处理类节点的详细信息，请参阅 [图像处理功能说明](README_image_processing.md)。

### 🧠 SAM类节点
SAM类节点集成了Meta的Segment Anything Model，提供了强大的图像分割功能，支持多种模型类型和加载方式。

有关SAM类节点的详细信息，请参阅 [YOLO和SAM类节点说明](README_yolo_and_sam.md)。

### 🎬 媒体处理类节点
媒体处理类节点提供了丰富的视频和图像处理功能，包括视频转GIF、视频转音频、图片转GIF、视频帧提取等。

有关媒体处理类节点的详细信息，请参阅 [媒体处理功能说明](README_media_processing.md)。

### 🦙 Ollama类节点
Ollama类节点集成了Ollama大语言模型服务，提供了连接配置、参数配置、文本生成和聊天对话等功能，支持与多种Ollama模型进行交互。

有关Ollama类节点的详细信息，请参阅 [Ollama类节点说明](README_ollama.md)。

### 🛠️ 实用工具类节点
实用工具类节点提供了一些辅助功能，包括值切换、随机执行、批量复制文件、文本处理等实用工具。

有关实用工具类节点的详细信息，请参阅 [实用工具类节点说明](README_practical_tools.md)。

## ⚠️ 注意事项

## 🛠️ 常见问题解决

## 📝 版本信息
- **当前版本**: v0.6.11
- **更新日期**: 2026年1月9日
- **更新日志**: 
  - 优化 TextToExcelNode：添加文件名冲突解决方案（覆盖、递增、跳过）
  - 优化 SaveImageNode：改进工作流信息保存机制
  - 新增 SaveTextNode：保存文本文件功能
  - 新增 MarkdownToExcelNode：MD转Excel功能
  - 新增实用工具节点：ToggleValueNode、StringMergeNode、RandomExecutionNode等 

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

## 鸣谢
- [comfyui-ollama](https://github.com/stavsap/comfyui-ollama) ：提供了Ollama大语言模型支持的基础框架，为XnanTool的Ollama类节点功能奠定了基础。


### 标签
#ComfyUI #AI绘画 #图像生成 #SDXL #Qwen #LoRA #工具插件 #AI创作 #目标检测 #图像分割 #YOLO #SAM #视频处理 #图片处理 #Ollama #大语言模型 #LLM #Z-Image-Turbo #FLUX2 #qwenimage #qwenimageedit #FLUX