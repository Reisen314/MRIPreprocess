"""
ROI feature extraction processor.
"""
from pathlib import Path
from typing import Dict, Any
import numpy as np
from .processing_data import ProcessingData

try:
    import ants
except ImportError:
    print("Warning: ANTsPy not available")
    ants = None


class ROIExtraction:
    """Extract ROI features using brain atlas."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.atlas_path = Path(config['atlas_path'])
        self.atlas = None
    
    def _load_atlas(self):
        """Load atlas template."""
        if self.atlas is None:
            if not self.atlas_path.exists():
                raise FileNotFoundError(
                    f"Atlas file not found: {self.atlas_path}\n"
                    f"Please download the atlas and place it at the specified path.\n"
                    f"You can disable ROI extraction in config if atlas is not available."
                )
            if ants is None:
                raise ImportError("ANTsPy required for ROI extraction")
            
            print(f"  Loading atlas: {self.atlas_path.name}")
            self.atlas = ants.image_read(str(self.atlas_path))
            print(f"  Atlas loaded successfully: shape {self.atlas.shape}")
    
    def run(self, data: ProcessingData, output_dir: Path = None) -> ProcessingData:
        """
        Extract ROI features from template space segmentation.
        
        Args:
            data: ProcessingData container
            output_dir: Optional output directory
            
        Returns:
            Updated ProcessingData container
        """
        if ants is None:
            raise ImportError("ANTsPy required for ROI extraction")
        
        print("Executing: roi_extraction (template space)")
        
        # Check prerequisites
        if not data.has_segmentation():
            raise ValueError("ROI extraction requires segmentation results")
        if not data.has_registration():
            raise ValueError("ROI extraction requires registration to template space")
        
        # Load atlas
        self._load_atlas()
        
        # Extract features
        roi_features = self._extract_roi_features(data)
        
        # Update template space data
        data.template["roi_features"] = roi_features
        data.processing_steps.append("roi_extraction")
        
        # Save results if configured
        if output_dir:
            self._save_results(data, output_dir)
        
        return data
    
    def _extract_roi_features(self, data: ProcessingData) -> Dict[str, np.ndarray]:
        """Extract ROI features from template space probability maps."""
        print("  Extracting ROI features")
        
        # Get atlas data
        atlas_data = self.atlas.numpy()
        
        # Get unique ROI labels (excluding background 0)
        roi_labels = np.unique(atlas_data)
        roi_labels = roi_labels[roi_labels > 0]
        
        num_rois = len(roi_labels)
        print(f"    Processing {num_rois} ROIs")
        
        # Extract features for each tissue type from template space
        features = {}
        
        # GM features
        if data.template["gm_probability"] is not None:
            gm_data = data.template["gm_probability"].numpy()
            gm_features = self._extract_features_for_tissue(
                gm_data, atlas_data, roi_labels
            )
            features['gm_features'] = gm_features
            print(f"    Extracted GM features: shape {gm_features.shape}")
        
        # WM features
        if data.template["wm_probability"] is not None:
            wm_data = data.template["wm_probability"].numpy()
            wm_features = self._extract_features_for_tissue(
                wm_data, atlas_data, roi_labels
            )
            features['wm_features'] = wm_features
            print(f"    Extracted WM features: shape {wm_features.shape}")
        
        return features
    
    def _extract_features_for_tissue(self, tissue_data: np.ndarray, 
                                     atlas_data: np.ndarray,
                                     roi_labels: np.ndarray) -> np.ndarray:
        """Extract features for one tissue type."""
        statistics = self.config.get('statistics', ['mean'])
        num_rois = len(roi_labels)
        num_stats = len(statistics)
        
        features = np.zeros((num_rois, num_stats))
        
        for i, roi_id in enumerate(roi_labels):
            roi_mask = atlas_data == roi_id
            roi_values = tissue_data[roi_mask]
            
            for j, stat in enumerate(statistics):
                if stat == 'mean':
                    features[i, j] = np.mean(roi_values)
                elif stat == 'std':
                    features[i, j] = np.std(roi_values)
                elif stat == 'volume':
                    features[i, j] = np.sum(roi_mask)
                elif stat == 'median':
                    features[i, j] = np.median(roi_values)
        
        # Flatten if only one statistic
        if num_stats == 1:
            features = features.flatten()
        
        return features
    
    def _save_results(self, data: ProcessingData, output_dir: Path):
        """Save ROI features from template space."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if data.template["roi_features"] is not None:
            atlas_name = self.config.get('atlas', 'atlas')
            
            # Save each feature type
            for feature_name, feature_array in data.template["roi_features"].items():
                feature_path = output_dir / f"{data.subject_id}_{atlas_name}_{feature_name}.npy"
                np.save(str(feature_path), feature_array)
                print(f"    Saved: {feature_path.name}")
