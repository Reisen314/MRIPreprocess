"""
PET preprocessing using MRI results.
"""
from pathlib import Path
from typing import Dict, Any
from .processing_data import ProcessingData

try:
    import ants
except ImportError:
    print("Warning: ANTsPy not available")
    ants = None


class PETProcessor:
    """
    PET preprocessing that depends on MRI processing results.
    
    Processing steps:
    1. Register PET to MRI native space (rigid registration)
    2. Apply MRI brain mask to PET
    3. Transform PET to MNI space using MRI transforms
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def run(self, data: ProcessingData, output_dir: Path = None) -> ProcessingData:
        """
        Process PET using MRI results.
        
        Args:
            data: ProcessingData container with MRI results
            output_dir: Optional output directory
            
        Returns:
            Updated ProcessingData container
        """
        if data.pet["original"] is None:
            return data  # No PET data to process
        
        if ants is None:
            raise ImportError("ANTsPy required for PET processing")
        
        print("Executing: PET processing")
        
        # Step 1: Register PET to MRI native space
        print("  Step 1: Registering PET to MRI native space...")
        self._register_to_mri(data)
        
        # Step 2: Apply MRI brain mask
        print("  Step 2: Applying brain mask...")
        self._apply_brain_mask(data)
        
        # Step 3: Transform to MNI space
        print("  Step 3: Transforming to MNI space...")
        self._transform_to_mni(data)
        
        data.processing_steps.append("pet_processing")
        
        # Save intermediate results if configured
        if self.config.get('save_intermediate', False) and output_dir:
            self._save_results(data, output_dir)
        
        return data
    
    def _register_to_mri(self, data: ProcessingData):
        """Rigid registration: PET → MRI native space."""
        if data.native["image"] is None:
            print("    Warning: No MRI image available, skipping registration")
            return
        
        print("    Applying rigid registration...")
        result = ants.registration(
            fixed=data.native["image"],      # MRI as fixed
            moving=data.pet["original"],     # PET as moving
            type_of_transform='Rigid',
            verbose=False
        )
        
        data.pet["registered_to_mri"] = result['warpedmovout']
        print("    PET registered to MRI native space")
    
    def _apply_brain_mask(self, data: ProcessingData):
        """Apply MRI brain mask to registered PET."""
        if data.pet["registered_to_mri"] is None:
            print("    Warning: No registered PET available, skipping masking")
            return
        
        if data.native["brain_mask"] is not None:
            pet_masked = data.pet["registered_to_mri"] * data.native["brain_mask"]
            data.pet["skull_stripped"] = pet_masked
            print("    Brain mask applied to PET")
        else:
            # If no brain mask, use registered PET directly
            data.pet["skull_stripped"] = data.pet["registered_to_mri"]
            print("    Warning: No brain mask available, using registered PET")
    
    def _transform_to_mni(self, data: ProcessingData):
        """Apply MRI→MNI transform to PET."""
        if data.pet["skull_stripped"] is None:
            print("    Warning: No skull-stripped PET available, skipping MNI transform")
            return
        
        # Check if MRI→MNI transform is available
        if data.transforms["native_to_template"] is None:
            print("    Warning: No MRI→MNI transform available, skipping")
            return
        
        # Check if template image is available
        if data.template["image"] is None:
            print("    Warning: No template image available, skipping")
            return
        
        # Apply transform
        data.pet["mni"] = ants.apply_transforms(
            fixed=data.template["image"],
            moving=data.pet["skull_stripped"],
            transformlist=data.transforms["native_to_template"],
            interpolator='linear'
        )
        print("    PET transformed to MNI space")
    
    def _save_results(self, data: ProcessingData, output_dir: Path):
        """Save PET processing results."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save registered PET
        if data.pet["registered_to_mri"] is not None:
            path = output_dir / f"{data.subject_id}_PET_registered.nii.gz"
            data.pet["registered_to_mri"].to_file(str(path))
            print(f"    Saved: {path.name}")
        
        # Save skull-stripped PET
        if data.pet["skull_stripped"] is not None:
            path = output_dir / f"{data.subject_id}_PET_skull_stripped.nii.gz"
            data.pet["skull_stripped"].to_file(str(path))
            print(f"    Saved: {path.name}")
