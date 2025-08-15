#!/usr/bin/env python3
"""
Run script for Mortgage Processing Agent API
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mortgage_processor.app import main

if __name__ == "__main__":
    main()
