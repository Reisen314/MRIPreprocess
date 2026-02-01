"""
Main preprocessing pipeline orchestrator.
"""
import yaml
from pathlib import Path
from typing import Union, Dict, Any

from .preprocessing import (
    ProcessingData,
    SkullStripping,
    Registration,
    Segmentation,
    ROIExtraction,
    QualityControl
)
from .utils.file_manager import FileManager

try:
    import ants
except ImportError:
    print("Warning: ANTsPy not available")
    ants = None


class PreprocessingPipeline:
    """
    Main preprocessing pipeline orchestrator.
    
    Manages the execution of all preprocessing steps in sequence,
    handling configuration, data flow, and output management.
    """
    
    def __init__(self, config_path: Union[str, Path]):
        """
        Initialize preprocessing pipeline.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Initialize file manager
        output_base = self.config['output']['base_dir']
        self.file_manager = FileManager(output_base)
        
        # Initialize processors
        self._init_processors()
        
        print(f"Pipeline initialized with config: {self.config_path.name}")
        print(f"Output directory: {output_base}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _init_processors(self):
        """Initialize all processing modules."""
        self.processors = {}
        
        # Initialize enabled processors
        if self.config['skull_stripping']['enabled']:
            self.processors['skull_stripping'] = SkullStripping(
                self.config['skull_stripping']
            )
        
        if self.config['registration']['enabled']:
            self.processors['registration'] = Registration(
                self.config['registration']
            )
        
        if self.config['segmentation']['enabled']:
            self.processors['segmentation'] = Segmentation(
                self.config['segmentation']
            )
        
        if self.config['roi_extraction']['enabled']:
            self.processors['roi_extraction'] = ROIExtraction(
                self.config['roi_extraction']
            )
        
        if self.config['quality_control']['enabled']:
            self.processors['quality_control'] = QualityControl(
                self.config['quality_control']
            )
        
        # Initialize PET processor if enabled
        if self.config.get('pet_processing', {}).get('enabled', False):
            from .preprocessing.pet_processor import PETProcessor
            self.processors['pet_processing'] = PETProcessor(
                self.config['pet_processing']
            )
        
        print(f"Enabled processors: {list(self.processors.keys())}")
    
    def run(self, subject_id: str, mri_path: Union[str, Path], 
            pet_path: Union[str, Path] = None,
            output_dir: Path = None) -> ProcessingData:
        """
        Run the complete preprocessing pipeline on a subject.
        
        Args:
            subject_id: Subject identifier
            mri_path: Path to input MRI image
            pet_path: Optional path to input PET image
            output_dir: Optional custom output directory
            
        Returns:
            ProcessingData container with all results
        """
        if ants is None:
            raise ImportError("ANTsPy required to run pipeline")
        
        print("\n" + "=" * 60)
        print(f"Processing Subject: {subject_id}")
        print("=" * 60)
        
        # Load input image
        mri_path = Path(mri_path)
        if not mri_path.exists():
            raise FileNotFoundError(f"MRI file not found: {mri_path}")
        
        print(f"Loading: {mri_path.name}")
        original_image = ants.image_read(str(mri_path))
        print(f"Image shape: {original_image.shape}")
        
        # Load PET image (optional)
        pet_image = None
        if pet_path is not None:
            pet_path = Path(pet_path)
            if pet_path.exists():
                print(f"Loading PET: {pet_path.name}")
                pet_image = ants.image_read(str(pet_path))
                print(f"PET shape: {pet_image.shape}")
            else:
                print(f"Warning: PET file not found: {pet_path}")
        
        # Initialize data container
        data = ProcessingData(original_image, subject_id, pet_image)
        
        # Setup output directories
        if output_dir is None:
            output_dir = self.file_manager.get_intermediate_dir(subject_id)
        else:
            output_dir = Path(output_dir)
        
        self.file_manager.create_subject_dirs(subject_id)
        
        # Execute processing steps in order (segmentation before registration)
        step_order = [
            'skull_stripping',
            'segmentation',      # Moved before registration
            'registration',
            'pet_processing',    # PET processing after registration
            'roi_extraction',
            'quality_control'
        ]
        
        for step_name in step_order:
            if step_name in self.processors:
                print(f"\n{'-' * 60}")
                try:
                    processor = self.processors[step_name]
                    # Use qc directory for quality_control, intermediate for others
                    if step_name == 'quality_control':
                        qc_dir = self.file_manager.get_qc_dir(subject_id)
                        data = processor.run(data, qc_dir)
                    else:
                        data = processor.run(data, output_dir)
                    print(f"Completed: {step_name}")
                except Exception as e:
                    print(f"Error in {step_name}: {str(e)}")
                    raise
        
        # Save final summary
        self._save_summary(data, output_dir)
        
        # Save final results
        self._save_final_results(data, subject_id)
        
        print("\n" + "=" * 60)
        print(f"Pipeline completed for subject: {subject_id}")
        print(f"Processing steps: {' -> '.join(data.processing_steps)}")
        print("=" * 60 + "\n")
        
        return data
    
    def _save_summary(self, data: ProcessingData, output_dir: Path):
        """Save processing summary."""
        summary_path = output_dir / f"{data.subject_id}_summary.txt"
        
        with open(summary_path, 'w') as f:
            f.write("Preprocessing Summary\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Subject ID: {data.subject_id}\n")
            f.write(f"Processing Steps: {len(data.processing_steps)}\n")
            f.write(f"Steps: {' -> '.join(data.processing_steps)}\n\n")
            
            f.write("Results:\n")
            f.write("-" * 60 + "\n")
            f.write(f"Brain extraction: {'Yes' if data.has_brain_extraction() else 'No'}\n")
            f.write(f"Registration: {'Yes' if data.has_registration() else 'No'}\n")
            f.write(f"Segmentation: {'Yes' if data.has_segmentation() else 'No'}\n")
            f.write(f"ROI features: {'Yes' if data.template.get('roi_features') else 'No'}\n\n")
            
            if data.qc_metrics:
                f.write("Quality Metrics:\n")
                f.write("-" * 60 + "\n")
                for key, value in data.qc_metrics.items():
                    if key not in ['processing_steps', 'num_steps']:
                        f.write(f"{key}: {value}\n")
        
        print(f"\nSaved summary: {summary_path.name}")
    
    def _save_final_results(self, data: ProcessingData, subject_id: str):
        """Save final results to final/ directory."""
        final_dir = self.file_manager.get_final_dir(subject_id)
        final_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\nSaving final results to: {final_dir}")
        
        # Save template space images (final standardized results)
        if data.template["image"] is not None:
            path = final_dir / f"{subject_id}_T1_MNI.nii.gz"
            data.template["image"].to_file(str(path))
            print(f"  Saved: {path.name}")
        
        if data.template["brain_mask"] is not None:
            path = final_dir / f"{subject_id}_brain_mask_MNI.nii.gz"
            data.template["brain_mask"].to_file(str(path))
            print(f"  Saved: {path.name}")
        
        if data.template["gm_probability"] is not None:
            path = final_dir / f"{subject_id}_GM_probability_MNI.nii.gz"
            data.template["gm_probability"].to_file(str(path))
            print(f"  Saved: {path.name}")
        
        if data.template["wm_probability"] is not None:
            path = final_dir / f"{subject_id}_WM_probability_MNI.nii.gz"
            data.template["wm_probability"].to_file(str(path))
            print(f"  Saved: {path.name}")
        
        if data.template["csf_probability"] is not None:
            path = final_dir / f"{subject_id}_CSF_probability_MNI.nii.gz"
            data.template["csf_probability"].to_file(str(path))
            print(f"  Saved: {path.name}")
        
        if data.template["segmentation_labels"] is not None:
            path = final_dir / f"{subject_id}_segmentation_MNI.nii.gz"
            data.template["segmentation_labels"].to_file(str(path))
            print(f"  Saved: {path.name}")
        
        # Save ROI features
        if data.template.get("roi_features") is not None:
            import numpy as np
            for feature_name, feature_array in data.template["roi_features"].items():
                path = final_dir / f"{subject_id}_{feature_name}.npy"
                np.save(str(path), feature_array)
                print(f"  Saved: {path.name}")
        
        # Save PET results
        if data.pet["mni"] is not None:
            path = final_dir / f"{subject_id}_PET_MNI.nii.gz"
            data.pet["mni"].to_file(str(path))
            print(f"  Saved: {path.name}")
        
        if data.pet["skull_stripped"] is not None:
            path = final_dir / f"{subject_id}_PET_skull_stripped.nii.gz"
            data.pet["skull_stripped"].to_file(str(path))
            print(f"  Saved: {path.name}")
        
        # Save final summary
        summary_path = final_dir / f"{subject_id}_final_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("Final Processing Results\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Subject ID: {subject_id}\n")
            f.write(f"Processing Steps: {' -> '.join(data.processing_steps)}\n\n")
            
            f.write("Final Outputs (MNI Space):\n")
            f.write("-" * 60 + "\n")
            f.write(f"T1 Image: {subject_id}_T1_MNI.nii.gz\n")
            f.write(f"Brain Mask: {subject_id}_brain_mask_MNI.nii.gz\n")
            f.write(f"GM Probability: {subject_id}_GM_probability_MNI.nii.gz\n")
            f.write(f"WM Probability: {subject_id}_WM_probability_MNI.nii.gz\n")
            f.write(f"CSF Probability: {subject_id}_CSF_probability_MNI.nii.gz\n")
            f.write(f"Segmentation: {subject_id}_segmentation_MNI.nii.gz\n")
            
            if data.pet["mni"] is not None:
                f.write(f"\nPET Results:\n")
                f.write(f"PET MNI: {subject_id}_PET_MNI.nii.gz\n")
                f.write(f"PET Skull-stripped: {subject_id}_PET_skull_stripped.nii.gz\n")
            
            if data.template.get("roi_features"):
                f.write(f"\nROI Features:\n")
                for feature_name in data.template["roi_features"].keys():
                    f.write(f"  - {subject_id}_{feature_name}.npy\n")
            
            if data.qc_metrics:
                f.write(f"\nQuality Metrics:\n")
                f.write("-" * 60 + "\n")
                for key, value in data.qc_metrics.items():
                    if key not in ['processing_steps', 'num_steps']:
                        f.write(f"{key}: {value}\n")
        
        print(f"  Saved: {summary_path.name}")
        print(f"\nFinal results saved to: {final_dir}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of pipeline configuration."""
        return {
            'version': self.config['general']['version'],
            'enabled_steps': list(self.processors.keys()),
            'output_dir': self.config['output']['base_dir'],
            'save_intermediate': self.config['general']['save_intermediate']
        }
