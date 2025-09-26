"""
Database Setup Module

Handles Neo4j database connection, setup, and health monitoring.
Production-ready with proper error handling and logging.
"""

from .connection import Neo4jConnection, get_connection
from .database_setup import setup_database, create_database_if_needed
from .health_check import verify_connection, health_check

__all__ = [
    "Neo4jConnection",
    "get_connection", 
    "setup_database",
    "create_database_if_needed",
    "verify_connection",
    "health_check"
]
