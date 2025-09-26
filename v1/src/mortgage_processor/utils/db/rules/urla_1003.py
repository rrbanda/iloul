"""
URLA Form 1003 Rules

This module contains comprehensive URLA (Uniform Residential Loan Application) 
Form 1003 rules for agentic mortgage application processing.
All rules are stored as Neo4j nodes to maintain the 100% data-driven approach.

Categories:
- URLA Field Requirements and Mappings
- Form Validation Rules
- Section Completeness Rules
- Compliance Requirements
- Output Format Specifications
"""

import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_urla_1003_rules(connection):
    """Load comprehensive URLA Form 1003 rules into Neo4j."""
    
    urla_rules = [
        # URLA Form Structure and Sections
        {
            "rule_id": "URLA_FORM_STRUCTURE",
            "category": "FormStructure",
            "rule_type": "section_definitions",
            "form_version": "1003_2021",
            "sections": [
                "Section_1_Borrower_Information",
                "Section_2_Financial_Information_Assets", 
                "Section_3_Financial_Information_Liabilities",
                "Section_4_Loan_and_Property_Information",
                "Section_5_Declarations",
                "Section_6_Acknowledgments_and_Agreements",
                "Section_7_Military_Service",
                "Section_8_Demographic_Information"
            ],
            "required_sections": ["Section_1_Borrower_Information", "Section_2_Financial_Information_Assets", "Section_3_Financial_Information_Liabilities", "Section_4_Loan_and_Property_Information", "Section_5_Declarations"],
            "description": "URLA Form 1003 section structure and requirements"
        },
        
        # Section 1: Borrower Information Field Mappings
        {
            "rule_id": "URLA_SECTION_1_BORROWER",
            "category": "FieldMapping",
            "rule_type": "borrower_information",
            "section": "Section_1_Borrower_Information",
            "field_mappings": {
                "borrower_first_name": "first_name",
                "borrower_middle_name": "middle_name",
                "borrower_last_name": "last_name",
                "borrower_suffix": "suffix",
                "borrower_ssn": "ssn",
                "borrower_home_phone": "phone",
                "borrower_dob": "date_of_birth",
                "borrower_email": "email",
                "borrower_married": "marital_status",
                "borrower_dependents": "number_of_dependents"
            },
            "required_fields": ["borrower_first_name", "borrower_last_name", "borrower_ssn", "borrower_dob", "borrower_home_phone"],
            "validation_rules": {
                "borrower_ssn": "format_xxx_xx_xxxx",
                "borrower_dob": "format_mm_dd_yyyy",
                "borrower_home_phone": "format_xxx_xxx_xxxx_or_international"
            },
            "description": "URLA Section 1 borrower information field mappings and validation"
        },
        
        # Current Address Information
        {
            "rule_id": "URLA_CURRENT_ADDRESS",
            "category": "FieldMapping",
            "rule_type": "current_address",
            "section": "Section_1_Borrower_Information",
            "field_mappings": {
                "current_street_address": "current_street",
                "current_city": "current_city",
                "current_state": "current_state",
                "current_zip": "current_zip",
                "current_country": "current_country",
                "years_at_current_address": "years_at_address",
                "months_at_current_address": "months_at_address",
                "housing_expense_rent": "monthly_rent",
                "housing_expense_own": "monthly_mortgage_payment"
            },
            "required_fields": ["current_street_address", "current_city", "current_state", "current_zip"],
            "address_tenure_requirement": "minimum_2_years_or_previous_address_required",
            "description": "URLA current address information requirements"
        },
        
        # Employment Information
        {
            "rule_id": "URLA_EMPLOYMENT_INFO",
            "category": "FieldMapping", 
            "rule_type": "employment_information",
            "section": "Section_1_Borrower_Information",
            "field_mappings": {
                "employer_name": "employer_name",
                "employer_address": "employer_address",
                "employer_phone": "employer_phone",
                "position_title": "job_title",
                "employment_start_date": "employment_start_date",
                "employment_years": "years_employed",
                "employment_months": "months_employed",
                "employment_type": "employment_type",
                "base_employment_income": "monthly_gross_income",
                "overtime_income": "monthly_overtime",
                "bonus_income": "monthly_bonus",
                "commission_income": "monthly_commission",
                "self_employed": "self_employed_indicator"
            },
            "employment_history_requirement": "minimum_2_years_required",
            "self_employed_requirements": ["tax_returns_2_years", "profit_loss_statements", "business_license"],
            "description": "URLA employment and income information requirements"
        },
        
        # Section 2: Financial Information - Assets
        {
            "rule_id": "URLA_SECTION_2_ASSETS",
            "category": "FieldMapping",
            "rule_type": "financial_assets",
            "section": "Section_2_Financial_Information_Assets",
            "asset_types": {
                "checking_accounts": "checking_account_balance",
                "savings_accounts": "savings_account_balance", 
                "investment_accounts": "investment_account_balance",
                "retirement_accounts": "retirement_account_balance",
                "life_insurance": "life_insurance_cash_value",
                "other_assets": "other_assets_value",
                "real_estate": "real_estate_value",
                "automobiles": "automobile_value"
            },
            "asset_verification_requirements": {
                "bank_accounts": "2_months_statements_required",
                "investment_accounts": "most_recent_statement_required",
                "retirement_accounts": "most_recent_statement_required"
            },
            "liquid_asset_calculation": "checking_savings_investment_minus_verification_of_deposit",
            "description": "URLA Section 2 asset information and verification requirements"
        },
        
        # Section 3: Financial Information - Liabilities
        {
            "rule_id": "URLA_SECTION_3_LIABILITIES",
            "category": "FieldMapping",
            "rule_type": "financial_liabilities",
            "section": "Section_3_Financial_Information_Liabilities",
            "liability_types": {
                "installment_loans": "installment_debt_balance",
                "revolving_credit": "revolving_debt_balance",
                "mortgage_loans": "mortgage_debt_balance",
                "other_liabilities": "other_debt_balance",
                "child_support": "child_support_payment",
                "alimony": "alimony_payment"
            },
            "monthly_payment_calculation": "required_for_dti_calculation",
            "liability_verification": "credit_report_and_statements_required",
            "description": "URLA Section 3 liability information and payment requirements"
        },
        
        # Section 4: Loan and Property Information
        {
            "rule_id": "URLA_SECTION_4_LOAN_PROPERTY",
            "category": "FieldMapping",
            "rule_type": "loan_property_information",
            "section": "Section_4_Loan_and_Property_Information",
            "field_mappings": {
                "mortgage_applied_for": "loan_program_type",
                "loan_amount": "loan_amount",
                "purpose_of_loan": "loan_purpose",
                "property_address": "property_address",
                "property_city": "property_city", 
                "property_state": "property_state",
                "property_zip": "property_zip",
                "property_type": "property_type",
                "manner_of_title": "title_manner",
                "source_of_down_payment": "down_payment_source",
                "estate_will_be_held": "estate_type"
            },
            "loan_purpose_types": ["Purchase", "Refinance", "Construction", "Other"],
            "property_types": ["Single Family Detached", "Condominium", "Planned Unit Development", "Manufactured Housing", "Townhouse", "Other"],
            "occupancy_types": ["Primary Residence", "Second Home", "Investment Property"],
            "description": "URLA Section 4 loan and property information requirements"
        },
        
        # Section 5: Declarations
        {
            "rule_id": "URLA_SECTION_5_DECLARATIONS",
            "category": "FieldMapping",
            "rule_type": "declarations",
            "section": "Section_5_Declarations",
            "declaration_questions": [
                "outstanding_judgments",
                "declared_bankruptcy_past_7_years",
                "foreclosure_or_deed_in_lieu",
                "party_to_lawsuit",
                "obligation_to_pay_alimony",
                "delinquent_on_debt",
                "down_payment_borrowed",
                "comaker_or_endorser",
                "us_citizen",
                "permanent_resident_alien",
                "primary_residence",
                "ownership_interest_in_property"
            ],
            "required_explanations": ["bankruptcy", "foreclosure", "lawsuit", "delinquent_debt"],
            "citizenship_verification": "required_documentation",
            "description": "URLA Section 5 declaration questions and requirements"
        },
        
        # Military Service Information (Section 7)
        {
            "rule_id": "URLA_SECTION_7_MILITARY",
            "category": "FieldMapping",
            "rule_type": "military_service",
            "section": "Section_7_Military_Service",
            "field_mappings": {
                "military_service": "military_service_indicator",
                "military_status": "military_status",
                "va_benefits": "va_benefits_indicator"
            },
            "military_status_types": ["Active Duty", "National Guard", "Reserves", "Retired", "Separated", "Never Served"],
            "va_loan_requirements": ["certificate_of_eligibility", "dd214_if_separated"],
            "description": "URLA Section 7 military service information"
        },
        
        # Form Validation and Completeness Rules
        {
            "rule_id": "URLA_VALIDATION_COMPLETENESS",
            "category": "ValidationRules",
            "rule_type": "form_completeness",
            "minimum_completion_percentage": 0.95,
            "critical_sections": ["Section_1_Borrower_Information", "Section_4_Loan_and_Property_Information"],
            "signature_requirements": {
                "borrower_signature": "required",
                "co_borrower_signature": "required_if_co_borrower",
                "date_signed": "required",
                "loan_officer_signature": "required"
            },
            "certification_statement": "borrower_certification_and_authorization_required",
            "description": "URLA form validation and completeness requirements"
        },
        
        # Compliance and Regulatory Requirements
        {
            "rule_id": "URLA_COMPLIANCE_REQUIREMENTS",
            "category": "ComplianceRules",
            "rule_type": "regulatory_compliance",
            "fannie_mae_requirements": "dll_requirements_compliance",
            "freddie_mac_requirements": "form_65_compliance",
            "fha_requirements": "hud_92900_compliance",
            "va_requirements": "va_26_1820_compliance",
            "usda_requirements": "rd_3555_compliance",
            "privacy_disclosures": ["privacy_notice", "information_sharing_disclosure"],
            "hmda_reporting": "demographic_information_section_8",
            "description": "URLA regulatory compliance and disclosure requirements"
        },
        
        # Output Format Specifications
        {
            "rule_id": "URLA_OUTPUT_FORMAT",
            "category": "OutputFormat",
            "rule_type": "form_generation",
            "output_formats": ["json", "xml", "pdf", "html"],
            "fannie_mae_xml_schema": "mismo_3_4_schema_compliance",
            "field_validation_rules": "mismo_data_dictionary_compliance",
            "form_layout": "official_urla_1003_layout",
            "electronic_signature_compliance": "esign_act_compliance",
            "audit_trail_requirements": "form_generation_tracking",
            "description": "URLA form output format and compliance specifications"
        }
    ]
    
    # Clear existing URLA rules
    with connection.driver.session(database=connection.database) as session:
        session.run("MATCH (r:URLARule) DELETE r")
    
    # Load new URLA rules
    with connection.driver.session(database=connection.database) as session:
        for rule in urla_rules:
            # Convert complex objects to JSON strings for storage
            rule_data = {}
            for key, value in rule.items():
                if isinstance(value, (dict, list)):
                    rule_data[key] = json.dumps(value)
                else:
                    rule_data[key] = value
            
            query = """
            CREATE (r:URLARule)
            SET r = $rule_data
            """
            
            session.run(query, {"rule_data": rule_data})
    
    logger.info(f"Loaded {len(urla_rules)} URLA Form 1003 rules successfully")
