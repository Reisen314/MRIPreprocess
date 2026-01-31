# 空间分离架构迁移指南

## 概述

重构了 `ProcessingData` 类，采用空间分离架构，明确区分 native space 和 template space 数据，从根本上避免空间混用问题。

## 主要变更

### 1. ProcessingData 数据结构

**之前：**
```python
data.primary_image
data.brain_mask
data.gm_probability
data.registered_image
```

**现在：**
```python
# Native space (原始采集空间)
data.native["image"]
data.native["brain_mask"]
data.native["gm_probability"]

# Template space (标准化空间)
data.template["image"]
data.template["brain_mask"]
data.template["gm_probability"]

# Transforms (空间变换)
data.transforms["native_to_template"]
data.transforms["template_to_native"]
```

### 2. Pipeline 步骤顺序调整

**之前：** skull_stripping → registration → segmentation → roi_extraction

**现在：** skull_stripping → **segmentation** → **registration** → roi_extraction

**原因：** 在原空间做分割，避免 image 和 mask 空间不匹配问题

### 3. 各模块空间使用

| 模块 | 操作空间 | 说明 |
|------|---------|------|
| Skull Stripping | Native | 在原空间提取脑组织 |
| Segmentation | Native | 在原空间做组织分割 |
| Registration | Native → Template | 配准并自动变换所有数据 |
| ROI Extraction | Template | 在模板空间使用 atlas |
| Quality Control | Both | 根据需要访问两个空间 |

## 关键改进

1. **空间明确性**：代码中明确标识数据所在空间
2. **自动变换**：Registration 自动将所有 native 数据变换到 template 空间
3. **防止错误**：编译时就能发现空间使用错误
4. **灵活性**：支持同时保留两个空间的数据

## 迁移检查清单

- [x] ProcessingData 重构
- [x] Skull Stripping 更新
- [x] Segmentation 更新
- [x] Registration 更新（含自动变换）
- [x] ROI Extraction 更新
- [x] Quality Control 更新
- [x] Pipeline 步骤顺序调整
- [x] 语法检查通过

## 测试建议

运行完整 pipeline 测试：
```bash
python main.py
```

预期结果：
- Atropos 应该能正常工作（不再有空间不匹配错误）
- 所有中间结果正确保存
- 最终输出在 template 空间
