"""
Base processor class for all preprocessing steps.
"""
import os
from pathlib import Path
from typing import Dict, Any, Union

try:
    from .processing_data import ProcessingData
except ImportError:
    from processing_data import ProcessingData


class BaseProcessor:
    """
    Base class for all preprocessing steps.
    
    Provides common functionality:
    - Configuration handling
    - Method execution
    - Result saving
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.methods = {}  # Subclasses populate this
    
    def run_methods(self, data: ProcessingData, suffix: str, 
                    output_dir: Path = None) -> ProcessingData:
        """
        Execute all enabled methods on the data.
        
        Args:
            data: ProcessingData container
            suffix: Suffix for output files
            output_dir: Optional output directory for saving
            
        Returns:
            Updated ProcessingData container
        """
        # Execute enabled methods
        for method_name, method_func in self.methods.items():
            if self._is_method_enabled(method_name):
                print(f"  Applying: {method_name}")
                
                method_config = self.config['methods'][method_name]
                output_data = method_func(data, method_config)
                
                if output_data is None:
                    raise RuntimeError(f"{method_name} returned None")
                if not isinstance(output_data, ProcessingData):
                    raise TypeError(
                        f"{method_name} must return ProcessingData, "
                        f"got {type(output_data)}")
                
                data = output_data
                
                # Save intermediate result if configured
                if self._should_save_intermediate() and output_dir:
                    self._save_result(data, method_name, suffix, output_dir)
        
        return data
    
    def _is_method_enabled(self, method_name: str) -> bool:
        """Check if method is enabled in config."""
        return (method_name in self.config.get('methods', {}) and 
                self.config['methods'][method_name].get('enabled', False))
    
    def _should_save_intermediate(self) -> bool:
        """Check if intermediate results should be saved."""
        return self.config.get('save_intermediate', False)
    
    def _save_result(self, data: ProcessingData, method_name: str, 
                    suffix: str, output_dir: Path):
        """Save processing result from native space."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        filename = f"{data.subject_id}_{method_name}_{suffix}.nii.gz"
        output_path = output_dir / filename
        
        # Save native space image using ANTs
        try:
            data.native["image"].to_file(str(output_path))
            print(f"    Saved: {filename}")
        except Exception as e:
            print(f"    Warning: Could not save {filename}: {e}")
    
    def run(self, data: ProcessingData, output_dir: Path = None) -> ProcessingData:
        """
        Main run method - subclasses should implement this.
        
        Args:
            data: ProcessingData container
            output_dir: Optional output directory
            
        Returns:
            Updated ProcessingData container
        """
        raise NotImplementedError("Subclasses must implement run method")