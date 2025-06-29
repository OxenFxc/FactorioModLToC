# 异星工厂模组汉化工具 (FactorioModLToC)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows-blue)](https://www.microsoft.com/windows)

一个专为异星工厂(Factorio)游戏模组设计的强大汉化工具，支持批量处理、AI翻译工作流、实时编辑和备份管理。**专为Windows系统优化**。

## ✨ 功能特性

### 🎯 **核心功能**
- 📁 **批量扫描模组**：自动扫描指定目录下的所有ZIP模组文件
- 🔍 **实时搜索**：支持模组名称、文件名、内部名称的快速搜索
- ✏️ **可视化编辑**：左右/上下对照编辑界面，支持拖拽调整比例
- 💾 **直接保存到ZIP**：无需解压缩，直接编辑ZIP文件内容

### 🤖 **AI翻译工作流**
- 📤 **文件导出**：导出源文件和目标文件，便于AI翻译
- 📥 **翻译导入**：支持从本地文件导入翻译结果
- 🔄 **批量处理**：支持多个语言文件的批量处理
- ⚙️ **配置管理**：导出路径和设置的持久化保存

### 🛡️ **安全特性**
- 💾 **自动备份**：编辑前自动创建备份文件(.zip.backup)
- 🔄 **备份还原**：双击备份文件可选择还原
- 🗑️ **备份管理**：右键删除不需要的备份文件
- ⚠️ **安全提示**：操作前的确认对话框

### 🎨 **用户体验**
- 🖱️ **双击操作**：双击模组直接进入编辑界面
- 📊 **状态显示**：实时显示操作状态和进度
- 🔧 **个性化设置**：可调整窗口布局和界面比例
- 🌍 **多语言支持**：支持所有Factorio支持的语言

## 🚀 快速开始

### 📋 系统要求
- **Windows 10/11** 操作系统
- Python 3.8 或更高版本
- tkinter GUI库（通常随Python安装）

### 📦 安装

1. **克隆仓库**
```bash
git clone https://github.com/your-username/factorio-mod-localizer.git
cd factorio-mod-localizer
```

2. **安装依赖**
```
pip install -r requirements.txt
```

3. **运行程序**
```
python factorio_mod_localizer.py
```

或**推荐**直接双击 `启动汉化工具.bat` 启动脚本

### 🎮 使用方法

1. **设置模组目录**
   - 默认扫描：`C:\Users\用户名\AppData\Roaming\Factorio\mods`
   - 或点击"浏览"选择自定义目录

2. **扫描模组**
   - 点击"扫描模组"按钮
   - 等待扫描完成，查看模组列表

3. **搜索模组**
   - 在搜索框中输入关键词
   - 支持模组名称、文件名、内部名称搜索

4. **编辑模组**
   - 双击要编辑的模组
   - 选择源语言和目标语言
   - 选择要编辑的文件
   - 在可调整大小的编辑器中进行翻译

5. **AI翻译工作流**
   - 点击"导出源文件"获取原文
   - 使用AI工具翻译
   - 点击"从本地导入"导入翻译结果
   - 保存到ZIP文件

## 📁 项目结构

```
factorio-mod-localizer/
├── factorio_mod_localizer.py    # 主程序文件
├── requirements.txt             # Python依赖
├── README.md                   # 项目说明
├── LICENSE                     # MIT许可证
```

## 🔧 配置文件

程序会自动创建 `factorio_localizer_config.json` 配置文件，包含：
- 模组目录路径
- 默认导出路径
- 窗口布局设置
- 其他用户偏好设置

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 这个项目
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建一个 Pull Request

### 开发指南
- 代码应遵循PEP 8规范
- 添加必要的注释和文档
- 测试新功能确保其正常工作
- 更新README.md（如果需要）

## 📝 版本历史

### v1.3.0 (当前版本)
- ✅ 可拖拽调整编辑框大小比例
- ✅ 增大窗口尺寸提供更好的工作空间
- ✅ 优化布局权重分配
- ✅ 改进用户体验

### v1.2.0
- ✅ 添加实时搜索功能
- ✅ 备份文件管理（显示、还原、删除）
- ✅ 保存后自动返回模组列表
- ✅ 改进备份文件处理逻辑

### v1.1.0
- ✅ 修复加载文件按钮问题
- ✅ 新增文件导出功能
- ✅ 新增本地文件导入功能
- ✅ 改进错误处理机制

### v1.0.0
- ✅ 基础模组扫描和编辑功能
- ✅ ZIP文件直接编辑
- ✅ 自动备份功能
- ✅ 基本GUI界面

## 🐛 问题反馈

如果您遇到任何问题或有功能建议，请：
1. 查看 [Issues](https://github.com/your-username/factorio-mod-localizer/issues) 是否已有相关问题
2. 如果没有，请创建新的Issue，详细描述问题或建议

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢异星工厂社区的支持
- 感谢所有贡献者和测试人员
- 特别感谢AI翻译工具提供的便利

## 🔗 相关链接

- [异星工厂官网](https://factorio.com/)
- [异星工厂模组门户](https://mods.factorio.com/)
- [Python tkinter文档](https://docs.python.org/3/library/tkinter.html)

---

**如果这个工具对您有帮助，请给个⭐Star⭐支持一下！** 
