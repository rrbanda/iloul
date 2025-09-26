"""
Relationships Creation Stage

Handles creation of graph relationships between entities.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RelationshipsStage:
    """Handles creation of graph relationships."""
    
    def execute(self, connection) -> Dict[str, Any]:
        """
        Execute relationships creation stage.
        
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
            logger.info("🔗 Creating graph relationships...")
            
            # Count relationships before
            initial_count = self._count_relationships(connection)
            
            # Create basic relationships
            basic_success = self._create_basic_relationships(connection)
            if not basic_success:
                result["errors"].append("Basic relationships creation failed")
                return result
            
            # Count relationships after
            final_count = self._count_relationships(connection)
            result["relationships_created"] = final_count - initial_count
            
            result["success"] = True
            logger.info(f" Relationships created: {result['relationships_created']}")
            
        except Exception as e:
            result["errors"].append(f"Relationships creation error: {str(e)}")
            logger.error(f" Relationships creation error: {e}")
        
        return result
    
    def _create_basic_relationships(self, connection) -> bool:
        """Create basic relationships between core entities."""
        try:
            # Basic relationships can be added here
            # For now, most relationships are created by the individual rule loaders
            
            # Example: Create relationships between loan programs and qualification requirements
            # This would be expanded based on specific business needs
            
            with connection.driver.session(database=connection.database) as session:
                # Create a simple relationship between FHA and credit score rules
                relationship_query = """
                MATCH (lp:LoanProgram {name: 'FHA'})
                MATCH (br:BusinessRule {rule_type: 'CreditScoreAssessment'})
                MERGE (lp)-[:HAS_CREDIT_REQUIREMENT]->(br)
                """
                session.run(relationship_query)
            
            return True
            
        except Exception as e:
            logger.error(f"Basic relationships creation failed: {e}")
            return False
    
    def _count_relationships(self, connection) -> int:
        """Count total relationships in the database."""
        try:
            with connection.driver.session(database=connection.database) as session:
                result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                return result.single()["count"]
        except Exception as e:
            logger.warning(f"Could not count relationships: {e}")
            return 0
