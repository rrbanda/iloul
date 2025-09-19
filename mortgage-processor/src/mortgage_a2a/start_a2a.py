#!/usr/bin/env python3
"""
A2A System Launcher

Entry point to start the mortgage A2A system.
"""
import sys
from pathlib import Path

# Add parent src directory to Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

def main():
    """Start the A2A system"""
    try:
        from mortgage_a2a.scripts.start_a2a_system import main as start_system
        start_system()
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f" Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
