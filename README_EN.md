# MRI Preprocessing Pipeline

> Medical image preprocessing system based on ANTs/ANTsPyNet with space-aware architecture and configuration-driven design, supporting MRI and PET multimodal processing

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Features

- **Complete preprocessing pipeline** - From raw T1 MRI to ROI feature extraction
- **Multimodal support** - Support for MRI + PET joint processing (v1.1+)
- **Space-aware architecture** - Clear separation of Native and Template spaces to prevent spatial misuse
- **Configuration-driven** - Flexible control of all processing parameters via YAML files
- **Modular design** - Unified data container and processor interface
- **Automatic output classification** - Intermediate results, final results, and quality reports stored separately
- **Flexible extension** - Support for multiple algorithms and parameter configurations

---

## Quick Start

### Installation

```bash
# Clone the project
git clone <repository-url>
cd MRIPreprocess

# Install dependencies
pip install antspyx antspynet pyyaml numpy
```

### Prepare Template Files

Download and place required template files (see [SETUP_TEMPLATES.md](SETUP_TEMPLATES.md)):
- `config/templates/MNI152_T1_1mm.nii.gz` - MNI152 template
- `config/templates/AAL116_MNI.nii.gz` - AAL116 brain atlas

### Run

```bash
# Process single MRI sample
python main.py --subject sub001 --mri data/sub001_T1.nii.gz

# Process MRI + PET (v1.1+)
python main.py --subject sub001 --mri data/sub001_T1.nii.gz --pet data/sub001_PET.nii.gz

# Use custom configuration
python main.py --subject sub001 --mri data/sub001_T1.nii.gz --config custom_config.yaml

# Batch process MRI
python scripts/batch_process.py --input data/ --pattern "*_T1.nii.gz"

# Batch process MRI + PET
python scripts/batch_process.py --input data/ --pattern "*_T1.nii.gz" --pet-pattern "*_PET.nii.gz"
```

---

## Processing Pipeline

### MRI Processing Pipeline

```
Raw T1 MRI
    ↓
1. Skull Stripping - Native Space
    ↓
2. Segmentation - Native Space
    ↓
3. Registration - Native → Template Space
    ↓
4. ROI Extraction - Template Space
    ↓
5. Quality Control
    ↓
Final Results (MNI Standard Space)
```

### PET Processing Pipeline (v1.1+)

```
Raw PET
    ↓
1. Registration to MRI - Rigid
    ↓
2. Apply Brain Mask (from MRI)
    ↓
3. Transform to MNI (using MRI→MNI transform)
    ↓
PET in MNI Standard Space
```

**Key Features:**
- PET processing fully depends on MRI processing results
- Uses MRI brain mask and transform fields to ensure spatial alignment
- PET is optional and does not affect MRI processing pipeline

### Processing Steps Details

| Step | Function | Algorithm | Output |
|------|----------|-----------|--------|
| **Skull Stripping** | Brain tissue extraction | ANTsPyNet / ANTs | Brain image + brain mask |
| **Segmentation** | Tissue segmentation | Atropos 3-class | CSF/GM/WM probability maps |
| **Registration** | Spatial normalization | SyN / Affine / Rigid | MNI space image + transform matrix |
| **PET Processing** | PET preprocessing | Rigid + Transform | PET MNI space image |
| **ROI Extraction** | Brain region feature extraction | AAL116 atlas | ROI statistical features |
| **Quality Control** | Quality assessment | Multi-dimensional metrics | QC report |

---

## Output Structure

### MRI Only Mode

```
output/
└── subject_id/
    ├── intermediate/              # Intermediate results (Native space)
    │   ├── sub001_antspynet_skull_stripped.nii.gz
    │   ├── sub001_segmentation_labels.nii.gz
    │   ├── sub001_gm_probability.nii.gz
    │   ├── sub001_wm_probability.nii.gz
    │   ├── sub001_csf_probability.nii.gz
    │   ├── sub001_registered.nii.gz
    │   └── sub001_summary.txt
    │
    ├── final/                     # Final results (MNI space) ⭐
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
    ├── qc/                        # Quality control
    │   └── sub001_qc_report.txt
    │
    └── logs/                      # Logs (reserved)
```

### MRI + PET Mode (v1.1+)

```
output/
└── subject_id/
    ├── intermediate/              # Intermediate results
    │   ├── ... (MRI intermediate results)
    │   ├── sub001_PET_registered.nii.gz      # PET registered to MRI
    │   └── sub001_PET_skull_stripped.nii.gz  # PET skull-stripped
    │
    ├── final/                     # Final results (MNI space) ⭐
    │   ├── ... (MRI final results)
    │   ├── sub001_PET_MNI.nii.gz             # PET MNI space ⭐
    │   ├── sub001_PET_skull_stripped.nii.gz  # PET skull-stripped
    │   └── sub001_final_summary.txt
    │
    ├── qc/
    │   └── sub001_qc_report.txt
    │
    └── logs/
```

**Usage Tips:**
- For analysis: Use MNI space files in `final/` directory
- For debugging: Check intermediate results in `intermediate/` directory
- Quality check: Review reports in `qc/` directory
- PET analysis: Use `final/sub001_PET_MNI.nii.gz`, perfectly aligned with MRI

---

## Configuration

Main configuration file: `config/pipeline_config.yaml`

```yaml
# General settings
general:
  version: "1.1.0"
  save_intermediate: true

# Enable/disable processing steps
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

# PET processing configuration (v1.1+)
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

## Testing

```bash
# Test configuration loading and Pipeline initialization
python test_pipeline.py

# Test base processor (no ANTsPy required)
python test_base_processor.py
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [CHANGELOG.md](development_document/CHANGELOG.md) | Development log and version history |
| [DATA_STRUCTURE_REFERENCE.md](DATA_STRUCTURE_REFERENCE.md) | Data structure reference |
| [TROUBLESHOOTING.md](development_document/TROUBLESHOOTING.md) | Troubleshooting guide |
| [SETUP_TEMPLATES.md](SETUP_TEMPLATES.md) | Template file setup |
| [MIGRATION_GUIDE.md](development_document/MIGRATION_GUIDE.md) | Architecture migration guide |
| [PET_SUPPORT_PLAN.md](development_document/PET_SUPPORT_PLAN.md) | PET support development plan |

---

## Project Structure

```
MRIPreprocess/
├── config/                        # Configuration and templates
│   ├── pipeline_config.yaml       # Main configuration file
│   └── templates/                 # MNI152, AAL116 templates
│
├── src/
│   ├── preprocessing/             # Preprocessing modules
│   │   ├── processing_data.py     # Data container (space-aware)
│   │   ├── base_processor.py      # Processor base class
│   │   ├── skull_stripping.py     # Skull stripping
│   │   ├── segmentation.py        # Tissue segmentation
│   │   ├── registration.py        # Registration
│   │   ├── pet_processor.py       # PET processing (v1.1+)
│   │   ├── roi_extraction.py      # ROI extraction
│   │   └── quality_control.py     # Quality control
│   ├── utils/
│   │   └── file_manager.py        # File management
│   └── pipeline.py                # Main pipeline orchestrator
│
├── scripts/
│   ├── process_single_subject.py  # Single subject processing
│   └── batch_process.py           # Batch processing
│
├── development_document/          # Development documentation
│   ├── CHANGELOG.md
│   ├── PET_SUPPORT_PLAN.md
│   └── ...
│
├── main.py                        # Command-line entry point
├── test_pipeline.py               # Test script
└── requirements.txt               # Dependencies
```

---

## Core Concepts

### Space-Aware Architecture

```python
ProcessingData:
  native:      # Original acquisition space
    - image, brain_mask
    - segmentation, probabilities
  
  template:    # MNI standard space
    - image, brain_mask
    - segmentation, probabilities
    - roi_features
  
  pet:         # PET data (v1.1+)
    - original (original space)
    - registered_to_mri (MRI native space)
    - skull_stripped (skull-stripped)
    - mni (MNI standard space)
  
  transforms:  # Spatial transforms
    - native_to_template
    - template_to_native
```

**Advantages:**
- Prevent spatial misuse errors
- Clear data space identification
- Support bidirectional workflows
- Support multimodal data management

### PET Processing Principle (v1.1+)

PET processing depends on MRI processing results to ensure spatial alignment:

1. **PET → MRI Native**: Rigid registration (fixed=MRI)
2. **Apply Brain Mask**: Use MRI brain mask
3. **PET → MNI**: Apply MRI→MNI transform field

**Mathematical Representation:**
```
PET_mni = Transform_mri→mni(Transform_pet→mri(PET_original))
```

**Advantages:**
- Ensure perfect alignment of PET and MRI in MNI space
- Avoid redundant registration computation
- Reuse MRI brain mask and transform fields

---

## Performance

**Typical Processing Time** (single sample):

| Step | MRI Only | MRI + PET |
|------|----------|-----------|
| Skull Stripping | ~30-60s | ~30-60s |
| Segmentation | ~2-5min | ~2-5min |
| Registration | ~5-10min | ~5-10min |
| PET Processing | - | ~1-2min |
| ROI Extraction | ~10-30s | ~10-30s |
| Quality Control | ~5-10s | ~5-10s |
| **Total** | **~8-16min** | **~9-18min** |

**Output Size:**
- MRI Only: ~45 MB per subject
- MRI + PET: ~60 MB per subject

---

## FAQ

### Template file not found
```
FileNotFoundError: Template file not found
```
**Solution:** Refer to [SETUP_TEMPLATES.md](SETUP_TEMPLATES.md) to download template files

### Spatial mismatch error
```
ValueError: operands could not be broadcast together
```
**Solution:** Fixed! Use the latest version with space-aware architecture

### PET Processing Related Questions

**Q: Is PET required?**  
A: No. PET is an optional parameter. Without PET, behavior is identical to v1.0.

**Q: Must PET and MRI be from the same subject?**  
A: Yes. PET is registered to the same subject's MRI, using MRI brain mask and transform fields.

**Q: Can I process only PET?**  
A: No. PET processing depends on MRI processing results. MRI must be provided.

### More Questions
Refer to [TROUBLESHOOTING.md](development_document/TROUBLESHOOTING.md)

---

## Development

### Adding New Processors

1. Inherit from `BaseProcessor` (simple processors) or implement independently (complex processors)
2. Implement `run(data, output_dir)` method
3. Register in `Pipeline`
4. Add configuration items in config file

### Contribution Guidelines

Issues and Pull Requests are welcome!

---

## Version History

- **v1.1.0** (2024-02) - Added PET multimodal support
- **v1.0.0** (2024-01) - Initial release, MRI preprocessing pipeline

---

## License

MIT License

---

## Acknowledgments

This project integrates excellent designs from:
- **MDL-Net** - Advanced technology stack
- **mri_preprocessing** - Excellent architecture patterns

---

## Contact

For questions or suggestions, please submit an Issue.

---

*Last Updated: 2024-02-02 | Version: v1.1.0*
