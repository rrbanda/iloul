"""
Underwriting Business Rules

Core underwriting rules for credit analysis, DTI calculations, 
income verification, and lending decisions.

Categories:
- CreditAnalysis: Credit score, history, derogatory events
- DTIAnalysis: Debt-to-income calculations and limits
- IncomeVerification: Income source analysis
- DecisionMatrix: Final approval/denial logic
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_underwriting_rules(connection) -> bool:
    """
    Load underwriting business rules into Neo4j.
    
    Args:
        connection: Neo4j connection instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Loading underwriting business rules...")
    
    underwriting_rules = [
        # Credit Analysis Rules
        {
            "rule_id": "UW_CREDIT_EXCELLENT",
            "category": "CreditAnalysis",
            "rule_type": "CreditScoring",
            "min_credit_score": 740,
            "max_credit_score": 850,
            "risk_level": "LOW",
            "qualification_boost": 25,
            "description": "Excellent credit score provides strong qualification",
            "loan_programs": ["conventional", "jumbo", "fha", "va", "usda"]
        },
        {
            "rule_id": "UW_CREDIT_GOOD",
            "category": "CreditAnalysis",
            "rule_type": "CreditScoring",
            "min_credit_score": 680,
            "max_credit_score": 739,
            "risk_level": "LOW",
            "qualification_boost": 15,
            "description": "Good credit score meets most program requirements",
            "loan_programs": ["conventional", "fha", "va", "usda"]
        },
        {
            "rule_id": "UW_CREDIT_FAIR",
            "category": "CreditAnalysis", 
            "rule_type": "CreditScoring",
            "min_credit_score": 620,
            "max_credit_score": 679,
            "risk_level": "MEDIUM",
            "qualification_boost": 0,
            "description": "Fair credit requires compensating factors",
            "loan_programs": ["fha", "va", "usda"]
        },
        {
            "rule_id": "UW_CREDIT_POOR",
            "category": "CreditAnalysis",
            "rule_type": "CreditScoring", 
            "min_credit_score": 580,
            "max_credit_score": 619,
            "risk_level": "HIGH",
            "qualification_boost": -15,
            "description": "Poor credit requires manual review and strong compensating factors",
            "loan_programs": ["fha", "va"]
        },
        
        # DTI Analysis Rules
        {
            "rule_id": "UW_DTI_EXCELLENT",
            "category": "DTIAnalysis",
            "rule_type": "DTILimits",
            "max_front_dti": 28.0,
            "max_back_dti": 36.0,
            "risk_level": "LOW",
            "qualification_boost": 20,
            "description": "Conservative DTI ratios indicate strong payment capacity",
            "compensating_factors_required": False
        },
        {
            "rule_id": "UW_DTI_STANDARD",
            "category": "DTIAnalysis",
            "rule_type": "DTILimits",
            "max_front_dti": 31.0,
            "max_back_dti": 43.0,
            "risk_level": "MEDIUM",
            "qualification_boost": 0,
            "description": "Standard DTI ratios meet most program guidelines",
            "compensating_factors_required": False
        },
        {
            "rule_id": "UW_DTI_HIGH",
            "category": "DTIAnalysis",
            "rule_type": "DTILimits",
            "max_front_dti": 33.0,
            "max_back_dti": 45.0,
            "risk_level": "HIGH",
            "qualification_boost": -10,
            "description": "High DTI ratios require compensating factors",
            "compensating_factors_required": True
        },
        
        # Income Verification Rules
        {
            "rule_id": "UW_INCOME_W2_STABLE",
            "category": "IncomeVerification",
            "rule_type": "IncomeSource",
            "income_type": "w2_employment",
            "stability_rating": "HIGH",
            "min_employment_years": 2.0,
            "income_multiplier": 1.0,
            "description": "Stable W-2 employment income at full value",
            "verification_required": ["paystubs", "w2", "voe"]
        },
        {
            "rule_id": "UW_INCOME_SELF_EMPLOYED",
            "category": "IncomeVerification", 
            "rule_type": "IncomeSource",
            "income_type": "self_employed",
            "stability_rating": "MEDIUM",
            "min_employment_years": 2.0,
            "income_multiplier": 0.75,
            "description": "Self-employed income averaged over 2 years at 75% value",
            "verification_required": ["tax_returns_2yr", "profit_loss", "bank_statements"]
        },
        {
            "rule_id": "UW_INCOME_COMMISSION",
            "category": "IncomeVerification",
            "rule_type": "IncomeSource", 
            "income_type": "commission",
            "stability_rating": "MEDIUM",
            "min_employment_years": 2.0,
            "income_multiplier": 0.75,
            "description": "Commission income averaged over 2 years at reduced value",
            "verification_required": ["paystubs", "w2_2yr", "voe", "tax_returns"]
        },
        
        # Decision Matrix Rules
        {
            "rule_id": "UW_APPROVE_STRONG",
            "category": "DecisionMatrix",
            "rule_type": "ApprovalConditions",
            "min_credit_score": 720,
            "max_dti": 36.0,
            "min_down_payment": 0.20,
            "decision": "APPROVE",
            "conditions": [],
            "description": "Strong profile qualifies for automatic approval"
        },
        {
            "rule_id": "UW_APPROVE_CONDITIONS",
            "category": "DecisionMatrix",
            "rule_type": "ApprovalConditions", 
            "min_credit_score": 640,
            "max_dti": 43.0,
            "min_down_payment": 0.05,
            "decision": "APPROVE_WITH_CONDITIONS",
            "conditions": ["income_verification", "asset_verification", "property_appraisal"],
            "description": "Qualified with standard conditions"
        },
        {
            "rule_id": "UW_REFER_MANUAL",
            "category": "DecisionMatrix",
            "rule_type": "ApprovalConditions",
            "min_credit_score": 580,
            "max_dti": 50.0,
            "min_down_payment": 0.03,
            "decision": "REFER_TO_MANUAL",
            "conditions": ["manual_underwriter_review", "compensating_factors_analysis"],
            "description": "Requires manual underwriter review"
        },
        
        # Compensating Factors
        {
            "rule_id": "UW_COMP_ASSETS",
            "category": "CompensatingFactors",
            "rule_type": "AssetCompensation",
            "min_cash_reserves_months": 3.0,
            "qualification_boost": 15,
            "description": "Significant cash reserves offset other risk factors",
            "applicable_scenarios": ["high_dti", "borderline_credit"]
        },
        {
            "rule_id": "UW_COMP_EMPLOYMENT",
            "category": "CompensatingFactors", 
            "rule_type": "EmploymentStability",
            "min_employment_years": 5.0,
            "qualification_boost": 10,
            "description": "Long employment history indicates income stability",
            "applicable_scenarios": ["high_dti", "self_employed"]
        }
    ]
    
    try:
        # Clear existing underwriting rules
        with connection.driver.session(database=connection.database) as session:
            session.run("MATCH (n:UnderwritingRule) DELETE n")
            logger.info("Cleared existing underwriting rules")
        
        # Create underwriting rule nodes
        for rule in underwriting_rules:
            # Build dynamic query based on available fields
            fields = []
            params = {}
            
            # Core fields
            core_fields = ["rule_id", "category", "rule_type", "description"]
            
            for field in core_fields:
                if field in rule:
                    fields.append(f"{field}: ${field}")
                    params[field] = rule[field]
            
            # Optional fields
            optional_fields = [
                "min_credit_score", "max_credit_score", "risk_level", "qualification_boost",
                "max_front_dti", "max_back_dti", "compensating_factors_required",
                "income_type", "stability_rating", "min_employment_years", "income_multiplier",
                "verification_required", "min_down_payment", "decision", "conditions",
                "applicable_scenarios", "loan_programs", "min_cash_reserves_months"
            ]
            
            for field in optional_fields:
                if field in rule and rule[field] is not None:
                    value = rule[field]
                    # Convert lists to JSON strings for Neo4j
                    if isinstance(value, list):
                        import json
                        value = json.dumps(value)
                    fields.append(f"{field}: ${field}")
                    params[field] = value
            
            # Add timestamps
            fields.extend(["created_at: datetime()", "updated_at: datetime()"])
            
            query = f"""
            CREATE (ur:UnderwritingRule {{
                {', '.join(fields)}
            }})
            """
            
            with connection.driver.session(database=connection.database) as session:
                session.run(query, params)
                logger.info(f"✅ Created UnderwritingRule: {rule['rule_id']}")
        
        logger.info(f"Successfully loaded {len(underwriting_rules)} underwriting rules")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading underwriting rules: {e}")
        return False


def create_underwriting_relationships(connection) -> bool:
    """Create relationships between underwriting rules and loan programs"""
    try:
        with connection.driver.session(database=connection.database) as session:
            # Connect credit analysis rules to applicable loan programs
            session.run("""
                MATCH (ur:UnderwritingRule {category: 'CreditAnalysis'}), (lp:LoanProgram)
                WHERE lp.name IN ['FHA', 'VA', 'USDA', 'Conventional', 'Jumbo']
                CREATE (ur)-[:APPLIES_TO]->(lp)
            """)
            
            # Connect DTI rules to all programs
            session.run("""
                MATCH (ur:UnderwritingRule {category: 'DTIAnalysis'}), (lp:LoanProgram)
                CREATE (ur)-[:APPLIES_TO]->(lp)
            """)
            
            logger.info("✅ Created underwriting rule relationships")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creating relationships: {e}")
        return False
