"""
Qualification Thresholds for Loan Programs

This module contains the qualification status thresholds used by the
MortgageAdvisorAgent to determine qualification levels.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_qualification_thresholds(connection):
    """Load qualification status thresholds into Neo4j."""
    
    thresholds = [
        {
            "status": "HighlyQualified",
            "min_score": 75,
            "max_score": 150,
            "description": "Highly qualified for this loan program",
            "recommendation_priority": 1
        },
        {
            "status": "Qualified",
            "min_score": 50,
            "max_score": 74,
            "description": "Qualified for this loan program",
            "recommendation_priority": 2
        },
        {
            "status": "QualifiedWithConditions",
            "min_score": 25,
            "max_score": 49,
            "description": "Qualified with some conditions or improvements needed",
            "recommendation_priority": 3
        },
        {
            "status": "NotQualified",
            "min_score": 0,
            "max_score": 24,
            "description": "Does not currently qualify for this loan program",
            "recommendation_priority": 4
        }
    ]
    
    for threshold in thresholds:
        query = """
        CREATE (qt:QualificationThreshold {
            status: $status,
            min_score: $min_score,
            max_score: $max_score,
            description: $description,
            recommendation_priority: $recommendation_priority
        })
        """
        
        connection.execute_query(query, threshold)
        logger.info(f"Created QualificationThreshold: {threshold['status']}")
    
    logger.info(f"Loaded {len(thresholds)} qualification thresholds successfully")
