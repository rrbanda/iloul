"""
Fannie Mae Secondary Market Rules

Requirements for loans to be eligible for sale to Fannie Mae,
including conforming loan limits, eligibility criteria, and
delivery requirements.

Key Fannie Mae Requirements:
- Conforming loan limits
- Credit score minimums
- LTV limits by property type
- Occupancy requirements
- Property eligibility standards
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_fannie_mae_rules(connection) -> bool:
    """
    Load Fannie Mae secondary market rules into Neo4j.
    
    Args:
        connection: Neo4j connection instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Loading Fannie Mae secondary market rules...")
    
    fannie_mae_rules = [
        # Conforming Loan Limits (2024)
        {
            "rule_id": "FANNIE_CONFORMING_LIMIT_STANDARD",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae",
            "investor": "Fannie Mae",
            "limit_type": "conforming_loan_limit",
            "loan_limit": 766550,  # 2024 standard limit
            "area_type": "standard_cost_area",
            "effective_date": "2024-01-01",
            "property_types": ["single_family", "condo", "townhouse"],
            "description": "2024 conforming loan limit for standard cost areas",
            "annual_adjustment": True
        },
        {
            "rule_id": "FANNIE_CONFORMING_LIMIT_HIGH_COST",
            "rule_type": "SecondaryMarket", 
            "category": "FannieMae",
            "investor": "Fannie Mae",
            "limit_type": "conforming_loan_limit",
            "loan_limit": 1149825,  # 2024 high cost limit
            "area_type": "high_cost_area",
            "effective_date": "2024-01-01",
            "property_types": ["single_family", "condo", "townhouse"],
            "description": "2024 conforming loan limit for high cost areas",
            "annual_adjustment": True
        },
        
        # Credit Score Requirements
        {
            "rule_id": "FANNIE_CREDIT_SCORE_MINIMUM",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae", 
            "investor": "Fannie Mae",
            "requirement_type": "credit_score",
            "min_credit_score": 620,
            "property_type": "primary_residence",
            "ltv_threshold": 0.80,
            "description": "Minimum 620 credit score for primary residence loans with LTV ≤ 80%",
            "compensating_factors_allowed": True
        },
        {
            "rule_id": "FANNIE_CREDIT_SCORE_HIGH_LTV",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae",
            "investor": "Fannie Mae", 
            "requirement_type": "credit_score",
            "min_credit_score": 640,
            "property_type": "primary_residence",
            "ltv_threshold": 0.95,
            "description": "Minimum 640 credit score for high LTV loans (>80%)",
            "compensating_factors_allowed": False
        },
        
        # LTV Limits by Property Type
        {
            "rule_id": "FANNIE_LTV_PRIMARY_RESIDENCE",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae",
            "investor": "Fannie Mae",
            "requirement_type": "ltv_limit",
            "max_ltv": 0.97,
            "property_type": "primary_residence",
            "loan_type": "purchase",
            "description": "Maximum 97% LTV for primary residence purchase loans",
            "first_time_buyer_eligible": True
        },
        {
            "rule_id": "FANNIE_LTV_SECOND_HOME",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae",
            "investor": "Fannie Mae",
            "requirement_type": "ltv_limit", 
            "max_ltv": 0.90,
            "property_type": "second_home",
            "loan_type": "purchase",
            "description": "Maximum 90% LTV for second home purchases",
            "min_down_payment_required": 0.10
        },
        {
            "rule_id": "FANNIE_LTV_INVESTMENT_PROPERTY",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae",
            "investor": "Fannie Mae",
            "requirement_type": "ltv_limit",
            "max_ltv": 0.75,
            "property_type": "investment_property", 
            "loan_type": "purchase",
            "description": "Maximum 75% LTV for investment property purchases",
            "min_down_payment_required": 0.25,
            "reserve_requirements": "2_months_payments"
        },
        
        # DTI Requirements
        {
            "rule_id": "FANNIE_DTI_STANDARD",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae",
            "investor": "Fannie Mae",
            "requirement_type": "debt_to_income",
            "max_dti": 0.45,
            "underwriting_system": "DU_Approve",
            "description": "Maximum 45% DTI for DU Approve recommendations",
            "compensating_factors_required": False
        },
        {
            "rule_id": "FANNIE_DTI_HIGH_RATIO",
            "rule_type": "SecondaryMarket", 
            "category": "FannieMae",
            "investor": "Fannie Mae",
            "requirement_type": "debt_to_income",
            "max_dti": 0.50,
            "underwriting_system": "DU_Approve",
            "compensating_factors_required": True,
            "description": "Maximum 50% DTI with strong compensating factors",
            "required_compensating_factors": ["high_credit_score", "significant_reserves", "stable_employment"]
        },
        
        # Property Eligibility
        {
            "rule_id": "FANNIE_PROPERTY_ELIGIBILITY_CONDO",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae",
            "investor": "Fannie Mae",
            "requirement_type": "property_eligibility",
            "property_type": "condominium",
            "project_approval_required": True,
            "warrantable_condo_required": True,
            "description": "Condos must be in Fannie Mae approved projects",
            "project_eligibility_criteria": ["legal_compliance", "financial_soundness", "marketability"]
        },
        {
            "rule_id": "FANNIE_PROPERTY_ELIGIBILITY_MANUFACTURED",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae", 
            "investor": "Fannie Mae",
            "requirement_type": "property_eligibility",
            "property_type": "manufactured_home",
            "eligible": True,
            "foundation_required": "permanent_foundation",
            "hud_code_compliance": True,
            "description": "Manufactured homes eligible if on permanent foundation and HUD code compliant"
        },
        
        # Reserve Requirements
        {
            "rule_id": "FANNIE_RESERVES_INVESTMENT",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae",
            "investor": "Fannie Mae",
            "requirement_type": "reserves",
            "property_type": "investment_property",
            "required_reserves_months": 2,
            "reserve_calculation": "PITIA",
            "description": "Investment properties require 2 months PITIA reserves",
            "acceptable_reserve_sources": ["checking", "savings", "money_market", "401k_60_percent"]
        },
        
        # Delivery and Documentation
        {
            "rule_id": "FANNIE_DELIVERY_TIMELINE",
            "rule_type": "SecondaryMarket",
            "category": "FannieMae",
            "investor": "Fannie Mae",
            "requirement_type": "delivery",
            "delivery_deadline_days": 60,
            "delivery_method": "electronic_delivery",
            "description": "Loans must be delivered within 60 days of funding",
            "required_documents": ["note", "mortgage", "urla_1003", "appraisal", "title_policy"]
        }
    ]
    
    try:
        # Clear existing Fannie Mae rules
        with connection.driver.session(database=connection.database) as session:
            session.run("MATCH (n:FannieMae_Rule) DELETE n")
            logger.info("Cleared existing Fannie Mae rules")
        
        # Create Fannie Mae rule nodes
        for rule in fannie_mae_rules:
            # Build dynamic query based on available fields
            fields = []
            params = {}
            
            # Core fields that should always be present
            core_fields = ["rule_id", "rule_type", "category", "investor", "description"]
            
            for field in core_fields:
                if field in rule:
                    fields.append(f"{field}: ${field}")
                    params[field] = rule[field]
            
            # Optional fields - only add if present and not None
            all_optional_fields = list(rule.keys())
            for field in all_optional_fields:
                if field not in core_fields and field in rule and rule[field] is not None:
                    fields.append(f"{field}: ${field}")
                    params[field] = rule[field]
            
            # Add timestamps
            fields.extend(["created_at: datetime()", "updated_at: datetime()"])
            
            query = f"""
            CREATE (fm:FannieMae_Rule {{
                {', '.join(fields)}
            }})
            """
            
            with connection.driver.session(database=connection.database) as session:
                session.run(query, params)
                logger.info(f" Created Fannie Mae Rule: {rule['rule_id']}")
        
        logger.info(f"Successfully loaded {len(fannie_mae_rules)} Fannie Mae rules")
        return True
        
    except Exception as e:
        logger.error(f" Error loading Fannie Mae rules: {e}")
        return False


def create_fannie_mae_relationships(connection) -> bool:
    """
    Create relationships between Fannie Mae rules and loan programs.
    
    Args:
        connection: Neo4j connection instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Creating Fannie Mae rule relationships...")
    
    try:
        relationship_queries = [
            # Connect conforming limits to conventional loans
            """
            MATCH (fm:FannieMae_Rule)
            WHERE fm.rule_id IN ['FANNIE_CONFORMING_LIMIT_STANDARD', 'FANNIE_CONFORMING_LIMIT_HIGH_COST']
            MATCH (lp:LoanProgram {name: 'Conventional'})
            CREATE (lp)-[:SELLABLE_TO_INVESTOR]->(fm)
            """,
            
            # Connect credit score requirements to conventional loans
            """
            MATCH (fm:FannieMae_Rule)
            WHERE fm.requirement_type = 'credit_score'
            MATCH (lp:LoanProgram {name: 'Conventional'})
            CREATE (lp)-[:MUST_MEET_INVESTOR_REQUIREMENTS]->(fm)
            """,
            
            # Connect LTV limits to conventional loans
            """
            MATCH (fm:FannieMae_Rule)
            WHERE fm.requirement_type = 'ltv_limit'
            MATCH (lp:LoanProgram {name: 'Conventional'})
            CREATE (lp)-[:SUBJECT_TO_LTV_LIMITS]->(fm)
            """,
            
            # Connect DTI requirements to conventional loans
            """
            MATCH (fm:FannieMae_Rule)
            WHERE fm.requirement_type = 'debt_to_income'
            MATCH (lp:LoanProgram {name: 'Conventional'})
            CREATE (lp)-[:EVALUATED_BY_INVESTOR_DTI]->(fm)
            """
        ]
        
        relationships_created = 0
        with connection.driver.session(database=connection.database) as session:
            for query in relationship_queries:
                result = session.run(query)
                summary = result.consume()
                relationships_created += summary.counters.relationships_created
        
        logger.info(f" Created {relationships_created} Fannie Mae rule relationships")
        return True
        
    except Exception as e:
        logger.error(f" Error creating Fannie Mae relationships: {e}")
        return False
