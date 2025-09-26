"""
Core Data Loading Stage

Handles loading of core mortgage entities like loan programs.
"""

import logging
from typing import Dict, Any
from database.core_data import load_loan_programs

logger = logging.getLogger(__name__)


class CoreDataStage:
    """Handles loading of core mortgage data."""
    
    def execute(self, connection) -> Dict[str, Any]:
        """
        Execute core data loading stage.
        
        Args:
            connection: Neo4j connection instance
            
        Returns:
            dict: Stage execution results
        """
        result = {
            "success": False,
            "nodes_created": 0,
            "relationships_created": 0,
            "errors": []
        }
        
        try:
            logger.info("📊 Loading core mortgage data...")
            
            # Load loan programs
            loan_program_success = load_loan_programs(connection)
            
            if loan_program_success:
                # Count created nodes
                with connection.driver.session(database=connection.database) as session:
                    loan_count_result = session.run("MATCH (n:LoanProgram) RETURN count(n) as count")
                    loan_count = loan_count_result.single()["count"]
                    result["nodes_created"] = loan_count
                
                result["success"] = True
                logger.info(f" Core data loaded: {result['nodes_created']} nodes created")
            else:
                result["errors"].append("Loan program loading failed")
                logger.error(" Core data loading failed")
            
        except Exception as e:
            result["errors"].append(f"Core data loading error: {str(e)}")
            logger.error(f" Core data loading error: {e}")
        
        return result
