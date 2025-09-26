"""
Underwriting Decision Rules

This module contains comprehensive underwriting rules for mortgage processing.
All rules are stored as Neo4j nodes to maintain the 100% data-driven approach.

Categories:
- Credit Analysis Rules
- Income Analysis Rules  
- Asset Analysis Rules
- DTI Analysis Rules
- Compensating Factors
- Approval Conditions
- Risk Assessment Rules
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_underwriting_rules(connection):
    """Load comprehensive underwriting decision rules into Neo4j."""
    
    underwriting_rules = [
        # Credit Analysis Rules
        {
            "rule_id": "CREDIT_SCORE_MINIMUM",
            "category": "CreditAnalysis",
            "rule_type": "minimum_requirements",
            "loan_programs": ["conventional", "fha", "va", "usda"],
            "minimum_scores": '{"conventional": 620, "fha": 580, "va": 580, "usda": 640}',
            "exceptions": ["compensating_factors", "manual_underwriting"],
            "credit_history_depth": "minimum_3_tradelines",
            "description": "Minimum credit score requirements by loan program"
        },
        {
            "rule_id": "CREDIT_DEROGATORY_EVENTS",
            "category": "CreditAnalysis",
            "rule_type": "derogatory_analysis",
            "bankruptcy_seasoning": '{"chapter_7": 48, "chapter_13": 24}',
            "foreclosure_seasoning": 36,
            "deed_in_lieu_seasoning": 48,
            "short_sale_seasoning": 24,
            "late_payment_tolerance": '{"30_day": 2, "60_day": 1, "90_day": 0}',
            "collection_treatment": "paid_or_payment_plan",
            "description": "Derogatory credit event analysis and seasoning requirements"
        },
        {
            "rule_id": "CREDIT_TRADELINE_ANALYSIS",
            "category": "CreditAnalysis", 
            "rule_type": "tradeline_requirements",
            "minimum_tradelines": 3,
            "account_types": ["revolving", "installment", "mortgage"],
            "account_age_minimum": "12_months_established",
            "payment_history_weight": 0.35,
            "utilization_preferred": 0.30,
            "new_credit_caution": "avoid_new_accounts_during_process",
            "description": "Credit tradeline analysis requirements"
        },
        
        # Income Analysis Rules
        {
            "rule_id": "INCOME_STABILITY_EMPLOYMENT",
            "category": "IncomeAnalysis",
            "rule_type": "employment_stability", 
            "minimum_employment_history": 24,
            "job_gap_tolerance": 30,
            "career_change_analysis": "related_field_preferred",
            "promotion_income_treatment": "base_salary_conservative",
            "probation_period_acceptable": 90,
            "multiple_income_sources": "diversification_risk_assessment",
            "description": "Employment stability and income continuity analysis"
        },
        {
            "rule_id": "INCOME_CALCULATION_VALIDATION",
            "category": "IncomeAnalysis",
            "rule_type": "income_calculation",
            "base_salary": "current_amount_if_stable",
            "commission_bonus": "2_year_average_trending",
            "overtime": "2_year_history_likely_continue",
            "self_employed": "tax_return_average_plus_depreciation",
            "rental_income": "lease_or_market_rent_75_percent",
            "retirement_income": "award_letter_or_statement",
            "description": "Income calculation and validation methodology"
        },
        
        # Asset Analysis Rules
        {
            "rule_id": "ASSET_VERIFICATION_REQUIREMENTS",
            "category": "AssetAnalysis",
            "rule_type": "asset_verification",
            "liquid_assets": "bank_statements_2_months",
            "retirement_assets": "statement_60_percent_value",
            "stock_bond_assets": "statement_70_percent_value",
            "gift_funds": "donor_verification_source",
            "down_payment_seasoning": "60_days_minimum",
            "reserve_requirements": '{"conventional": 2, "fha": 0, "va": 0}',
            "description": "Asset verification and reserve requirements"
        },
        {
            "rule_id": "ASSET_LARGE_DEPOSITS",
            "category": "AssetAnalysis",
            "rule_type": "large_deposit_analysis",
            "large_deposit_threshold": 1000,
            "acceptable_sources": ["payroll", "tax_refund", "gift", "asset_liquidation"],
            "documentation_required": "source_verification_letter",
            "unacceptable_sources": ["cash_advance", "borrowed_funds", "undisclosed_debt"],
            "explanation_threshold": "50_percent_monthly_income",
            "description": "Large deposit analysis and source verification"
        },
        
        # DTI Analysis Rules
        {
            "rule_id": "DTI_RATIO_LIMITS",
            "category": "DTIAnalysis",
            "rule_type": "ratio_limits",
            "front_end_ratio": '{"conventional": 0.28, "fha": 0.31, "va": 0.41, "usda": 0.29}',
            "back_end_ratio": '{"conventional": 0.36, "fha": 0.43, "va": 0.41, "usda": 0.41}',
            "compensating_factors": "allow_higher_ratios",
            "automated_underwriting": "may_exceed_with_approval",
            "manual_underwriting": "stricter_adherence_required",
            "description": "Debt-to-income ratio limits by loan program"
        },
        {
            "rule_id": "DTI_DEBT_CALCULATION",
            "category": "DTIAnalysis",
            "rule_type": "debt_calculation",
            "monthly_payments": "minimum_payment_or_actual",
            "installment_debt": "remaining_payments_over_10_months",
            "revolving_debt": "minimum_payment_or_5_percent_balance",
            "alimony_child_support": "court_ordered_payments",
            "co_signed_debt": "include_unless_12_month_payment_history",
            "student_loans": "actual_payment_or_calculated_payment",
            "description": "Monthly debt calculation methodology"
        },
        
        # Compensating Factors Rules
        {
            "rule_id": "COMPENSATING_FACTORS_STRONG",
            "category": "CompensatingFactors",
            "rule_type": "strong_factors",
            "large_down_payment": 0.20,
            "significant_reserves": "6_months_payments",
            "excellent_credit": 740,
            "stable_income_history": "5_years_same_line_work", 
            "minimal_debt": "low_overall_debt_burden",
            "education_training": "job_related_advanced_education",
            "description": "Strong compensating factors for underwriting flexibility"
        },
        {
            "rule_id": "COMPENSATING_FACTORS_MODERATE",
            "category": "CompensatingFactors",
            "rule_type": "moderate_factors",
            "good_payment_history": "no_late_payments_12_months",
            "conservative_ltv": 0.80,
            "adequate_reserves": "2_months_payments",
            "good_credit": 680,
            "stable_employment": "2_years_same_employer",
            "cash_flow_improvement": "reduced_housing_payment",
            "description": "Moderate compensating factors for risk mitigation"
        },
        
        # Approval Conditions Rules
        {
            "rule_id": "CONDITIONS_PRIOR_TO_DOCS",
            "category": "ApprovalConditions",
            "condition_type": "prior_to_docs",
            "income_verification": "final_employment_verification",
            "asset_verification": "updated_bank_statements",
            "credit_update": "supplement_credit_report",
            "appraisal_completion": "satisfactory_appraisal_review",
            "title_insurance": "clear_title_commitment",
            "insurance_binder": "homeowners_insurance_in_place",
            "description": "Standard conditions prior to document preparation"
        },
        {
            "rule_id": "CONDITIONS_PRIOR_TO_FUNDING",
            "category": "ApprovalConditions",
            "condition_type": "prior_to_funding",
            "final_walkthrough": "property_in_same_condition",
            "closing_disclosure": "signed_cd_3_day_review",
            "funding_authorization": "all_conditions_satisfied",
            "recording_requirements": "deed_of_trust_recorded",
            "insurance_effective": "policy_effective_at_closing",
            "occupancy_verification": "borrower_occupancy_confirmed",
            "description": "Standard conditions prior to loan funding"
        },
        
        # Risk Assessment Rules
        {
            "rule_id": "RISK_LAYERED_ASSESSMENT",
            "category": "RiskAssessment",
            "risk_type": "layered_risk",
            "high_ltv": 0.95,
            "high_dti": 0.40,
            "low_credit_score": 640,
            "limited_reserves": "less_than_2_months",
            "risk_combinations": "limit_high_risk_factors",
            "mitigation_required": "compensating_factors_or_conditions",
            "description": "Layered risk assessment and mitigation requirements"
        },
        {
            "rule_id": "RISK_FIRST_TIME_BUYER",
            "category": "RiskAssessment", 
            "risk_type": "first_time_buyer",
            "definition": "no_homeownership_3_years",
            "education_requirement": "homebuyer_counseling",
            "reserve_enhancement": "additional_reserves_preferred",
            "payment_shock": "analyze_rent_to_payment_increase",
            "support_programs": "down_payment_assistance_available",
            "monitoring": "early_payment_default_risk",
            "description": "First-time homebuyer risk assessment and support"
        },
        {
            "rule_id": "RISK_INVESTMENT_PROPERTY", 
            "category": "RiskAssessment",
            "risk_type": "investment_property",
            "down_payment_minimum": 0.25,
            "reserve_requirements": "6_months_payments",
            "rental_experience": "preferred_not_required",
            "cash_flow_analysis": "positive_cash_flow_preferred",
            "vacancy_factor": "applied_to_rental_income",
            "exit_strategy": "consider_property_marketability",
            "description": "Investment property risk assessment requirements"
        }
    ]
    
    for rule in underwriting_rules:
        # Ensure all parameters are explicitly set
        rule_params = {key: rule.get(key) for key in [
            "rule_id", "category", "rule_type", "loan_programs", "minimum_scores", "exceptions",
            "credit_history_depth", "bankruptcy_seasoning", "foreclosure_seasoning", "deed_in_lieu_seasoning",
            "short_sale_seasoning", "late_payment_tolerance", "collection_treatment", "minimum_tradelines",
            "account_types", "account_age_minimum", "payment_history_weight", "utilization_preferred",
            "new_credit_caution", "minimum_employment_history", "job_gap_tolerance", "career_change_analysis",
            "promotion_income_treatment", "probation_period_acceptable", "multiple_income_sources",
            "base_salary", "commission_bonus", "overtime", "self_employed", "rental_income", "retirement_income",
            "liquid_assets", "retirement_assets", "stock_bond_assets", "gift_funds", "down_payment_seasoning",
            "reserve_requirements", "large_deposit_threshold", "acceptable_sources", "documentation_required",
            "unacceptable_sources", "explanation_threshold", "front_end_ratio", "back_end_ratio",
            "compensating_factors", "automated_underwriting", "manual_underwriting", "monthly_payments",
            "installment_debt", "revolving_debt", "alimony_child_support", "co_signed_debt", "student_loans",
            "large_down_payment", "significant_reserves", "excellent_credit", "stable_income_history",
            "minimal_debt", "education_training", "good_payment_history", "conservative_ltv",
            "adequate_reserves", "good_credit", "stable_employment", "cash_flow_improvement",
            "condition_type", "income_verification", "asset_verification", "credit_update",
            "appraisal_completion", "title_insurance", "insurance_binder", "final_walkthrough",
            "closing_disclosure", "funding_authorization", "recording_requirements", "insurance_effective",
            "occupancy_verification", "risk_type", "high_ltv", "high_dti", "low_credit_score",
            "limited_reserves", "risk_combinations", "mitigation_required", "definition",
            "education_requirement", "reserve_enhancement", "payment_shock", "support_programs",
            "monitoring", "down_payment_minimum", "rental_experience", "cash_flow_analysis",
            "vacancy_factor", "exit_strategy", "description"
        ]}
        query = """
        CREATE (ur:UnderwritingRule {
            rule_id: $rule_id,
            category: $category,
            rule_type: $rule_type,
            loan_programs: $loan_programs,
            minimum_scores: $minimum_scores,
            exceptions: $exceptions,
            credit_history_depth: $credit_history_depth,
            bankruptcy_seasoning: $bankruptcy_seasoning,
            foreclosure_seasoning: $foreclosure_seasoning,
            deed_in_lieu_seasoning: $deed_in_lieu_seasoning,
            short_sale_seasoning: $short_sale_seasoning,
            late_payment_tolerance: $late_payment_tolerance,
            collection_treatment: $collection_treatment,
            minimum_tradelines: $minimum_tradelines,
            account_types: $account_types,
            account_age_minimum: $account_age_minimum,
            payment_history_weight: $payment_history_weight,
            utilization_preferred: $utilization_preferred,
            new_credit_caution: $new_credit_caution,
            minimum_employment_history: $minimum_employment_history,
            job_gap_tolerance: $job_gap_tolerance,
            career_change_analysis: $career_change_analysis,
            promotion_income_treatment: $promotion_income_treatment,
            probation_period_acceptable: $probation_period_acceptable,
            multiple_income_sources: $multiple_income_sources,
            base_salary: $base_salary,
            commission_bonus: $commission_bonus,
            overtime: $overtime,
            self_employed: $self_employed,
            rental_income: $rental_income,
            retirement_income: $retirement_income,
            liquid_assets: $liquid_assets,
            retirement_assets: $retirement_assets,
            stock_bond_assets: $stock_bond_assets,
            gift_funds: $gift_funds,
            down_payment_seasoning: $down_payment_seasoning,
            reserve_requirements: $reserve_requirements,
            large_deposit_threshold: $large_deposit_threshold,
            acceptable_sources: $acceptable_sources,
            documentation_required: $documentation_required,
            unacceptable_sources: $unacceptable_sources,
            explanation_threshold: $explanation_threshold,
            front_end_ratio: $front_end_ratio,
            back_end_ratio: $back_end_ratio,
            compensating_factors: $compensating_factors,
            automated_underwriting: $automated_underwriting,
            manual_underwriting: $manual_underwriting,
            monthly_payments: $monthly_payments,
            installment_debt: $installment_debt,
            revolving_debt: $revolving_debt,
            alimony_child_support: $alimony_child_support,
            co_signed_debt: $co_signed_debt,
            student_loans: $student_loans,
            large_down_payment: $large_down_payment,
            significant_reserves: $significant_reserves,
            excellent_credit: $excellent_credit,
            stable_income_history: $stable_income_history,
            minimal_debt: $minimal_debt,
            education_training: $education_training,
            good_payment_history: $good_payment_history,
            conservative_ltv: $conservative_ltv,
            adequate_reserves: $adequate_reserves,
            good_credit: $good_credit,
            stable_employment: $stable_employment,
            cash_flow_improvement: $cash_flow_improvement,
            condition_type: $condition_type,
            income_verification: $income_verification,
            asset_verification: $asset_verification,
            credit_update: $credit_update,
            appraisal_completion: $appraisal_completion,
            title_insurance: $title_insurance,
            insurance_binder: $insurance_binder,
            final_walkthrough: $final_walkthrough,
            closing_disclosure: $closing_disclosure,
            funding_authorization: $funding_authorization,
            recording_requirements: $recording_requirements,
            insurance_effective: $insurance_effective,
            occupancy_verification: $occupancy_verification,
            risk_type: $risk_type,
            high_ltv: $high_ltv,
            high_dti: $high_dti,
            low_credit_score: $low_credit_score,
            limited_reserves: $limited_reserves,
            risk_combinations: $risk_combinations,
            mitigation_required: $mitigation_required,
            definition: $definition,
            education_requirement: $education_requirement,
            reserve_enhancement: $reserve_enhancement,
            payment_shock: $payment_shock,
            support_programs: $support_programs,
            monitoring: $monitoring,
            down_payment_minimum: $down_payment_minimum,
            rental_experience: $rental_experience,
            cash_flow_analysis: $cash_flow_analysis,
            vacancy_factor: $vacancy_factor,
            exit_strategy: $exit_strategy,
            description: $description
        })
        """
        
        connection.execute_query(query, rule_params)
        logger.info(f"Created UnderwritingRule: {rule['rule_id']}")
    
    logger.info(f"Loaded {len(underwriting_rules)} underwriting rules successfully")
