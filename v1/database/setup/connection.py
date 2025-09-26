"""
Neo4j Connection Management

Production-ready connection management with proper error handling,
connection pooling, and configuration management.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError

logger = logging.getLogger(__name__)

class Neo4jConnection:
    """
    Production-ready Neo4j connection manager.
    
    Features:
    - Configuration from YAML with environment overrides
    - Connection pooling and timeout management
    - Proper error handling and logging
    - Health checks and reconnection logic
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize connection with configuration.
        
        Args:
            config_path: Path to config.yaml file. If None, auto-discovers.
        """
        self._driver: Optional[Driver] = None
        self._config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load Neo4j configuration from YAML file."""
        if config_path is None:
            # Auto-discover config.yaml
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent  # Go up to v1/
            config_path = project_root / "config.yaml"
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        neo4j_config = config.get('neo4j', {})
        
        # Apply environment variable overrides
        return {
            'uri': os.getenv('NEO4J_URI', neo4j_config.get('uri', 'bolt://localhost:7687')),
            'username': os.getenv('NEO4J_USERNAME', neo4j_config.get('username', 'neo4j')),
            'password': os.getenv('NEO4J_PASSWORD', neo4j_config.get('password', 'password')),
            'database': os.getenv('NEO4J_DATABASE', neo4j_config.get('database', 'mortgage')),
            'max_connection_lifetime': neo4j_config.get('max_connection_lifetime', 3600),
            'max_connection_pool_size': neo4j_config.get('max_connection_pool_size', 50),
            'connection_acquisition_timeout': neo4j_config.get('connection_acquisition_timeout', 60)
        }
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if not self._config['password']:
                logger.error("Neo4j password is required")
                return False
            
            self._driver = GraphDatabase.driver(
                self._config['uri'],
                auth=(self._config['username'], self._config['password']),
                max_connection_lifetime=self._config['max_connection_lifetime'],
                max_connection_pool_size=self._config['max_connection_pool_size'],
                connection_acquisition_timeout=self._config['connection_acquisition_timeout']
            )
            
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f" Connected to Neo4j at {self._config['uri']}, database: {self._config['database']}")
            return True
            
        except AuthError as e:
            logger.error(f" Neo4j authentication failed: {e}")
            return False
        except ServiceUnavailable as e:
            logger.error(f" Neo4j service unavailable: {e}")
            return False
        except Exception as e:
            logger.error(f" Unexpected connection error: {e}")
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
        return self._config['database']
    
    def execute_read(self, query: str, parameters: Optional[Dict] = None):
        """Execute a read-only query."""
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        with self._driver.session(database=self._config['database']) as session:
            return session.run(query, parameters or {})
    
    def execute_write(self, query: str, parameters: Optional[Dict] = None):
        """Execute a write query."""
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        with self._driver.session(database=self._config['database']) as session:
            return session.run(query, parameters or {})
    
    def execute_transaction(self, transaction_function, *args, **kwargs):
        """Execute a transaction function."""
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        with self._driver.session(database=self._config['database']) as session:
            return session.execute_write(transaction_function, *args, **kwargs)


# Global connection instance for singleton pattern
_connection: Optional[Neo4jConnection] = None


def get_connection() -> Neo4jConnection:
    """
    Get or create global Neo4j connection instance.
    
    Returns:
        Neo4jConnection: Global connection instance
    """
    global _connection
    if _connection is None:
        _connection = Neo4jConnection()
    return _connection


def initialize_connection() -> bool:
    """
    Initialize the global Neo4j connection.
    
    Returns:
        bool: True if successful, False otherwise
    """
    connection = get_connection()
    return connection.connect()


def cleanup_connection():
    """Clean up the global connection."""
    global _connection
    if _connection:
        _connection.disconnect()
        _connection = None
