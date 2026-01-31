# 故障排除指南

## 常见错误及解决方案

### 1. Atlas/Template 文件未找到

**错误信息：**
```
FileNotFoundError: Atlas file not found: config/templates/AAL116_MNI.nii.gz
FileNotFoundError: Template file not found: config/templates/MNI152_T1_1mm.nii.gz
```

**原因：** 模板文件未下载或路径不正确

**解决方案：**

#### 方案A：下载模板文件（推荐）
参考 `SETUP_TEMPLATES.md` 下载并放置模板文件

#### 方案B：禁用相关功能
如果暂时不需要某些功能，可以在配置文件中禁用：

```yaml
# config/pipeline_config.yaml

# 禁用配准（如果没有 MNI152 模板）
registration:
  enabled: false

# 禁用 ROI 提取（如果没有 Atlas）
roi_extraction:
  enabled: false
```

#### 方案C：使用自己的模板
修改配置文件指向你自己的模板：

```yaml
registration:
  template: "path/to/your/template.nii.gz"

roi_extraction:
  atlas_path: "path/to/your/atlas.nii.gz"
```

---

### 2. 空间不匹配错误

**错误信息：**
```
ValueError: operands could not be broadcast together with shapes (182,218,182) (192,192,160)
```

**原因：** 图像和掩膜在不同空间

**解决方案：** 
✅ 已修复！使用最新的空间分离架构，这个问题已经解决。

---

### 3. ANTsPy 未安装

**错误信息：**
```
ImportError: ANTsPy required for ...
```

**解决方案：**
```bash
pip install antspyx antspynet
```

---

### 4. 内存不足

**错误信息：**
```
MemoryError: Unable to allocate ...
```

**解决方案：**
1. 关闭其他程序释放内存
2. 禁用 `save_intermediate` 减少内存占用
3. 一次处理一个样本，不要批量处理

```yaml
general:
  save_intermediate: false
```

---

### 5. 配准失败

**错误信息：**
```
RuntimeError: Registration failed
```

**解决方案：**
1. 检查输入图像质量
2. 尝试更简单的配准方法：

```yaml
registration:
  methods:
    syn:
      enabled: false
    affine:
      enabled: true  # 使用更快的仿射配准
```

---

### 6. Atropos 分割失败

**错误信息：**
```
Atropos exited with non-zero status
```

**解决方案：**
✅ 已有 fallback 机制！会自动切换到简单分割方法。

如果仍然失败，检查：
1. 脑提取是否成功（brain_mask 是否正确）
2. 图像质量是否足够好

---

## 调试技巧

### 1. 启用详细输出
代码已经包含详细的 print 输出，观察每个步骤的执行情况

### 2. 检查中间结果
```yaml
general:
  save_intermediate: true
```
查看 `output/subject_id/` 目录中的中间文件

### 3. 逐步测试
先禁用所有步骤，然后逐个启用：

```yaml
skull_stripping:
  enabled: true
segmentation:
  enabled: false
registration:
  enabled: false
roi_extraction:
  enabled: false
quality_control:
  enabled: false
```

### 4. 使用测试脚本
```bash
python test_pipeline.py  # 测试配置加载
```

---

## 获取帮助

如果以上方案都无法解决问题：

1. 检查 `output/subject_id/` 目录中的日志
2. 记录完整的错误信息
3. 检查输入数据格式是否正确（NIfTI 格式）
4. 确认 Python 版本 >= 3.7
