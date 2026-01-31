"""
Simple test script for BaseProcessor and ProcessingData.
"""
import yaml
from pathlib import Path
from src.preprocessing.skull_stripping import SkullStripping
from src.preprocessing.processing_data import ProcessingData
from src.utils.file_manager import FileManager

def test_base_processor():
    """Test BaseProcessor with SkullStripping and ProcessingData."""
    
    print("=" * 60)
    print("Testing BaseProcessor with ProcessingData")
    print("=" * 60)
    
    # Load config
    config_path = Path("config/pipeline_config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create file manager
    file_manager = FileManager("output")
    
    # Create skull stripping processor
    skull_config = config['skull_stripping']
    processor = SkullStripping(skull_config)
    
    print("\n1. Configuration Test:")
    print(f"   Config loaded: {config_path}")
    print(f"   Methods available: {list(processor.methods.keys())}")
    print(f"   Enabled methods: {[m for m in processor.methods.keys() if processor._is_method_enabled(m)]}")
    print(f"   Save intermediate: {processor._should_save_intermediate()}")
    
    # Create test ProcessingData
    print("\n2. ProcessingData Test:")
    print("   Creating mock ProcessingData...")
    
    # Mock image object (since ANTs is not installed)
    class MockImage:
        def __init__(self):
            self.shape = (256, 256, 256)
        def __mul__(self, other):
            return self
        def to_file(self, path):
            print(f"      Mock save to: {path}")
    
    mock_image = MockImage()
    data = ProcessingData(mock_image, "test_subject")
    
    print(f"   Subject ID: {data.subject_id}")
    print(f"   Has brain extraction: {data.has_brain_extraction()}")
    print(f"   Has registration: {data.has_registration()}")
    print(f"   Has segmentation: {data.has_segmentation()}")
    print(f"   Processing steps: {data.processing_steps}")
    
    # Test update_primary
    print("\n3. Update Primary Test:")
    data.update_primary(mock_image, "test_step")
    print(f"   Processing steps after update: {data.processing_steps}")
    
    # Create output directory
    print("\n4. File Manager Test:")
    dirs = file_manager.create_subject_dirs('test_subject')
    print(f"   Created directories:")
    for name, path in dirs.items():
        print(f"      {name}: {path}")
    
    # Test processing summary
    print("\n5. Processing Summary:")
    summary = data.get_processing_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("BaseProcessor and ProcessingData setup successful!")
    print("=" * 60)
    print("\nNote: To test with real images, install ANTsPy:")
    print("  pip install antspyx antspynet")

if __name__ == "__main__":
    test_base_processor()