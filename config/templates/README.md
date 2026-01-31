# 配准模板文件夹

此文件夹用于存放配准所需的模板文件。

## 必需文件

### MNI152模板
- `MNI152_T1_1mm.nii.gz` - MNI152标准空间T1模板（1mm分辨率）
- 下载地址: https://www.bic.mni.mcgill.ca/ServicesAtlases/ICBM152NLin2009

### 脑区模板
- `AAL90_MNI.nii.gz` - AAL90脑区模板
- `AAL116_MNI.nii.gz` - AAL116脑区模板
- 下载地址: http://www.gin.cnrs.fr/en/tools/aal/

## 文件放置

将下载的模板文件放置在此目录下，确保配置文件中的路径正确。

## 注意事项

- 模板文件较大，不包含在git仓库中
- 首次使用前需要手动下载
- 确保模板文件与配置文件中的路径一致
