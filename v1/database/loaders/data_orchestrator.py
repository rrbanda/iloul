"""
Data Orchestrator

Modern, inclusive orchestrator for mortgage knowledge graph data loading.
Coordinates all loading operations through modular stages with comprehensive
error handling and progress tracking.

Architecture:
- Orchestrates individual loading stages
- Provides comprehensive logging and monitoring
- Ensures data integrity throughout the process
- Maintains backward compatibility with existing systems

Usage:
    from database.loaders import load_all_mortgage_data
    result = load_all_mortgage_data()
"""

import logging
from typing import Dict, Any
from .stages import StageOrchestrator

logger = logging.getLogger(__name__)


def load_all_mortgage_data() -> Dict[str, Any]:
    """
    Load complete mortgage knowledge graph data using modular orchestration.
    
    This function serves as the main entry point for loading all mortgage
    data through a series of coordinated stages:
    
    1. Database Setup - Connection verification and setup
    2. Data Clearing - Clean existing data
    3. Core Data Loading - Load fundamental entities (loan programs)
    4. Business Rules Loading - Load all business logic and rules
    5. Relationship Creation - Connect entities with graph relationships
    6. Data Verification - Validate integrity and completeness
    
    Returns:
        dict: Comprehensive loading results including:
            - success: Overall success status
            - stages_completed: List of successfully completed stages
            - stages_failed: List of failed stages (if any)
            - total_nodes_created: Count of all nodes created
            - total_relationships_created: Count of all relationships created
            - errors: List of any errors encountered
            - stage_results: Detailed results from each stage
    
    Example:
        >>> result = load_all_mortgage_data()
        >>> if result["success"]:
        ...     print(f" Loaded {result['total_nodes_created']} nodes successfully")
        ... else:
        ...     print(f" Loading failed: {result['errors']}")
    """
    logger.info("🚀 Initializing mortgage knowledge graph data orchestrator...")
    
    try:
        # Create and execute orchestrator
        orchestrator = StageOrchestrator()
        
        # Validate stage dependencies before execution
        if not orchestrator.validate_stage_order():
            return {
                "success": False,
                "errors": ["Invalid stage dependency order"],
                "stages_completed": [],
                "stages_failed": [],
                "total_nodes_created": 0,
                "total_relationships_created": 0
            }
        
        # Execute all stages
        results = orchestrator.execute_all_stages()
        
        return results
        
    except Exception as e:
        logger.error(f" Data orchestrator error: {e}")
        return {
            "success": False,
            "errors": [f"Orchestrator initialization error: {str(e)}"],
            "stages_completed": [],
            "stages_failed": [],
            "total_nodes_created": 0,
            "total_relationships_created": 0
        }


# Backward compatibility aliases
load_all_data = load_all_mortgage_data
verify_data_integrity = None  # Will be set below

def _get_data_integrity_verifier(connection=None):
    """Get data integrity verifier for backward compatibility."""
    from database.setup import get_connection
    from .utils import DataIntegrityVerifier
    
    try:
        if connection is None:
            connection = get_connection()
        verifier = DataIntegrityVerifier(connection)
        return verifier.verify_all()
    except Exception as e:
        logger.error(f"Data integrity verification error: {e}")
        return {
            "data_complete": False,
            "status": "error",
            "error": str(e),
            "issues": [f"Verification error: {str(e)}"]
        }

# Set backward compatibility function
verify_data_integrity = _get_data_integrity_verifier
