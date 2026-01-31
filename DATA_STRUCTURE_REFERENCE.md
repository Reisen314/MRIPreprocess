# ProcessingData 数据结构参考

## 空间分离架构

ProcessingData 采用空间分离架构，明确区分 native space 和 template space 数据。

## 数据访问方式

### ❌ 旧方式（已废弃）
```python
data.primary_image
data.original_image
data.brain_mask
data.registered_image
data.transform_matrix
data.gm_probability
data.wm_probability
data.csf_probability
data.segmentation_labels
data.roi_features
```

### ✅ 新方式（当前）

#### Native Space（原始采集空间）
```python
data.native["image"]              # 当前处理的图像
data.native["original_image"]     # 原始输入图像（不变）
data.native["brain_mask"]         # 脑掩膜
data.native["segmentation_labels"] # 分割标签
data.native["gm_probability"]     # 灰质概率图
data.native["wm_probability"]     # 白质概率图
data.native["csf_probability"]    # 脑脊液概率图
```

#### Template Space（标准化空间）
```python
data.template["image"]            # 配准后的图像
data.template["brain_mask"]       # 变换后的脑掩膜
data.template["segmentation_labels"] # 变换后的分割标签
data.template["gm_probability"]   # 变换后的灰质概率图
data.template["wm_probability"]   # 变换后的白质概率图
data.template["csf_probability"]  # 变换后的脑脊液概率图
data.template["roi_labels"]       # Atlas 标签
data.template["roi_features"]     # 提取的 ROI 特征
```

#### Transforms（空间变换）
```python
data.transforms["native_to_template"]  # 前向变换矩阵
data.transforms["template_to_native"]  # 反向变换矩阵
```

#### Metadata（元数据）
```python
data.subject_id                   # 被试 ID
data.processing_steps             # 处理步骤列表
data.qc_metrics                   # 质量控制指标
```

## 各模块使用的空间

| 模块 | 输入空间 | 输出空间 | 说明 |
|------|---------|---------|------|
| Skull Stripping | Native | Native | 在原空间提取脑组织 |
| Segmentation | Native | Native | 在原空间做组织分割 |
| Registration | Native | Template | 配准并自动变换所有数据 |
| ROI Extraction | Template | Template | 在模板空间使用 atlas |
| Quality Control | Both | - | 根据需要访问两个空间 |

## 辅助方法

### 检查方法
```python
data.has_brain_extraction()  # 是否完成脑提取
data.has_registration()      # 是否完成配准
data.has_segmentation()      # 是否完成分割
```

### 空间变换方法
```python
# 将 native 空间的数据变换到 template 空间
data.transform_to_template(
    field_name="brain_mask",
    interpolator='nearestNeighbor'  # 或 'linear'
)
```

### 获取摘要
```python
summary = data.get_processing_summary()
# 返回：
# {
#     'subject_id': 'sub001',
#     'processing_steps': ['skull_stripping', 'segmentation', ...],
#     'has_brain_mask': True,
#     'has_registration': True,
#     'has_segmentation': True,
#     'qc_metrics': {...}
# }
```

## 处理流程示例

```python
# 1. 初始化（Pipeline 自动完成）
data = ProcessingData(original_image, "sub001")

# 2. Skull Stripping（在 native 空间）
data.native["image"] = brain_image
data.native["brain_mask"] = brain_mask

# 3. Segmentation（在 native 空间）
data.native["segmentation_labels"] = seg_labels
data.native["gm_probability"] = gm_prob
data.native["wm_probability"] = wm_prob
data.native["csf_probability"] = csf_prob

# 4. Registration（连接两个空间）
data.template["image"] = registered_image
data.transforms["native_to_template"] = fwd_transforms
# 自动变换所有 native 数据到 template 空间
data.template["brain_mask"] = ...
data.template["gm_probability"] = ...
# ... 等等

# 5. ROI Extraction（在 template 空间）
data.template["roi_features"] = roi_features

# 6. Quality Control（访问两个空间）
# 使用 native 空间计算 SNR
# 使用 template 空间计算配准质量
```

## 迁移指南

如果你有旧代码需要更新：

### 1. 简单属性访问
```python
# 旧代码
mask = data.brain_mask

# 新代码
mask = data.native["brain_mask"]  # 或 data.template["brain_mask"]
```

### 2. 属性赋值
```python
# 旧代码
data.brain_mask = new_mask

# 新代码
data.native["brain_mask"] = new_mask
```

### 3. 条件检查
```python
# 旧代码
if data.brain_mask is not None:
    ...

# 新代码
if data.native["brain_mask"] is not None:
    ...
```

### 4. 选择正确的空间
- 如果在 registration 之前：使用 `data.native`
- 如果在 registration 之后：根据需要选择
  - 需要原始分辨率：`data.native`
  - 需要标准空间（如使用 atlas）：`data.template`

## 常见错误

### AttributeError: 'ProcessingData' object has no attribute 'xxx'
**原因：** 使用了旧的属性名

**解决：** 使用新的字典访问方式
```python
# 错误
data.original_image

# 正确
data.native["original_image"]
```

### KeyError: 'xxx'
**原因：** 访问了不存在的字段

**解决：** 检查字段名拼写，或先检查是否存在
```python
if data.native.get("brain_mask") is not None:
    mask = data.native["brain_mask"]
```

### 空间混用
**原因：** 在错误的空间访问数据

**解决：** 确认当前处理步骤应该使用哪个空间
- Segmentation 之前：只有 native 空间有数据
- Registration 之后：两个空间都有数据
