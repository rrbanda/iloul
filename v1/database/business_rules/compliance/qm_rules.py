"""
QM (Qualified Mortgage) Compliance Rules

CFPB Qualified Mortgage requirements that ensure consumer protection
and regulatory compliance for mortgage lending.

Key QM Requirements:
- DTI limits (43% maximum)
- Points and fees caps
- Income verification requirements
- No risky loan features
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_qm_rules(connection) -> bool:
    """
    Load QM (Qualified Mortgage) compliance rules into Neo4j.
    
    Args:
        connection: Neo4j connection instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Loading QM compliance rules...")
    
    qm_rules = [
        # Core QM DTI Requirements
        {
            "rule_id": "QM_DTI_LIMIT_GENERAL",
            "rule_type": "RegulatoryCompliance",
            "category": "QualifiedMortgage",
            "compliance_framework": "QM",
            "regulatory_authority": "CFPB",
            "max_dti": 0.43,
            "mandatory": True,
            "effective_date": "2014-01-10",
            "description": "QM loans cannot exceed 43% DTI except for GSE eligible loans",
            "penalty_for_violation": "Loss of legal presumption of compliance",
            "applicable_loan_types": ["conventional", "fha", "va", "usda"]
        },
        {
            "rule_id": "QM_GSE_DTI_EXCEPTION", 
            "rule_type": "RegulatoryCompliance",
            "category": "QualifiedMortgage",
            "compliance_framework": "QM",
            "regulatory_authority": "CFPB",
            "max_dti": None,  # No DTI limit for GSE eligible loans
            "mandatory": True,
            "effective_date": "2014-01-10",
            "description": "GSE eligible loans exempt from 43% DTI limit until January 2021",
            "exception_type": "GSE_Eligible",
            "applicable_loan_types": ["conventional"]
        },
        
        # Points and Fees Limits
        {
            "rule_id": "QM_POINTS_FEES_LIMIT_LARGE",
            "rule_type": "RegulatoryCompliance", 
            "category": "QualifiedMortgage",
            "compliance_framework": "QM",
            "regulatory_authority": "CFPB",
            "points_fees_limit": 0.03,  # 3% for loans >= $110,260
            "loan_amount_threshold": 110260,
            "threshold_type": "minimum",
            "mandatory": True,
            "description": "Points and fees cannot exceed 3% for loans $110,260 and above",
            "calculation_basis": "loan_amount"
        },
        {
            "rule_id": "QM_POINTS_FEES_LIMIT_SMALL",
            "rule_type": "RegulatoryCompliance",
            "category": "QualifiedMortgage", 
            "compliance_framework": "QM",
            "regulatory_authority": "CFPB",
            "points_fees_limit": 3307,  # Fixed dollar amount for smaller loans
            "loan_amount_threshold": 110260,
            "threshold_type": "maximum",
            "mandatory": True,
            "description": "Points and fees cannot exceed $3,307 for loans under $110,260",
            "calculation_basis": "fixed_amount"
        },
        
        # Income Verification Requirements
        {
            "rule_id": "QM_INCOME_VERIFICATION",
            "rule_type": "RegulatoryCompliance",
            "category": "QualifiedMortgage",
            "compliance_framework": "QM", 
            "regulatory_authority": "CFPB",
            "income_verification_required": True,
            "assets_verification_required": True,
            "employment_verification_required": True,
            "mandatory": True,
            "description": "QM requires verification of borrower's ability to repay",
            "verification_methods": ["tax_returns", "pay_stubs", "bank_statements", "employment_verification"],
            "documentation_retention": "3_years"
        },
        
        # Prohibited Loan Features
        {
            "rule_id": "QM_PROHIBITED_FEATURES",
            "rule_type": "RegulatoryCompliance",
            "category": "QualifiedMortgage",
            "compliance_framework": "QM",
            "regulatory_authority": "CFPB",
            "prohibited_features": [
                "interest_only_payments",
                "negative_amortization", 
                "balloon_payments",
                "terms_exceeding_30_years"
            ],
            "mandatory": True,
            "description": "QM loans cannot have risky features",
            "exceptions": ["rural_or_underserved_areas"]
        },
        
        # Safe Harbor vs Rebuttable Presumption
        {
            "rule_id": "QM_SAFE_HARBOR_APR",
            "rule_type": "RegulatoryCompliance",
            "category": "QualifiedMortgage",
            "compliance_framework": "QM",
            "regulatory_authority": "CFPB", 
            "safe_harbor_apr_threshold": 1.5,  # 1.5% above APOR
            "protection_level": "safe_harbor",
            "mandatory": False,
            "description": "QM loans with APR 1.5% or less above APOR receive safe harbor protection",
            "legal_protection": "Cannot be challenged as non-QM"
        },
        {
            "rule_id": "QM_REBUTTABLE_PRESUMPTION_APR", 
            "rule_type": "RegulatoryCompliance",
            "category": "QualifiedMortgage",
            "compliance_framework": "QM",
            "regulatory_authority": "CFPB",
            "rebuttable_presumption_apr_min": 1.5,  # Between 1.5% and 3.5% above APOR
            "rebuttable_presumption_apr_max": 3.5,
            "protection_level": "rebuttable_presumption", 
            "mandatory": False,
            "description": "QM loans with APR 1.5-3.5% above APOR receive rebuttable presumption",
            "legal_protection": "Presumed compliant but can be rebutted"
        }
    ]
    
    try:
        # Clear existing QM rules
        with connection.driver.session(database=connection.database) as session:
            session.run("MATCH (n:QM_Rule) DELETE n")
            logger.info("Cleared existing QM rules")
        
        # Create QM rule nodes
        for rule in qm_rules:
            # Build dynamic query based on available fields
            fields = []
            params = {}
            
            # Always include these core fields
            core_fields = ["rule_id", "rule_type", "category", "compliance_framework", 
                          "regulatory_authority", "mandatory", "description"]
            
            for field in core_fields:
                if field in rule:
                    fields.append(f"{field}: ${field}")
                    params[field] = rule[field]
            
            # Add optional fields if they exist and are not None
            optional_fields = ["max_dti", "effective_date", "penalty_for_violation", 
                             "applicable_loan_types", "exception_type", "points_fees_limit",
                             "loan_amount_threshold", "threshold_type", "calculation_basis",
                             "income_verification_required", "assets_verification_required",
                             "employment_verification_required", "verification_methods",
                             "documentation_retention", "prohibited_features", "exceptions",
                             "safe_harbor_apr_threshold", "protection_level", "legal_protection",
                             "rebuttable_presumption_apr_min", "rebuttable_presumption_apr_max"]
            
            for field in optional_fields:
                if field in rule and rule[field] is not None:
                    fields.append(f"{field}: ${field}")
                    params[field] = rule[field]
            
            # Add timestamps
            fields.extend(["created_at: datetime()", "updated_at: datetime()"])
            
            query = f"""
            CREATE (qm:QM_Rule {{
                {', '.join(fields)}
            }})
            """
            
            with connection.driver.session(database=connection.database) as session:
                session.run(query, params)
                logger.info(f" Created QM Rule: {rule['rule_id']}")
        
        logger.info(f"Successfully loaded {len(qm_rules)} QM compliance rules")
        return True
        
    except Exception as e:
        logger.error(f" Error loading QM rules: {e}")
        return False


def create_qm_relationships(connection) -> bool:
    """
    Create relationships between QM rules and loan programs.
    
    Args:
        connection: Neo4j connection instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Creating QM rule relationships...")
    
    try:
        relationship_queries = [
            # Connect QM DTI rules to all loan programs
            """
            MATCH (qm:QM_Rule {rule_id: 'QM_DTI_LIMIT_GENERAL'})
            MATCH (lp:LoanProgram)
            WHERE lp.name IN ['FHA', 'VA', 'USDA', 'Conventional']
            CREATE (lp)-[:MUST_COMPLY_WITH]->(qm)
            """,
            
            # Connect GSE exception to conventional loans only
            """
            MATCH (qm:QM_Rule {rule_id: 'QM_GSE_DTI_EXCEPTION'})
            MATCH (lp:LoanProgram {name: 'Conventional'})
            CREATE (lp)-[:HAS_EXCEPTION]->(qm)
            """,
            
            # Connect points and fees rules to all programs
            """
            MATCH (qm:QM_Rule)
            WHERE qm.rule_id IN ['QM_POINTS_FEES_LIMIT_LARGE', 'QM_POINTS_FEES_LIMIT_SMALL']
            MATCH (lp:LoanProgram)
            CREATE (lp)-[:MUST_COMPLY_WITH]->(qm)
            """,
            
            # Connect verification requirements to all programs
            """
            MATCH (qm:QM_Rule {rule_id: 'QM_INCOME_VERIFICATION'})
            MATCH (lp:LoanProgram)
            CREATE (lp)-[:REQUIRES_VERIFICATION_PER]->(qm)
            """
        ]
        
        relationships_created = 0
        with connection.driver.session(database=connection.database) as session:
            for query in relationship_queries:
                result = session.run(query)
                summary = result.consume()
                relationships_created += summary.counters.relationships_created
        
        logger.info(f" Created {relationships_created} QM rule relationships")
        return True
        
    except Exception as e:
        logger.error(f" Error creating QM relationships: {e}")
        return False
