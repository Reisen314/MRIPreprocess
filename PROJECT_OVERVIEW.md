# 项目概览

## 一句话介绍

基于 ANTs/ANTsPyNet 的 MRI 预处理管道，采用空间分离架构，从原始 T1 MRI 到 ROI 特征提取的完整解决方案。

---

## 核心价值

### 🎯 解决的问题

1. **空间混用** - 传统 pipeline 容易混淆 native 和 template 空间
2. **配置复杂** - 参数硬编码，难以调整和复现
3. **输出混乱** - 中间结果和最终结果混在一起
4. **错误难查** - 错误信息不清晰，难以定位问题

### ✨ 我们的方案

1. **空间分离架构** - 明确区分 native 和 template 空间
2. **配置驱动** - YAML 配置文件，参数可追溯
3. **分类输出** - intermediate/final/qc 目录清晰分类
4. **友好错误** - 清晰的错误信息和解决建议

---

## 技术架构

### 数据流

```
Input (Native Space)
    ↓
[Skull Stripping] → brain_mask
    ↓
[Segmentation] → CSF/GM/WM probabilities
    ↓
[Registration] → Transform to MNI
    ↓ (自动变换所有数据)
Template Space
    ↓
[ROI Extraction] → Features
    ↓
[Quality Control] → Report
    ↓
Output (MNI Space)
```

### 核心组件

```
ProcessingData (数据容器)
    ├── native: {原始空间数据}
    ├── template: {标准空间数据}
    └── transforms: {空间变换矩阵}

Pipeline (管道编排器)
    ├── 加载配置
    ├── 初始化处理器
    ├── 按序执行
    └── 保存结果

Processors (处理器)
    ├── SkullStripping
    ├── Segmentation
    ├── Registration
    ├── ROIExtraction
    └── QualityControl
```

---

## 关键设计

### 1. 空间分离

**问题：** 传统方式容易混用不同空间的数据

**解决：**
```python
# ❌ 旧方式 - 不知道在哪个空间
data.brain_mask

# ✅ 新方式 - 明确空间
data.native["brain_mask"]      # 原空间
data.template["brain_mask"]    # 模板空间
```

### 2. 处理顺序

**问题：** Segmentation 在 Registration 后导致空间不匹配

**解决：**
```
旧顺序: skull_stripping → registration → segmentation ❌
新顺序: skull_stripping → segmentation → registration ✅
```

### 3. 自动变换

**问题：** 手动变换容易遗漏

**解决：**
```python
# Registration 自动变换所有 native 数据
registration.run(data)
# 自动完成：
# - data.template["brain_mask"] = transform(data.native["brain_mask"])
# - data.template["gm_probability"] = transform(data.native["gm_probability"])
# - ...
```

---

## 使用场景

### 场景 1：研究分析

```bash
# 处理所有被试
python scripts/batch_process.py --input data/ --pattern "*_T1.nii.gz"

# 使用 final/ 目录中的 MNI 空间数据进行统计分析
```

**输出：** 所有被试在标准空间，可直接比较

### 场景 2：方法开发

```bash
# 处理单个样本
python main.py --subject test --mri test_data.nii.gz

# 检查 intermediate/ 目录调试每个步骤
```

**输出：** 完整的中间结果，便于调试

### 场景 3：质量控制

```bash
# 批量处理后检查质量
ls output/*/qc/*.txt

# 筛选低质量数据
grep "warning" output/*/qc/*.txt
```

**输出：** 独立的 QC 报告，便于批量检查

---

## 性能特点

### 时间

- 单个样本：~8-16 分钟
- 批量处理：支持串行（稳定）
- 未来：支持并行（规划中）

### 空间

- 输入：~10-20 MB (原始 T1)
- 输出：~45 MB (完整结果)
- 内存：~2-4 GB (处理时)

### 可扩展性

- ✅ 添加新处理器：继承 BaseProcessor
- ✅ 添加新算法：配置文件中启用
- ✅ 添加新模板：更新配置路径

---

## 与其他工具对比

| 特性 | 本项目 | FSL | SPM | FreeSurfer |
|------|--------|-----|-----|------------|
| 空间分离 | ✅ | ❌ | ❌ | ⚠️ |
| 配置驱动 | ✅ | ⚠️ | ❌ | ❌ |
| Python API | ✅ | ❌ | ⚠️ | ❌ |
| 易于扩展 | ✅ | ❌ | ❌ | ❌ |
| 学习曲线 | 低 | 中 | 高 | 高 |
| 处理速度 | 快 | 快 | 中 | 慢 |

---

## 依赖关系

```
Python 3.7+
    ├── antspyx (核心处理)
    ├── antspynet (深度学习)
    ├── pyyaml (配置解析)
    └── numpy (数据处理)

外部文件
    ├── MNI152_T1_1mm.nii.gz (配准模板)
    └── AAL116_MNI.nii.gz (脑区模板)
```

---

## 开发路线图

### ✅ v1.0.0 (当前)
- 完整的预处理流程
- 空间分离架构
- 配置驱动系统
- 分类输出

### 🚧 v1.1.0 (计划中)
- 完善 QC 指标
- 日志系统
- 进度条显示
- 错误恢复

### 💡 v1.2.0 (规划中)
- 并行处理
- 可视化输出
- 更多脑区模板
- 配置验证

### 🌟 v2.0.0 (未来)
- MDL-Net 对接
- Web 界面
- 数据库管理
- 多模态支持

---

## 快速链接

- **快速开始**: [README.md](README.md)
- **开发日志**: [CHANGELOG.md](CHANGELOG.md)
- **数据结构**: [DATA_STRUCTURE_REFERENCE.md](DATA_STRUCTURE_REFERENCE.md)
- **故障排除**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **模板设置**: [SETUP_TEMPLATES.md](SETUP_TEMPLATES.md)

---

## 贡献者

欢迎贡献！请查看 [README.md](README.md) 了解如何参与。

---

*最后更新：2024-01-22*
