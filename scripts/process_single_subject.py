"""
Process a single subject through the preprocessing pipeline.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import main

if __name__ == '__main__':
    sys.exit(main())
