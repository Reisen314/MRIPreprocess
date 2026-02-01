# PET处理支持开发计划

## 版本信息
- 当前版本: v1.0.0 (MRI预处理)
- 开发分支: feature/pet-support
- 目标版本: v1.1.0 (MRI + PET多模态预处理)

## 设计原则

### 核心理念
PET处理完全依赖MRI处理结果，作为MRI pipeline的集成部分而非独立模块。

### 关键原则
1. 向后兼容：PET作为可选参数，不影响现有MRI处理流程
2. 依赖复用：使用MRI的脑掩膜和变换场，避免重复计算
3. 空间清晰：明确的空间层次管理，防止空间混淆
4. 处理顺序：PET处理必须在MRI registration之后执行

## PET处理流程

### 空间转换路径
```
PET原始空间
    ↓ (刚体配准, fixed=MRI native)
PET在MRI native空间
    ↓ (应用MRI脑掩膜)
PET去颅骨
    ↓ (应用MRI→MNI变换场)
PET在MNI标准空间
```

### 依赖关系
- PET配准依赖：MRI native空间图像 (data.native["image"])
- PET去颅骨依赖：MRI脑掩膜 (data.native["brain_mask"])
- PET标准化依赖：MRI→MNI变换场 (data.transforms["native_to_template"])

## 实施方案

### 1. 数据结构扩展

**文件**: `src/preprocessing/processing_data.py`

**修改内容**:
在ProcessingData类的__init__方法中添加PET数据字段：

```python
def __init__(self, primary_image, subject_id: str, pet_image=None):
    # ... 现有MRI字段 ...
    
    # PET数据（次模态，依赖MRI）
    self.pet = {
        "original": pet_image,           # 原始PET图像
        "registered_to_mri": None,       # 配准到MRI native空间
        "skull_stripped": None,          # 应用MRI脑掩膜后
        "mni": None,                     # MNI标准空间
    }
```

**改动量**: 约30行

### 2. PET处理器

**文件**: `src/preprocessing/pet_processor.py` (新建)

**功能实现**:
```python
class PETProcessor:
    """PET预处理，依赖MRI处理结果"""
    
    def run(self, data: ProcessingData, output_dir: Path) -> ProcessingData:
        """
        执行PET处理三步骤：
        1. 刚体配准到MRI native空间
        2. 应用MRI脑掩膜
        3. 应用MRI→MNI变换场
        """
        if data.pet["original"] is None:
            return data  # 无PET数据，直接返回
        
        self._register_to_mri(data)
        self._apply_brain_mask(data)
        self._transform_to_mni(data)
        
        data.processing_steps.append("pet_processing")
        return data
    
    def _register_to_mri(self, data):
        """刚体配准：PET → MRI native空间"""
        result = ants.registration(
            fixed=data.native["image"],      # MRI作为fixed
            moving=data.pet["original"],
            type_of_transform='Rigid'
        )
        data.pet["registered_to_mri"] = result['warpedmovout']
    
    def _apply_brain_mask(self, data):
        """应用MRI脑掩膜到配准后的PET"""
        if data.native["brain_mask"] is not None:
            pet_masked = data.pet["registered_to_mri"] * data.native["brain_mask"]
            data.pet["skull_stripped"] = pet_masked
        else:
            data.pet["skull_stripped"] = data.pet["registered_to_mri"]
    
    def _transform_to_mni(self, data):
        """应用MRI→MNI变换场到PET"""
        if data.transforms["native_to_template"] is not None:
            data.pet["mni"] = ants.apply_transforms(
                fixed=data.template["image"],
                moving=data.pet["skull_stripped"],
                transformlist=data.transforms["native_to_template"],
                interpolator='linear'
            )
```

**改动量**: 约100行

### 3. Pipeline修改

**文件**: `src/pipeline.py`

**修改内容**:

1. run()方法签名修改：
```python
def run(self, subject_id: str, mri_path: Union[str, Path], 
        pet_path: Union[str, Path] = None,  # 新增可选参数
        output_dir: Path = None) -> ProcessingData:
```

2. 图像加载部分：
```python
# Load MRI
original_image = ants.image_read(str(mri_path))

# Load PET (optional)
pet_image = None
if pet_path is not None:
    pet_path = Path(pet_path)
    if pet_path.exists():
        print(f"Loading PET: {pet_path.name}")
        pet_image = ants.image_read(str(pet_path))

# Initialize data container
data = ProcessingData(original_image, subject_id, pet_image)
```

3. 处理步骤顺序：
```python
step_order = [
    'skull_stripping',
    'segmentation',
    'registration',
    'pet_processing',    # 新增：必须在registration之后
    'roi_extraction',
    'quality_control'
]
```

4. 初始化处理器：
```python
def _init_processors(self):
    # ... 现有处理器 ...
    
    if self.config.get('pet_processing', {}).get('enabled', False):
        from .preprocessing.pet_processor import PETProcessor
        self.processors['pet_processing'] = PETProcessor(
            self.config['pet_processing']
        )
```

5. 保存PET结果：
```python
def _save_final_results(self, data, subject_id):
    # ... 现有MRI保存代码 ...
    
    # Save PET results
    if data.pet["mni"] is not None:
        path = final_dir / f"{subject_id}_PET_MNI.nii.gz"
        data.pet["mni"].to_file(str(path))
        print(f"  Saved: {path.name}")
    
    if data.pet["skull_stripped"] is not None:
        path = final_dir / f"{subject_id}_PET_skull_stripped.nii.gz"
        data.pet["skull_stripped"].to_file(str(path))
        print(f"  Saved: {path.name}")
```

**改动量**: 约60行

### 4. CLI修改

**文件**: `main.py`

**修改内容**:

1. 添加PET参数：
```python
parser.add_argument(
    '--pet', '-p',
    type=Path,
    help='Path to PET image (optional, will be registered to MRI)'
)
```

2. 传递参数：
```python
result = pipeline.run(
    subject_id=args.subject,
    mri_path=args.mri,
    pet_path=args.pet,  # 新增
    output_dir=args.output
)
```

**改动量**: 约10行

### 5. 批处理修改

**文件**: `scripts/batch_process.py`

**修改内容**:

1. 修改find_subjects()函数：
```python
def find_subjects(input_dir: Path, mri_pattern: str, 
                 pet_pattern: str = None,
                 subject_list: Path = None) -> List[Tuple[str, Path, Path]]:
    """
    查找被试数据
    
    Returns:
        List of (subject_id, mri_path, pet_path) tuples
    """
    subjects = []
    
    for mri_path in input_dir.glob(mri_pattern):
        subject_id = mri_path.stem.replace('.nii', '')
        
        # 尝试查找匹配的PET文件
        pet_path = None
        if pet_pattern:
            pet_matches = list(input_dir.glob(f"*{subject_id}*{pet_pattern}"))
            if pet_matches:
                pet_path = pet_matches[0]
        
        subjects.append((subject_id, mri_path, pet_path))
    
    return subjects
```

2. 修改处理循环：
```python
for i, (subject_id, mri_path, pet_path) in enumerate(subjects, 1):
    result = pipeline.run(
        subject_id=subject_id,
        mri_path=mri_path,
        pet_path=pet_path,  # 新增
        output_dir=args.output
    )
```

3. 添加命令行参数：
```python
parser.add_argument(
    '--pet-pattern',
    help='File pattern for PET images (optional)'
)
```

**改动量**: 约30行

### 6. 配置文件

**文件**: `config/pipeline_config.yaml`

**修改内容**:
```yaml
# PET processing configuration
pet_processing:
  enabled: true
  registration_type: "Rigid"  # PET到MRI使用刚体配准
  save_intermediate: true
```

**改动量**: 约5行

### 7. 模块导入

**文件**: `src/preprocessing/__init__.py`

**修改内容**:
```python
from .pet_processor import PETProcessor
```

**改动量**: 约2行

## 改动量统计

| 文件 | 改动类型 | 代码量 |
|------|---------|--------|
| processing_data.py | 扩展 | ~30行 |
| pet_processor.py | 新建 | ~100行 |
| pipeline.py | 修改 | ~60行 |
| main.py | 修改 | ~10行 |
| batch_process.py | 修改 | ~30行 |
| pipeline_config.yaml | 扩展 | ~5行 |
| __init__.py | 修改 | ~2行 |
| **总计** | | **~237行** |

## 实施步骤

### Phase 1: 数据结构 (15分钟)
1. 扩展ProcessingData类，添加pet字段
2. 修改__init__方法接受pet_image参数

### Phase 2: 核心处理器 (30分钟)
1. 创建pet_processor.py文件
2. 实现PETProcessor类的三个核心方法
3. 添加错误处理和日志输出

### Phase 3: Pipeline集成 (20分钟)
1. 修改Pipeline.run()方法签名
2. 添加PET图像加载逻辑
3. 更新处理步骤顺序
4. 修改_init_processors()
5. 更新_save_final_results()

### Phase 4: CLI和批处理 (15分钟)
1. 修改main.py添加--pet参数
2. 修改batch_process.py支持PET文件查找
3. 更新配置文件

### Phase 5: 测试 (30-45分钟)
1. 单样本MRI测试（验证向后兼容）
2. 单样本MRI+PET测试
3. 批处理测试
4. 验证空间对齐

### Phase 6: 文档更新 (15分钟)
1. 更新README.md
2. 更新CHANGELOG.md
3. 添加PET使用示例

**预计总时间**: 2-2.5小时

## 测试计划

### 1. 向后兼容性测试
```bash
# 测试纯MRI处理（不提供PET）
python main.py --subject sub001 --mri data/sub001_T1.nii.gz
```
预期：行为与v1.0.0完全一致

### 2. MRI+PET处理测试
```bash
# 测试MRI+PET处理
python main.py --subject sub001 --mri data/sub001_T1.nii.gz --pet data/sub001_PET.nii.gz
```
预期：
- MRI处理正常完成
- PET配准到MRI native空间
- PET应用MRI脑掩膜
- PET转换到MNI空间
- 输出文件包含PET结果

### 3. 批处理测试
```bash
# 测试批处理
python scripts/batch_process.py --input data/ --pattern "*_T1.nii.gz" --pet-pattern "*_PET.nii.gz"
```
预期：
- 自动匹配MRI和PET文件
- 批量处理所有被试
- 生成完整的输出结果

### 4. 空间对齐验证
使用ITK-SNAP或FSLeyes可视化验证：
- PET_MNI.nii.gz与T1_MNI.nii.gz对齐
- PET_skull_stripped.nii.gz与brain_mask对齐

## 关键技术点

### 1. 空间转换数学原理
```
设：
- T_pet→mri: PET → MRI native 的刚体变换
- T_mri→mni: MRI native → MNI 的非线性变换

则：
PET_mni = T_mri→mni(T_pet→mri(PET_original))
```

实现中分两步：
1. 第一步：PET_registered = T_pet→mri(PET_original)
2. 第二步：PET_mni = T_mri→mni(PET_registered)

### 2. 变换场复用
MRI→MNI的变换场保存在：
```python
data.transforms["native_to_template"]  # 前向变换
data.transforms["template_to_native"]  # 反向变换
```

PET直接使用前向变换：
```python
ants.apply_transforms(
    fixed=data.template["image"],
    moving=data.pet["skull_stripped"],
    transformlist=data.transforms["native_to_template"],
    interpolator='linear'
)
```

### 3. 脑掩膜复用
MRI脑掩膜保存在：
```python
data.native["brain_mask"]  # MRI native空间的脑掩膜
```

PET配准到MRI native空间后，可直接应用此掩膜：
```python
pet_masked = data.pet["registered_to_mri"] * data.native["brain_mask"]
```

### 4. 配准类型选择
- PET→MRI：使用刚体配准（Rigid）
  - 原因：同一被试的不同模态，只需校正位置和方向
  - 保持PET的强度信息不变
- MRI→MNI：使用非线性配准（SyN）
  - 原因：不同被试间的解剖差异需要非线性变换

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 破坏现有MRI功能 | 低 | 高 | 充分测试向后兼容性 |
| PET配准失败 | 中 | 中 | 添加错误处理和日志 |
| 空间混淆 | 低 | 高 | 使用清晰的命名和注释 |
| 性能问题 | 低 | 低 | PET处理是可选的 |

## 输出文件结构

### MRI only模式
```
output/
└── sub001/
    ├── intermediate/
    │   └── sub001_*.nii.gz
    ├── final/
    │   ├── sub001_T1_MNI.nii.gz
    │   ├── sub001_brain_mask_MNI.nii.gz
    │   └── sub001_*_probability_MNI.nii.gz
    └── qc/
        └── sub001_qc_report.txt
```

### MRI + PET模式
```
output/
└── sub001/
    ├── intermediate/
    │   └── sub001_*.nii.gz
    ├── final/
    │   ├── sub001_T1_MNI.nii.gz
    │   ├── sub001_PET_MNI.nii.gz              # 新增
    │   ├── sub001_PET_skull_stripped.nii.gz   # 新增
    │   ├── sub001_brain_mask_MNI.nii.gz
    │   └── sub001_*_probability_MNI.nii.gz
    └── qc/
        └── sub001_qc_report.txt
```

## 使用示例

### 单样本处理
```bash
# MRI only
python main.py --subject sub001 --mri data/sub001_T1.nii.gz

# MRI + PET
python main.py --subject sub001 \
    --mri data/sub001_T1.nii.gz \
    --pet data/sub001_PET.nii.gz
```

### 批处理
```bash
# MRI only
python scripts/batch_process.py \
    --input data/ \
    --pattern "*_T1.nii.gz"

# MRI + PET
python scripts/batch_process.py \
    --input data/ \
    --pattern "*_T1.nii.gz" \
    --pet-pattern "*_PET.nii.gz"
```

## 版本发布计划

1. 完成开发和测试
2. 合并feature/pet-support到main分支
3. 创建v1.1.0 tag
4. 更新文档和CHANGELOG
5. 发布release notes

## 总结

本次更新通过集成式设计实现PET支持，充分复用MRI处理结果，保持代码简洁和向后兼容。PET处理作为可选功能，不影响现有MRI处理流程，同时为多模态医学图像分析提供了完整的预处理解决方案。
