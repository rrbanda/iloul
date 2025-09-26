#!/usr/bin/env python3
"""
Mortgage Knowledge Graph Data Loader

Production-grade script to load complete mortgage knowledge graph into Neo4j.
This script provides a simple interface to load all mortgage data with
comprehensive error handling and progress reporting.

Usage:
    python load_mortgage_data.py                    # Load all data
    python load_mortgage_data.py --verify-only      # Verify existing data
    python load_mortgage_data.py --clear-first      # Clear existing data first
    python load_mortgage_data.py --verbose          # Detailed logging

Features:
- Complete mortgage knowledge graph loading
- Data integrity verification
- Progress tracking with detailed reporting
- Error handling with rollback capabilities
- Performance monitoring
"""

import sys
import argparse
import logging
from pathlib import Path

# Add the database package to path
sys.path.insert(0, str(Path(__file__).parent))

from database.loaders import load_all_mortgage_data, verify_data_integrity
from database.setup import setup_database, get_connection, health_check
from database.management import clear_all_data, get_current_data_summary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Load mortgage knowledge graph data into Neo4j",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python load_mortgage_data.py                    # Load all data
  python load_mortgage_data.py --verify-only      # Check existing data
  python load_mortgage_data.py --clear-first      # Clear and reload
  python load_mortgage_data.py --verbose          # Detailed output
        """
    )
    
    parser.add_argument("--verify-only", action="store_true", 
                       help="Verify existing data integrity without loading")
    parser.add_argument("--clear-first", action="store_true",
                       help="Clear existing data before loading")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--force", action="store_true",
                       help="Skip confirmation prompts")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🏦 MORTGAGE KNOWLEDGE GRAPH LOADER")
    print("=" * 50)
    
    # Step 1: Initial health check
    print("\n🔍 Step 1: Database Health Check")
    if not health_check():
        print(" Database health check failed")
        print("   Please ensure Neo4j Desktop is running and 'mortgage' database exists")
        return 1
    print(" Database connection healthy")
    
    # Step 2: Get current data summary
    connection = get_connection()
    current_data = get_current_data_summary(connection)
    
    print(f"\n📊 Current Database Status:")
    print(f"   • Total Nodes: {current_data['total_nodes']}")
    print(f"   • Total Relationships: {current_data['total_relationships']}")
    if current_data['labels_present']:
        print(f"   • Node Types: {', '.join(current_data['labels_present'])}")
    
    # Handle verify-only mode
    if args.verify_only:
        return handle_verify_only(connection)
    
    # Handle clear-first mode
    if args.clear_first and current_data['total_nodes'] > 0:
        if not handle_clear_data(connection, args.force):
            return 1
    
    # Step 3: Load data
    print("\n📥 Step 3: Loading Mortgage Knowledge Graph")
    loading_result = load_all_mortgage_data()
    
    if loading_result["success"]:
        print_success_summary(loading_result)
        return 0
    else:
        print_failure_summary(loading_result)
        return 1


def handle_verify_only(connection):
    """Handle verification-only mode."""
    print("\n Verifying Data Integrity...")
    
    verification_result = verify_data_integrity(connection)
    
    if verification_result["data_complete"]:
        print(" Data integrity verification PASSED")
        print(f"   • Node counts: {verification_result['node_counts']}")
        print(f"   • Relationships: {verification_result['total_relationships']}")
        return 0
    else:
        print(" Data integrity verification FAILED")
        print("   Issues found:")
        for issue in verification_result.get("issues", []):
            print(f"   - {issue}")
        return 1


def handle_clear_data(connection, force: bool):
    """Handle data clearing with confirmation."""
    if not force:
        print("\n⚠️  WARNING: About to clear existing data")
        response = input("   Type 'CONFIRM' to proceed: ").strip()
        if response != "CONFIRM":
            print("   Operation cancelled")
            return False
    
    print("\n🗑️  Clearing existing data...")
    if clear_all_data(connection):
        print(" Existing data cleared")
        return True
    else:
        print(" Failed to clear existing data")
        return False


def print_success_summary(result):
    """Print success summary with statistics."""
    print("\n🎉 LOADING COMPLETED SUCCESSFULLY")
    print("=" * 40)
    print(f" Stages Completed: {len(result['stages_completed'])}")
    for stage in result['stages_completed']:
        print(f"   • {stage}")
    print(f"📊 Total Nodes Created: {result['total_nodes_created']}")
    print(f"🔗 Total Relationships Created: {result['total_relationships_created']}")
    print(f"⏱️  Loading Time: {result.get('loading_time_seconds', 'N/A')} seconds")
    print("=" * 40)
    print("💡 Next Steps:")
    print("   • Test agent functionality")
    print("   • Run mortgage application scenarios")
    print("   • Monitor system performance")


def print_failure_summary(result):
    """Print failure summary with error details."""
    print("\n LOADING FAILED")
    print("=" * 40)
    print(f"⏹️  Stages Completed: {len(result['stages_completed'])}")
    for stage in result['stages_completed']:
        print(f"    {stage}")
    
    if result['stages_failed']:
        print(f" Stages Failed: {len(result['stages_failed'])}")
        for stage in result['stages_failed']:
            print(f"    {stage}")
    
    print("\n🔧 Errors:")
    for error in result['errors']:
        print(f"   • {error}")
    
    print("\n💡 Troubleshooting:")
    print("   • Check Neo4j connection")
    print("   • Verify database permissions")
    print("   • Review error logs above")
    print("   • Try running with --verbose flag")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
