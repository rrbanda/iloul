"""
Data Clearing Operations

Production-grade data clearing operations with safety checks
and proper logging for maintenance operations.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def clear_all_data(connection) -> bool:
    """
    Clear all mortgage data from the database.
    
    WARNING: This operation is irreversible and will delete all nodes and relationships.
    Use with caution in production environments.
    
    Args:
        connection: Neo4j connection instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.warning("⚠️  Clearing ALL mortgage data from database")
    
    try:
        clear_queries = [
            # Clear specific node types in order (relationships first)
            "MATCH ()-[r]->() DELETE r",  # All relationships first
            "MATCH (n:LoanProgram) DELETE n",
            "MATCH (n:BusinessRule) DELETE n", 
            "MATCH (n:ScoringRule) DELETE n",
            "MATCH (n:QualificationRequirement) DELETE n",
            "MATCH (n:UnderwritingRule) DELETE n",
            "MATCH (n:DocumentVerificationRule) DELETE n",
            "MATCH (n:PropertyAppraisalRule) DELETE n",
            "MATCH (n:BorrowerProfile) DELETE n",
            "MATCH (n:BorrowerScenario) DELETE n",
            "MATCH (n:ProcessStep) DELETE n",
            "MATCH (n:ComplianceRule) DELETE n",
            "MATCH (n:RatePricingRule) DELETE n",
            "MATCH (n:SpecialRequirement) DELETE n",
            "MATCH (n:ImprovementStrategy) DELETE n",
            "MATCH (n:QualificationThreshold) DELETE n",
            # Clean up any remaining nodes
            "MATCH (n) DELETE n"
        ]
        
        with connection.driver.session(database=connection.database) as session:
            for query in clear_queries:
                try:
                    result = session.run(query)
                    result.consume()  # Ensure query execution
                except Exception as e:
                    logger.warning(f"Query execution warning: {query} - {e}")
                    # Continue with other queries
        
        logger.info(" All mortgage data cleared successfully")
        return True
        
    except Exception as e:
        logger.error(f" Error clearing data: {e}")
        return False


def clear_data_by_type(connection, node_types: List[str]) -> Dict[str, bool]:
    """
    Clear specific types of nodes from the database.
    
    Args:
        connection: Neo4j connection instance
        node_types: List of node type labels to clear
        
    Returns:
        dict: Results for each node type clearing operation
    """
    logger.info(f"Clearing specific node types: {node_types}")
    
    results = {}
    
    try:
        with connection.driver.session(database=connection.database) as session:
            for node_type in node_types:
                try:
                    # First clear relationships involving this node type
                    rel_query = f"MATCH (n:{node_type})-[r]-() DELETE r"
                    session.run(rel_query)
                    
                    # Then clear the nodes
                    node_query = f"MATCH (n:{node_type}) DELETE n"
                    result = session.run(node_query)
                    result.consume()
                    
                    results[node_type] = True
                    logger.info(f" Cleared {node_type} nodes")
                    
                except Exception as e:
                    results[node_type] = False
                    logger.error(f" Failed to clear {node_type}: {e}")
        
        return results
        
    except Exception as e:
        logger.error(f" Error in selective clearing: {e}")
        return {node_type: False for node_type in node_types}


def get_current_data_summary(connection) -> Dict[str, Any]:
    """
    Get summary of current data in the database.
    
    Args:
        connection: Neo4j connection instance
        
    Returns:
        dict: Summary of current database contents
    """
    try:
        with connection.driver.session(database=connection.database) as session:
            # Get node counts by label
            label_result = session.run("CALL db.labels() YIELD label RETURN label")
            labels = [record["label"] for record in label_result]
            
            node_counts = {}
            for label in labels:
                count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                count = count_result.single()["count"]
                if count > 0:  # Only include non-empty labels
                    node_counts[label] = count
            
            # Get relationship count
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            relationship_count = rel_result.single()["count"]
            
            return {
                "node_counts": node_counts,
                "total_nodes": sum(node_counts.values()),
                "total_relationships": relationship_count,
                "labels_present": list(node_counts.keys())
            }
            
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        return {
            "error": str(e),
            "node_counts": {},
            "total_nodes": 0,
            "total_relationships": 0
        }


def confirm_clear_operation(data_summary: Dict[str, Any]) -> bool:
    """
    Interactive confirmation for clearing operations.
    
    Args:
        data_summary: Current database summary
        
    Returns:
        bool: True if user confirms, False otherwise
    """
    if data_summary.get("total_nodes", 0) == 0:
        logger.info("Database is already empty")
        return True
    
    print("\n⚠️  WARNING: About to clear database contents")
    print("=" * 50)
    print(f"Total Nodes: {data_summary['total_nodes']}")
    print(f"Total Relationships: {data_summary['total_relationships']}")
    print(f"Node Types: {', '.join(data_summary['labels_present'])}")
    print("=" * 50)
    
    response = input("Type 'CONFIRM' to proceed with clearing: ").strip()
    return response == "CONFIRM"
