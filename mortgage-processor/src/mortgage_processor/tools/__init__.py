"""
Tools package for mortgage processing system
Organized by functional area for better maintainability
"""

# Core mortgage processing tools
from .core import (
    # Document processing tools
    classify_document_type,
    validate_document_expiration,
    extract_personal_information,
    extract_income_information,
    check_document_quality,
    authorize_credit_check,
    generate_urla_1003_form,
    cross_validate_documents,
    get_current_date_time,
    
    # Conversational application tools
    extract_personal_info,
    extract_employment_info,
    extract_property_info,
    extract_financial_info,
    analyze_application_state,
    
    # Database tools
    submit_application_to_database,
    check_application_status,
    
    # Dynamic UI tools
    generate_contextual_prompts,
    generate_next_step_guidance,
    
    # Mortgage business logic tools
    calculate_debt_to_income_ratio,
    calculate_loan_to_value_ratio,
    calculate_monthly_payment,
    assess_affordability,
    check_loan_program_eligibility,
    generate_pre_approval_assessment,
    
    # Credit & income verification tools
    simulate_credit_check,
    verify_employment_history,
    validate_income_sources,
    analyze_bank_statements
)

# Property-related tools
from .property import (
    request_property_appraisal,
    analyze_property_value,
    check_property_compliance,
    calculate_property_taxes,
    assess_property_risks
)

# Underwriting tools
from .underwriting import (
    comprehensive_risk_analysis,
    loan_decision_engine,
    guideline_compliance_check,
    generate_approval_conditions,
    exception_analysis
)

# Compliance tools
from .compliance import (
    trid_compliance_check,
    fair_lending_analysis,
    documentation_completeness_check,
    regulatory_validation,
    audit_trail_generator
)

# Closing tools
from .closing import (
    prepare_closing_documents,
    coordinate_title_escrow,
    calculate_closing_costs,
    schedule_closing_meeting,
    post_closing_coordination
)

# Customer service tools
from .customer_service import (
    get_application_status,
    update_customer_on_status,
    request_additional_documents,
    track_document_submission,
    create_customer_issue_ticket,
    escalate_customer_issue,
    schedule_customer_callback,
    send_proactive_communication,
    provide_general_mortgage_support
)

__all__ = [
    # Core tools
    "classify_document_type",
    "validate_document_expiration", 
    "extract_personal_information",
    "extract_income_information",
    "check_document_quality",
    "authorize_credit_check",
    "generate_urla_1003_form",
    "cross_validate_documents",
    "get_current_date_time",
    "extract_personal_info",
    "extract_employment_info", 
    "extract_property_info",
    "extract_financial_info",
    "analyze_application_state",
    "submit_application_to_database",
    "check_application_status",
    "generate_contextual_prompts",
    "generate_next_step_guidance",
    "calculate_debt_to_income_ratio",
    "calculate_loan_to_value_ratio",
    "calculate_monthly_payment",
    "assess_affordability",
    "check_loan_program_eligibility",
    "generate_pre_approval_assessment",
    "simulate_credit_check",
    "verify_employment_history",
    "validate_income_sources",
    "analyze_bank_statements",
    
    # Property tools
    "request_property_appraisal",
    "analyze_property_value",
    "check_property_compliance", 
    "calculate_property_taxes",
    "assess_property_risks",
    
    # Underwriting tools
    "comprehensive_risk_analysis",
    "loan_decision_engine",
    "guideline_compliance_check",
    "generate_approval_conditions",
    "exception_analysis",
    
    # Compliance tools
    "trid_compliance_check",
    "fair_lending_analysis",
    "documentation_completeness_check",
    "regulatory_validation",
    "audit_trail_generator",
    
    # Closing tools
    "prepare_closing_documents",
    "coordinate_title_escrow",
    "calculate_closing_costs",
    "schedule_closing_meeting",
    "post_closing_coordination",
    
    # Customer service tools
    "get_application_status",
    "update_customer_on_status",
    "request_additional_documents",
    "track_document_submission",
    "create_customer_issue_ticket",
    "escalate_customer_issue",
    "schedule_customer_callback",
    "send_proactive_communication",
    "provide_general_mortgage_support"
]
