"""
Core Data Tests

Tests for loan programs, borrower profiles, and other core mortgage data.
"""

import unittest
import logging
from database.setup import get_connection, setup_database
from database.core_data import load_loan_programs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCoreData(unittest.TestCase):
    """Test core mortgage data loading and integrity."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests."""
        logger.info("Setting up test database...")
        result = setup_database()
        if not result:
            raise Exception("Failed to setup test database")
        cls.connection = get_connection()
    
    def test_loan_programs_loading(self):
        """Test loan programs loading."""
        logger.info("Testing loan programs loading...")
        
        # Load loan programs
        result = load_loan_programs(self.connection)
        self.assertTrue(result, "Failed to load loan programs")
        
        # Verify loan programs were created
        with self.connection.driver.session(database=self.connection.database) as session:
            result = session.run("MATCH (lp:LoanProgram) RETURN count(lp) as count")
            count = result.single()["count"]
            self.assertGreaterEqual(count, 5, "Expected at least 5 loan programs")
        
        logger.info(" Loan programs loading test passed")
    
    def test_loan_program_properties(self):
        """Test loan program properties and data integrity."""
        logger.info("Testing loan program properties...")
        
        # Load data first
        load_loan_programs(self.connection)
        
        # Check FHA loan properties
        with self.connection.driver.session(database=self.connection.database) as session:
            result = session.run("""
                MATCH (lp:LoanProgram {name: 'FHA'})
                RETURN lp.min_credit_score as credit_score,
                       lp.min_down_payment as down_payment,
                       lp.type as type
            """)
            
            record = result.single()
            self.assertIsNotNone(record, "FHA loan program not found")
            self.assertEqual(record["credit_score"], 580)
            self.assertEqual(record["down_payment"], 0.035)
            self.assertEqual(record["type"], "Government-backed")
        
        # Check VA loan properties
        with self.connection.driver.session(database=self.connection.database) as session:
            result = session.run("""
                MATCH (lp:LoanProgram {name: 'VA'})
                RETURN lp.min_down_payment as down_payment,
                       lp.mortgage_insurance_required as pmi_required
            """)
            
            record = result.single()
            self.assertIsNotNone(record, "VA loan program not found")
            self.assertEqual(record["down_payment"], 0.0)  # Zero down
            self.assertEqual(record["pmi_required"], False)  # No PMI
        
        logger.info(" Loan program properties test passed")
    
    def test_loan_program_completeness(self):
        """Test that all expected loan programs are loaded."""
        logger.info("Testing loan program completeness...")
        
        # Load data first
        load_loan_programs(self.connection)
        
        expected_programs = ["FHA", "VA", "USDA", "Conventional", "Jumbo"]
        
        with self.connection.driver.session(database=self.connection.database) as session:
            result = session.run("MATCH (lp:LoanProgram) RETURN lp.name as name ORDER BY name")
            actual_programs = [record["name"] for record in result]
        
        for program in expected_programs:
            self.assertIn(program, actual_programs, f"Missing loan program: {program}")
        
        logger.info(" Loan program completeness test passed")
    
    def test_data_validation(self):
        """Test data validation and constraints."""
        logger.info("Testing data validation...")
        
        # Load data first
        load_loan_programs(self.connection)
        
        # All loan programs should have required fields
        with self.connection.driver.session(database=self.connection.database) as session:
            result = session.run("""
                MATCH (lp:LoanProgram)
                WHERE lp.name IS NULL OR lp.full_name IS NULL OR lp.type IS NULL
                RETURN count(lp) as invalid_count
            """)
            
            invalid_count = result.single()["invalid_count"]
            self.assertEqual(invalid_count, 0, "Found loan programs with missing required fields")
        
        # All down payment percentages should be valid (0-1)
        with self.connection.driver.session(database=self.connection.database) as session:
            result = session.run("""
                MATCH (lp:LoanProgram)
                WHERE lp.min_down_payment < 0 OR lp.min_down_payment > 1
                RETURN count(lp) as invalid_count
            """)
            
            invalid_count = result.single()["invalid_count"]
            self.assertEqual(invalid_count, 0, "Found invalid down payment percentages")
        
        logger.info(" Data validation test passed")


def run_core_data_tests():
    """Run all core data tests."""
    print("📊 RUNNING CORE DATA TESTS")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCoreData)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n ALL CORE DATA TESTS PASSED")
        return True
    else:
        print(f"\n {len(result.failures)} TESTS FAILED")
        for failure in result.failures:
            print(f"   - {failure[0]}: {failure[1]}")
        return False


if __name__ == '__main__':
    run_core_data_tests()
