"""
Document Verification Rules

This module contains comprehensive document verification rules for mortgage processing.
All rules are stored as Neo4j nodes to maintain the 100% data-driven approach.

Categories:
- Pay Stub Verification
- Tax Return Verification  
- Bank Statement Verification
- Employment Verification
- Asset Documentation
- Self-Employed Documentation
- Property Documentation
- Credit Documentation
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_document_verification_rules(connection):
    """Load comprehensive document verification rules into Neo4j."""
    
    document_rules = [
        # Pay Stub Rules
        {
            "rule_id": "PAY_STUB_STANDARD",
            "category": "PayStub",
            "document_type": "pay_stub",
            "required_count": 2,
            "time_period": "most_recent_30_days",
            "validation_criteria": ["consecutive_periods", "current_employer", "year_to_date_totals"],
            "required_fields": ["gross_income", "deductions", "employer_name", "pay_period", "year_to_date"],
            "exceptions": ["recent_job_change", "seasonal_employment"],
            "alternative_docs": ["employment_letter", "bank_statements"],
            "description": "Standard pay stub verification for employed borrowers"
        },
        {
            "rule_id": "PAY_STUB_COMMISSION",
            "category": "PayStub",
            "document_type": "pay_stub_commission",
            "required_count": 4,
            "time_period": "most_recent_60_days",
            "validation_criteria": ["commission_breakdown", "base_salary_consistent", "commission_history"],
            "required_fields": ["base_salary", "commission_amount", "total_income", "year_to_date"],
            "exceptions": ["new_commission_position"],
            "additional_requirements": ["commission_tax_returns_2_years"],
            "description": "Pay stub verification for commission-based borrowers"
        },
        {
            "rule_id": "PAY_STUB_HOURLY",
            "category": "PayStub",
            "document_type": "pay_stub_hourly",
            "required_count": 2,
            "time_period": "most_recent_30_days",
            "validation_criteria": ["hours_consistent", "overtime_documented", "rate_verified"],
            "required_fields": ["hourly_rate", "hours_worked", "overtime_hours", "total_pay"],
            "overtime_rules": "consistent_2_year_history_required",
            "description": "Pay stub verification for hourly employees"
        },
        
        # Tax Return Rules
        {
            "rule_id": "TAX_RETURN_W2_STANDARD",
            "category": "TaxReturn",
            "document_type": "tax_return_1040",
            "required_count": 2,
            "time_period": "most_recent_2_years",
            "validation_criteria": ["signed_returns", "all_schedules", "irs_transcripts_match"],
            "required_fields": ["adjusted_gross_income", "total_income", "deductions"],
            "required_schedules": ["Schedule_A", "Schedule_B", "Schedule_C", "Schedule_E"],
            "verification_method": "irs_transcript_4506T",
            "description": "Standard tax return verification for employed borrowers"
        },
        {
            "rule_id": "TAX_RETURN_SELF_EMPLOYED",
            "category": "TaxReturn", 
            "document_type": "tax_return_self_employed",
            "required_count": 2,
            "time_period": "most_recent_2_years",
            "validation_criteria": ["schedule_c_required", "business_income_stable", "depreciation_add_back"],
            "required_schedules": ["Schedule_C", "Schedule_SE"],
            "income_calculation": "net_income_plus_depreciation",
            "trending_requirements": "stable_or_increasing",
            "description": "Tax return verification for self-employed borrowers"
        },
        {
            "rule_id": "TAX_RETURN_RENTAL_INCOME",
            "category": "TaxReturn",
            "document_type": "tax_return_rental",
            "required_count": 2,
            "time_period": "most_recent_2_years",
            "validation_criteria": ["schedule_e_required", "rental_properties_listed", "depreciation_analyzed"],
            "required_schedules": ["Schedule_E"],
            "income_calculation": "net_rental_plus_depreciation",
            "vacancy_factor": 0.75,
            "description": "Tax return verification for rental income"
        },
        
        # Bank Statement Rules
        {
            "rule_id": "BANK_STATEMENT_STANDARD",
            "category": "BankStatement",
            "document_type": "bank_statement",
            "required_count": 2,
            "time_period": "most_recent_60_days",
            "validation_criteria": ["consecutive_months", "sufficient_funds", "deposit_consistency"],
            "required_fields": ["account_number", "ending_balance", "deposits", "withdrawals"],
            "red_flags": ["large_deposits_unexplained", "overdraft_fees", "returned_items"],
            "asset_verification": "funds_to_close_plus_reserves",
            "description": "Standard bank statement verification for assets and deposits"
        },
        {
            "rule_id": "BANK_STATEMENT_GIFT_FUNDS",
            "category": "BankStatement",
            "document_type": "bank_statement_gift",
            "required_count": 2,
            "time_period": "most_recent_60_days",
            "validation_criteria": ["gift_deposit_sourced", "donor_bank_statement", "gift_letter"],
            "required_documentation": ["gift_letter", "donor_bank_statement", "wire_transfer_receipt"],
            "gift_limits": '{"conventional": 0.25, "fha": 1.0, "va": 1.0}',
            "description": "Bank statement verification when gift funds are used"
        },
        {
            "rule_id": "BANK_STATEMENT_BUSINESS",
            "category": "BankStatement",
            "document_type": "bank_statement_business",
            "required_count": 3,
            "time_period": "most_recent_90_days",
            "validation_criteria": ["business_name_match", "deposits_consistent", "business_expenses_reasonable"],
            "required_for": ["self_employed", "business_owners"],
            "analysis_requirements": ["cash_flow_analysis", "deposit_trending"],
            "description": "Business bank statement verification for self-employed borrowers"
        },
        
        # Employment Verification Rules
        {
            "rule_id": "EMPLOYMENT_VOE_STANDARD",
            "category": "Employment",
            "document_type": "verification_of_employment",
            "required_count": 1,
            "time_period": "within_10_days_of_closing",
            "validation_criteria": ["employment_confirmed", "income_confirmed", "position_stable"],
            "required_fields": ["employer_name", "position", "hire_date", "salary", "employment_status"],
            "verbal_verification": "required_if_over_30_days",
            "probability_of_continuance": "likely",
            "description": "Standard employment verification"
        },
        {
            "rule_id": "EMPLOYMENT_VOE_PROBATION",
            "category": "Employment",
            "document_type": "verification_of_employment_probation",
            "required_count": 1,
            "time_period": "within_10_days_of_closing",
            "validation_criteria": ["probation_period_documented", "employer_confidence", "position_permanent"],
            "probation_requirements": "employer_letter_confirmation",
            "acceptable_probation": "90_days_or_less",
            "description": "Employment verification for borrowers in probationary period"
        },
        {
            "rule_id": "EMPLOYMENT_OFFER_LETTER",
            "category": "Employment",
            "document_type": "employment_offer_letter",
            "required_count": 1,
            "time_period": "new_job_start_within_60_days",
            "validation_criteria": ["unconditional_offer", "start_date_confirmed", "salary_specified"],
            "required_fields": ["employer_name", "position", "start_date", "salary", "employment_type"],
            "additional_requirements": ["employer_verification", "employment_gap_explanation"],
            "description": "Employment verification for new job offers"
        },
        
        # Asset Documentation Rules
        {
            "rule_id": "ASSET_401K_STATEMENT",
            "category": "AssetVerification",
            "document_type": "401k_statement",
            "required_count": 1,
            "time_period": "most_recent_quarterly",
            "validation_criteria": ["account_balance", "vesting_schedule", "loan_balance"],
            "usable_percentage": 0.60,
            "required_fields": ["account_balance", "employee_contribution", "employer_match", "loans"],
            "description": "401k/retirement account verification for assets"
        },
        {
            "rule_id": "ASSET_STOCK_BONDS",
            "category": "AssetVerification", 
            "document_type": "investment_statement",
            "required_count": 2,
            "time_period": "most_recent_60_days",
            "validation_criteria": ["market_value", "liquidity", "volatility_discount"],
            "volatility_discount": 0.30,
            "liquidity_requirements": "publicly_traded",
            "description": "Stock and bond verification with volatility discounting"
        },
        {
            "rule_id": "ASSET_CHECKING_SAVINGS",
            "category": "AssetVerification",
            "document_type": "deposit_account_statement",
            "required_count": 2,
            "time_period": "most_recent_60_days",
            "validation_criteria": ["sufficient_balance", "funds_seasoned", "source_documented"],
            "seasoning_requirement": "60_days_minimum",
            "large_deposit_threshold": 1000,
            "description": "Checking and savings account verification"
        },
        
        # Self-Employed Documentation Rules
        {
            "rule_id": "SELF_EMPLOYED_PL_STATEMENT",
            "category": "SelfEmployed",
            "document_type": "profit_loss_statement",
            "required_count": 1,
            "time_period": "year_to_date",
            "validation_criteria": ["cpa_prepared", "interim_statement", "business_trends"],
            "required_fields": ["gross_income", "business_expenses", "net_income"],
            "cpa_requirement": "required_if_ytd_over_2_months",
            "description": "Profit and loss statement for self-employed borrowers"
        },
        {
            "rule_id": "SELF_EMPLOYED_BUSINESS_LICENSE",
            "category": "SelfEmployed",
            "document_type": "business_license",
            "required_count": 1,
            "time_period": "current_and_valid",
            "validation_criteria": ["license_current", "business_name_match", "scope_of_work"],
            "required_fields": ["business_name", "license_number", "expiration_date", "business_type"],
            "description": "Business license verification for self-employed borrowers"
        },
        {
            "rule_id": "SELF_EMPLOYED_ACCOUNTANT_LETTER",
            "category": "SelfEmployed",
            "document_type": "accountant_letter",
            "required_count": 1,
            "time_period": "current_year",
            "validation_criteria": ["cpa_licensed", "business_analysis", "income_confirmation"],
            "required_content": ["business_viability", "income_stability", "financial_outlook"],
            "cpa_license_verification": "required",
            "description": "CPA letter for self-employed borrower verification"
        },
        
        # Property Documentation Rules
        {
            "rule_id": "PROPERTY_PURCHASE_CONTRACT",
            "category": "PropertyDocs",
            "document_type": "purchase_contract",
            "required_count": 1,
            "time_period": "current_transaction",
            "validation_criteria": ["fully_executed", "price_confirmed", "contingencies_clear"],
            "required_fields": ["purchase_price", "earnest_money", "closing_date", "contingencies"],
            "required_signatures": ["buyer", "seller"],
            "description": "Purchase contract verification for property acquisition"
        },
        {
            "rule_id": "PROPERTY_HOMEOWNERS_INSURANCE",
            "category": "PropertyDocs",
            "document_type": "homeowners_insurance",
            "required_count": 1,
            "time_period": "effective_at_closing",
            "validation_criteria": ["coverage_adequate", "lender_named", "premium_escrowed"],
            "coverage_requirements": "replacement_cost_minimum",
            "required_fields": ["coverage_amount", "deductible", "premium", "effective_date"],
            "description": "Homeowners insurance verification and adequacy"
        },
        {
            "rule_id": "PROPERTY_APPRAISAL_REPORT",
            "category": "PropertyDocs",
            "document_type": "appraisal_report",
            "required_count": 1,
            "time_period": "within_120_days",
            "validation_criteria": ["licensed_appraiser", "property_value", "market_analysis"],
            "required_fields": ["property_value", "appraiser_license", "comparable_sales", "property_condition"],
            "value_requirements": "support_loan_amount",
            "description": "Property appraisal report verification"
        },
        
        # Credit Documentation Rules
        {
            "rule_id": "CREDIT_EXPLANATION_LETTER",
            "category": "CreditDocs",
            "document_type": "letter_of_explanation_credit",
            "required_count": 1,
            "time_period": "current_application",
            "validation_criteria": ["borrower_signed", "specific_explanation", "supporting_docs"],
            "required_for": ["late_payments", "collections", "bankruptcies", "foreclosures"],
            "supporting_documentation": "required_when_applicable",
            "description": "Letter of explanation for credit issues"
        },
        {
            "rule_id": "CREDIT_DISPUTE_RESOLUTION",
            "category": "CreditDocs",
            "document_type": "credit_dispute_resolution",
            "required_count": 1,
            "time_period": "prior_to_closing",
            "validation_criteria": ["dispute_resolved", "updated_credit_report", "score_impact_assessed"],
            "resolution_timeframe": "30_days_maximum",
            "description": "Credit dispute resolution documentation"
        },
        {
            "rule_id": "CREDIT_REPORT_RESIDENTIAL",
            "category": "CreditDocs",
            "document_type": "residential_credit_report",
            "required_count": 1,
            "time_period": "within_90_days",
            "validation_criteria": ["tri_merge_report", "scores_available", "all_borrowers_included"],
            "required_fields": ["credit_scores", "payment_history", "account_details", "public_records"],
            "score_requirements": "middle_score_used",
            "description": "Residential mortgage credit report verification"
        }
    ]
    
    for rule in document_rules:
        # Ensure all parameters are explicitly set
        rule_params = {
            "rule_id": rule.get("rule_id"),
            "category": rule.get("category"),
            "document_type": rule.get("document_type"),
            "required_count": rule.get("required_count"),
            "time_period": rule.get("time_period"),
            "validation_criteria": rule.get("validation_criteria"),
            "required_fields": rule.get("required_fields"),
            "exceptions": rule.get("exceptions"),
            "alternative_docs": rule.get("alternative_docs"),
            "additional_requirements": rule.get("additional_requirements"),
            "required_schedules": rule.get("required_schedules"),
            "verification_method": rule.get("verification_method"),
            "income_calculation": rule.get("income_calculation"),
            "trending_requirements": rule.get("trending_requirements"),
            "red_flags": rule.get("red_flags"),
            "asset_verification": rule.get("asset_verification"),
            "required_documentation": rule.get("required_documentation"),
            "gift_limits": rule.get("gift_limits"),
            "verbal_verification": rule.get("verbal_verification"),
            "probability_of_continuance": rule.get("probability_of_continuance"),
            "probation_requirements": rule.get("probation_requirements"),
            "acceptable_probation": rule.get("acceptable_probation"),
            "usable_percentage": rule.get("usable_percentage"),
            "volatility_discount": rule.get("volatility_discount"),
            "liquidity_requirements": rule.get("liquidity_requirements"),
            "cpa_requirement": rule.get("cpa_requirement"),
            "required_signatures": rule.get("required_signatures"),
            "coverage_requirements": rule.get("coverage_requirements"),
            "required_for": rule.get("required_for"),
            "supporting_documentation": rule.get("supporting_documentation"),
            "resolution_timeframe": rule.get("resolution_timeframe"),
            "overtime_rules": rule.get("overtime_rules"),
            "vacancy_factor": rule.get("vacancy_factor"),
            "analysis_requirements": rule.get("analysis_requirements"),
            "seasoning_requirement": rule.get("seasoning_requirement"),
            "large_deposit_threshold": rule.get("large_deposit_threshold"),
            "required_content": rule.get("required_content"),
            "cpa_license_verification": rule.get("cpa_license_verification"),
            "value_requirements": rule.get("value_requirements"),
            "score_requirements": rule.get("score_requirements"),
            "description": rule.get("description")
        }
        
        query = """
        CREATE (dvr:DocumentVerificationRule {
            rule_id: $rule_id,
            category: $category,
            document_type: $document_type,
            required_count: $required_count,
            time_period: $time_period,
            validation_criteria: $validation_criteria,
            required_fields: $required_fields,
            exceptions: $exceptions,
            alternative_docs: $alternative_docs,
            additional_requirements: $additional_requirements,
            required_schedules: $required_schedules,
            verification_method: $verification_method,
            income_calculation: $income_calculation,
            trending_requirements: $trending_requirements,
            red_flags: $red_flags,
            asset_verification: $asset_verification,
            required_documentation: $required_documentation,
            gift_limits: $gift_limits,
            verbal_verification: $verbal_verification,
            probability_of_continuance: $probability_of_continuance,
            probation_requirements: $probation_requirements,
            acceptable_probation: $acceptable_probation,
            usable_percentage: $usable_percentage,
            volatility_discount: $volatility_discount,
            liquidity_requirements: $liquidity_requirements,
            cpa_requirement: $cpa_requirement,
            required_signatures: $required_signatures,
            coverage_requirements: $coverage_requirements,
            required_for: $required_for,
            supporting_documentation: $supporting_documentation,
            resolution_timeframe: $resolution_timeframe,
            overtime_rules: $overtime_rules,
            vacancy_factor: $vacancy_factor,
            analysis_requirements: $analysis_requirements,
            seasoning_requirement: $seasoning_requirement,
            large_deposit_threshold: $large_deposit_threshold,
            required_content: $required_content,
            cpa_license_verification: $cpa_license_verification,
            value_requirements: $value_requirements,
            score_requirements: $score_requirements,
            description: $description
        })
        """
        
        connection.execute_query(query, rule_params)
        logger.info(f"Created DocumentVerificationRule: {rule['rule_id']}")
    
    logger.info(f"Loaded {len(document_rules)} document verification rules successfully")
