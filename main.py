"""
Main entry point for MRI preprocessing pipeline.
"""
import argparse
from pathlib import Path
from src.pipeline import PreprocessingPipeline


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='MRI Preprocessing Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single subject (MRI only)
  python main.py --subject sub001 --mri data/sub001_T1.nii.gz
  
  # Process with PET
  python main.py --subject sub001 --mri data/sub001_T1.nii.gz --pet data/sub001_PET.nii.gz
  
  # Use custom config
  python main.py --subject sub001 --mri data/sub001_T1.nii.gz --config custom_config.yaml
  
  # Custom output directory
  python main.py --subject sub001 --mri data/sub001_T1.nii.gz --output results/
        """
    )
    
    parser.add_argument(
        '--subject', '-s',
        required=True,
        help='Subject ID'
    )
    
    parser.add_argument(
        '--mri', '-m',
        required=True,
        type=Path,
        help='Path to T1 MRI file (.nii or .nii.gz)'
    )
    
    parser.add_argument(
        '--pet', '-p',
        type=Path,
        help='Path to PET image (optional, will be registered to MRI)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=Path,
        default=Path('config/pipeline_config.yaml'),
        help='Path to configuration file (default: config/pipeline_config.yaml)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Custom output directory (optional)'
    )
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    
    # Validate inputs
    if not args.mri.exists():
        print(f"Error: MRI file not found: {args.mri}")
        return 1
    
    if not args.config.exists():
        print(f"Error: Config file not found: {args.config}")
        return 1
    
    try:
        # Initialize pipeline
        pipeline = PreprocessingPipeline(args.config)
        
        # Print configuration summary
        config_summary = pipeline.get_config_summary()
        print("\nPipeline Configuration:")
        print(f"  Version: {config_summary['version']}")
        print(f"  Enabled steps: {', '.join(config_summary['enabled_steps'])}")
        print(f"  Output directory: {config_summary['output_dir']}")
        
        # Run pipeline
        result = pipeline.run(
            subject_id=args.subject,
            mri_path=args.mri,
            pet_path=args.pet,
            output_dir=args.output
        )
        
        # Print final summary
        print("\nProcessing Summary:")
        summary = result.get_processing_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
