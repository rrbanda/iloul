"""
Database Health Check and Monitoring

Production-ready health checking for database connectivity and data integrity.
"""

import logging
from typing import Dict, Any
from .connection import get_connection

logger = logging.getLogger(__name__)


def verify_connection() -> Dict[str, Any]:
    """
    Comprehensive connection verification.
    
    Returns:
        dict: Health check results with status and details
    """
    connection = get_connection()
    
    health_status = {
        "healthy": False,
        "checks": {},
        "errors": []
    }
    
    # Check 1: Basic connectivity
    try:
        if not connection.driver:
            if not connection.connect():
                health_status["errors"].append("Failed to establish connection")
                return health_status
        
        health_status["checks"]["connection"] = " Connected"
        
    except Exception as e:
        health_status["errors"].append(f"Connection error: {e}")
        return health_status
    
    # Check 2: Database access
    try:
        with connection.driver.session(database=connection.database) as session:
            result = session.run("RETURN 1 as test")
            test_value = result.single()["test"]
            
            if test_value == 1:
                health_status["checks"]["database_access"] = f" Database '{connection.database}' accessible"
            else:
                health_status["errors"].append("Database query returned unexpected result")
                return health_status
                
    except Exception as e:
        health_status["errors"].append(f"Database access error: {e}")
        return health_status
    
    # Check 3: Basic write/read operations
    try:
        with connection.driver.session(database=connection.database) as session:
            # Write test
            session.run("CREATE (health:HealthCheck {timestamp: datetime(), test: 'write_test'})")
            
            # Read test
            result = session.run("MATCH (health:HealthCheck {test: 'write_test'}) RETURN count(health) as count")
            count = result.single()["count"]
            
            # Cleanup
            session.run("MATCH (health:HealthCheck {test: 'write_test'}) DELETE health")
            
            if count > 0:
                health_status["checks"]["read_write"] = " Read/write operations working"
            else:
                health_status["errors"].append("Write/read test failed")
                return health_status
                
    except Exception as e:
        health_status["errors"].append(f"Read/write test error: {e}")
        return health_status
    
    # All checks passed
    health_status["healthy"] = True
    health_status["checks"]["overall"] = " All health checks passed"
    
    return health_status


def health_check() -> bool:
    """
    Simple boolean health check.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    result = verify_connection()
    return result["healthy"]


def get_data_integrity_report() -> Dict[str, Any]:
    """
    Check data integrity and completeness.
    
    Returns:
        dict: Data integrity report with counts and validation results
    """
    connection = get_connection()
    
    try:
        with connection.driver.session(database=connection.database) as session:
            # Check for essential node types
            essential_checks = {
                "LoanProgram": "MATCH (n:LoanProgram) RETURN count(n) as count",
                "BusinessRule": "MATCH (n:BusinessRule) RETURN count(n) as count", 
                "ScoringRule": "MATCH (n:ScoringRule) RETURN count(n) as count",
                "UnderwritingRule": "MATCH (n:UnderwritingRule) RETURN count(n) as count"
            }
            
            node_counts = {}
            for node_type, query in essential_checks.items():
                result = session.run(query)
                count = result.single()["count"]
                node_counts[node_type] = count
            
            # Check relationships
            rel_result = session.run("MATCH ()-[r:HAS_REQUIREMENT]->() RETURN count(r) as count")
            relationship_count = rel_result.single()["count"]
            
            # Validate data completeness
            issues = []
            if node_counts.get("LoanProgram", 0) < 3:
                issues.append("Insufficient loan programs loaded")
            if node_counts.get("BusinessRule", 0) < 10:
                issues.append("Insufficient business rules loaded")
            if relationship_count < 5:
                issues.append("Insufficient relationships created")
            
            return {
                "status": "healthy" if not issues else "incomplete",
                "node_counts": node_counts,
                "relationship_count": relationship_count,
                "issues": issues,
                "data_complete": len(issues) == 0
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "data_complete": False
        }


def performance_metrics() -> Dict[str, Any]:
    """
    Get database performance metrics.
    
    Returns:
        dict: Performance metrics and timing information
    """
    connection = get_connection()
    
    try:
        import time
        
        with connection.driver.session(database=connection.database) as session:
            # Simple query timing
            start_time = time.time()
            result = session.run("MATCH (n) RETURN count(n) as total_nodes")
            total_nodes = result.single()["total_nodes"]
            simple_query_time = time.time() - start_time
            
            # Complex query timing
            start_time = time.time()
            result = session.run("""
                MATCH (lp:LoanProgram)-[r:HAS_REQUIREMENT]->(qr:QualificationRequirement)
                RETURN lp.name, count(qr) as requirements
                ORDER BY requirements DESC
                LIMIT 10
            """)
            complex_results = list(result)
            complex_query_time = time.time() - start_time
            
            return {
                "total_nodes": total_nodes,
                "simple_query_time_ms": round(simple_query_time * 1000, 2),
                "complex_query_time_ms": round(complex_query_time * 1000, 2),
                "complex_results_count": len(complex_results),
                "status": "good" if simple_query_time < 0.1 else "slow"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
