"""
Application Intake Rules

This module contains comprehensive application intake rules for mortgage processing.
All rules are stored as Neo4j nodes to maintain the 100% data-driven approach.

Categories:
- Application Requirements
- Validation Rules
- Initial Qualification Rules
- Workflow Routing Rules
- Status Management Rules
"""

import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_application_intake_rules(connection):
    """Load comprehensive application intake rules into Neo4j."""
    
    application_rules = [
        # Application Requirements
        {
            "rule_id": "APPLICATION_REQUIRED_FIELDS",
            "category": "ApplicationRequirements",
            "rule_type": "required_fields",
            "personal_info": ["first_name", "last_name", "ssn", "date_of_birth", "phone", "email"],
            "current_address": ["street", "city", "state", "zip", "years_at_address"],
            "employment": ["employer_name", "title", "years_employed", "monthly_income"],
            "loan_details": ["loan_purpose", "loan_amount", "property_address", "property_value"],
            "financial": ["assets", "debts", "monthly_expenses"],
            "property_info": ["property_type", "occupancy_type", "property_use"],
            "description": "Required fields for complete mortgage application"
        },
        {
            "rule_id": "APPLICATION_LOAN_PURPOSE_TYPES",
            "category": "ApplicationRequirements",
            "rule_type": "loan_purpose_validation",
            "valid_purposes": ["purchase", "refinance", "cash_out_refinance", "construction", "renovation"],
            "purpose_requirements": {
                "purchase": ["purchase_contract", "property_address", "purchase_price"],
                "refinance": ["current_mortgage_info", "property_value", "payoff_amount"],
                "cash_out_refinance": ["current_mortgage_info", "cash_out_amount", "cash_out_purpose"],
                "construction": ["construction_plans", "builder_info", "construction_timeline"],
                "renovation": ["renovation_plans", "contractor_info", "renovation_cost"]
            },
            "description": "Valid loan purposes and their specific requirements"
        },
        {
            "rule_id": "APPLICATION_PROPERTY_TYPES",
            "category": "ApplicationRequirements",
            "rule_type": "property_validation",
            "valid_property_types": ["single_family_detached", "condominium", "townhouse", "pud", "manufactured", "multi_family_2_4_units"],
            "occupancy_types": ["primary_residence", "second_home", "investment_property"],
            "property_use_restrictions": {
                "primary_residence": "must_occupy_within_60_days",
                "second_home": "cannot_be_rental_property",
                "investment_property": "rental_income_allowed"
            },
            "description": "Valid property types and occupancy requirements"
        },
        
        # Validation Rules
        {
            "rule_id": "APPLICATION_DATA_VALIDATION",
            "category": "ValidationRules",
            "rule_type": "data_format_validation",
            "ssn_format": "xxx-xx-xxxx",
            "phone_format": "xxx-xxx-xxxx",
            "email_format": "valid_email_address",
            "zip_code_format": "xxxxx or xxxxx-xxxx",
            "loan_amount_range": {"min": 50000, "max": 5000000},
            "income_range": {"min": 1000, "max": 100000},
            "credit_score_range": {"min": 300, "max": 850},
            "description": "Data format validation rules for application fields"
        },
        {
            "rule_id": "APPLICATION_COMPLETENESS_CHECK",
            "category": "ValidationRules",
            "rule_type": "completeness_validation",
            "required_completion_percentage": 0.85,
            "critical_fields": ["ssn", "loan_amount", "property_address", "employment_info", "monthly_income"],
            "optional_fields": ["previous_address", "co_borrower_info", "additional_assets"],
            "conditional_requirements": {
                "self_employed": ["tax_returns", "profit_loss_statements"],
                "co_borrower": ["co_borrower_employment", "co_borrower_income"],
                "investment_property": ["rental_income_documentation", "property_management_info"]
            },
            "description": "Application completeness validation requirements"
        },
        
        # Initial Qualification Rules
        {
            "rule_id": "INITIAL_QUALIFICATION_CREDIT",
            "category": "InitialQualification",
            "rule_type": "credit_pre_screen",
            "minimum_credit_scores": {"conventional": 620, "fha": 580, "va": 580, "usda": 640},
            "credit_issues_flags": ["bankruptcy", "foreclosure", "collections", "late_payments"],
            "auto_decline_conditions": ["credit_score_below_500", "bankruptcy_within_12_months", "foreclosure_within_36_months"],
            "manual_review_triggers": ["credit_score_580_to_620", "collections_over_5000", "late_payments_last_12_months"],
            "description": "Initial credit qualification and pre-screening rules"
        },
        {
            "rule_id": "INITIAL_QUALIFICATION_INCOME",
            "category": "InitialQualification", 
            "rule_type": "income_pre_screen",
            "minimum_income_requirements": {"single_borrower": 3000, "joint_borrowers": 4000},
            "income_stability_requirements": {"employment_months": 24, "self_employed_years": 2},
            "income_documentation_levels": {
                "full_documentation": "w2_paystubs_tax_returns",
                "bank_statement": "bank_statements_12_months",
                "asset_depletion": "asset_statements_calculations"
            },
            "dti_pre_screen_limits": {"front_end": 0.31, "back_end": 0.45},
            "description": "Initial income qualification and pre-screening rules"
        },
        {
            "rule_id": "INITIAL_QUALIFICATION_ASSETS",
            "category": "InitialQualification",
            "rule_type": "asset_pre_screen", 
            "minimum_down_payment": {"conventional": 0.05, "fha": 0.035, "va": 0.0, "usda": 0.0},
            "reserve_requirements": {
                "primary_residence": "2_months_payment",
                "second_home": "4_months_payment", 
                "investment_property": "6_months_payment"
            },
            "acceptable_asset_types": ["checking", "savings", "investment", "retirement", "gift_funds"],
            "unacceptable_assets": ["crypto", "unsecured_loans", "credit_card_advances"],
            "description": "Initial asset qualification and down payment requirements"
        },
        
        # Workflow Routing Rules
        {
            "rule_id": "WORKFLOW_ROUTING_DECISIONS",
            "category": "WorkflowRouting",
            "rule_type": "agent_routing",
            "routing_logic": {
                "incomplete_application": "return_to_applicant",
                "needs_guidance": "route_to_mortgage_advisor",
                "ready_for_documents": "route_to_document_agent",
                "needs_pre_approval": "route_to_underwriting_agent",
                "property_questions": "route_to_appraisal_agent"
            },
            "routing_triggers": {
                "guidance_needed": ["first_time_buyer", "loan_program_questions", "qualification_concerns"],
                "document_ready": ["application_complete", "initial_qualification_passed"],
                "appraisal_needed": ["property_value_questions", "market_analysis_needed"],
                "underwriting_ready": ["documents_verified", "appraisal_completed"]
            },
            "description": "Workflow routing decisions based on application status and needs"
        },
        {
            "rule_id": "WORKFLOW_PRIORITY_LEVELS",
            "category": "WorkflowRouting",
            "rule_type": "priority_assignment",
            "priority_levels": {
                "high": ["purchase_contracts_expiring", "rate_lock_expiring", "closing_within_30_days"],
                "medium": ["refinance_applications", "pre_approval_requests"],
                "low": ["rate_shopping", "general_inquiries", "incomplete_applications"]
            },
            "processing_timeframes": {
                "high": "same_day_response",
                "medium": "24_hour_response", 
                "low": "72_hour_response"
            },
            "escalation_rules": ["high_priority_over_24_hours", "medium_priority_over_72_hours"],
            "description": "Application priority levels and processing timeframes"
        },
        
        # Status Management Rules
        {
            "rule_id": "APPLICATION_STATUS_LIFECYCLE",
            "category": "StatusManagement",
            "rule_type": "status_tracking",
            "status_progression": [
                "received", "in_review", "incomplete", "complete", 
                "in_processing", "underwriting", "approved", "denied", "closed"
            ],
            "status_definitions": {
                "received": "application_submitted_initial_review",
                "in_review": "reviewing_for_completeness",
                "incomplete": "missing_required_information",
                "complete": "all_required_fields_present",
                "in_processing": "documents_being_verified",
                "underwriting": "credit_and_risk_analysis",
                "approved": "loan_approved_conditions_met",
                "denied": "application_denied_reasons_provided",
                "closed": "loan_funded_or_withdrawn"
            },
            "description": "Application status lifecycle and definitions"
        },
        {
            "rule_id": "APPLICATION_COMMUNICATION_RULES",
            "category": "StatusManagement",
            "rule_type": "communication_requirements",
            "notification_triggers": {
                "status_change": "notify_applicant_within_1_hour",
                "additional_documents_needed": "notify_applicant_immediately",
                "approval_or_denial": "notify_applicant_within_2_hours",
                "milestone_reached": "notify_applicant_same_day"
            },
            "communication_methods": ["email", "phone", "secure_portal", "text_message"],
            "required_disclosures": {
                "initial_application": ["loan_estimate", "disclosure_package"],
                "underwriting": ["conditions_list", "additional_requirements"],
                "closing": ["closing_disclosure", "final_documents"]
            },
            "description": "Communication requirements and notification rules"
        }
    ]
    
    # Clear existing application intake rules
    with connection.driver.session(database=connection.database) as session:
        session.run("MATCH (r:ApplicationIntakeRule) DELETE r")
    
    # Load new rules
    with connection.driver.session(database=connection.database) as session:
        for rule in application_rules:
            # Convert complex objects to JSON strings for storage
            rule_data = {}
            for key, value in rule.items():
                if isinstance(value, (dict, list)):
                    rule_data[key] = json.dumps(value)
                else:
                    rule_data[key] = value
            
            query = """
            CREATE (r:ApplicationIntakeRule)
            SET r = $rule_data
            """
            
            session.run(query, {"rule_data": rule_data})
    
    logger.info(f"Loaded {len(application_rules)} application intake rules successfully")
