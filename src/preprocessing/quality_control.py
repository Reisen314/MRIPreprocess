"""
Quality control processor.
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


class QualityControl:
    """Quality control and metrics calculation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.template_path = None
        self.template = None
        
        # Try to get template path from config
        if 'template' in config:
            self.template_path = Path(config['template'])
    
    def run(self, data: ProcessingData, output_dir: Path = None) -> ProcessingData:
        """
        Perform quality control checks.
        
        Args:
            data: ProcessingData container
            output_dir: Optional output directory
            
        Returns:
            Updated ProcessingData container
        """
        print("Executing: quality_control")
        
        # Calculate quality metrics
        metrics = {}
        
        # Image quality metrics
        if data.native["original_image"] is not None:
            metrics.update(self._calculate_image_quality(data))
        
        # Registration quality metrics
        if data.has_registration() and self.template_path:
            metrics.update(self._calculate_registration_quality(data))
        
        # Segmentation quality metrics
        if data.has_segmentation():
            metrics.update(self._calculate_segmentation_quality(data))
        
        # Processing summary
        metrics['processing_steps'] = data.processing_steps.copy()
        metrics['num_steps'] = len(data.processing_steps)
        
        # Update data container
        data.qc_metrics = metrics
        data.processing_steps.append("quality_control")
        
        # Generate report if configured
        if self.config.get('generate_report', False) and output_dir:
            self._generate_report(data, output_dir)
        
        # Check thresholds
        self._check_thresholds(metrics)
        
        return data
    
    def _calculate_image_quality(self, data: ProcessingData) -> Dict[str, float]:
        """Calculate basic image quality metrics from native space."""
        print("  Calculating image quality metrics")
        
        metrics = {}
        
        # SNR calculation using native space data
        if data.native["brain_mask"] is not None:
            brain_data = data.native["image"].numpy()
            mask_data = data.native["brain_mask"].numpy()
            
            # Signal: mean intensity in brain
            signal = np.mean(brain_data[mask_data > 0])
            
            # Noise: std of background
            background = brain_data[mask_data == 0]
            if len(background) > 0:
                noise = np.std(background)
                if noise > 0:
                    snr = signal / noise
                    metrics['snr'] = float(snr)
                    print(f"    SNR: {snr:.2f}")
        
        return metrics
    
    def _calculate_registration_quality(self, data: ProcessingData) -> Dict[str, float]:
        """Calculate registration quality metrics from template space."""
        print("  Calculating registration quality metrics")
        
        metrics = {}
        
        if ants is None:
            return metrics
        
        # Load template if needed (optional for QC)
        if self.template is None and self.template_path:
            if self.template_path.exists():
                try:
                    self.template = ants.image_read(str(self.template_path))
                    print(f"    Loaded template for QC: {self.template_path.name}")
                except Exception as e:
                    print(f"    Warning: Could not load template for QC: {e}")
            else:
                print(f"    Note: Template not found for registration QC: {self.template_path}")
        
        if self.template is not None and data.template["image"] is not None:
            # Mutual information
            try:
                mi = ants.image_mutual_information(
                    data.template["image"], 
                    self.template
                )
                metrics['registration_mi'] = float(mi)
                print(f"    Registration MI: {mi:.4f}")
            except Exception as e:
                print(f"    Warning: Could not calculate MI: {e}")
        
        return metrics
    
    def _calculate_segmentation_quality(self, data: ProcessingData) -> Dict[str, float]:
        """Calculate segmentation quality metrics from template space."""
        print("  Calculating segmentation quality metrics")
        
        metrics = {}
        
        # Use template space data if available, otherwise native
        space = data.template if data.has_registration() else data.native
        
        # Volume calculations
        if space["gm_probability"] is not None:
            gm_data = space["gm_probability"].numpy()
            gm_volume = np.sum(gm_data > 0.5)
            metrics['gm_volume'] = float(gm_volume)
            print(f"    GM volume: {gm_volume:.0f} voxels")
        
        if space["wm_probability"] is not None:
            wm_data = space["wm_probability"].numpy()
            wm_volume = np.sum(wm_data > 0.5)
            metrics['wm_volume'] = float(wm_volume)
            print(f"    WM volume: {wm_volume:.0f} voxels")
        
        return metrics
    
    def _check_thresholds(self, metrics: Dict[str, float]):
        """Check if metrics meet quality thresholds."""
        thresholds = self.config.get('thresholds', {})
        
        warnings = []
        
        # Check SNR
        if 'snr' in metrics and 'snr_min' in thresholds:
            if metrics['snr'] < thresholds['snr_min']:
                warnings.append(f"SNR ({metrics['snr']:.2f}) below threshold ({thresholds['snr_min']})")
        
        # Check registration MI
        if 'registration_mi' in metrics and 'registration_mi_min' in thresholds:
            if metrics['registration_mi'] < thresholds['registration_mi_min']:
                warnings.append(f"Registration MI ({metrics['registration_mi']:.4f}) below threshold ({thresholds['registration_mi_min']})")
        
        if warnings:
            print("  Quality warnings:")
            for warning in warnings:
                print(f"    - {warning}")
        else:
            print("  All quality checks passed")
    
    def _generate_report(self, data: ProcessingData, output_dir: Path):
        """Generate QC report."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = output_dir / f"{data.subject_id}_qc_report.txt"
        
        with open(report_path, 'w') as f:
            f.write(f"Quality Control Report\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Subject ID: {data.subject_id}\n")
            f.write(f"Processing Steps: {', '.join(data.processing_steps)}\n\n")
            
            f.write(f"Quality Metrics:\n")
            f.write(f"-" * 50 + "\n")
            for key, value in data.qc_metrics.items():
                if key not in ['processing_steps', 'num_steps']:
                    f.write(f"{key}: {value}\n")
        
        print(f"    Saved: {report_path.name}")
