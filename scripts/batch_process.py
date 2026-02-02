"""
Batch processing script for multiple subjects.
"""
import argparse
import sys
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import PreprocessingPipeline


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Batch MRI Preprocessing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all MRI subjects in a directory
  python scripts/batch_process.py --input data/ --pattern "*_T1.nii.gz"
  
  # Process MRI + PET
  python scripts/batch_process.py --input data/ --pattern "*_T1.nii.gz" --pet-pattern "*_PET.nii.gz"
  
  # Use subject list file
  python scripts/batch_process.py --subject-list subjects.txt --input data/
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        type=Path,
        help='Input directory containing MRI files'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        default='*.nii.gz',
        help='File pattern to match MRI files (default: *.nii.gz)'
    )
    
    parser.add_argument(
        '--pet-pattern',
        help='File pattern to match PET files (optional)'
    )
    
    parser.add_argument(
        '--subject-list', '-l',
        type=Path,
        help='Text file with subject IDs (one per line)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=Path,
        default=Path('config/pipeline_config.yaml'),
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Custom output directory (optional)'
    )
    
    return parser.parse_args()


def find_subjects(input_dir: Path, pattern: str, 
                 pet_pattern: str = None,
                 subject_list: Path = None) -> List[Tuple[str, Path, Path]]:
    """
    Find subjects to process.
    
    Returns:
        List of (subject_id, mri_path, pet_path) tuples
    """
    subjects = []
    
    if subject_list and subject_list.exists():
        # Load from subject list
        with open(subject_list, 'r') as f:
            subject_ids = [line.strip() for line in f if line.strip()]
        
        for subject_id in subject_ids:
            # Try to find matching MRI file
            mri_matches = list(input_dir.glob(f"*{subject_id}*{pattern}"))
            if mri_matches:
                mri_path = mri_matches[0]
                
                # Try to find matching PET file
                pet_path = None
                if pet_pattern:
                    # Build search pattern, avoiding double wildcards
                    pet_search_pattern = f"*{subject_id}*" + pet_pattern.lstrip('*')
                    pet_matches = list(input_dir.glob(pet_search_pattern))
                    if pet_matches:
                        pet_path = pet_matches[0]
                
                subjects.append((subject_id, mri_path, pet_path))
            else:
                print(f"Warning: No MRI file found for subject {subject_id}")
    else:
        # Find all matching MRI files
        for mri_path in input_dir.glob(pattern):
            # Extract subject ID from filename
            # Remove .nii.gz or .nii extension first
            filename = mri_path.name
            if filename.endswith('.nii.gz'):
                filename = filename[:-7]
            elif filename.endswith('.nii'):
                filename = filename[:-4]
            
            # Extract subject ID (remove modality suffix like _T1, _PET)
            # Assume subject ID is everything before the last underscore
            parts = filename.rsplit('_', 1)
            subject_id = parts[0] if len(parts) > 1 else filename
            
            # Try to find matching PET file
            pet_path = None
            if pet_pattern:
                # Build search pattern, avoiding double wildcards
                pet_search_pattern = f"*{subject_id}*" + pet_pattern.lstrip('*')
                pet_matches = list(input_dir.glob(pet_search_pattern))
                if pet_matches:
                    pet_path = pet_matches[0]
            
            subjects.append((subject_id, mri_path, pet_path))
    
    return subjects


def main():
    """Main function."""
    args = parse_args()
    
    # Validate inputs
    if not args.input.exists():
        print(f"Error: Input directory not found: {args.input}")
        return 1
    
    if not args.config.exists():
        print(f"Error: Config file not found: {args.config}")
        return 1
    
    # Find subjects
    subjects = find_subjects(args.input, args.pattern, args.pet_pattern, args.subject_list)
    
    if not subjects:
        print("Error: No subjects found")
        return 1
    
    print(f"\nFound {len(subjects)} subjects to process")
    print("=" * 60)
    
    # Initialize pipeline
    try:
        pipeline = PreprocessingPipeline(args.config)
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        return 1
    
    # Process each subject
    results = []
    failed = []
    
    for i, (subject_id, mri_path, pet_path) in enumerate(subjects, 1):
        print(f"\n[{i}/{len(subjects)}] Processing: {subject_id}")
        if pet_path:
            print(f"  MRI: {mri_path.name}")
            print(f"  PET: {pet_path.name}")
        print("-" * 60)
        
        try:
            result = pipeline.run(
                subject_id=subject_id,
                mri_path=mri_path,
                pet_path=pet_path,
                output_dir=args.output
            )
            results.append((subject_id, result))
            print(f"Success: {subject_id}")
            
        except Exception as e:
            print(f"Failed: {subject_id}")
            print(f"Error: {str(e)}")
            failed.append((subject_id, str(e)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Batch Processing Summary")
    print("=" * 60)
    print(f"Total subjects: {len(subjects)}")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed subjects:")
        for subject_id, error in failed:
            print(f"  - {subject_id}: {error}")
    
    return 0 if len(failed) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
