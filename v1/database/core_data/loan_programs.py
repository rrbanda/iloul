"""
Loan Programs Data

Core loan program definitions with their characteristics, benefits, and requirements.
These form the foundation of the mortgage recommendation system.

Loan Programs:
- FHA: Government-backed, low down payment
- VA: Veterans, zero down payment
- USDA: Rural properties, zero down payment  
- Conventional: Standard loans, flexible
- Jumbo: High-value properties
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def load_loan_programs(connection) -> bool:
    """
    Load all loan program data into Neo4j.
    
    Args:
        connection: Neo4j connection instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Loading loan programs...")
    
    loan_programs = [
        {
            "name": "FHA",
            "full_name": "FHA (Federal Housing Administration) Loan",
            "type": "Government-backed",
            "summary": "Government-insured loan designed for first-time buyers and those with lower credit scores or limited down payment funds",
            "min_credit_score": 580,
            "min_down_payment": 0.035,  # 3.5%
            "max_dti": 0.57,  # 57%
            "mortgage_insurance_required": True,
            "typical_interest_rate": 6.875,
            "benefits": [
                "Low down payment requirement (3.5%)",
                "Lower credit score acceptance", 
                "Gift funds allowed for down payment",
                "Down payment assistance programs available",
                "Assumable loans",
                "Streamline refinancing options available"
            ],
            "drawbacks": [
                "Mortgage insurance required for life of loan",
                "Loan limits lower than conventional",
                "Property must meet FHA standards",
                "Higher total cost due to mortgage insurance"
            ],
            "best_for": [
                "First-time homebuyers",
                "Buyers with limited savings for down payment", 
                "Borrowers with credit scores between 580-640",
                "Those who qualify for down payment assistance"
            ],
            "loan_limits": {
                "low_cost_area": 472030,
                "high_cost_area": 1089300
            }
        },
        {
            "name": "VA",
            "full_name": "VA (Veterans Affairs) Loan", 
            "type": "Government-backed",
            "summary": "Zero down payment loans exclusively for eligible veterans, active military, and surviving spouses",
            "min_credit_score": None,  # No official minimum
            "min_down_payment": 0.0,  # 0%
            "max_dti": 0.41,  # 41%
            "mortgage_insurance_required": False,
            "typical_interest_rate": 6.625,
            "benefits": [
                "No down payment required",
                "No private mortgage insurance (PMI)",
                "Competitive interest rates",
                "No prepayment penalties", 
                "Assumable loans",
                "Help with foreclosure avoidance",
                "Reusable benefit"
            ],
            "drawbacks": [
                "Limited to eligible veterans and military",
                "VA funding fee required (unless exempt)",
                "Property must meet VA minimum property requirements",
                "Must be primary residence only",
                "Limited to specific loan amounts"
            ],
            "best_for": [
                "Eligible veterans and active military personnel",
                "Military families with limited savings",
                "Those wanting to avoid PMI",
                "Buyers seeking competitive rates with no down payment"
            ],
            "eligibility_requirements": [
                "90+ days active duty during wartime",
                "181+ days active duty during peacetime", 
                "6+ years National Guard or Reserves",
                "Surviving spouse of service member"
            ]
        },
        {
            "name": "USDA",
            "full_name": "USDA Rural Development Loan",
            "type": "Government-backed", 
            "summary": "Zero down payment loans for rural and suburban properties with income restrictions",
            "min_credit_score": 640,
            "min_down_payment": 0.0,  # 0%
            "max_dti": None,  # Varies by income
            "mortgage_insurance_required": True,
            "typical_interest_rate": 6.750,
            "benefits": [
                "No down payment required",
                "Below-market interest rates",
                "Low monthly guarantee fee",
                "100% financing available",
                "Fixed-rate loans",
                "Assumable with qualification"
            ],
            "drawbacks": [
                "Geographic restrictions (rural areas only)",
                "Income limits apply",
                "Longer processing times",
                "Must be primary residence", 
                "Property condition requirements"
            ],
            "best_for": [
                "Rural property buyers",
                "Moderate-income families",
                "Those with limited down payment funds",
                "Buyers in qualifying suburban areas"
            ],
            "income_limits": {
                "moderate_income": "115% of area median income",
                "low_income": "80% of area median income"
            }
        },
        {
            "name": "Conventional",
            "full_name": "Conventional Loan",
            "type": "Non-government",
            "summary": "Standard loans not backed by government, offering flexibility for qualified borrowers",
            "min_credit_score": 620,
            "min_down_payment": 0.03,  # 3%
            "max_dti": 0.43,  # 43%
            "mortgage_insurance_required": True,  # If less than 20% down
            "typical_interest_rate": 7.000,
            "benefits": [
                "No government fees or restrictions",
                "Higher loan limits than government programs",
                "PMI can be removed when reaching 20% equity",
                "Faster processing than government loans",
                "Can be used for primary, secondary, or investment properties",
                "Variety of loan terms available"
            ],
            "drawbacks": [
                "Higher credit score requirements",
                "Larger down payment typically needed",
                "Stricter income and asset verification",
                "PMI required with less than 20% down",
                "Less flexible with credit issues"
            ],
            "best_for": [
                "Borrowers with good credit (740+)",
                "Those with stable income and employment",
                "Buyers who can put down 10-20%+",
                "Purchase of higher-priced properties",
                "Investment property purchases"
            ],
            "conforming_limits": {
                "standard_area": 766550,
                "high_cost_area": 1149825
            }
        },
        {
            "name": "Jumbo",
            "full_name": "Jumbo Loan",
            "type": "Non-conforming",
            "summary": "Loans above conforming loan limits for higher-priced properties",
            "min_credit_score": 700,
            "min_down_payment": 0.10,  # 10%
            "max_dti": 0.43,  # 43%
            "mortgage_insurance_required": False,
            "typical_interest_rate": 7.250,
            "benefits": [
                "Can finance high-value properties",
                "Competitive rates for qualified borrowers",
                "Various term options available",
                "No loan amount restrictions",
                "Can be used for luxury properties"
            ],
            "drawbacks": [
                "Stricter qualification requirements",
                "Larger down payment required",
                "Higher interest rates than conforming loans",
                "More extensive documentation required", 
                "Limited lender options",
                "Larger cash reserves needed"
            ],
            "best_for": [
                "High-income borrowers",
                "Luxury property purchases",
                "High-cost real estate markets",
                "Borrowers with excellent credit and substantial assets",
                "Those exceeding conforming loan limits"
            ],
            "minimum_loan_amounts": {
                "standard_area": 766551,
                "high_cost_area": 1149826
            }
        }
    ]
    
    try:
        # Clear existing loan programs
        with connection.driver.session(database=connection.database) as session:
            session.run("MATCH (n:LoanProgram) DETACH DELETE n")
            logger.info("Cleared existing loan programs")
        
        # Create loan program nodes
        for program in loan_programs:
            query = """
            CREATE (lp:LoanProgram {
                name: $name,
                full_name: $full_name,
                type: $type,
                summary: $summary,
                min_credit_score: $min_credit_score,
                min_down_payment: $min_down_payment,
                max_dti: $max_dti,
                mortgage_insurance_required: $mortgage_insurance_required,
                typical_interest_rate: $typical_interest_rate,
                benefits: $benefits,
                drawbacks: $drawbacks,
                best_for: $best_for,
                created_at: datetime(),
                updated_at: datetime()
            })
            """
            
            with connection.driver.session(database=connection.database) as session:
                session.run(query, program)
                logger.info(f" Created LoanProgram: {program['name']}")
        
        logger.info(f"Successfully loaded {len(loan_programs)} loan programs")
        return True
        
    except Exception as e:
        logger.error(f" Error loading loan programs: {e}")
        return False


def get_loan_program_summary() -> Dict[str, Any]:
    """
    Get summary information about loaded loan programs.
    
    Returns:
        dict: Summary of loan programs with key characteristics
    """
    return {
        "total_programs": 5,
        "government_backed": ["FHA", "VA", "USDA"],
        "conventional_programs": ["Conventional", "Jumbo"],
        "zero_down_programs": ["VA", "USDA"],
        "low_down_programs": ["FHA", "Conventional"],
        "key_features": {
            "FHA": "3.5% down, 580 credit score",
            "VA": "0% down, no PMI, military only",
            "USDA": "0% down, rural areas, income limits",
            "Conventional": "3% down, flexible terms",
            "Jumbo": "High-value properties, 10% down"
        }
    }
