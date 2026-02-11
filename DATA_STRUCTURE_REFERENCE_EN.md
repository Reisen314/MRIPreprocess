# ProcessingData Structure Reference

## Space-Aware Architecture

ProcessingData adopts a space-aware architecture that clearly separates native space and template space data.

## Data Access Methods

### Old Method (Deprecated)
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

### New Method (Current)

#### Native Space (Original Acquisition Space)
```python
data.native["image"]              # Current processed image
data.native["original_image"]     # Original input image (immutable)
data.native["brain_mask"]         # Brain mask
data.native["segmentation_labels"] # Segmentation labels
data.native["gm_probability"]     # Gray matter probability map
data.native["wm_probability"]     # White matter probability map
data.native["csf_probability"]    # CSF probability map
```

#### Template Space (Standardized Space)
```python
data.template["image"]            # Registered image
data.template["brain_mask"]       # Transformed brain mask
data.template["segmentation_labels"] # Transformed segmentation labels
data.template["gm_probability"]   # Transformed GM probability map
data.template["wm_probability"]   # Transformed WM probability map
data.template["csf_probability"]  # Transformed CSF probability map
data.template["roi_labels"]       # Atlas labels
data.template["roi_features"]     # Extracted ROI features
```

#### PET Data (v1.1+)
```python
data.pet["original"]              # Original PET image
data.pet["registered_to_mri"]     # PET registered to MRI native space
data.pet["skull_stripped"]        # PET after applying brain mask
data.pet["mni"]                   # PET in MNI standard space
```

#### Transforms (Spatial Transforms)
```python
data.transforms["native_to_template"]  # Forward transform matrix
data.transforms["template_to_native"]  # Inverse transform matrix
```

#### Metadata
```python
data.subject_id                   # Subject ID
data.processing_steps             # List of processing steps
data.qc_metrics                   # Quality control metrics
```

## Space Usage by Module

| Module | Input Space | Output Space | Description |
|--------|-------------|--------------|-------------|
| Skull Stripping | Native | Native | Extract brain tissue in native space |
| Segmentation | Native | Native | Tissue segmentation in native space |
| Registration | Native | Template | Register and automatically transform all data |
| PET Processing | Native | Template | Process PET using MRI results |
| ROI Extraction | Template | Template | Use atlas in template space |
| Quality Control | Both | - | Access both spaces as needed |

## Helper Methods

### Check Methods
```python
data.has_brain_extraction()  # Whether brain extraction is complete
data.has_registration()      # Whether registration is complete
data.has_segmentation()      # Whether segmentation is complete
```

### Space Transform Method
```python
# Transform data from native space to template space
data.transform_to_template(
    field_name="brain_mask",
    interpolator='nearestNeighbor'  # or 'linear'
)
```

### Get Summary
```python
summary = data.get_processing_summary()
# Returns:
# {
#     'subject_id': 'sub001',
#     'processing_steps': ['skull_stripping', 'segmentation', ...],
#     'has_brain_mask': True,
#     'has_registration': True,
#     'has_segmentation': True,
#     'qc_metrics': {...}
# }
```

## Processing Workflow Example

```python
# 1. Initialize (automatically done by Pipeline)
data = ProcessingData(original_image, "sub001")

# 2. Skull Stripping (in native space)
data.native["image"] = brain_image
data.native["brain_mask"] = brain_mask

# 3. Segmentation (in native space)
data.native["segmentation_labels"] = seg_labels
data.native["gm_probability"] = gm_prob
data.native["wm_probability"] = wm_prob
data.native["csf_probability"] = csf_prob

# 4. Registration (connects two spaces)
data.template["image"] = registered_image
data.transforms["native_to_template"] = fwd_transforms
# Automatically transform all native data to template space
data.template["brain_mask"] = ...
data.template["gm_probability"] = ...
# ... etc.

# 5. PET Processing (v1.1+, if PET is provided)
data.pet["registered_to_mri"] = pet_registered
data.pet["skull_stripped"] = pet_masked
data.pet["mni"] = pet_mni

# 6. ROI Extraction (in template space)
data.template["roi_features"] = roi_features

# 7. Quality Control (access both spaces)
# Use native space to calculate SNR
# Use template space to calculate registration quality
```

## Migration Guide

If you have old code that needs updating:

### 1. Simple Attribute Access
```python
# Old code
mask = data.brain_mask

# New code
mask = data.native["brain_mask"]  # or data.template["brain_mask"]
```

### 2. Attribute Assignment
```python
# Old code
data.brain_mask = new_mask

# New code
data.native["brain_mask"] = new_mask
```

### 3. Conditional Checks
```python
# Old code
if data.brain_mask is not None:
    ...

# New code
if data.native["brain_mask"] is not None:
    ...
```

### 4. Choosing the Correct Space
- Before registration: use `data.native`
- After registration: choose based on needs
  - Need original resolution: `data.native`
  - Need standard space (e.g., using atlas): `data.template`

## Common Errors

### AttributeError: 'ProcessingData' object has no attribute 'xxx'
**Cause:** Using old attribute names

**Solution:** Use new dictionary access method
```python
# Wrong
data.original_image

# Correct
data.native["original_image"]
```

### KeyError: 'xxx'
**Cause:** Accessing non-existent field

**Solution:** Check field name spelling, or check existence first
```python
if data.native.get("brain_mask") is not None:
    mask = data.native["brain_mask"]
```

### Space Misuse
**Cause:** Accessing data in wrong space

**Solution:** Confirm which space should be used for current processing step
- Before Segmentation: only native space has data
- After Registration: both spaces have data

## PET Data Structure (v1.1+)

### PET Processing Workflow
```python
# 1. Load PET (automatically done by Pipeline if provided)
data.pet["original"] = pet_image

# 2. Register PET to MRI native space
data.pet["registered_to_mri"] = registered_pet

# 3. Apply MRI brain mask
data.pet["skull_stripped"] = masked_pet

# 4. Transform to MNI using MRI transforms
data.pet["mni"] = pet_in_mni
```

### PET Data Access
```python
# Check if PET is available
if data.pet["original"] is not None:
    # Process PET
    pet_mni = data.pet["mni"]
```

### PET Space Relationship
- `pet["original"]`: Original PET acquisition space
- `pet["registered_to_mri"]`: Aligned with `native["image"]`
- `pet["skull_stripped"]`: Same space as `registered_to_mri`, masked
- `pet["mni"]`: Aligned with `template["image"]`
