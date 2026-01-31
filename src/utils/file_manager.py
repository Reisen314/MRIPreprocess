"""
File management utilities.
"""
import os
from pathlib import Path
from typing import Union, Dict


class FileManager:
    """Handles file and directory operations."""
    
    def __init__(self, base_output_dir: Union[str, Path]):
        self.base_output_dir = Path(base_output_dir)
    
    def create_subject_dirs(self, subject_id: str) -> Dict[str, Path]:
        """
        Create directory structure for a subject.
        
        Returns:
            Dictionary with directory paths
        """
        subject_dir = self.base_output_dir / subject_id
        
        dirs = {
            'base': subject_dir,
            'intermediate': subject_dir / 'intermediate',
            'final': subject_dir / 'final',
            'qc': subject_dir / 'qc',
            'logs': subject_dir / 'logs'
        }
        
        # Create all directories
        for dir_path in dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return dirs
    
    def get_output_path(self, subject_id: str, filename: str, 
                       subdir: str = 'intermediate') -> Path:
        """Get output path for a file."""
        return self.base_output_dir / subject_id / subdir / filename
    
    def save_image(self, image, subject_id: str, filename: str, 
                   subdir: str = 'intermediate'):
        """
        Save ANTs image to file.
        
        Args:
            image: ANTs Image object
            subject_id: Subject identifier
            filename: Output filename
            subdir: Subdirectory name
        """
        output_path = self.get_output_path(subject_id, filename, subdir)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            image.to_file(str(output_path))
            return output_path
        except Exception as e:
            print(f"Warning: Could not save {filename}: {e}")
            return None
    
    def save_transform(self, transform, subject_id: str, filename: str,
                      subdir: str = 'intermediate'):
        """
        Save transform matrix to file.
        
        Args:
            transform: ANTs transform object or path
            subject_id: Subject identifier
            filename: Output filename
            subdir: Subdirectory name
        """
        output_path = self.get_output_path(subject_id, filename, subdir)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Transform is usually a file path from ANTs
        # Just record the path or copy if needed
        return output_path
    
    def get_subject_dir(self, subject_id: str) -> Path:
        """Get base directory for a subject."""
        return self.base_output_dir / subject_id
    
    def get_intermediate_dir(self, subject_id: str) -> Path:
        """Get intermediate directory for a subject."""
        return self.base_output_dir / subject_id / 'intermediate'
    
    def get_final_dir(self, subject_id: str) -> Path:
        """Get final output directory for a subject."""
        return self.base_output_dir / subject_id / 'final'
    
    def get_qc_dir(self, subject_id: str) -> Path:
        """Get QC directory for a subject."""
        return self.base_output_dir / subject_id / 'qc'