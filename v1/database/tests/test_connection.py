"""
Connection Tests

Tests for database connectivity, setup, and health monitoring.
"""

import unittest
import logging
from database.setup import get_connection, setup_database, verify_connection, health_check

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestConnection(unittest.TestCase):
    """Test database connection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.connection = get_connection()
    
    def tearDown(self):
        """Clean up after tests."""
        if self.connection and self.connection.driver:
            self.connection.disconnect()
    
    def test_config_loading(self):
        """Test configuration loading from YAML."""
        logger.info("Testing configuration loading...")
        
        # Connection should have valid config
        self.assertIsNotNone(self.connection._config)
        self.assertIn('uri', self.connection._config)
        self.assertIn('username', self.connection._config)
        self.assertIn('database', self.connection._config)
        
        # Database should be 'mortgage'
        self.assertEqual(self.connection._config['database'], 'mortgage')
        
        logger.info(" Configuration loading test passed")
    
    def test_basic_connection(self):
        """Test basic Neo4j connection."""
        logger.info("Testing basic Neo4j connection...")
        
        # Should be able to connect
        result = self.connection.connect()
        self.assertTrue(result, "Failed to connect to Neo4j")
        
        # Driver should be available
        self.assertIsNotNone(self.connection.driver)
        
        # Should be able to execute simple query
        with self.connection.driver.session(database=self.connection.database) as session:
            result = session.run("RETURN 1 as test")
            value = result.single()["test"]
            self.assertEqual(value, 1)
        
        logger.info(" Basic connection test passed")
    
    def test_database_setup(self):
        """Test complete database setup process."""
        logger.info("Testing database setup...")
        
        result = setup_database()
        self.assertTrue(result, "Database setup failed")
        
        logger.info(" Database setup test passed")
    
    def test_health_check(self):
        """Test health check functionality.""" 
        logger.info("Testing health check...")
        
        # Setup database first
        setup_result = setup_database()
        self.assertTrue(setup_result)
        
        # Health check should pass
        health_result = health_check()
        self.assertTrue(health_result, "Health check failed")
        
        # Detailed health check
        detailed_health = verify_connection()
        self.assertTrue(detailed_health["healthy"])
        self.assertIn("connection", detailed_health["checks"])
        self.assertIn("database_access", detailed_health["checks"])
        self.assertIn("read_write", detailed_health["checks"])
        
        logger.info(" Health check test passed")
    
    def test_read_write_operations(self):
        """Test basic read and write operations."""
        logger.info("Testing read/write operations...")
        
        # Connect first
        self.connection.connect()
        
        # Test write operation
        test_data = {"name": "test_node", "timestamp": "2024-01-01"}
        result = self.connection.execute_write(
            "CREATE (t:TestNode $props) RETURN t",
            {"props": test_data}
        )
        self.assertIsNotNone(result)
        
        # Test read operation
        result = self.connection.execute_read(
            "MATCH (t:TestNode {name: $name}) RETURN t.name as name",
            {"name": "test_node"}
        )
        record = result.single()
        self.assertEqual(record["name"], "test_node")
        
        # Cleanup
        self.connection.execute_write(
            "MATCH (t:TestNode {name: $name}) DELETE t",
            {"name": "test_node"}
        )
        
        logger.info(" Read/write operations test passed")


def run_connection_tests():
    """Run all connection tests."""
    print("🔌 RUNNING CONNECTION TESTS")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestConnection)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n ALL CONNECTION TESTS PASSED")
        return True
    else:
        print(f"\n {len(result.failures)} TESTS FAILED")
        return False


if __name__ == '__main__':
    run_connection_tests()
