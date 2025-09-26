"""
Data Clearing Stage

Handles clearing of existing data before loading new data.
"""

import logging
from typing import Dict, Any
from database.management import clear_all_data

logger = logging.getLogger(__name__)


class DataClearingStage:
    """Handles clearing of existing data."""
    
    def execute(self, connection) -> Dict[str, Any]:
        """
        Execute data clearing stage.
        
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
            logger.warning("⚠️ Clearing ALL mortgage data from database")
            
            # Clear existing data
            clear_success = clear_all_data(connection)
            
            if clear_success:
                result["success"] = True
                logger.info(" All mortgage data cleared successfully")
            else:
                result["errors"].append("Data clearing failed")
                logger.error(" Data clearing failed")
            
        except Exception as e:
            result["errors"].append(f"Data clearing error: {str(e)}")
            logger.error(f" Data clearing error: {e}")
        
        return result
