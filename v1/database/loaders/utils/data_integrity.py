"""
Data Integrity Verification

Comprehensive verification of database state and data integrity
after loading operations.
"""

import logging
from typing import Dict, Any, List
from .loader_config import LoaderConfig

logger = logging.getLogger(__name__)


class DataIntegrityVerifier:
    """Handles comprehensive data integrity verification."""
    
    def __init__(self, connection):
        self.connection = connection
        self.config = LoaderConfig()
    
    def verify_all(self) -> Dict[str, Any]:
        """
        Perform comprehensive data integrity verification.
        
        Returns:
            dict: Verification results with completeness status
        """
        try:
            logger.info("🔍 Starting comprehensive data integrity verification...")
            
            # Get node counts for all entity types
            node_counts = self._get_node_counts()
            
            # Get relationship counts
            relationship_count = self._get_relationship_count()
            
            # Validate against minimum requirements
            issues = self._validate_requirements(node_counts, relationship_count)
            
            # Additional integrity checks
            integrity_issues = self._check_data_integrity()
            issues.extend(integrity_issues)
            
            result = {
                "data_complete": len(issues) == 0,
                "node_counts": node_counts,
                "total_relationships": relationship_count,
                "issues": issues,
                "status": "complete" if len(issues) == 0 else "incomplete"
            }
            
            if result["data_complete"]:
                logger.info(" Data integrity verification passed")
            else:
                logger.warning(f"⚠️ Data integrity issues found: {len(issues)}")
                
            return result
            
        except Exception as e:
            logger.error(f" Data integrity verification failed: {e}")
            return {
                "data_complete": False,
                "status": "error",
                "error": str(e),
                "issues": [f"Verification error: {str(e)}"]
            }
    
    def _get_node_counts(self) -> Dict[str, int]:
        """Get counts for all node types."""
        node_queries = {
            "loan_programs": "MATCH (n:LoanProgram) RETURN count(n) as count",
            "business_rules": "MATCH (n:BusinessRule) RETURN count(n) as count", 
            "qm_rules": "MATCH (n:QM_Rule) RETURN count(n) as count",
            "fannie_mae_rules": "MATCH (n:FannieMae_Rule) RETURN count(n) as count",
            "property_risk_rules": "MATCH (n:PropertyRisk_Rule) RETURN count(n) as count",
            "borrower_scenarios": "MATCH (n:BorrowerScenario) RETURN count(n) as count"
        }
        
        node_counts = {}
        with self.connection.driver.session(database=self.connection.database) as session:
            for node_type, query in node_queries.items():
                try:
                    result = session.run(query)
                    count = result.single()["count"]
                    node_counts[node_type] = count
                except Exception as e:
                    logger.warning(f"Could not count {node_type}: {e}")
                    node_counts[node_type] = 0
        
        return node_counts
    
    def _get_relationship_count(self) -> int:
        """Get total relationship count."""
        with self.connection.driver.session(database=self.connection.database) as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            return result.single()["count"]
    
    def _validate_requirements(self, node_counts: Dict[str, int], relationship_count: int) -> List[str]:
        """Validate against minimum requirements."""
        issues = []
        
        # Check minimum node counts
        for node_type, min_count in self.config.MIN_NODE_COUNTS.items():
            actual_count = node_counts.get(node_type, 0)
            if actual_count < min_count:
                issues.append(f"Insufficient {node_type}: {actual_count} < {min_count} required")
        
        # Check minimum relationship count
        if relationship_count < self.config.MIN_RELATIONSHIP_COUNT:
            issues.append(f"Insufficient relationships: {relationship_count} < {self.config.MIN_RELATIONSHIP_COUNT} required")
        
        return issues
    
    def _check_data_integrity(self) -> List[str]:
        """Perform additional data integrity checks."""
        issues = []
        
        with self.connection.driver.session(database=self.connection.database) as session:
            # Check for critical orphaned nodes (only check core entities that must have relationships)
            orphan_query = """
            MATCH (n:LoanProgram)
            WHERE NOT (n)--()
            RETURN count(n) as orphaned_loan_programs
            """
            
            try:
                result = session.run(orphan_query)
                orphaned_loan_programs = result.single()["orphaned_loan_programs"]
                if orphaned_loan_programs > 0:
                    issues.append(f"Found {orphaned_loan_programs} loan programs without any relationships")
            except Exception as e:
                logger.warning(f"Could not check for orphaned loan programs: {e}")
            
            # Check for duplicate rule IDs
            duplicate_query = """
            MATCH (n)
            WHERE n.rule_id IS NOT NULL
            WITH n.rule_id as rule_id, count(n) as count
            WHERE count > 1
            RETURN rule_id, count
            """
            
            try:
                result = session.run(duplicate_query)
                for record in result:
                    rule_id = record["rule_id"]
                    count = record["count"]
                    issues.append(f"Duplicate rule_id '{rule_id}' found {count} times")
            except Exception as e:
                logger.warning(f"Could not check for duplicate rule IDs: {e}")
        
        return issues
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get comprehensive summary statistics."""
        node_counts = self._get_node_counts()
        relationship_count = self._get_relationship_count()
        
        return {
            "total_nodes": sum(node_counts.values()),
            "total_relationships": relationship_count,
            "node_breakdown": node_counts,
            "graph_density": relationship_count / max(sum(node_counts.values()), 1)
        }
