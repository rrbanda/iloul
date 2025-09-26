"""
Business Rules Loading Stage

Handles loading of all business rules including enhanced rule types.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BusinessRulesStage:
    """Handles loading of all business rules."""
    
    def execute(self, connection) -> Dict[str, Any]:
        """
        Execute business rules loading stage.
        
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
            logger.info("⚖️ Loading business rules...")
            
            # Load basic business rules
            basic_success = self._load_basic_business_rules(connection)
            if not basic_success:
                result["errors"].append("Basic business rules loading failed")
                return result
            
            # Load enhanced rule sets
            enhanced_success = self._load_enhanced_rules(connection)
            if not enhanced_success:
                result["errors"].append("Enhanced rules loading failed")
                return result
            
            # Count all created rule nodes
            rule_count = self._count_rule_nodes(connection)
            result["nodes_created"] = rule_count
            
            result["success"] = True
            logger.info(f" Enhanced business rules loaded: {result['nodes_created']} nodes created")
            
        except Exception as e:
            result["errors"].append(f"Business rules loading error: {str(e)}")
            logger.error(f" Business rules loading error: {e}")
        
        return result
    
    def _load_basic_business_rules(self, connection) -> bool:
        """Load basic business rules."""
        try:
            basic_rules = [
                {
                    "rule_type": "CreditScoreAssessment",
                    "category": "excellent",
                    "min_threshold": 740,
                    "max_threshold": 850,
                    "description": "Excellent credit score - qualifies for best rates"
                },
                {
                    "rule_type": "CreditScoreAssessment", 
                    "category": "good",
                    "min_threshold": 680,
                    "max_threshold": 739,
                    "description": "Good credit score - qualifies for most programs"
                }
            ]
            
            with connection.driver.session(database=connection.database) as session:
                for rule in basic_rules:
                    session.run("""
                        CREATE (br:BusinessRule {
                            rule_type: $rule_type,
                            category: $category,
                            min_threshold: $min_threshold,
                            max_threshold: $max_threshold,
                            description: $description,
                            created_at: datetime()
                        })
                    """, rule)
            
            return True
            
        except Exception as e:
            logger.error(f"Basic business rules loading failed: {e}")
            return False
    
    def _load_enhanced_rules(self, connection) -> bool:
        """Load all enhanced rule types."""
        try:
            # Load QM compliance rules
            logger.info("Loading QM compliance rules...")
            from database.business_rules.compliance.qm_rules import load_qm_rules, create_qm_relationships
            if not load_qm_rules(connection):
                return False
            create_qm_relationships(connection)
            
            # Load Fannie Mae secondary market rules
            logger.info("Loading Fannie Mae secondary market rules...")
            from database.business_rules.secondary_market.fannie_mae_rules import load_fannie_mae_rules, create_fannie_mae_relationships
            if not load_fannie_mae_rules(connection):
                return False
            create_fannie_mae_relationships(connection)
            
            # Load property risk assessment rules
            logger.info("Loading property risk assessment rules...")
            from database.business_rules.risk_assessment.property_risk_rules import load_property_risk_rules, create_property_risk_relationships
            if not load_property_risk_rules(connection):
                return False
            create_property_risk_relationships(connection)
            
            return True
            
        except Exception as e:
            logger.error(f"Enhanced rules loading failed: {e}")
            return False
    
    def _count_rule_nodes(self, connection) -> int:
        """Count all rule nodes in the database."""
        try:
            with connection.driver.session(database=connection.database) as session:
                counts_query = """
                MATCH (br:BusinessRule) 
                WITH count(br) as business_count
                MATCH (qm:QM_Rule) 
                WITH business_count, count(qm) as qm_count
                MATCH (fm:FannieMae_Rule) 
                WITH business_count, qm_count, count(fm) as fannie_count
                MATCH (pr:PropertyRisk_Rule) 
                WITH business_count, qm_count, fannie_count, count(pr) as risk_count
                RETURN business_count + qm_count + fannie_count + risk_count as total_count
                """
                result = session.run(counts_query)
                return result.single()["total_count"]
        except Exception as e:
            logger.warning(f"Could not count rule nodes: {e}")
            return 0
