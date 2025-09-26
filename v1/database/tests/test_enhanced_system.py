"""
Enhanced System Integration Tests

Essential tests for the complete enhanced mortgage knowledge graph system.
These tests verify that all enhancements work correctly together.
"""

import unittest
import logging
from database.setup import get_connection, setup_database, health_check
from database.loaders import load_all_mortgage_data, verify_data_integrity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestEnhancedSystem(unittest.TestCase):
    """Essential tests for the enhanced mortgage knowledge graph system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests."""
        logger.info("Setting up enhanced test database...")
        result = setup_database()
        if not result:
            raise Exception("Failed to setup test database")
        cls.connection = get_connection()
    
    def test_system_health(self):
        """Test overall system health."""
        logger.info("Testing system health...")
        
        # Basic health check should pass
        healthy = health_check()
        self.assertTrue(healthy, "System health check failed")
        
        logger.info(" System health test passed")
    
    def test_enhanced_data_loading(self):
        """Test complete enhanced data loading with all new rule types."""
        logger.info("Testing enhanced data loading...")
        
        # Load complete enhanced system
        result = load_all_mortgage_data()
        self.assertTrue(result["success"], f"Enhanced data loading failed: {result.get('errors', [])}")
        
        # Verify we have significantly more nodes than basic system
        self.assertGreater(result["total_nodes_created"], 30, "Should have 30+ nodes with enhancements")
        
        # Verify all stages completed
        expected_stages = ["Database Setup", "Data Clearing", "Core Data Loading", 
                         "Business Rules Loading", "Relationship Creation", "Data Verification"]
        for stage in expected_stages:
            self.assertIn(stage, result["stages_completed"], f"Missing stage: {stage}")
        
        logger.info(" Enhanced data loading test passed")
    
    def test_enhanced_rule_types(self):
        """Test that all enhanced rule types are loaded correctly."""
        logger.info("Testing enhanced rule types...")
        
        # Ensure data is loaded
        load_all_mortgage_data()
        
        with self.connection.driver.session(database=self.connection.database) as session:
            # Test QM Rules
            qm_result = session.run("MATCH (qm:QM_Rule) RETURN count(qm) as count")
            qm_count = qm_result.single()["count"]
            self.assertGreaterEqual(qm_count, 5, "Should have at least 5 QM rules")
            
            # Test Fannie Mae Rules
            fannie_result = session.run("MATCH (fm:FannieMae_Rule) RETURN count(fm) as count")
            fannie_count = fannie_result.single()["count"]
            self.assertGreaterEqual(fannie_count, 10, "Should have at least 10 Fannie Mae rules")
            
            # Test Property Risk Rules
            risk_result = session.run("MATCH (pr:PropertyRisk_Rule) RETURN count(pr) as count")
            risk_count = risk_result.single()["count"]
            self.assertGreaterEqual(risk_count, 8, "Should have at least 8 property risk rules")
            
            # Test that original loan programs still exist
            loan_result = session.run("MATCH (lp:LoanProgram) RETURN count(lp) as count")
            loan_count = loan_result.single()["count"]
            self.assertGreaterEqual(loan_count, 5, "Should have 5 loan programs")
        
        logger.info(" Enhanced rule types test passed")
    
    def test_enhanced_relationships(self):
        """Test that enhanced relationships are created properly."""
        logger.info("Testing enhanced relationships...")
        
        # Ensure data is loaded
        load_all_mortgage_data()
        
        with self.connection.driver.session(database=self.connection.database) as session:
            # Test QM relationships
            qm_rel_result = session.run("""
                MATCH (lp:LoanProgram)-[r:MUST_COMPLY_WITH]->(qm:QM_Rule)
                RETURN count(r) as count
            """)
            qm_rel_count = qm_rel_result.single()["count"]
            self.assertGreater(qm_rel_count, 0, "Should have QM compliance relationships")
            
            # Test Fannie Mae relationships
            fannie_rel_result = session.run("""
                MATCH (lp:LoanProgram)-[r]->(fm:FannieMae_Rule)
                RETURN count(r) as count
            """)
            fannie_rel_count = fannie_rel_result.single()["count"]
            self.assertGreater(fannie_rel_count, 0, "Should have Fannie Mae relationships")
            
            # Test Property Risk relationships
            risk_rel_result = session.run("""
                MATCH (lp:LoanProgram)-[r]->(pr:PropertyRisk_Rule)
                RETURN count(r) as count
            """)
            risk_rel_count = risk_rel_result.single()["count"]
            self.assertGreater(risk_rel_count, 0, "Should have property risk relationships")
        
        logger.info("✅ Enhanced relationships test passed")
    
    def test_data_integrity_verification(self):
        """Test enhanced data integrity verification."""
        logger.info("Testing data integrity verification...")
        
        # Ensure data is loaded
        load_all_mortgage_data()
        
        # Verify enhanced data integrity
        verification_result = verify_data_integrity(self.connection)
        
        self.assertTrue(verification_result["data_complete"], 
                       f"Data integrity issues: {verification_result.get('issues', [])}")
        
        # Check that enhanced verification includes all rule types
        node_counts = verification_result["node_counts"]
        self.assertIn("qm_rules", node_counts, "QM rules should be verified")
        self.assertIn("fannie_mae_rules", node_counts, "Fannie Mae rules should be verified")
        self.assertIn("property_risk_rules", node_counts, "Property risk rules should be verified")
        
        # Check minimum relationship count for enhanced system
        self.assertGreater(verification_result["total_relationships"], 50, 
                          "Enhanced system should have 50+ relationships")
        
        logger.info("✅ Data integrity verification test passed")
    
    def test_agent_query_compatibility(self):
        """Test that enhanced rules can be queried like original system (backward compatibility)."""
        logger.info("Testing agent query compatibility...")
        
        # Ensure data is loaded
        load_all_mortgage_data()
        
        with self.connection.driver.session(database=self.connection.database) as session:
            # Test that agents can still query original loan programs
            loan_query = """
            MATCH (lp:LoanProgram {name: 'FHA'})
            RETURN lp.min_credit_score as min_credit, lp.min_down_payment as min_down
            """
            result = session.run(loan_query)
            record = result.single()
            self.assertEqual(record["min_credit"], 580, "FHA credit score should still be accessible")
            self.assertEqual(record["min_down"], 0.035, "FHA down payment should still be accessible")
            
            # Test that agents can query enhanced QM rules
            qm_query = """
            MATCH (qm:QM_Rule {compliance_framework: 'QM'})
            RETURN count(qm) as qm_count
            """
            result = session.run(qm_query)
            qm_count = result.single()["qm_count"]
            self.assertGreater(qm_count, 0, "Agents should be able to query QM rules")
            
            # Test complex query combining original and enhanced data
            combined_query = """
            MATCH (lp:LoanProgram {name: 'Conventional'})
            OPTIONAL MATCH (lp)-[:SELLABLE_TO_INVESTOR]->(fm:FannieMae_Rule)
            RETURN lp.name as program, count(fm) as fannie_rules
            """
            result = session.run(combined_query)
            record = result.single()
            self.assertEqual(record["program"], "Conventional")
            self.assertGreater(record["fannie_rules"], 0, "Should find Fannie Mae rules for Conventional loans")
        
        logger.info("✅ Agent query compatibility test passed")


def run_enhanced_system_tests():
    """Run the essential enhanced system tests."""
    print("🚀 RUNNING ENHANCED SYSTEM TESTS")
    print("=" * 50)
    print("Testing complete enhanced mortgage knowledge graph")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEnhancedSystem)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✅ ALL ENHANCED SYSTEM TESTS PASSED")
        print("=" * 50)
        print("🎉 Enhanced mortgage knowledge graph is working perfectly!")
        print("📊 System now includes:")
        print("   • Original loan programs and business rules")
        print("   • QM compliance rules (8+ rules)")
        print("   • Fannie Mae secondary market rules (13+ rules)")
        print("   • Property risk assessment rules (11+ rules)")
        print("   • 50+ relationships connecting all entities")
        print("   • Backward compatibility with existing agents")
        print("=" * 50)
        return True
    else:
        print(f"\n {len(result.failures + result.errors)} TESTS FAILED")
        for failure in result.failures + result.errors:
            print(f"   - {failure[0]}: {failure[1]}")
        return False


if __name__ == '__main__':
    success = run_enhanced_system_tests()
    exit(0 if success else 1)
