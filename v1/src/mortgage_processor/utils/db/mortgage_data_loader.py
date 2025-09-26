"""
Mortgage Data Loader for Neo4j

This module loads core mortgage data into the Neo4j database for the
MortgageAdvisorAgent to query. It creates basic nodes for loan programs,
qualification requirements, and mortgage guidance information.

Usage:
    python -m mortgage_processor.utils.db.mortgage_data_loader
    
Or programmatically:
    from mortgage_processor.utils.db.mortgage_data_loader import load_mortgage_data
    load_mortgage_data()
"""

import logging
from typing import Dict, List, Any
from .neo4j_connection import get_neo4j_connection, initialize_connection

logger = logging.getLogger(__name__)


def clear_existing_data():
    """Clear existing mortgage data from Neo4j database."""
    connection = get_neo4j_connection()
    
    clear_queries = [
        "MATCH (n:LoanProgram) DETACH DELETE n",
        "MATCH (n:QualificationRequirement) DETACH DELETE n", 
        "MATCH (n:DocumentRequirement) DETACH DELETE n",
        "MATCH (n:ProcessStep) DETACH DELETE n",
        "MATCH (n:BorrowerProfile) DETACH DELETE n",
        "MATCH (n:LoanLimit) DETACH DELETE n",
        "MATCH (n:BusinessRule) DETACH DELETE n",
        "MATCH (n:ScoringRule) DETACH DELETE n",
        "MATCH (n:QualificationThreshold) DETACH DELETE n",
        "MATCH (n:SpecialRequirement) DETACH DELETE n",
        "MATCH (n:ImprovementStrategy) DETACH DELETE n",
        "MATCH (n:DocumentVerificationRule) DETACH DELETE n",
        "MATCH (n:IncomeCalculationRule) DETACH DELETE n",
        "MATCH (n:PropertyAppraisalRule) DETACH DELETE n",
        "MATCH (n:UnderwritingRule) DETACH DELETE n",
        "MATCH (n:ComplianceRule) DETACH DELETE n",
        "MATCH (n:RatePricingRule) DETACH DELETE n",
        "MATCH (n:IDVerificationRule) DETACH DELETE n"
    ]
    
    for query in clear_queries:
        try:
            connection.execute_query(query)
            logger.info(f"Executed: {query}")
        except Exception as e:
            logger.warning(f"Failed to execute {query}: {e}")


def load_loan_programs():
    """Load loan program data into Neo4j."""
    connection = get_neo4j_connection()
    
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
            ]
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
            ]
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
            ]
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
            ]
        }
    ]
    
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
            benefits: $benefits,
            drawbacks: $drawbacks,
            best_for: $best_for
        })
        """
        
        connection.execute_query(query, program)
        logger.info(f"Created LoanProgram: {program['name']}")


def load_qualification_requirements():
    """Load qualification requirement data into Neo4j."""
    connection = get_neo4j_connection()
    
    requirements = [
        {
            "program": "FHA",
            "requirement_type": "CreditScore",
            "minimum_value": 580,
            "details": "580+ for 3.5% down, 500-579 for 10% down",
            "notes": "Some lenders may require higher scores (620+)"
        },
        {
            "program": "FHA", 
            "requirement_type": "DownPayment",
            "minimum_value": 0.035,
            "details": "3.5% with 580+ credit score, 10% with 500-579 credit score",
            "notes": "Can come from savings, gifts, or down payment assistance programs"
        },
        {
            "program": "VA",
            "requirement_type": "CreditScore", 
            "minimum_value": None,
            "details": "No official minimum, most lenders require 580-620+",
            "notes": "VA doesn't set minimum but lenders have their own requirements"
        },
        {
            "program": "VA",
            "requirement_type": "DownPayment",
            "minimum_value": 0.0,
            "details": "No down payment required",
            "notes": "100% financing available"
        },
        {
            "program": "USDA",
            "requirement_type": "CreditScore",
            "minimum_value": 640,
            "details": "640+ for automated underwriting, lower scores may qualify with manual underwriting",
            "notes": "Some lenders may accept 580+ with compensating factors"
        },
        {
            "program": "Conventional",
            "requirement_type": "CreditScore",
            "minimum_value": 620,
            "details": "620+ typically required, better rates at 740+",
            "notes": "Higher scores get better interest rates"
        },
        {
            "program": "Jumbo",
            "requirement_type": "CreditScore",
            "minimum_value": 700,
            "details": "700+ typically required, 740+ for best rates",
            "notes": "Higher requirements than conforming loans"
        }
    ]
    
    # Create qualification requirement nodes and relationships
    for req in requirements:
        query = """
        MATCH (lp:LoanProgram {name: $program})
        CREATE (qr:QualificationRequirement {
            requirement_type: $requirement_type,
            minimum_value: $minimum_value,
            details: $details,
            notes: $notes
        })
        CREATE (lp)-[:HAS_REQUIREMENT]->(qr)
        """
        
        connection.execute_query(query, req)
        logger.info(f"Created QualificationRequirement: {req['program']} - {req['requirement_type']}")


def load_process_steps():
    """Load mortgage process step guidance into Neo4j."""
    connection = get_neo4j_connection()
    
    process_steps = [
        {
            "category": "PreApplication",
            "step_order": 1,
            "title": "Check Credit Score",
            "description": "Review your credit report and score from all three bureaus",
            "timeline": "Start 3-6 months before applying",
            "tips": [
                "Get free credit reports from annualcreditreport.com",
                "Look for errors and dispute them",
                "Pay down high balances to improve score",
                "Don't close old credit cards"
            ]
        },
        {
            "category": "PreApplication", 
            "step_order": 2,
            "title": "Save for Down Payment",
            "description": "Accumulate funds for down payment and closing costs",
            "timeline": "6-12 months before applying",
            "tips": [
                "Aim for 3-20% depending on loan program",
                "Research down payment assistance programs",
                "Consider gift funds from family",
                "Keep funds in savings account for paper trail"
            ]
        },
        {
            "category": "Application",
            "step_order": 1,
            "title": "Get Pre-approved",
            "description": "Submit application and documents for pre-approval",
            "timeline": "Before house hunting",
            "tips": [
                "Shop with multiple lenders",
                "Compare rates and fees",
                "Get pre-approval letter",
                "Don't make major financial changes during process"
            ]
        },
        {
            "category": "PostApplication",
            "step_order": 1,
            "title": "Submit Documentation",
            "description": "Provide all required documents to lender",
            "timeline": "Within 7-14 days of application",
            "tips": [
                "Organize documents in advance",
                "Respond quickly to lender requests",
                "Keep copies of everything",
                "Update lender on any changes"
            ]
        }
    ]
    
    for step in process_steps:
        query = """
        CREATE (ps:ProcessStep {
            category: $category,
            step_order: $step_order,
            title: $title,
            description: $description,
            timeline: $timeline,
            tips: $tips
        })
        """
        
        connection.execute_query(query, step)
        logger.info(f"Created ProcessStep: {step['category']} - {step['title']}")


def load_borrower_profiles():
    """Load borrower profile scenarios into Neo4j.""" 
    connection = get_neo4j_connection()
    
    profiles = [
        {
            "profile_name": "FirstTimeBuyer",
            "description": "First-time homebuyer with limited savings",
            "typical_credit_range": "580-680",
            "typical_down_payment": "3-5%",
            "recommended_programs": ["FHA", "VA", "USDA"],
            "key_considerations": [
                "Take advantage of first-time buyer programs",
                "Consider FHA loans for lower down payment",
                "Look into down payment assistance",
                "Focus on building credit before applying"
            ]
        },
        {
            "profile_name": "HighIncomeStrong Credit",
            "description": "High-income borrower with excellent credit",
            "typical_credit_range": "740+",
            "typical_down_payment": "10-20%+",
            "recommended_programs": ["Conventional", "Jumbo"],
            "key_considerations": [
                "May qualify for best interest rates",
                "Consider conventional loans to avoid mortgage insurance",
                "Jumbo loans for high-value properties",
                "Shop around for competitive rates"
            ]
        },
        {
            "profile_name": "Military",
            "description": "Active military or eligible veteran",
            "typical_credit_range": "580+",
            "typical_down_payment": "0%",
            "recommended_programs": ["VA"],
            "key_considerations": [
                "VA loans offer best terms for eligible borrowers",
                "No down payment required",
                "No mortgage insurance",
                "Certificate of Eligibility required"
            ]
        },
        {
            "profile_name": "RuralBuyer",
            "description": "Buyer looking in rural or suburban areas",
            "typical_credit_range": "640+", 
            "typical_down_payment": "0-3%",
            "recommended_programs": ["USDA", "FHA"],
            "key_considerations": [
                "Check USDA property eligibility first",
                "Income limits may apply for USDA",
                "USDA offers zero down payment",
                "FHA as backup option"
            ]
        }
    ]
    
    for profile in profiles:
        query = """
        CREATE (bp:BorrowerProfile {
            profile_name: $profile_name,
            description: $description,
            typical_credit_range: $typical_credit_range,
            typical_down_payment: $typical_down_payment,
            recommended_programs: $recommended_programs,
            key_considerations: $key_considerations
        })
        """
        
        connection.execute_query(query, profile)
        logger.info(f"Created BorrowerProfile: {profile['profile_name']}")


# Business rules moved to rules/business_rules.py


# Scoring rules moved to rules/scoring_rules.py


# Qualification thresholds moved to rules/qualification_thresholds.py


def create_relationships():
    """Create relationships between entities."""
    connection = get_neo4j_connection()
    
    # Connect borrower profiles to recommended loan programs
    relationship_queries = [
        """
        MATCH (bp:BorrowerProfile {profile_name: "FirstTimeBuyer"})
        MATCH (lp:LoanProgram) WHERE lp.name IN ["FHA", "VA", "USDA"]
        CREATE (bp)-[:RECOMMENDED_FOR]->(lp)
        """,
        """
        MATCH (bp:BorrowerProfile {profile_name: "HighIncomeStrong Credit"})
        MATCH (lp:LoanProgram) WHERE lp.name IN ["Conventional", "Jumbo"]
        CREATE (bp)-[:RECOMMENDED_FOR]->(lp)
        """,
        """
        MATCH (bp:BorrowerProfile {profile_name: "Military"})
        MATCH (lp:LoanProgram {name: "VA"})
        CREATE (bp)-[:RECOMMENDED_FOR]->(lp)
        """,
        """
        MATCH (bp:BorrowerProfile {profile_name: "RuralBuyer"})
        MATCH (lp:LoanProgram) WHERE lp.name IN ["USDA", "FHA"] 
        CREATE (bp)-[:RECOMMENDED_FOR]->(lp)
        """
    ]
    
    for query in relationship_queries:
        connection.execute_query(query)
        logger.info("Created relationship")


# Special requirements moved to rules/special_requirements.py

# Improvement strategies moved to rules/improvement_strategies.py


def load_mortgage_data():
    """Main function to load all mortgage data into Neo4j."""
    logger.info("Starting mortgage data loading process...")
    
    # Initialize connection
    if not initialize_connection():
        logger.error("Failed to connect to Neo4j database")
        return False
    
    try:
        # Clear existing data
        logger.info("Clearing existing data...")
        clear_existing_data()
        
        # Load core data
        logger.info("Loading loan programs...")
        load_loan_programs()
        
        logger.info("Loading qualification requirements...")
        load_qualification_requirements()
        
        logger.info("Loading process steps...")
        load_process_steps()
        
        logger.info("Loading borrower profiles...")
        load_borrower_profiles()
        
        # Load all rules from modular structure
        connection = get_neo4j_connection()
        
        # Core rules (original MortgageAdvisorAgent rules)
        logger.info("Loading business rules...")
        from .rules.business_rules import load_business_rules
        load_business_rules(connection)
        
        logger.info("Loading scoring rules...")
        from .rules.scoring_rules import load_scoring_rules
        load_scoring_rules(connection)
        
        logger.info("Loading qualification thresholds...")
        from .rules.qualification_thresholds import load_qualification_thresholds
        load_qualification_thresholds(connection)
        
        logger.info("Loading special requirements...")
        from .rules.special_requirements import load_special_requirements
        load_special_requirements(connection)
        
        logger.info("Loading improvement strategies...")
        from .rules.improvement_strategies import load_improvement_strategies
        load_improvement_strategies(connection)
        
        # Comprehensive rule sets for end-to-end processing
        logger.info("Loading document verification rules...")
        from .rules.document_verification import load_document_verification_rules
        load_document_verification_rules(connection)
        
        logger.info("Loading income calculation rules...")
        from .rules.income_calculation import load_income_calculation_rules
        load_income_calculation_rules(connection)
        
        logger.info("Loading property appraisal rules...")
        from .rules.property_appraisal import load_property_appraisal_rules
        load_property_appraisal_rules(connection)
        
        logger.info("Loading underwriting rules...")
        from .rules.underwriting import load_underwriting_rules
        load_underwriting_rules(connection)
        
        logger.info("Loading compliance rules...")
        from .rules.compliance import load_compliance_rules
        load_compliance_rules(connection)
        
        logger.info("Loading rate pricing rules...")
        from .rules.rate_pricing import load_rate_pricing_rules
        load_rate_pricing_rules(connection)
        
        logger.info("Loading ID verification rules...")
        from .rules.id_verification import load_id_verification_rules
        load_id_verification_rules(connection)
        
        logger.info("Creating relationships...")
        create_relationships()
        
        logger.info("Mortgage data loading completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error loading mortgage data: {e}")
        return False


def verify_data_load():
    """Verify that data was loaded correctly."""
    connection = get_neo4j_connection()
    
    verification_queries = [
        # Core mortgage data
        ("LoanProgram nodes", "MATCH (n:LoanProgram) RETURN count(n) as count"),
        ("QualificationRequirement nodes", "MATCH (n:QualificationRequirement) RETURN count(n) as count"),
        ("ProcessStep nodes", "MATCH (n:ProcessStep) RETURN count(n) as count"),
        ("BorrowerProfile nodes", "MATCH (n:BorrowerProfile) RETURN count(n) as count"),
        ("BusinessRule nodes", "MATCH (n:BusinessRule) RETURN count(n) as count"),
        ("ScoringRule nodes", "MATCH (n:ScoringRule) RETURN count(n) as count"),
        ("QualificationThreshold nodes", "MATCH (n:QualificationThreshold) RETURN count(n) as count"),
        ("SpecialRequirement nodes", "MATCH (n:SpecialRequirement) RETURN count(n) as count"),
        ("ImprovementStrategy nodes", "MATCH (n:ImprovementStrategy) RETURN count(n) as count"),
        
        # Comprehensive rule sets for end-to-end processing
        ("DocumentVerificationRule nodes", "MATCH (n:DocumentVerificationRule) RETURN count(n) as count"),
        ("IncomeCalculationRule nodes", "MATCH (n:IncomeCalculationRule) RETURN count(n) as count"),
        ("PropertyAppraisalRule nodes", "MATCH (n:PropertyAppraisalRule) RETURN count(n) as count"),
        ("UnderwritingRule nodes", "MATCH (n:UnderwritingRule) RETURN count(n) as count"),
        ("ComplianceRule nodes", "MATCH (n:ComplianceRule) RETURN count(n) as count"),
        ("RatePricingRule nodes", "MATCH (n:RatePricingRule) RETURN count(n) as count"),
        ("IDVerificationRule nodes", "MATCH (n:IDVerificationRule) RETURN count(n) as count"),
        
        # Relationships
        ("HAS_REQUIREMENT relationships", "MATCH ()-[r:HAS_REQUIREMENT]->() RETURN count(r) as count"),
        ("RECOMMENDED_FOR relationships", "MATCH ()-[r:RECOMMENDED_FOR]->() RETURN count(r) as count")
    ]
    
    print("\nData Load Verification:")
    print("=" * 50)
    
    for description, query in verification_queries:
        try:
            result = connection.execute_query(query)
            count = result.single()["count"]
            print(f"{description}: {count}")
        except Exception as e:
            print(f"{description}: ERROR - {e}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Load mortgage data
    success = load_mortgage_data()
    
    if success:
        # Verify the load
        verify_data_load()
        print("\nMortgage data successfully loaded into Neo4j!")
        print("You can now test the MortgageAdvisorAgent tools.")
    else:
        print("\nFailed to load mortgage data. Check logs for details.")
