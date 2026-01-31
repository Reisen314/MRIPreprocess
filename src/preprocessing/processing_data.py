"""
Unified data container for preprocessing pipeline with space-aware architecture.
"""
from typing import Dict, Any, Optional

try:
    import ants
except ImportError:
    ants = None


class ProcessingData:
    """
    Space-aware container for preprocessing data.
    
    Separates native and template space data to prevent spatial mismatches.
    """
    
    def __init__(self, primary_image, subject_id: str):
        """
        Initialize processing data container.
        
        Args:
            primary_image: Initial image in native space (ANTs Image)
            subject_id: Subject identifier
        """
        self.subject_id = subject_id
        
        # Native space (original acquisition space)
        self.native = {
            "image": primary_image,
            "original_image": primary_image,
            "brain_mask": None,
            "segmentation_labels": None,
            "gm_probability": None,
            "wm_probability": None,
            "csf_probability": None,
        }
        
        # Template space (standardized space after registration)
        self.template = {
            "image": None,
            "brain_mask": None,
            "segmentation_labels": None,
            "gm_probability": None,
            "wm_probability": None,
            "csf_probability": None,
            "roi_labels": None,
            "roi_features": None,
        }
        
        # Spatial transforms
        self.transforms = {
            "native_to_template": None,
            "template_to_native": None,
        }
        
        # Metadata
        self.processing_steps = []
        self.qc_metrics = {}
    
    def transform_to_template(self, field_name: str, interpolator: str = 'linear'):
        """
        Transform a field from native to template space.
        
        Args:
            field_name: Name of the field to transform
            interpolator: 'linear' or 'nearestNeighbor'
        """
        if ants is None or self.transforms["native_to_template"] is None:
            return
        
        if self.native[field_name] is not None and self.template["image"] is not None:
            self.template[field_name] = ants.apply_transforms(
                fixed=self.template["image"],
                moving=self.native[field_name],
                transformlist=self.transforms["native_to_template"],
                interpolator=interpolator
            )
    
    def has_brain_extraction(self) -> bool:
        """Check if brain extraction has been performed."""
        return self.native["brain_mask"] is not None
    
    def has_registration(self) -> bool:
        """Check if registration has been performed."""
        return self.template["image"] is not None
    
    def has_segmentation(self) -> bool:
        """Check if segmentation has been performed (in either space)."""
        return (self.native["gm_probability"] is not None or 
                self.template["gm_probability"] is not None)
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of processing steps and results."""
        return {
            'subject_id': self.subject_id,
            'processing_steps': self.processing_steps.copy(),
            'has_brain_mask': self.has_brain_extraction(),
            'has_registration': self.has_registration(),
            'has_segmentation': self.has_segmentation(),
            'qc_metrics': self.qc_metrics.copy()
        }
