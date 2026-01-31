"""
Tissue segmentation processor using ANTs Atropos.
"""
from pathlib import Path
from typing import Dict, Any
from .processing_data import ProcessingData

try:
    import ants
except ImportError:
    print("Warning: ANTsPy not available")
    ants = None


class Segmentation:
    """Tissue segmentation using ANTs Atropos."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def run(self, data: ProcessingData, output_dir: Path = None) -> ProcessingData:
        """
        Perform tissue segmentation in native space.
        
        Args:
            data: ProcessingData container
            output_dir: Optional output directory
            
        Returns:
            Updated ProcessingData container
        """
        if ants is None:
            raise ImportError("ANTsPy required for segmentation")
        
        print("Executing: segmentation (native space)")
        
        # Determine which segmentation method to use
        if self.config['methods']['atropos']['enabled']:
            self._atropos_segmentation(data)
        else:
            raise ValueError("No segmentation method enabled")
        
        # Save intermediate results if configured
        if self.config.get('save_intermediate', False) and output_dir:
            self._save_results(data, output_dir)
        
        return data
    
    def _atropos_segmentation(self, data: ProcessingData):
        """Atropos 3-class segmentation in native space."""
        config = self.config['methods']['atropos']
        
        print("  Applying: Atropos segmentation")
        
        num_classes = config.get('num_classes', 3)
        
        try:
            # Use native space image and mask
            if data.native["brain_mask"] is not None:
                seg_result = ants.atropos(
                    a=data.native["image"],
                    x=data.native["brain_mask"],
                    i=f'kmeans[{num_classes}]',
                    m='[0.2,1x1x1]',
                    c='[5,0]',
                    priorweight=0.0,
                    v=1
                )
            else:
                seg_result = ants.atropos(
                    a=data.native["image"],
                    i=f'kmeans[{num_classes}]',
                    m='[0.2,1x1x1]',
                    c='[5,0]',
                    priorweight=0.0,
                    v=1
                )
        except Exception as e:
            print(f"    Atropos failed with error: {e}")
            print(f"    Trying alternative segmentation method...")
            seg_result = self._simple_segmentation(data, num_classes)
        
        # Update native space data
        data.native["segmentation_labels"] = seg_result['segmentation']
        
        if len(seg_result['probabilityimages']) >= 3:
            data.native["csf_probability"] = seg_result['probabilityimages'][0]
            data.native["gm_probability"] = seg_result['probabilityimages'][1]
            data.native["wm_probability"] = seg_result['probabilityimages'][2]
            print(f"    Generated {num_classes} tissue probability maps")
        
        data.processing_steps.append("segmentation")
    
    def _simple_segmentation(self, data: ProcessingData, num_classes: int) -> Dict:
        """Simple threshold-based segmentation as fallback."""
        import numpy as np
        
        print("    Using simple threshold-based segmentation")
        
        # Get native space image data
        img_data = data.native["image"].numpy()
        
        # Apply brain mask if available
        if data.native["brain_mask"] is not None:
            mask_data = data.native["brain_mask"].numpy()
            img_data = img_data * mask_data
        
        # Calculate thresholds using percentiles
        brain_voxels = img_data[img_data > 0]
        if len(brain_voxels) == 0:
            raise ValueError("No brain voxels found for segmentation")
        
        # Simple 3-class segmentation based on intensity
        p33 = np.percentile(brain_voxels, 33)
        p66 = np.percentile(brain_voxels, 66)
        
        # Create segmentation labels
        seg_labels = np.zeros_like(img_data)
        seg_labels[img_data > 0] = 1  # CSF (low intensity)
        seg_labels[img_data > p33] = 2  # GM (medium intensity)
        seg_labels[img_data > p66] = 3  # WM (high intensity)
        
        # Create probability maps
        csf_prob = (seg_labels == 1).astype(float)
        gm_prob = (seg_labels == 2).astype(float)
        wm_prob = (seg_labels == 3).astype(float)
        
        # Convert to ANTs images
        seg_image = data.native["image"].new_image_like(seg_labels)
        csf_image = data.native["image"].new_image_like(csf_prob)
        gm_image = data.native["image"].new_image_like(gm_prob)
        wm_image = data.native["image"].new_image_like(wm_prob)
        
        return {
            'segmentation': seg_image,
            'probabilityimages': [csf_image, gm_image, wm_image]
        }
    
    def _save_results(self, data: ProcessingData, output_dir: Path):
        """Save segmentation results from native space."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save segmentation labels
        if data.native["segmentation_labels"] is not None:
            labels_path = output_dir / f"{data.subject_id}_segmentation_labels.nii.gz"
            data.native["segmentation_labels"].to_file(str(labels_path))
            print(f"    Saved: {labels_path.name}")
        
        # Save probability maps
        for tissue in ["csf", "gm", "wm"]:
            prob_key = f"{tissue}_probability"
            if data.native[prob_key] is not None:
                prob_path = output_dir / f"{data.subject_id}_{tissue}_probability.nii.gz"
                data.native[prob_key].to_file(str(prob_path))
                print(f"    Saved: {prob_path.name}")
