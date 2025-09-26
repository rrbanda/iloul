"""
Income Calculation Rules

This module contains comprehensive income calculation rules for mortgage processing.
All rules are stored as Neo4j nodes to maintain the 100% data-driven approach.

Categories:
- W2 Employment Income
- Self-Employed Income
- Commission and Bonus Income
- Rental Income
- Social Security and Pension Income
- Investment Income
- Support Income (Child Support, Alimony)
- Disability Income
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_income_calculation_rules(connection):
    """Load comprehensive income calculation rules into Neo4j."""
    
    income_rules = [
        # W2 Income Rules
        {
            "rule_id": "INCOME_W2_STANDARD",
            "category": "W2Income", 
            "income_type": "w2_salary",
            "calculation_method": "current_salary_annualized",
            "required_history": 2,
            "stability_requirement": "same_employer_2_years",
            "acceptable_variance": 0.10,
            "trending_analysis": "stable_or_increasing_preferred",
            "documentation_required": ["pay_stubs_current", "w2_forms_2_years", "verification_employment"],
            "description": "Standard W2 salary income calculation"
        },
        {
            "rule_id": "INCOME_W2_HOURLY",
            "category": "W2Income",
            "income_type": "w2_hourly", 
            "calculation_method": "hours_times_rate_annualized",
            "required_history": 2,
            "minimum_hours_weekly": 30,
            "overtime_calculation": "average_2_years_if_consistent",
            "seasonal_adjustment": "required_if_applicable",
            "overtime_threshold": 0.25,
            "documentation_required": ["pay_stubs_ytd", "employment_verification"],
            "description": "W2 hourly income calculation with overtime considerations"
        },
        {
            "rule_id": "INCOME_W2_COMMISSION",
            "category": "W2Income",
            "income_type": "w2_commission",
            "calculation_method": "average_24_months",
            "required_history": 2,
            "declining_trend_threshold": 0.20,
            "base_salary_treatment": "add_to_commission_average",
            "draw_against_commission": "deduct_from_calculation",
            "employer_confirmation": "commission_likely_continue",
            "documentation_required": ["pay_stubs_commission_detail", "tax_returns_2_years"],
            "description": "W2 commission income calculation with trend analysis"
        },
        {
            "rule_id": "INCOME_W2_PART_TIME",
            "category": "W2Income",
            "income_type": "w2_part_time",
            "calculation_method": "current_rate_times_hours",
            "required_history": 2,
            "minimum_hours_weekly": 20,
            "stability_requirement": "consistent_schedule_2_years",
            "multiple_jobs_treatment": "separate_calculation_each",
            "documentation_required": ["pay_stubs_all_jobs", "employment_verification_each"],
            "description": "Part-time W2 income calculation"
        },
        
        # Self-Employed Income Rules
        {
            "rule_id": "INCOME_SELF_EMPLOYED_STANDARD",
            "category": "SelfEmployedIncome",
            "income_type": "self_employed",
            "calculation_method": "net_income_plus_depreciation_average",
            "required_history": 2,
            "depreciation_addback": "real_estate_equipment_only",
            "business_expense_analysis": "required",
            "trending_requirement": "stable_or_increasing",
            "minimum_business_history": 2,
            "documentation_required": ["tax_returns_2_years", "profit_loss_ytd", "business_license"],
            "description": "Standard self-employed income calculation"
        },
        {
            "rule_id": "INCOME_SELF_EMPLOYED_PARTNERSHIP",
            "category": "SelfEmployedIncome", 
            "income_type": "partnership_k1",
            "calculation_method": "k1_income_plus_depreciation",
            "required_history": 2,
            "ownership_percentage": "required_documentation",
            "guaranteed_payments": "include_in_calculation",
            "depreciation_treatment": "add_back_applicable_portion",
            "cash_flow_analysis": "required",
            "documentation_required": ["k1_forms_2_years", "partnership_agreement", "tax_returns"],
            "description": "Partnership K-1 income calculation"
        },
        {
            "rule_id": "INCOME_SELF_EMPLOYED_CORP",
            "category": "SelfEmployedIncome",
            "income_type": "s_corporation",
            "calculation_method": "w2_wages_plus_k1_distributions",
            "required_history": 2,
            "reasonable_salary_analysis": "required",
            "distribution_consistency": "stable_preferred",
            "ownership_percentage": "required_25_percent_minimum",
            "documentation_required": ["corporate_tax_returns", "k1_forms", "personal_tax_returns"],
            "description": "S-Corporation income calculation for business owners"
        },
        
        # Commission and Bonus Income Rules
        {
            "rule_id": "INCOME_BONUS_CONSISTENT",
            "category": "BonusIncome",
            "income_type": "bonus",
            "calculation_method": "average_2_years",
            "required_history": 2,
            "consistency_requirement": "received_both_years",
            "employer_likelihood": "letter_required",
            "declining_trend_treatment": "use_most_recent_year",
            "bonus_types": ["annual_bonus", "performance_bonus", "discretionary_bonus"],
            "documentation_required": ["employment_verification", "bonus_history", "employer_letter"],
            "description": "Consistent bonus income calculation"
        },
        {
            "rule_id": "INCOME_OVERTIME_STANDARD",
            "category": "OvertimeIncome",
            "income_type": "overtime",
            "calculation_method": "average_2_years",
            "required_history": 2,
            "minimum_consistency": "50_percent_of_period",
            "employer_confirmation": "likely_to_continue",
            "seasonal_consideration": "adjust_if_applicable",
            "mandatory_vs_voluntary": "voluntary_requires_higher_consistency",
            "documentation_required": ["pay_stubs_overtime_detail", "employment_verification"],
            "description": "Overtime income calculation and verification"
        },
        
        # Rental Income Rules  
        {
            "rule_id": "INCOME_RENTAL_EXISTING",
            "category": "RentalIncome",
            "income_type": "rental_existing",
            "calculation_method": "lease_agreement_amount",
            "required_history": 2,
            "vacancy_factor": 0.75,
            "expense_consideration": "taxes_insurance_maintenance",
            "management_fee_deduction": "if_applicable",
            "rental_history_required": "2_years_landlord_experience",
            "documentation_required": ["lease_agreements", "tax_returns_schedule_e", "rental_history"],
            "description": "Existing rental property income calculation"
        },
        {
            "rule_id": "INCOME_RENTAL_SUBJECT_PROPERTY",
            "category": "RentalIncome",
            "income_type": "rental_subject_property",
            "calculation_method": "market_rent_analysis",
            "required_documentation": "lease_agreement_or_appraisal",
            "vacancy_factor": 0.75,
            "expense_factor": 0.25,
            "minimum_landlord_experience": "not_required_if_property_manager",
            "market_rent_verification": "appraisal_or_rental_survey",
            "documentation_required": ["market_rent_analysis", "lease_agreement_executed"],
            "description": "Subject property rental income calculation"
        },
        {
            "rule_id": "INCOME_RENTAL_MULTIPLE_PROPERTIES",
            "category": "RentalIncome",
            "income_type": "rental_portfolio",
            "calculation_method": "net_rental_income_average",
            "required_history": 2,
            "portfolio_analysis": "property_by_property",
            "vacancy_factor": 0.75,
            "expense_factor": 0.25,
            "management_experience": "required_for_multiple_properties",
            "documentation_required": ["schedule_e_complete", "property_management_agreement", "lease_agreements_all"],
            "description": "Multiple rental property income calculation"
        },
        
        # Social Security and Pension Rules
        {
            "rule_id": "INCOME_SOCIAL_SECURITY",
            "category": "GovernmentIncome",
            "income_type": "social_security",
            "calculation_method": "award_letter_monthly_times_12",
            "required_documentation": "award_letter_current_year",
            "stability_assumption": "stable_unless_stated_otherwise",
            "cola_adjustments": "include_if_documented",
            "minimum_continuance": "3_years_or_indefinite",
            "tax_treatment": "consider_if_taxable",
            "documentation_required": ["social_security_award_letter", "benefit_verification"],
            "description": "Social Security income calculation"
        },
        {
            "rule_id": "INCOME_PENSION_STANDARD",
            "category": "RetirementIncome",
            "income_type": "pension",
            "calculation_method": "award_letter_or_statement",
            "required_documentation": "pension_administrator_letter",
            "continuance_period": "remaining_life_minimum_3_years",
            "cola_adjustments": "include_if_applicable",
            "survivor_benefits": "consider_if_applicable",
            "documentation_required": ["pension_award_letter", "administrator_verification"],
            "description": "Pension income calculation and verification"
        },
        {
            "rule_id": "INCOME_MILITARY_RETIREMENT",
            "category": "MilitaryIncome",
            "income_type": "military_retirement",
            "calculation_method": "military_pay_statement",
            "required_documentation": "retirement_orders_pay_statement",
            "stability_assumption": "stable_for_life",
            "cola_adjustments": "automatic_adjustments_included",
            "disability_portion": "separate_calculation_if_applicable",
            "documentation_required": ["retirement_orders", "military_pay_statement"],
            "description": "Military retirement income calculation"
        },
        
        # Investment Income Rules
        {
            "rule_id": "INCOME_DIVIDEND_INTEREST",
            "category": "InvestmentIncome",
            "income_type": "dividend_interest",
            "calculation_method": "average_2_years_tax_returns",
            "required_history": 2,
            "asset_depletion_consideration": "if_no_continuing_dividend",
            "trending_analysis": "stable_or_increasing_preferred", 
            "source_documentation": "1099_forms_brokerage_statements",
            "documentation_required": ["tax_returns_schedule_b", "1099_forms", "investment_statements"],
            "description": "Dividend and interest income calculation"
        },
        {
            "rule_id": "INCOME_CAPITAL_GAINS",
            "category": "InvestmentIncome",
            "income_type": "capital_gains",
            "calculation_method": "recurring_gains_only",
            "required_history": 2,
            "recurring_requirement": "consistent_pattern_required",
            "one_time_exclusion": "exclude_non_recurring_gains",
            "asset_depletion_alternative": "if_gains_not_recurring",
            "documentation_required": ["tax_returns_schedule_d", "investment_history"],
            "description": "Capital gains income calculation (recurring only)"
        },
        
        # Support Income Rules
        {
            "rule_id": "INCOME_CHILD_SUPPORT",
            "category": "SupportIncome",
            "income_type": "child_support",
            "calculation_method": "court_order_or_agreement",
            "required_documentation": "divorce_decree_separation_agreement",
            "minimum_continuance": "3_years_minimum",
            "payment_history": "12_months_consistent_receipt",
            "enforcement_consideration": "automatic_deduction_preferred",
            "documentation_required": ["divorce_decree", "payment_history_12_months", "child_support_order"],
            "description": "Child support income calculation"
        },
        {
            "rule_id": "INCOME_ALIMONY",
            "category": "SupportIncome", 
            "income_type": "alimony",
            "calculation_method": "court_order_amount",
            "required_documentation": "divorce_decree",
            "minimum_continuance": "3_years_minimum",
            "tax_treatment": "consider_tax_implications",
            "modification_risk": "assess_likelihood",
            "documentation_required": ["divorce_decree", "payment_history", "tax_treatment_documentation"],
            "description": "Alimony income calculation and verification"
        },
        
        # Disability Income Rules
        {
            "rule_id": "INCOME_DISABILITY_LONG_TERM",
            "category": "DisabilityIncome",
            "income_type": "disability_long_term",
            "calculation_method": "award_letter_amount",
            "required_documentation": "award_letter_benefits_statement",
            "minimum_continuance": "3_years_minimum",
            "likelihood_continuance": "probable",
            "medical_review_impact": "consider_review_schedule",
            "documentation_required": ["disability_award_letter", "medical_review_schedule"],
            "description": "Long-term disability income calculation"
        },
        {
            "rule_id": "INCOME_DISABILITY_VA",
            "category": "DisabilityIncome",
            "income_type": "va_disability",
            "calculation_method": "va_rating_award_amount",
            "required_documentation": "va_disability_award_letter",
            "stability_assumption": "stable_unless_rating_change",
            "tax_treatment": "non_taxable",
            "permanent_vs_temporary": "distinguish_for_continuance",
            "documentation_required": ["va_disability_award", "rating_decision"],
            "description": "VA disability income calculation"
        },
        
        # Other Income Rules
        {
            "rule_id": "INCOME_UNEMPLOYMENT",
            "category": "UnemploymentIncome", 
            "income_type": "unemployment_benefits",
            "calculation_method": "current_benefit_amount",
            "required_documentation": "unemployment_benefits_statement",
            "maximum_usage": "temporary_income_only",
            "continuation_likelihood": "assess_benefit_period_remaining",
            "employment_prospects": "required_analysis",
            "documentation_required": ["unemployment_award_letter", "job_search_documentation"],
            "description": "Unemployment benefits (temporary income consideration)"
        },
        {
            "rule_id": "INCOME_TRUST_DISTRIBUTION",
            "category": "TrustIncome",
            "income_type": "trust_distributions",
            "calculation_method": "trust_document_distribution_amount",
            "required_documentation": "trust_agreement_distribution_history",
            "distribution_frequency": "monthly_quarterly_annual",
            "trustee_confirmation": "required",
            "continuation_assurance": "trust_terms_guarantee_required",
            "documentation_required": ["trust_agreement", "distribution_history", "trustee_letter"],
            "description": "Trust distribution income calculation"
        }
    ]
    
    for rule in income_rules:
        # Ensure all parameters are explicitly set
        rule_params = {
            "rule_id": rule.get("rule_id"),
            "category": rule.get("category"),
            "income_type": rule.get("income_type"),
            "calculation_method": rule.get("calculation_method"),
            "required_history": rule.get("required_history"),
            "stability_requirement": rule.get("stability_requirement"),
            "acceptable_variance": rule.get("acceptable_variance"),
            "trending_analysis": rule.get("trending_analysis"),
            "documentation_required": rule.get("documentation_required"),
            "minimum_hours_weekly": rule.get("minimum_hours_weekly"),
            "overtime_calculation": rule.get("overtime_calculation"),
            "seasonal_adjustment": rule.get("seasonal_adjustment"),
            "overtime_threshold": rule.get("overtime_threshold"),
            "declining_trend_threshold": rule.get("declining_trend_threshold"),
            "base_salary_treatment": rule.get("base_salary_treatment"),
            "draw_against_commission": rule.get("draw_against_commission"),
            "employer_confirmation": rule.get("employer_confirmation"),
            "multiple_jobs_treatment": rule.get("multiple_jobs_treatment"),
            "depreciation_addback": rule.get("depreciation_addback"),
            "business_expense_analysis": rule.get("business_expense_analysis"),
            "trending_requirement": rule.get("trending_requirement"),
            "minimum_business_history": rule.get("minimum_business_history"),
            "ownership_percentage": rule.get("ownership_percentage"),
            "guaranteed_payments": rule.get("guaranteed_payments"),
            "depreciation_treatment": rule.get("depreciation_treatment"),
            "cash_flow_analysis": rule.get("cash_flow_analysis"),
            "reasonable_salary_analysis": rule.get("reasonable_salary_analysis"),
            "distribution_consistency": rule.get("distribution_consistency"),
            "consistency_requirement": rule.get("consistency_requirement"),
            "employer_likelihood": rule.get("employer_likelihood"),
            "declining_trend_treatment": rule.get("declining_trend_treatment"),
            "bonus_types": rule.get("bonus_types"),
            "minimum_consistency": rule.get("minimum_consistency"),
            "seasonal_consideration": rule.get("seasonal_consideration"),
            "mandatory_vs_voluntary": rule.get("mandatory_vs_voluntary"),
            "vacancy_factor": rule.get("vacancy_factor"),
            "expense_consideration": rule.get("expense_consideration"),
            "management_fee_deduction": rule.get("management_fee_deduction"),
            "rental_history_required": rule.get("rental_history_required"),
            "required_documentation": rule.get("required_documentation"),
            "expense_factor": rule.get("expense_factor"),
            "minimum_landlord_experience": rule.get("minimum_landlord_experience"),
            "market_rent_verification": rule.get("market_rent_verification"),
            "portfolio_analysis": rule.get("portfolio_analysis"),
            "management_experience": rule.get("management_experience"),
            "stability_assumption": rule.get("stability_assumption"),
            "cola_adjustments": rule.get("cola_adjustments"),
            "minimum_continuance": rule.get("minimum_continuance"),
            "tax_treatment": rule.get("tax_treatment"),
            "continuance_period": rule.get("continuance_period"),
            "survivor_benefits": rule.get("survivor_benefits"),
            "disability_portion": rule.get("disability_portion"),
            "asset_depletion_consideration": rule.get("asset_depletion_consideration"),
            "source_documentation": rule.get("source_documentation"),
            "recurring_requirement": rule.get("recurring_requirement"),
            "one_time_exclusion": rule.get("one_time_exclusion"),
            "asset_depletion_alternative": rule.get("asset_depletion_alternative"),
            "payment_history": rule.get("payment_history"),
            "enforcement_consideration": rule.get("enforcement_consideration"),
            "modification_risk": rule.get("modification_risk"),
            "likelihood_continuance": rule.get("likelihood_continuance"),
            "medical_review_impact": rule.get("medical_review_impact"),
            "permanent_vs_temporary": rule.get("permanent_vs_temporary"),
            "maximum_usage": rule.get("maximum_usage"),
            "continuation_likelihood": rule.get("continuation_likelihood"),
            "employment_prospects": rule.get("employment_prospects"),
            "distribution_frequency": rule.get("distribution_frequency"),
            "trustee_confirmation": rule.get("trustee_confirmation"),
            "continuation_assurance": rule.get("continuation_assurance"),
            "description": rule.get("description")
        }
        
        query = """
        CREATE (icr:IncomeCalculationRule {
            rule_id: $rule_id,
            category: $category,
            income_type: $income_type,
            calculation_method: $calculation_method,
            required_history: $required_history,
            stability_requirement: $stability_requirement,
            acceptable_variance: $acceptable_variance,
            trending_analysis: $trending_analysis,
            documentation_required: $documentation_required,
            minimum_hours_weekly: $minimum_hours_weekly,
            overtime_calculation: $overtime_calculation,
            seasonal_adjustment: $seasonal_adjustment,
            overtime_threshold: $overtime_threshold,
            declining_trend_threshold: $declining_trend_threshold,
            base_salary_treatment: $base_salary_treatment,
            draw_against_commission: $draw_against_commission,
            employer_confirmation: $employer_confirmation,
            multiple_jobs_treatment: $multiple_jobs_treatment,
            depreciation_addback: $depreciation_addback,
            business_expense_analysis: $business_expense_analysis,
            trending_requirement: $trending_requirement,
            minimum_business_history: $minimum_business_history,
            ownership_percentage: $ownership_percentage,
            guaranteed_payments: $guaranteed_payments,
            depreciation_treatment: $depreciation_treatment,
            cash_flow_analysis: $cash_flow_analysis,
            reasonable_salary_analysis: $reasonable_salary_analysis,
            distribution_consistency: $distribution_consistency,
            consistency_requirement: $consistency_requirement,
            employer_likelihood: $employer_likelihood,
            declining_trend_treatment: $declining_trend_treatment,
            bonus_types: $bonus_types,
            minimum_consistency: $minimum_consistency,
            seasonal_consideration: $seasonal_consideration,
            mandatory_vs_voluntary: $mandatory_vs_voluntary,
            vacancy_factor: $vacancy_factor,
            expense_consideration: $expense_consideration,
            management_fee_deduction: $management_fee_deduction,
            rental_history_required: $rental_history_required,
            required_documentation: $required_documentation,
            expense_factor: $expense_factor,
            minimum_landlord_experience: $minimum_landlord_experience,
            market_rent_verification: $market_rent_verification,
            portfolio_analysis: $portfolio_analysis,
            management_experience: $management_experience,
            stability_assumption: $stability_assumption,
            cola_adjustments: $cola_adjustments,
            minimum_continuance: $minimum_continuance,
            tax_treatment: $tax_treatment,
            continuance_period: $continuance_period,
            survivor_benefits: $survivor_benefits,
            disability_portion: $disability_portion,
            asset_depletion_consideration: $asset_depletion_consideration,
            source_documentation: $source_documentation,
            recurring_requirement: $recurring_requirement,
            one_time_exclusion: $one_time_exclusion,
            asset_depletion_alternative: $asset_depletion_alternative,
            payment_history: $payment_history,
            enforcement_consideration: $enforcement_consideration,
            modification_risk: $modification_risk,
            likelihood_continuance: $likelihood_continuance,
            medical_review_impact: $medical_review_impact,
            permanent_vs_temporary: $permanent_vs_temporary,
            maximum_usage: $maximum_usage,
            continuation_likelihood: $continuation_likelihood,
            employment_prospects: $employment_prospects,
            distribution_frequency: $distribution_frequency,
            trustee_confirmation: $trustee_confirmation,
            continuation_assurance: $continuation_assurance,
            description: $description
        })
        """
        
        connection.execute_query(query, rule_params)
        logger.info(f"Created IncomeCalculationRule: {rule['rule_id']}")
    
    logger.info(f"Loaded {len(income_rules)} income calculation rules successfully")
