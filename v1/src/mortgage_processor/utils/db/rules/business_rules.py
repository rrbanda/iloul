"""
Business Rules for Mortgage Qualification Logic

This module contains the core business rules for credit score, down payment,
and DTI assessments that are used by the MortgageAdvisorAgent tools.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_business_rules(connection):
    """Load business rules for mortgage qualification logic into Neo4j."""
    
    business_rules = [
        {
            "rule_type": "CreditScoreAssessment",
            "category": "excellent",
            "min_threshold": 740,
            "max_threshold": 850,
            "description": "Excellent credit score - qualifies for best rates",
            "qualification_boost": 25,
            "recommendation_message": "Excellent credit score - qualifies for best rates and most programs"
        },
        {
            "rule_type": "CreditScoreAssessment", 
            "category": "good",
            "min_threshold": 680,
            "max_threshold": 739,
            "description": "Good credit score - qualifies for most programs",
            "qualification_boost": 15,
            "recommendation_message": "Good credit score - qualifies for most programs"
        },
        {
            "rule_type": "CreditScoreAssessment",
            "category": "fair", 
            "min_threshold": 620,
            "max_threshold": 679,
            "description": "Fair credit score - may limit some program options",
            "qualification_boost": 5,
            "recommendation_message": "Fair credit score - may limit some program options"
        },
        {
            "rule_type": "CreditScoreAssessment",
            "category": "poor",
            "min_threshold": 300,
            "max_threshold": 619,
            "description": "Credit score improvement would expand loan options",
            "qualification_boost": -10,
            "recommendation_message": "Credit score improvement would expand loan options"
        },
        {
            "rule_type": "DownPaymentAssessment",
            "category": "excellent",
            "min_threshold": 0.20,
            "max_threshold": 1.0,
            "description": "20%+ down payment - avoids mortgage insurance",
            "qualification_boost": 20,
            "recommendation_message": "20%+ down payment - avoids mortgage insurance"
        },
        {
            "rule_type": "DownPaymentAssessment",
            "category": "good",
            "min_threshold": 0.10,
            "max_threshold": 0.199,
            "description": "Solid down payment amount",
            "qualification_boost": 10,
            "recommendation_message": "Solid down payment amount"
        },
        {
            "rule_type": "DownPaymentAssessment",
            "category": "fair",
            "min_threshold": 0.035,
            "max_threshold": 0.099,
            "description": "Lower down payment - consider government programs",
            "qualification_boost": 0,
            "recommendation_message": "Lower down payment - consider government programs"
        },
        {
            "rule_type": "DownPaymentAssessment",
            "category": "limited",
            "min_threshold": 0.0,
            "max_threshold": 0.034,
            "description": "Limited down payment - focus on zero-down programs",
            "qualification_boost": -5,
            "recommendation_message": "Limited down payment - focus on zero-down programs"
        },
        {
            "rule_type": "DTIAssessment",
            "category": "excellent",
            "min_threshold": 0.0,
            "max_threshold": 0.28,
            "description": "Low debt-to-income ratio - strong financial position",
            "qualification_boost": 20,
            "recommendation_message": "Low debt-to-income ratio - strong financial position"
        },
        {
            "rule_type": "DTIAssessment",
            "category": "good",
            "min_threshold": 0.281,
            "max_threshold": 0.43,
            "description": "Acceptable debt-to-income ratio",
            "qualification_boost": 10,
            "recommendation_message": "Acceptable debt-to-income ratio"
        },
        {
            "rule_type": "DTIAssessment",
            "category": "high",
            "min_threshold": 0.431,
            "max_threshold": 1.0,
            "description": "High debt-to-income ratio - may need to reduce debt",
            "qualification_boost": -15,
            "recommendation_message": "High debt-to-income ratio - may need to reduce debt"
        }
    ]
    
    for rule in business_rules:
        query = """
        CREATE (br:BusinessRule {
            rule_type: $rule_type,
            category: $category,
            min_threshold: $min_threshold,
            max_threshold: $max_threshold,
            description: $description,
            qualification_boost: $qualification_boost,
            recommendation_message: $recommendation_message
        })
        """
        
        connection.execute_query(query, rule)
        logger.info(f"Created BusinessRule: {rule['rule_type']} - {rule['category']}")
    
    logger.info(f"Loaded {len(business_rules)} business rules successfully")
