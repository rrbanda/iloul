"""
Database Loaders Module

Modern, modular orchestration of mortgage knowledge graph data loading including:
- Core data (loan programs, borrower profiles, process steps)
- Business rules (organized by category)  
- Graph relationships between entities
- Data integrity verification

Main entry point: load_all_mortgage_data()
Architecture: Modular stages with comprehensive orchestration
"""

from .data_orchestrator import load_all_mortgage_data, load_all_data, verify_data_integrity

__all__ = [
    "load_all_mortgage_data",  # New preferred name
    "load_all_data",          # Backward compatibility
    "verify_data_integrity"
]
