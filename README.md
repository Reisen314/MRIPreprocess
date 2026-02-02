# MRI 预处理管道

基于 ANTs/ANTsPyNet 的医学图像预处理系统，采用空间分离架构和配置驱动设计，支持 MRI 和 PET 多模态处理。

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 特性

- 完整的预处理流程：从原始 T1 MRI 到 ROI 特征提取
- 多模态支持：支持 MRI + PET 联合处理（v1.1+）
- 空间分离架构：明确区分 Native 和 Template 空间，防止空间混用
- 配置驱动：通过 YAML 文件灵活控制所有处理参数
- 模块化设计：统一的数据容器和处理器接口
- 自动分类输出：中间结果、最终结果、质量报告分类存储
- 灵活扩展：支持多种算法和参数配置

---

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/Reisen314/MRIPreprocess.git
cd MRIPreprocess

# 安装依赖
pip install requirements.txt
```

### 准备模板文件

下载并放置必需的模板文件（详见 [SETUP_TEMPLATES.md](SETUP_TEMPLATES.md)）：
- `config/templates/MNI152_T1_1mm.nii.gz` - MNI152 模板
- `config/templates/AAL116_MNI.nii.gz` - AAL116 脑区模板

### 运行

```bash
# 处理单个 MRI 样本
python main.py --subject sub001 --mri data/sub001_T1.nii.gz

# 处理 MRI + PET（v1.1+）
python main.py --subject sub001 --mri data/sub001_T1.nii.gz --pet data/sub001_PET.nii.gz

# 使用自定义配置
python main.py --subject sub001 --mri data/sub001_T1.nii.gz --config custom_config.yaml

# 批量处理 MRI
python scripts/batch_process.py --input data/ --pattern "*_T1.nii.gz"

# 批量处理 MRI + PET
python scripts/batch_process.py --input data/ --pattern "*_T1.nii.gz" --pet-pattern "*_PET.nii.gz"
```

---

## 处理流程

### MRI 处理流程

```
原始 T1 MRI
    ↓
1. Skull Stripping (颅骨剥离) - Native Space
    ↓
2. Segmentation (组织分割) - Native Space
    ↓
3. Registration (配准) - Native → Template Space
    ↓
4. ROI Extraction (ROI 特征提取) - Template Space
    ↓
5. Quality Control (质量控制)
    ↓
最终结果 (MNI 标准空间)
```

### PET 处理流程（v1.1+）

```
原始 PET
    ↓
1. Registration to MRI (配准到 MRI) - Rigid
    ↓
2. Apply Brain Mask (应用 MRI 脑掩膜)
    ↓
3. Transform to MNI (应用 MRI→MNI 变换场)
    ↓
PET 在 MNI 标准空间
```

**关键特性：**
- PET 处理完全依赖 MRI 处理结果
- 使用 MRI 的脑掩膜和变换场，确保空间对齐
- PET 为可选参数，不影响 MRI 处理流程

### 各步骤详情

| 步骤 | 功能 | 算法 | 输出 |
|------|------|------|------|
| **Skull Stripping** | 脑组织提取 | ANTsPyNet / ANTs | 脑图像 + 脑掩膜 |
| **Segmentation** | 组织分割 | Atropos 3-class | CSF/GM/WM 概率图 |
| **Registration** | 空间标准化 | SyN / Affine / Rigid | MNI 空间图像 + 变换矩阵 |
| **PET Processing** | PET 预处理 | Rigid + Transform | PET MNI 空间图像 |
| **ROI Extraction** | 脑区特征提取 | AAL116 模板 | ROI 统计特征 |
| **Quality Control** | 质量评估 | 多维度指标 | QC 报告 |

---

## 输出结构

### MRI Only 模式

```
output/
└── subject_id/
    ├── intermediate/              # 中间结果 (Native 空间)
    │   ├── sub001_antspynet_skull_stripped.nii.gz
    │   ├── sub001_segmentation_labels.nii.gz
    │   ├── sub001_gm_probability.nii.gz
    │   ├── sub001_wm_probability.nii.gz
    │   ├── sub001_csf_probability.nii.gz
    │   ├── sub001_registered.nii.gz
    │   └── sub001_summary.txt
    │
    ├── final/                     # 最终结果 (MNI 空间) ⭐
    │   ├── sub001_T1_MNI.nii.gz
    │   ├── sub001_brain_mask_MNI.nii.gz
    │   ├── sub001_GM_probability_MNI.nii.gz
    │   ├── sub001_WM_probability_MNI.nii.gz
    │   ├── sub001_CSF_probability_MNI.nii.gz
    │   ├── sub001_segmentation_MNI.nii.gz
    │   ├── sub001_gm_features.npy
    │   ├── sub001_wm_features.npy
    │   └── sub001_final_summary.txt
    │
    ├── qc/                        # 质量控制
    │   └── sub001_qc_report.txt
    │
    └── logs/                      # 日志 (预留)
```

### MRI + PET 模式（v1.1+）

```
output/
└── subject_id/
    ├── intermediate/              # 中间结果
    │   ├── ... (MRI 中间结果)
    │   ├── sub001_PET_registered.nii.gz      # PET 配准到 MRI
    │   └── sub001_PET_skull_stripped.nii.gz  # PET 去颅骨
    │
    ├── final/                     # 最终结果 (MNI 空间) ⭐
    │   ├── ... (MRI 最终结果)
    │   ├── sub001_PET_MNI.nii.gz             # PET MNI 空间 ⭐
    │   ├── sub001_PET_skull_stripped.nii.gz  # PET 去颅骨
    │   └── sub001_final_summary.txt
    │
    ├── qc/
    │   └── sub001_qc_report.txt
    │
    └── logs/
```

**使用建议**：
- 用于分析：使用 final/ 目录中的 MNI 空间文件
- 用于调试：检查 intermediate/ 目录中的中间结果
- 质量检查：查看 qc/ 目录中的报告
- PET 分析：使用 final/sub001_PET_MNI.nii.gz，与 MRI 完美对齐

---

## 配置

主配置文件：`config/pipeline_config.yaml`

```yaml
# 通用配置
general:
  version: "1.1.0"
  save_intermediate: true

# 启用/禁用处理步骤
skull_stripping:
  enabled: true
  methods:
    antspynet:
      enabled: true
      model: "t1v1"

segmentation:
  enabled: true
  methods:
    atropos:
      enabled: true
      num_classes: 3

registration:
  enabled: true
  template: "config/templates/MNI152_T1_1mm.nii.gz"
  methods:
    syn:
      enabled: true

# PET 处理配置（v1.1+）
pet_processing:
  enabled: true
  registration_type: "Rigid"
  save_intermediate: true

roi_extraction:
  enabled: true
  atlas: "AAL116"
  atlas_path: "config/templates/AAL116_MNI.nii.gz"

quality_control:
  enabled: true
  generate_report: true
```

---

## 测试

```bash
# 测试配置加载和 Pipeline 初始化
python test_pipeline.py

# 测试基础处理器（无需 ANTsPy）
python test_base_processor.py
```

---

## 文档

| 文档 | 说明 |
|------|------|
| [CHANGELOG.md](development_document/CHANGELOG.md) | 开发日志和版本历史 |
| [DATA_STRUCTURE_REFERENCE.md](DATA_STRUCTURE_REFERENCE.md) | 数据结构参考 |
| [TROUBLESHOOTING.md](development_document/TROUBLESHOOTING.md) | 故障排除指南 |
| [SETUP_TEMPLATES.md](SETUP_TEMPLATES.md) | 模板文件设置 |
| [MIGRATION_GUIDE.md](development_document/MIGRATION_GUIDE.md) | 架构迁移指南 |
| [PET_SUPPORT_PLAN.md](development_document/PET_SUPPORT_PLAN.md) | PET 支持开发计划 |
| [开发计划.md](development_document/开发计划.md) | 原始开发计划 |

---

## 项目结构

```
MRIPreprocess/
├── config/                        # 配置和模板
│   ├── pipeline_config.yaml       # 主配置文件
│   └── templates/                 # MNI152, AAL116 等模板
│
├── src/
│   ├── preprocessing/             # 预处理模块
│   │   ├── processing_data.py     # 数据容器（空间分离）
│   │   ├── base_processor.py      # 处理器基类
│   │   ├── skull_stripping.py     # 颅骨剥离
│   │   ├── segmentation.py        # 组织分割
│   │   ├── registration.py        # 配准
│   │   ├── pet_processor.py       # PET 处理（v1.1+）
│   │   ├── roi_extraction.py      # ROI 提取
│   │   └── quality_control.py     # 质量控制
│   ├── utils/
│   │   └── file_manager.py        # 文件管理
│   └── pipeline.py                # 主管道编排器
│
├── scripts/
│   ├── process_single_subject.py  # 单样本处理
│   └── batch_process.py           # 批量处理
│
├── development_document/          # 开发文档
│   ├── CHANGELOG.md
│   ├── PET_SUPPORT_PLAN.md
│   └── ...
│
├── main.py                        # 命令行入口
├── test_pipeline.py               # 测试脚本
└── requirements.txt               # 依赖列表
```

---

## 核心概念

### 空间分离架构

```python
ProcessingData:
  native:      # 原始采集空间
    - image, brain_mask
    - segmentation, probabilities
  
  template:    # MNI 标准空间
    - image, brain_mask
    - segmentation, probabilities
    - roi_features
  
  pet:         # PET 数据（v1.1+）
    - original (原始空间)
    - registered_to_mri (MRI native 空间)
    - skull_stripped (去颅骨)
    - mni (MNI 标准空间)
  
  transforms:  # 空间变换
    - native_to_template
    - template_to_native
```

**优势**：
- 防止空间混用错误
- 明确数据所在空间
- 支持双向工作流
- 支持多模态数据管理

### PET 处理原理（v1.1+）

PET 处理依赖 MRI 处理结果，确保空间对齐：

1. **PET → MRI Native**：刚体配准（fixed=MRI）
2. **应用脑掩膜**：使用 MRI 的脑掩膜
3. **PET → MNI**：应用 MRI→MNI 的变换场

**数学表示：**
```
PET_mni = Transform_mri→mni(Transform_pet→mri(PET_original))
```

**优势**：
- 保证 PET 和 MRI 在 MNI 空间完美对齐
- 避免重复计算配准
- 复用 MRI 的脑掩膜和变换场

---

## 性能

**典型处理时间**（单个样本）：

| 步骤 | MRI Only | MRI + PET |
|------|----------|-----------|
| Skull Stripping | ~30-60秒 | ~30-60秒 |
| Segmentation | ~2-5分钟 | ~2-5分钟 |
| Registration | ~5-10分钟 | ~5-10分钟 |
| PET Processing | - | ~1-2分钟 |
| ROI Extraction | ~10-30秒 | ~10-30秒 |
| Quality Control | ~5-10秒 | ~5-10秒 |
| **总计** | **~8-16分钟** | **~9-18分钟** |

**输出大小：**
- MRI Only: ~45 MB per subject
- MRI + PET: ~60 MB per subject

---

## 常见问题

### 模板文件未找到
```
FileNotFoundError: Template file not found
```
**解决**：参考 [SETUP_TEMPLATES.md](SETUP_TEMPLATES.md) 下载模板文件

### 空间不匹配错误
```
ValueError: operands could not be broadcast together
```
**解决**：已修复！使用最新版本的空间分离架构

### PET 处理相关问题

**Q: PET 是必需的吗？**  
A: 不是。PET 是可选参数，不提供时行为与 v1.0 完全一致。

**Q: PET 和 MRI 必须来自同一被试吗？**  
A: 是的。PET 会配准到同一被试的 MRI，使用 MRI 的脑掩膜和变换场。

**Q: 可以只处理 PET 吗？**  
A: 不可以。PET 处理依赖 MRI 处理结果，必须同时提供 MRI。

### 更多问题
参考 [TROUBLESHOOTING.md](development_document/TROUBLESHOOTING.md)

---

## 开发

### 添加新的处理器

1. 继承 `BaseProcessor`（简单处理器）或独立实现（复杂处理器）
2. 实现 `run(data, output_dir)` 方法
3. 在 `Pipeline` 中注册
4. 在配置文件中添加配置项

### 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## 版本历史

- **v1.1.0** (2024-02) - 添加 PET 多模态支持
- **v1.0.0** (2024-01) - 初始版本，MRI 预处理管道

---

## 许可证

MIT License

---

## 致谢

本项目融合了以下项目的优秀设计：
- **MDL-Net** - 先进的技术栈
- **mri_preprocessing** - 优秀的架构模式

---

## 联系

如有问题或建议，请提交 Issue。

---

*最后更新：2024-02-02 | 版本：v1.1.0*
