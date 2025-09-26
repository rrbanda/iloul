"""
Database Setup and Management

Production-ready database setup with proper error handling and verification.
"""

import logging
from typing import Dict, Any
from .connection import get_connection

logger = logging.getLogger(__name__)


def setup_database() -> bool:
    """
    Complete database setup process.
    
    Steps:
    1. Test Neo4j server connection
    2. Check if target database exists
    3. Create database if needed
    4. Verify database access
    
    Returns:
        bool: True if setup successful, False otherwise
    """
    logger.info("🏦 Starting mortgage database setup...")
    
    connection = get_connection()
    
    # Step 1: Connect to Neo4j server
    if not connection.connect():
        logger.error(" Failed to connect to Neo4j server")
        return False
    
    # Step 2: Check if database exists
    database_name = connection.database
    if not _check_database_exists(connection, database_name):
        # Step 3: Create database if needed
        if not create_database_if_needed(connection, database_name):
            logger.error(f" Failed to create database '{database_name}'")
            return False
    
    # Step 4: Verify database access
    if not _verify_database_access(connection, database_name):
        logger.error(f" Cannot access database '{database_name}'")
        return False
    
    logger.info(" Database setup completed successfully")
    return True


def create_database_if_needed(connection, database_name: str) -> bool:
    """
    Create database if it doesn't exist.
    
    Args:
        connection: Neo4j connection instance
        database_name: Name of database to create
        
    Returns:
        bool: True if database exists or was created successfully
    """
    try:
        logger.info(f"Creating database '{database_name}' if needed...")
        
        # Use system database to create new database
        with connection.driver.session(database="system") as session:
            result = session.run(f"CREATE DATABASE `{database_name}` IF NOT EXISTS")
            result.consume()  # Ensure query is executed
            
        logger.info(f" Database '{database_name}' is ready")
        return True
        
    except Exception as e:
        logger.error(f" Error creating database '{database_name}': {e}")
        return False


def _check_database_exists(connection, database_name: str) -> bool:
    """Check if database exists."""
    try:
        with connection.driver.session(database="system") as session:
            result = session.run("SHOW DATABASES")
            databases = [record["name"] for record in result]
            return database_name in databases
    except Exception as e:
        logger.error(f"Error checking database existence: {e}")
        return False


def _verify_database_access(connection, database_name: str) -> bool:
    """Verify database access with read/write test."""
    try:
        with connection.driver.session(database=database_name) as session:
            # Test write
            session.run("CREATE (test:TestNode {purpose: 'access_test', timestamp: datetime()})")
            
            # Test read
            result = session.run("MATCH (test:TestNode {purpose: 'access_test'}) RETURN count(test) as count")
            count = result.single()["count"]
            
            # Cleanup
            session.run("MATCH (test:TestNode {purpose: 'access_test'}) DELETE test")
            
            return count > 0
    except Exception as e:
        logger.error(f"Database access verification failed: {e}")
        return False


def get_database_info() -> Dict[str, Any]:
    """
    Get database information and statistics.
    
    Returns:
        dict: Database information including node counts and relationships
    """
    connection = get_connection()
    
    try:
        with connection.driver.session(database=connection.database) as session:
            # Get node counts by label
            node_counts = {}
            result = session.run("""
                CALL db.labels() YIELD label
                CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {}) 
                YIELD value
                RETURN label, value.count as count
            """)
            
            for record in result:
                node_counts[record["label"]] = record["count"]
            
            # Get relationship counts
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as total_relationships")
            total_relationships = rel_result.single()["total_relationships"]
            
            return {
                "database": connection.database,
                "node_counts": node_counts,
                "total_relationships": total_relationships,
                "status": "healthy"
            }
            
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {
            "database": connection.database,
            "status": "error",
            "error": str(e)
        }
