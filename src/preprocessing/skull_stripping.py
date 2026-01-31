"""
Skull stripping processor using ANTsPyNet.
"""
from pathlib import Path
from typing import Dict, Any
from .base_processor import BaseProcessor
from .processing_data import ProcessingData

try:
    import ants
    import antspynet
except ImportError:
    print("Warning: ANTsPy/ANTsPyNet not available")
    ants = None
    antspynet = None


class SkullStripping(BaseProcessor):
    """Skull stripping using ANTsPyNet brain extraction."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Register available methods
        self.methods = {
            "antspynet": self.antspynet_extraction,
            "ants": self.ants_extraction,
        }
    
    def run(self, data: ProcessingData, output_dir: Path = None) -> ProcessingData:
        """Run skull stripping on the data."""
        return self.run_methods(data, suffix="skull_stripped", output_dir=output_dir)
    
    def antspynet_extraction(self, data: ProcessingData, config: Dict[str, Any]) -> ProcessingData:
        """Brain extraction using ANTsPyNet."""
        if ants is None or antspynet is None:
            raise ImportError("ANTsPy/ANTsPyNet required for brain extraction")
        
        # Perform brain extraction in native space
        brain_mask = antspynet.brain_extraction(
            data.native["image"], 
            modality="t1", 
            verbose=False
        )
        brain_image = data.native["image"] * brain_mask
        
        # Update native space data
        data.native["image"] = brain_image
        data.native["brain_mask"] = brain_mask
        data.processing_steps.append("skull_stripping")
        
        return data
    
    def ants_extraction(self, data: ProcessingData, config: Dict[str, Any]) -> ProcessingData:
        """Brain extraction using ANTs."""
        if ants is None:
            raise ImportError("ANTsPy required for brain extraction")
        
        # Simple threshold-based extraction in native space
        threshold = config.get('threshold', 0.1)
        brain_mask = ants.get_mask(data.native["image"], low_thresh=threshold)
        brain_image = data.native["image"] * brain_mask
        
        # Update native space data
        data.native["image"] = brain_image
        data.native["brain_mask"] = brain_mask
        data.processing_steps.append("skull_stripping")
        
        return data