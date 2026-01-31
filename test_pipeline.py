"""
Test script for pipeline without real data.
"""
import yaml
from pathlib import Path
from src.pipeline import PreprocessingPipeline


def test_pipeline_init():
    """Test pipeline initialization."""
    print("=" * 60)
    print("Testing Pipeline Initialization")
    print("=" * 60)
    
    # Load config
    config_path = Path("config/pipeline_config.yaml")
    
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        return False
    
    try:
        # Initialize pipeline
        pipeline = PreprocessingPipeline(config_path)
        
        # Print configuration
        print("\nPipeline Configuration:")
        config_summary = pipeline.get_config_summary()
        for key, value in config_summary.items():
            print(f"  {key}: {value}")
        
        # Print enabled processors
        print("\nEnabled Processors:")
        for name in pipeline.processors.keys():
            print(f"  - {name}")
        
        print("\n" + "=" * 60)
        print("Pipeline initialization successful!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test configuration loading."""
    print("\n" + "=" * 60)
    print("Testing Configuration Loading")
    print("=" * 60)
    
    config_path = Path("config/pipeline_config.yaml")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print("\nConfiguration Structure:")
    for key in config.keys():
        if isinstance(config[key], dict):
            enabled = config[key].get('enabled', 'N/A')
            print(f"  {key}: enabled={enabled}")
        else:
            print(f"  {key}: {type(config[key]).__name__}")
    
    return True


if __name__ == "__main__":
    print("\nMRI Preprocessing Pipeline Test Suite")
    print("=" * 60)
    
    # Test 1: Config loading
    test1 = test_config_loading()
    
    # Test 2: Pipeline initialization
    test2 = test_pipeline_init()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Config loading: {'PASS' if test1 else 'FAIL'}")
    print(f"Pipeline init: {'PASS' if test2 else 'FAIL'}")
    print("=" * 60)
    
    print("\nNote: To test with real data, install ANTsPy:")
    print("  pip install antspyx antspynet")
    print("\nThen run:")
    print("  python main.py --subject test --mri path/to/mri.nii.gz")
