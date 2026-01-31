# 开发日志

## 项目概述

MRI 预处理管道 - 基于 ANTs/ANTsPyNet 的医学图像预处理系统，采用配置驱动和空间分离架构。

---

## v1.0.0 - 2024-01-22

### 🎉 初始版本发布

#### ✨ 核心功能

**1. 空间分离架构**
- 实现 Native Space 和 Template Space 的明确分离
- 防止空间混用导致的处理错误
- 自动空间变换功能

**2. 完整的预处理流程**
- Skull Stripping（颅骨剥离）
  - ANTsPyNet 深度学习方法
  - ANTs 传统方法
- Segmentation（组织分割）
  - Atropos 3类分割（CSF/GM/WM）
  - Fallback 简单分割
- Registration（配准）
  - SyN 非线性配准
  - Affine 仿射配准
  - Rigid 刚体配准
- ROI Extraction（ROI 特征提取）
  - 支持 AAL116 脑区模板
  - 提取 GM/WM 统计特征
- Quality Control（质量控制）
  - 组织体积计算
  - 配准质量评估

**3. 配置驱动系统**
- YAML 配置文件
- 灵活的算法选择
- 参数可配置

**4. 文件管理**
- 自动目录创建
- 分类输出（intermediate/final/qc）
- 清晰的文件命名

---

### 🔧 技术实现

#### 数据结构
```python
ProcessingData:
  - native: {image, brain_mask, segmentation, probabilities}
  - template: {image, brain_mask, segmentation, probabilities, roi_features}
  - transforms: {native_to_template, template_to_native}
```

#### 处理顺序
```
skull_stripping (native) 
  → segmentation (native) 
  → registration (native → template) 
  → roi_extraction (template) 
  → quality_control (both)
```

#### 关键设计决策

**1. Segmentation 在 Registration 之前**
- 原因：避免 image 和 mask 空间不匹配
- 优势：在原空间分割精度更高
- 实现：Registration 自动变换所有 native 数据到 template 空间

**2. 就地修改（In-place Modification）**
- 所有处理器修改同一个 ProcessingData 对象
- 优势：内存效率高，适合大型医学图像
- 实现：外层方法返回对象（支持链式调用），内层方法直接修改

**3. 混合处理器架构**
- 简单处理器：继承 BaseProcessor（如 SkullStripping）
- 复杂处理器：独立实现（如 Registration, Segmentation）
- 优势：代码复用与灵活性的平衡

---

### 🐛 已修复的问题

#### 1. Atropos 空间不匹配错误
**问题：**
```
ValueError: operands could not be broadcast together with shapes (182,218,182) (192,192,160)
```

**原因：**
- Segmentation 在 Registration 之后执行
- Image 已配准到模板空间，但 mask 仍在原空间

**解决方案：**
- 调整处理顺序：Segmentation → Registration
- 实现空间分离架构
- Registration 自动变换所有数据

#### 2. 模板文件加载失败
**问题：**
```
AttributeError: 'NoneType' object has no attribute 'numpy'
```

**原因：**
- 模板文件不存在时静默失败
- 后续使用 None 对象导致崩溃

**解决方案：**
- 添加文件存在性检查
- 提供清晰的错误信息和解决建议
- 区分必需和可选的模板文件

#### 3. 旧属性引用
**问题：**
```
AttributeError: 'ProcessingData' object has no attribute 'original_image'
```

**原因：**
- 重构为空间分离架构后，遗漏更新某些引用

**解决方案：**
- 全面检查并更新所有旧属性引用
- 创建数据结构参考文档

---

### 📁 输出结构

```
output/
└── subject_id/
    ├── intermediate/     # Native 空间中间结果
    ├── final/           # MNI 空间最终结果
    ├── qc/              # 质量控制报告
    └── logs/            # 日志（预留）
```

---

### 📚 文档

- `README.md` - 项目概述和快速开始
- `CHANGELOG.md` - 开发日志（本文件）
- `DATA_STRUCTURE_REFERENCE.md` - 数据结构参考
- `TROUBLESHOOTING.md` - 故障排除指南
- `SETUP_TEMPLATES.md` - 模板文件设置指南
- `MIGRATION_GUIDE.md` - 架构迁移指南
- `开发计划.md` - 原始开发计划

---

### 🎯 性能指标

**测试环境：**
- 单个 T1 MRI 样本
- 图像尺寸：~182×218×182

**处理时间：**
- Skull Stripping: ~30-60秒
- Segmentation: ~2-5分钟
- Registration: ~5-10分钟
- ROI Extraction: ~10-30秒
- Quality Control: ~5-10秒
- **总计：** ~8-16分钟

**输出文件：**
- Intermediate: ~15 MB
- Final: ~30 MB
- Total: ~45 MB per subject

---

### ✅ 验收标准

- [x] 所有处理步骤成功执行
- [x] 无空间不匹配错误
- [x] Atropos 分割正常工作
- [x] ROI 特征成功提取
- [x] 文件正确分类到各目录
- [x] 组织体积在正常范围
- [x] 配置驱动系统工作正常
- [x] 错误信息清晰友好

---

### 🚀 未来计划

#### 短期（v1.1.0）
- [ ] 完善 QC 指标（SNR, Registration MI）
- [ ] 添加日志系统（Python logging）
- [ ] 改进错误恢复机制
- [ ] 添加进度条显示

#### 中期（v1.2.0）
- [ ] 并行处理支持
- [ ] 可视化输出（分割结果叠加图）
- [ ] 更多脑区模板（Brodmann, Schaefer）
- [ ] 配置验证和建议

#### 长期（v2.0.0）
- [ ] MDL-Net 对接
- [ ] Web 界面
- [ ] 数据库管理
- [ ] 版本管理系统
- [ ] 多模态支持（T2, FLAIR）

---

### 🙏 致谢

本项目融合了以下项目的优秀设计：
- **MDL-Net**: 先进的技术栈（ANTs, ANTsPyNet）
- **mri_preprocessing**: 优秀的架构模式（配置驱动，模块化设计）

---

### 📝 开发笔记

#### 关键学习点

1. **医学图像处理的空间概念至关重要**
   - Native space vs Template space
   - 空间变换的时机和方法
   - 插值方法的选择（nearestNeighbor vs linear）

2. **错误处理的重要性**
   - 清晰的错误信息比静默失败好得多
   - 提供解决方案建议
   - 区分致命错误和警告

3. **架构设计的权衡**
   - 代码复用 vs 灵活性
   - 内存效率 vs 代码简洁
   - 配置驱动 vs 硬编码

4. **文档的价值**
   - 好的文档节省大量调试时间
   - 数据结构参考文档特别重要
   - 故障排除指南提升用户体验

---

### 📊 项目统计

**代码量：**
- Python 文件：~15 个
- 总代码行数：~2000 行
- 配置文件：1 个
- 文档文件：7 个

**测试覆盖：**
- 单元测试：待添加
- 集成测试：手动测试通过
- 端到端测试：成功处理真实数据

**依赖：**
- antspyx
- antspynet
- pyyaml
- numpy

---

## 版本历史

### v1.0.0 (2024-01-22)
- 初始版本发布
- 完整的预处理流程
- 空间分离架构
- 配置驱动系统

---

*最后更新：2026-01-22*
