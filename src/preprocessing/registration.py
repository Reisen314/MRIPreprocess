"""
Image registration processor using ANTs.
"""
from pathlib import Path
from typing import Dict, Any
from .processing_data import ProcessingData

try:
    import ants
except ImportError:
    print("Warning: ANTsPy not available")
    ants = None


class Registration:
    """Image registration to template space using ANTs."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.template_path = Path(config['template'])
        self.template = None
    
    def _load_template(self):
        """Load template image."""
        if self.template is None:
            if not self.template_path.exists():
                raise FileNotFoundError(
                    f"Template file not found: {self.template_path}\n"
                    f"Please download MNI152 template and place it at the specified path.\n"
                    f"You can disable registration in config if template is not available."
                )
            if ants is None:
                raise ImportError("ANTsPy required for registration")
            
            print(f"  Loading template: {self.template_path.name}")
            self.template = ants.image_read(str(self.template_path))
            print(f"  Template loaded successfully: shape {self.template.shape}")
    
    def run(self, data: ProcessingData, output_dir: Path = None) -> ProcessingData:
        """
        Register native image to template space and transform all native data.
        
        Args:
            data: ProcessingData container
            output_dir: Optional output directory
            
        Returns:
            Updated ProcessingData container
        """
        if ants is None:
            raise ImportError("ANTsPy required for registration")
        
        print("Executing: registration (native -> template)")
        
        # Load template
        self._load_template()
        
        # Determine which registration method to use
        if self.config['methods']['syn']['enabled']:
            result = self._syn_registration(data)
        elif self.config['methods']['affine']['enabled']:
            result = self._affine_registration(data)
        elif self.config['methods']['rigid']['enabled']:
            result = self._rigid_registration(data)
        else:
            raise ValueError("No registration method enabled")
        
        # Store template space image and transforms
        data.template["image"] = result['warpedmovout']
        data.transforms["native_to_template"] = result['fwdtransforms']
        data.transforms["template_to_native"] = result['invtransforms']
        
        # Transform all native space data to template space
        self._transform_all_to_template(data)
        
        data.processing_steps.append("registration")
        
        # Save intermediate results if configured
        if self.config.get('save_intermediate', False) and output_dir:
            self._save_results(data, output_dir)
        
        return data
    
    def _syn_registration(self, data: ProcessingData) -> Dict:
        """SyN non-linear registration."""
        config = self.config['methods']['syn']
        
        print("  Applying: SyN registration")
        
        result = ants.registration(
            fixed=self.template,
            moving=data.native["image"],
            type_of_transform='SyN',
            grad_step=config.get('grad_step', 0.1),
            flow_sigma=config.get('flow_sigma', 3),
            total_sigma=config.get('total_sigma', 0),
            verbose=False
        )
        
        return result
    
    def _affine_registration(self, data: ProcessingData) -> Dict:
        """Affine registration."""
        print("  Applying: Affine registration")
        
        result = ants.registration(
            fixed=self.template,
            moving=data.native["image"],
            type_of_transform='Affine',
            verbose=False
        )
        
        return result
    
    def _rigid_registration(self, data: ProcessingData) -> Dict:
        """Rigid registration."""
        print("  Applying: Rigid registration")
        
        result = ants.registration(
            fixed=self.template,
            moving=data.native["image"],
            type_of_transform='Rigid',
            verbose=False
        )
        
        return result
    
    def _transform_all_to_template(self, data: ProcessingData):
        """Transform all native space data to template space."""
        print("  Transforming native data to template space...")
        
        # Transform brain mask (nearest neighbor for binary mask)
        if data.native["brain_mask"] is not None:
            data.transform_to_template("brain_mask", interpolator='nearestNeighbor')
            print("    - brain_mask")
        
        # Transform segmentation labels (nearest neighbor for labels)
        if data.native["segmentation_labels"] is not None:
            data.transform_to_template("segmentation_labels", interpolator='nearestNeighbor')
            print("    - segmentation_labels")
        
        # Transform probability maps (linear interpolation)
        for tissue in ["csf_probability", "gm_probability", "wm_probability"]:
            if data.native[tissue] is not None:
                data.transform_to_template(tissue, interpolator='linear')
                print(f"    - {tissue}")
    
    def _save_results(self, data: ProcessingData, output_dir: Path):
        """Save registration results from template space."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save registered image
        if data.template["image"] is not None:
            registered_path = output_dir / f"{data.subject_id}_registered.nii.gz"
            data.template["image"].to_file(str(registered_path))
            print(f"    Saved: {registered_path.name}")
        
        # Note: Transform matrices are saved by ANTs automatically
        if data.transforms["native_to_template"]:
            print(f"    Transform saved by ANTs")
