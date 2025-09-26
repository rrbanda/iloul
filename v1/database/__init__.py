"""
Mortgage Database Package

A well-organized, production-ready database package for mortgage processing.
This package provides a clean separation of concerns for all database operations.

Structure:
- setup/: Database connection and setup utilities
- core_data/: Basic mortgage entities (loan programs, borrower profiles)
- business_rules/: Organized by mortgage workflow (application -> underwriting -> pricing)
- loaders/: Data loading scripts
- management/: Database management utilities
- tests/: Comprehensive test suite

Usage:
    from database import setup_database, load_all_data
    
    # Setup database
    setup_database()
    
    # Load all mortgage knowledge
    load_all_data()
"""

__version__ = "1.0.0"
__author__ = "Mortgage Processing Team"

# Main database operations
from .setup import setup_database, verify_connection
from .loaders import load_all_mortgage_data, load_all_data, verify_data_integrity

__all__ = [
    "setup_database",
    "verify_connection", 
    "load_all_data",
    "verify_data_integrity"
]
