#!/usr/bin/env python3
"""
A2A System Test Launcher

Entry point to test the mortgage A2A system.
"""
import sys
import asyncio
from pathlib import Path

# Add parent src directory to Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

def main():
    """Test the A2A system"""
    try:
        from mortgage_a2a.tests.test_a2a_system import main as test_system
        success = asyncio.run(test_system())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f" Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
