# 模板文件设置指南

## 必需的模板文件

运行完整 pipeline 需要以下模板文件：

### 1. MNI152 模板（用于配准）

**文件路径：** `config/templates/MNI152_T1_1mm.nii.gz`

**下载方式：**

**选项 A：从 FSL 下载**
```bash
# 如果已安装 FSL
cp $FSLDIR/data/standard/MNI152_T1_1mm.nii.gz config/templates/
```

**选项 B：从 TemplateFlow 下载**
```bash
pip install templateflow
python -c "from templateflow import api; api.get('MNI152NLin2009cAsym', resolution=1, suffix='T1w', extension='nii.gz')"
# 然后复制到 config/templates/MNI152_T1_1mm.nii.gz
```

**选项 C：直接下载**
- 访问：https://www.bic.mni.mcgill.ca/ServicesAtlases/ICBM152NLin2009
- 或：https://nist.mni.mcgill.ca/mni-icbm152-non-linear-6th-generation-symmetric-average-brain-stereotaxic-registration-model/

### 2. AAL116 Atlas（用于 ROI 提取）

**文件路径：** `config/templates/AAL116_MNI.nii.gz`

**下载方式：**

**选项 A：从 SPM 下载**
- 访问：https://www.gin.cnrs.fr/en/tools/aal/
- 下载 AAL atlas
- 将 AAL116 版本重命名为 `AAL116_MNI.nii.gz`

**选项 B：使用 nilearn**
```bash
pip install nilearn
python -c "from nilearn import datasets; atlas = datasets.fetch_atlas_aal(); print(atlas.maps)"
# 复制到 config/templates/AAL116_MNI.nii.gz
```

## 快速设置

### 创建模板目录
```bash
mkdir -p config/templates
```

### 验证文件
```bash
# 检查文件是否存在
ls -lh config/templates/
```

应该看到：
```
MNI152_T1_1mm.nii.gz
AAL116_MNI.nii.gz
```

## 临时解决方案：禁用需要模板的步骤

如果暂时无法获取模板文件，可以在配置中禁用相关步骤：

**编辑 `config/pipeline_config.yaml`：**

```yaml
# 禁用配准
registration:
  enabled: false  # 改为 false

# 禁用 ROI 提取
roi_extraction:
  enabled: false  # 改为 false
```

这样可以只运行：
- Skull Stripping（颅骨剥离）
- Segmentation（组织分割，在 native 空间）
- Quality Control（质量控制，部分功能）

## 测试模板加载

运行测试脚本验证模板是否正确加载：

```bash
python test_pipeline.py
```

如果模板文件正确，应该看到：
```
Loading template: MNI152_T1_1mm.nii.gz
Template loaded successfully: shape (...)
```

## 常见问题

### Q: 模板文件太大怎么办？
A: MNI152 1mm 模板约 8MB，AAL atlas 约 2MB，都不算大。如果空间有限，可以使用 2mm 版本。

### Q: 可以使用其他模板吗？
A: 可以！只需修改配置文件中的路径：
```yaml
registration:
  template: "path/to/your/template.nii.gz"

roi_extraction:
  atlas_path: "path/to/your/atlas.nii.gz"
```

### Q: 如何验证模板文件是否正确？
A: 使用 ANTsPy 加载测试：
```python
import ants
template = ants.image_read('config/templates/MNI152_T1_1mm.nii.gz')
print(f"Shape: {template.shape}")
print(f"Spacing: {template.spacing}")
```

## 下一步

模板文件准备好后，运行完整 pipeline：

```bash
python main.py --subject test --mri path/to/your/T1.nii.gz
```
