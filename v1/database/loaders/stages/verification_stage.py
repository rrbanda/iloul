"""
Data Verification Stage

Handles comprehensive data integrity verification after loading.
"""

import logging
from typing import Dict, Any
from ..utils import DataIntegrityVerifier

logger = logging.getLogger(__name__)


class VerificationStage:
    """Handles data integrity verification."""
    
    def execute(self, connection) -> Dict[str, Any]:
        """
        Execute data verification stage.
        
        Args:
            connection: Neo4j connection instance
            
        Returns:
            dict: Stage execution results
        """
        result = {
            "success": False,
            "nodes_created": 0,
            "relationships_created": 0,
            "errors": [],
            "verification_details": {}
        }
        
        try:
            logger.info(" Performing data integrity verification...")
            
            # Create verifier and run verification
            verifier = DataIntegrityVerifier(connection)
            verification_result = verifier.verify_all()
            
            # Store verification details
            result["verification_details"] = verification_result
            
            if verification_result["data_complete"]:
                result["success"] = True
                logger.info(" Data integrity verification passed")
                
                # Get summary stats
                stats = verifier.get_summary_stats()
                logger.info(f"📊 Final Statistics:")
                logger.info(f"   • Total Nodes: {stats['total_nodes']}")
                logger.info(f"   • Total Relationships: {stats['total_relationships']}")
                logger.info(f"   • Graph Density: {stats['graph_density']:.3f}")
                
            else:
                result["success"] = False
                issues = verification_result.get("issues", [])
                result["errors"].extend(issues)
                logger.warning(f"⚠️ Data integrity verification failed with {len(issues)} issues")
                
        except Exception as e:
            result["errors"].append(f"Data verification error: {str(e)}")
            logger.error(f" Data verification error: {e}")
        
        return result
