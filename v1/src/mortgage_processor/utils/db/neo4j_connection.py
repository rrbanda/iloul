"""
Neo4j Database Connection Management

This module provides connection management for Neo4j database integration.
Designed to work with both local Neo4j Desktop and production deployments.

Features:
- Configuration from centralized config.yaml system
- Connection pooling and health checks
- Proper error handling and logging
- Support for Neo4j Desktop default configurations
- Environment variable overrides
"""

import logging
from typing import Optional, Dict, Any
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError

try:
    from ...config import AppConfig
except ImportError:
    # Fallback for different import paths during testing
    from mortgage_processor.config import AppConfig


logger = logging.getLogger(__name__)


class Neo4jConnection:
    """
    Neo4j database connection manager with centralized configuration.
    
    Supports both local Neo4j Desktop and production deployments with
    configuration from config.yaml and environment variable overrides.
    """
    
    def __init__(self, config: Optional[AppConfig] = None):
        self._driver: Optional[Driver] = None
        self._app_config = config or AppConfig.load()
        self._neo4j_config = self._app_config.neo4j
    
    @property
    def config(self) -> Dict[str, Any]:
        """
        Get Neo4j configuration as dictionary.
        
        Configuration comes from config.yaml with environment variable overrides.
        Supports your local Neo4j Desktop "mortgage" database instance.
        """
        return {
            "uri": self._neo4j_config.uri,
            "username": self._neo4j_config.username,
            "password": self._neo4j_config.password,
            "database": self._neo4j_config.database,
            "max_connection_lifetime": self._neo4j_config.max_connection_lifetime,
            "max_connection_pool_size": self._neo4j_config.max_connection_pool_size,
            "connection_acquisition_timeout": self._neo4j_config.connection_acquisition_timeout,
            "enable_mcp": self._neo4j_config.enable_mcp
        }
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        config = self.config
        if not config["password"]:
            logger.error("Neo4j password is required. Set NEO4J_PASSWORD environment variable or configure in config.yaml")
            return False
        
        try:
            self._driver = GraphDatabase.driver(
                config["uri"],
                auth=(config["username"], config["password"]),
                max_connection_lifetime=config["max_connection_lifetime"],
                max_connection_pool_size=config["max_connection_pool_size"],
                connection_acquisition_timeout=config["connection_acquisition_timeout"]
            )
            
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {config['uri']} database '{config['database']}'")
            return True
            
        except AuthError as e:
            logger.error(f"Neo4j authentication failed: {e}")
            return False
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable at {config['uri']}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Neo4j: {e}")
            return False
    
    def disconnect(self):
        """Close the Neo4j connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")
    
    @property
    def driver(self) -> Optional[Driver]:
        """Get the Neo4j driver instance."""
        return self._driver
    
    @property 
    def database(self) -> str:
        """Get the configured database name."""
        return self.config["database"]
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the Neo4j connection.
        
        Returns:
            Dict with health status information
        """
        config = self.config
        if not self._driver:
            return {
                "healthy": False,
                "error": "No connection established",
                "config": {k: v for k, v in config.items() if k != "password"}
            }
        
        try:
            with self._driver.session(database=config["database"]) as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
                return {
                    "healthy": True,
                    "database": config["database"],
                    "uri": config["uri"],
                    "test_query_result": test_value
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "database": config["database"],
                "uri": config["uri"]
            }
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Any:
        """
        Execute a Cypher query against the database.
        
        Args:
            query: Cypher query string
            parameters: Query parameters dictionary
            
        Returns:
            Query result
            
        Raises:
            RuntimeError: If not connected to database
        """
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j database. Call connect() first.")
        
        with self._driver.session(database=self.config["database"]) as session:
            return session.run(query, parameters or {})
    
    def execute_write_transaction(self, transaction_function, *args, **kwargs):
        """
        Execute a write transaction.
        
        Args:
            transaction_function: Function to execute in transaction
            *args, **kwargs: Arguments to pass to transaction function
            
        Returns:
            Transaction result
        """
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j database. Call connect() first.")
        
        with self._driver.session(database=self.config["database"]) as session:
            return session.execute_write(transaction_function, *args, **kwargs)
    
    def execute_read_transaction(self, transaction_function, *args, **kwargs):
        """
        Execute a read transaction.
        
        Args:
            transaction_function: Function to execute in transaction  
            *args, **kwargs: Arguments to pass to transaction function
            
        Returns:
            Transaction result
        """
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j database. Call connect() first.")
        
        with self._driver.session(database=self.config["database"]) as session:
            return session.execute_read(transaction_function, *args, **kwargs)


# Global connection instance
_neo4j_connection: Optional[Neo4jConnection] = None


def get_neo4j_connection() -> Neo4jConnection:
    """
    Get or create a global Neo4j connection instance.
    
    This function provides a singleton pattern for database connections,
    ensuring connection reuse across the application.
    
    Returns:
        Neo4jConnection: Global connection instance
    """
    global _neo4j_connection
    
    if _neo4j_connection is None:
        _neo4j_connection = Neo4jConnection()
    
    return _neo4j_connection


def initialize_connection() -> bool:
    """
    Initialize the global Neo4j connection.
    
    Returns:
        bool: True if initialization successful
    """
    connection = get_neo4j_connection()
    return connection.connect()


def cleanup_connection():
    """Clean up the global Neo4j connection."""
    global _neo4j_connection
    
    if _neo4j_connection:
        _neo4j_connection.disconnect()
        _neo4j_connection = None
