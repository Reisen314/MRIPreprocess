# 文档索引

> 快速找到你需要的文档

---

## 📖 按用途分类

### 🚀 新手入门

| 文档 | 用途 | 阅读时间 |
|------|------|---------|
| [README.md](README.md) | 项目介绍和快速开始 | 5 分钟 |
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | 项目概览和核心概念 | 10 分钟 |
| [SETUP_TEMPLATES.md](SETUP_TEMPLATES.md) | 模板文件设置指南 | 5 分钟 |

**推荐阅读顺序：** README → PROJECT_OVERVIEW → SETUP_TEMPLATES

---

### 🔧 日常使用

| 文档 | 用途 | 何时查看 |
|------|------|---------|
| [config/pipeline_config.yaml](config/pipeline_config.yaml) | 配置参数 | 需要调整处理参数时 |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 故障排除 | 遇到错误时 |
| [DATA_STRUCTURE_REFERENCE.md](DATA_STRUCTURE_REFERENCE.md) | 数据结构参考 | 编写代码时 |

**常见场景：**
- 遇到错误 → TROUBLESHOOTING.md
- 修改参数 → pipeline_config.yaml
- 访问数据 → DATA_STRUCTURE_REFERENCE.md

---

### 👨‍💻 开发扩展

| 文档 | 用途 | 何时查看 |
|------|------|---------|
| [开发计划.md](开发计划.md) | 原始设计文档 | 了解设计思路时 |
| [CHANGELOG.md](CHANGELOG.md) | 开发日志 | 了解版本历史时 |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | 架构迁移指南 | 更新旧代码时 |
| [DATA_STRUCTURE_REFERENCE.md](DATA_STRUCTURE_REFERENCE.md) | 数据结构详解 | 开发新功能时 |

**开发流程：**
1. 查看 开发计划.md 了解整体架构
2. 参考 DATA_STRUCTURE_REFERENCE.md 编写代码
3. 更新 CHANGELOG.md 记录变更

---

## 📚 按文档类型分类

### 📘 用户文档

- **[README.md](README.md)** - 项目主文档
  - 项目介绍
  - 安装说明
  - 快速开始
  - 配置说明
  - 输出结构

- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - 项目概览
  - 核心价值
  - 技术架构
  - 关键设计
  - 使用场景
  - 性能特点

- **[SETUP_TEMPLATES.md](SETUP_TEMPLATES.md)** - 模板设置
  - 模板文件列表
  - 下载链接
  - 安装步骤
  - 验证方法

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障排除
  - 常见错误
  - 解决方案
  - 调试技巧
  - FAQ

---

### 📗 开发文档

- **[开发计划.md](开发计划.md)** - 原始设计
  - 项目目标
  - 技术栈选择
  - 架构设计
  - 处理步骤规范
  - 开发阶段规划

- **[CHANGELOG.md](CHANGELOG.md)** - 开发日志
  - 版本历史
  - 功能变更
  - Bug 修复
  - 性能改进
  - 未来计划

- **[DATA_STRUCTURE_REFERENCE.md](DATA_STRUCTURE_REFERENCE.md)** - 数据结构
  - ProcessingData 详解
  - 空间分离架构
  - 数据访问方式
  - 迁移指南
  - 常见错误

- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - 迁移指南
  - 架构变更说明
  - 迁移步骤
  - 代码对比
  - 注意事项

---

### 📙 配置文档

- **[config/pipeline_config.yaml](config/pipeline_config.yaml)** - 主配置
  - 通用设置
  - 各步骤配置
  - 算法参数
  - 输出设置

---

## 🔍 按问题查找

### "我想开始使用这个项目"
→ [README.md](README.md) → [SETUP_TEMPLATES.md](SETUP_TEMPLATES.md)

### "我遇到了错误"
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### "我想修改处理参数"
→ [config/pipeline_config.yaml](config/pipeline_config.yaml)

### "我想了解数据结构"
→ [DATA_STRUCTURE_REFERENCE.md](DATA_STRUCTURE_REFERENCE.md)

### "我想添加新功能"
→ [开发计划.md](开发计划.md) → [DATA_STRUCTURE_REFERENCE.md](DATA_STRUCTURE_REFERENCE.md)

### "我想了解版本历史"
→ [CHANGELOG.md](CHANGELOG.md)

### "我想了解整体架构"
→ [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### "我有旧代码需要更新"
→ [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

---

## 📊 文档完整性

| 类型 | 文档数量 | 完成度 |
|------|---------|--------|
| 用户文档 | 4 | ✅ 100% |
| 开发文档 | 4 | ✅ 100% |
| 配置文档 | 1 | ✅ 100% |
| 代码注释 | - | ⚠️ 80% |
| API 文档 | - | ❌ 0% |

---

## 🎯 推荐阅读路径

### 路径 1：快速上手（30 分钟）
1. README.md (5 分钟)
2. SETUP_TEMPLATES.md (5 分钟)
3. 运行测试 (10 分钟)
4. 处理样本 (10 分钟)

### 路径 2：深入理解（1 小时）
1. README.md (5 分钟)
2. PROJECT_OVERVIEW.md (10 分钟)
3. 开发计划.md (20 分钟)
4. DATA_STRUCTURE_REFERENCE.md (15 分钟)
5. CHANGELOG.md (10 分钟)

### 路径 3：开发扩展（2 小时）
1. PROJECT_OVERVIEW.md (10 分钟)
2. 开发计划.md (30 分钟)
3. DATA_STRUCTURE_REFERENCE.md (30 分钟)
4. 阅读源代码 (30 分钟)
5. 编写测试代码 (20 分钟)

---

## 📝 文档维护

### 更新频率

- **README.md**: 每个版本
- **CHANGELOG.md**: 每次重要变更
- **配置文件**: 按需更新
- **其他文档**: 按需更新

### 文档规范

- 使用 Markdown 格式
- 保持简洁清晰
- 提供代码示例
- 包含实际用例
- 定期审查更新

---

## 🔗 外部资源

### 依赖文档
- [ANTsPy Documentation](https://antspy.readthedocs.io/)
- [ANTsPyNet Documentation](https://github.com/ANTsX/ANTsPyNet)
- [YAML Specification](https://yaml.org/spec/)

### 相关项目
- [MDL-Net](https://github.com/...)
- [mri_preprocessing](https://github.com/...)

### 学习资源
- [MRI 预处理基础](https://...)
- [脑图像分析教程](https://...)

---

*最后更新：2024-01-22*
