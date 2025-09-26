#!/usr/bin/env python3
"""
Database Test Runner

Single, streamlined test runner for the mortgage knowledge graph database.
Runs essential tests to verify the system is production-ready.

Usage:
    python database/tests/run_tests.py
    python database/tests/run_tests.py --verbose

Features:
- Complete system verification
- Connection testing
- Data loading validation
- Enhanced system testing
- Clear pass/fail reporting
"""

import sys
import argparse
import logging
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.tests.test_enhanced_system import run_enhanced_system_tests

# Configure logging
def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Run the complete database test suite."""
    parser = argparse.ArgumentParser(description='Run mortgage database tests')
    parser.add_argument('--verbose', action='store_true', 
                       help='Enable verbose logging')
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    print("🏦 MORTGAGE KNOWLEDGE GRAPH TESTS")
    print("=" * 60)
    print("Running streamlined test suite for production readiness")
    print("=" * 60)
    
    try:
        # Run the enhanced system tests (most comprehensive)
        success = run_enhanced_system_tests()
        
        if success:
            print("\n🎉 ALL TESTS PASSED")
            print("=" * 40)
            print("✅ System is production-ready")
            print("✅ Database connection verified")
            print("✅ Data loading confirmed")
            print("✅ Enhanced features working")
            print("✅ Agent compatibility verified")
            print("=" * 40)
            print("💡 Your mortgage knowledge graph is ready for use!")
            return 0
        else:
            print("\n❌ TESTS FAILED")
            print("=" * 40)
            print("System requires attention before production use.")
            print("Review test output above for specific issues.")
            return 1
            
    except Exception as e:
        logger.error(f"Test runner error: {e}")
        print(f"\n❌ TEST RUNNER ERROR: {e}")
        print("Please check your setup and try again.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
