"""
Scoring Rules for Loan Program Recommendations

This module contains the scoring rules used by the MortgageAdvisorAgent
to calculate recommendation scores for different loan programs.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_scoring_rules(connection):
    """Load scoring rules for loan program recommendations into Neo4j."""
    
    scoring_rules = [
        {
            "rule_name": "CreditScoreMatch",
            "points": 25,
            "description": "Points for meeting minimum credit score requirement"
        },
        {
            "rule_name": "CreditScoreExceed",
            "points": 5,
            "description": "Bonus points for exceeding minimum credit score by 50+ points"
        },
        {
            "rule_name": "DownPaymentMatch",
            "points": 25,
            "description": "Points for meeting minimum down payment requirement"
        },
        {
            "rule_name": "DownPaymentExceed",
            "points": 10,
            "description": "Bonus points for exceeding minimum down payment by 5%+"
        },
        {
            "rule_name": "DTIMatch",
            "points": 25,
            "description": "Points for meeting DTI requirement"
        },
        {
            "rule_name": "DTIExcellent",
            "points": 15,
            "description": "Points for excellent DTI (under 28%)"
        },
        {
            "rule_name": "VAEligibility",
            "points": 30,
            "description": "Special bonus for VA loan eligibility"
        },
        {
            "rule_name": "USDAEligibility",
            "points": 25,
            "description": "Special bonus for USDA area eligibility"
        },
        {
            "rule_name": "FirstTimeBuyerFHA",
            "points": 15,
            "description": "Bonus for first-time buyers with FHA loans"
        },
        {
            "rule_name": "ProfileMatch",
            "points": 20,
            "description": "Points for matching target borrower profile"
        }
    ]
    
    for rule in scoring_rules:
        query = """
        CREATE (sr:ScoringRule {
            rule_name: $rule_name,
            points: $points,
            description: $description
        })
        """
        
        connection.execute_query(query, rule)
        logger.info(f"Created ScoringRule: {rule['rule_name']}")
    
    logger.info(f"Loaded {len(scoring_rules)} scoring rules successfully")
