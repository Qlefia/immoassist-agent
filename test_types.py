#!/usr/bin/env python3
"""
Simple type checking test for core modules.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports() -> None:
    """Test that all core modules can be imported."""
    try:
        from app import __author__, __version__
        print(f"✓ app/__init__.py: {__version__} by {__author__}")

        from app.config import config
        print(f"✓ app/config.py: {config.environment} environment")

        # Test exceptions module
        import app.exceptions
        print("✓ app/exceptions.py: Exception classes imported")

        # Test logging module
        import app.logging_config
        print("✓ app/logging_config.py: Logging functions imported")

        print("\n🎉 All core modules imported successfully!")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()
