"""
Compliance Rules

This module contains comprehensive regulatory compliance rules for mortgage processing.
All rules are stored as Neo4j nodes to maintain the 100% data-driven approach.

Categories:
- QM/ATR Rules (Qualified Mortgage/Ability to Repay)
- TRID Rules (TILA-RESPA Integrated Disclosure)
- Fair Lending Rules
- HMDA Reporting Rules
- State-Specific Requirements
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_compliance_rules(connection):
    """Load comprehensive regulatory compliance rules into Neo4j."""
    
    compliance_rules = [
        # QM/ATR Rules
        {
            "rule_id": "QM_ATR_BASIC_REQUIREMENTS",
            "category": "QM_ATR",
            "rule_type": "basic_requirements",
            "dti_limit": 0.43,
            "income_verification": "required",
            "asset_verification": "required", 
            "employment_verification": "required",
            "monthly_payment_calculation": "highest_payment_first_5_years",
            "points_and_fees_limit": 0.03,
            "safe_harbor_threshold": 0.43,
            "description": "Basic QM/ATR requirements for ability to repay"
        },
        {
            "rule_id": "QM_POINTS_AND_FEES",
            "category": "QM_ATR",
            "rule_type": "points_and_fees",
            "loan_amount_thresholds": '{"over_100k": 0.03, "50k_to_100k": 3000, "20k_to_50k": 0.05, "12.5k_to_20k": 1000, "under_12.5k": 0.08}',
            "included_fees": ["origination_fees", "broker_fees", "discount_points", "prepayment_penalties"],
            "excluded_fees": ["title_insurance", "appraisal", "credit_report", "flood_determination"],
            "calculation_method": "finance_charge_based",
            "description": "QM points and fees calculation and limits"
        },
        {
            "rule_id": "QM_GENERAL_PROHIBITIONS",
            "category": "QM_ATR",
            "rule_type": "prohibited_features",
            "interest_only_payments": False,
            "negative_amortization": False,
            "balloon_payments": False,
            "loan_term_maximum": 360,
            "excessive_upfront_points_fees": "see_points_fees_limits",
            "prepayment_penalties": "limited_circumstances_only",
            "description": "QM prohibited loan features and characteristics"
        },
        
        # TRID Rules
        {
            "rule_id": "TRID_LOAN_ESTIMATE_TIMING",
            "category": "TRID",
            "rule_type": "loan_estimate",
            "delivery_requirement": "3_business_days_after_application",
            "application_definition": "6_pieces_of_information",
            "required_information": ["name", "income", "ssn", "property_address", "loan_amount", "property_value"],
            "delivery_methods": ["hand_delivery", "mail", "email_if_consented"],
            "validity_period": "10_business_days",
            "revision_circumstances": ["changed_circumstances", "borrower_requested_changes"],
            "description": "TRID Loan Estimate timing and delivery requirements"
        },
        {
            "rule_id": "TRID_CLOSING_DISCLOSURE_TIMING",
            "category": "TRID",
            "rule_type": "closing_disclosure",
            "delivery_requirement": "3_business_days_before_consummation",
            "delivery_methods": ["hand_delivery", "mail", "email_if_consented"],
            "right_to_cancel": "federal_holidays_not_business_days",
            "changes_requiring_new_waiting": ["apr_increase_0.125", "loan_product_change", "prepayment_penalty_added"],
            "tolerance_violations": "cure_and_correct_required",
            "record_retention": "5_years_after_consummation",
            "description": "TRID Closing Disclosure timing and delivery requirements"
        },
        {
            "rule_id": "TRID_TOLERANCE_CATEGORIES",
            "category": "TRID",
            "rule_type": "fee_tolerances",
            "zero_tolerance": ["lender_fees", "broker_fees", "transfer_taxes", "prepaid_interest"],
            "ten_percent_tolerance": ["recording_fees", "title_services_borrower_selected", "required_services_borrower_selected"],
            "good_faith_tolerance": ["title_services_lender_selected", "required_services_lender_selected", "homeowners_insurance"],
            "changed_circumstances": ["acts_of_god", "war", "disaster", "other_extraordinary_events"],
            "cure_period": "30_days_after_consummation",
            "description": "TRID fee tolerance categories and cure requirements"
        },
        
        # Fair Lending Rules
        {
            "rule_id": "FAIR_LENDING_ECOA",
            "category": "FairLending",
            "rule_type": "ecoa_compliance",
            "prohibited_bases": ["race", "color", "religion", "national_origin", "sex", "marital_status", "age", "receipt_of_public_assistance"],
            "adverse_action_notice": "30_days_after_decision",
            "credit_scoring_requirements": "empirically_derived_demonstrably_sound",
            "spousal_signature": "limited_circumstances_only",
            "income_evaluation": "part_time_temporary_alimony_consideration",
            "record_retention": "25_months_after_notice",
            "description": "Equal Credit Opportunity Act compliance requirements"
        },
        {
            "rule_id": "FAIR_LENDING_FHA",
            "category": "FairLending",
            "rule_type": "fair_housing_act",
            "protected_classes": ["race", "color", "religion", "sex", "handicap", "familial_status", "national_origin"],
            "advertising_compliance": "no_discriminatory_language",
            "appraisal_bias": "property_valuation_non_discriminatory",
            "marketing_practices": "equal_opportunity_advertising",
            "complaints_procedure": "established_complaint_process",
            "training_requirements": "fair_lending_training_all_staff",
            "description": "Fair Housing Act compliance requirements"
        },
        {
            "rule_id": "FAIR_LENDING_PRICING",
            "category": "FairLending",
            "rule_type": "pricing_practices",
            "discretionary_pricing": "controls_and_monitoring_required",
            "rate_lock_policies": "consistently_applied",
            "exception_pricing": "documented_business_justification",
            "compensation_plans": "incentive_structure_review",
            "disparate_impact": "statistical_monitoring_required",
            "corrective_actions": "identified_disparities_addressed",
            "description": "Fair lending pricing practices and monitoring"
        },
        
        # HMDA Reporting Rules
        {
            "rule_id": "HMDA_REPORTING_REQUIREMENTS",
            "category": "HMDA",
            "rule_type": "reporting_requirements",
            "covered_loans": ["home_purchase", "refinance", "home_improvement", "other_residential"],
            "loan_threshold": "no_threshold_all_covered_loans",
            "data_points": 48,
            "submission_deadline": "march_1_following_calendar_year",
            "public_disclosure": "loan_level_data_published",
            "record_retention": "3_years_minimum",
            "description": "HMDA data collection and reporting requirements"
        },
        {
            "rule_id": "HMDA_DATA_ACCURACY",
            "category": "HMDA",
            "rule_type": "data_accuracy",
            "edit_checks": "automated_validation_required",
            "verification_procedures": "quality_control_processes",
            "correction_deadlines": "prior_to_submission_deadline",
            "resubmission_procedures": "corrected_data_resubmission",
            "staff_training": "hmda_data_collection_training",
            "system_controls": "data_integrity_controls",
            "description": "HMDA data accuracy and quality control requirements"
        },
        
        # State-Specific Requirements
        {
            "rule_id": "STATE_LICENSING_REQUIREMENTS",
            "category": "StateLicensing",
            "rule_type": "originator_licensing",
            "nmls_requirement": "state_licensed_or_registered",
            "continuing_education": "annual_ce_requirements",
            "background_checks": "criminal_background_investigation",
            "surety_bond": "state_specific_bond_requirements",
            "testing_requirements": "state_and_national_testing",
            "license_maintenance": "annual_renewal_required",
            "description": "State mortgage originator licensing requirements"
        },
        {
            "rule_id": "STATE_DISCLOSURE_REQUIREMENTS",
            "category": "StateDisclosures",
            "rule_type": "additional_disclosures",
            "right_to_cancel": "state_specific_cancellation_rights",
            "property_tax_disclosure": "tax_assessment_disclosure",
            "flood_zone_disclosure": "flood_hazard_notification",
            "lead_paint_disclosure": "pre_1978_properties",
            "homestead_exemption": "state_homestead_notifications",
            "transfer_tax_disclosure": "state_local_transfer_taxes",
            "description": "State-specific disclosure requirements"
        },
        {
            "rule_id": "STATE_USURY_LIMITS",
            "category": "StateUsury",
            "rule_type": "interest_rate_limits",
            "rate_limits_applicable": "state_specific_limits",
            "calculation_method": "annual_percentage_rate_basis",
            "exemptions": "first_lien_mortgages_federal_preemption",
            "penalty_provisions": "state_penalty_structures",
            "monitoring_requirements": "rate_limit_compliance_monitoring",
            "documentation": "compliance_documentation_required",
            "description": "State usury law compliance requirements"
        }
    ]
    
    for rule in compliance_rules:
        # Ensure all parameters are explicitly set
        rule_params = {key: rule.get(key) for key in [
            "rule_id", "category", "rule_type", "dti_limit", "income_verification", "asset_verification",
            "employment_verification", "monthly_payment_calculation", "points_and_fees_limit",
            "safe_harbor_threshold", "loan_amount_thresholds", "included_fees", "excluded_fees",
            "calculation_method", "interest_only_payments", "negative_amortization", "balloon_payments",
            "loan_term_maximum", "excessive_upfront_points_fees", "prepayment_penalties",
            "delivery_requirement", "application_definition", "required_information", "delivery_methods",
            "validity_period", "revision_circumstances", "right_to_cancel", "changes_requiring_new_waiting",
            "tolerance_violations", "record_retention", "zero_tolerance", "ten_percent_tolerance",
            "good_faith_tolerance", "changed_circumstances", "cure_period", "prohibited_bases",
            "adverse_action_notice", "credit_scoring_requirements", "spousal_signature", "income_evaluation",
            "protected_classes", "advertising_compliance", "appraisal_bias", "marketing_practices",
            "complaints_procedure", "training_requirements", "discretionary_pricing", "rate_lock_policies",
            "exception_pricing", "compensation_plans", "disparate_impact", "corrective_actions",
            "covered_loans", "loan_threshold", "data_points", "submission_deadline", "public_disclosure",
            "edit_checks", "verification_procedures", "correction_deadlines", "resubmission_procedures",
            "staff_training", "system_controls", "nmls_requirement", "continuing_education",
            "background_checks", "surety_bond", "testing_requirements", "license_maintenance",
            "property_tax_disclosure", "flood_zone_disclosure", "lead_paint_disclosure",
            "homestead_exemption", "transfer_tax_disclosure", "rate_limits_applicable", "exemptions",
            "penalty_provisions", "monitoring_requirements", "documentation", "description"
        ]}
        query = """
        CREATE (cr:ComplianceRule {
            rule_id: $rule_id,
            category: $category,
            rule_type: $rule_type,
            dti_limit: $dti_limit,
            income_verification: $income_verification,
            asset_verification: $asset_verification,
            employment_verification: $employment_verification,
            monthly_payment_calculation: $monthly_payment_calculation,
            points_and_fees_limit: $points_and_fees_limit,
            safe_harbor_threshold: $safe_harbor_threshold,
            loan_amount_thresholds: $loan_amount_thresholds,
            included_fees: $included_fees,
            excluded_fees: $excluded_fees,
            calculation_method: $calculation_method,
            interest_only_payments: $interest_only_payments,
            negative_amortization: $negative_amortization,
            balloon_payments: $balloon_payments,
            loan_term_maximum: $loan_term_maximum,
            excessive_upfront_points_fees: $excessive_upfront_points_fees,
            prepayment_penalties: $prepayment_penalties,
            delivery_requirement: $delivery_requirement,
            application_definition: $application_definition,
            required_information: $required_information,
            delivery_methods: $delivery_methods,
            validity_period: $validity_period,
            revision_circumstances: $revision_circumstances,
            right_to_cancel: $right_to_cancel,
            changes_requiring_new_waiting: $changes_requiring_new_waiting,
            tolerance_violations: $tolerance_violations,
            record_retention: $record_retention,
            zero_tolerance: $zero_tolerance,
            ten_percent_tolerance: $ten_percent_tolerance,
            good_faith_tolerance: $good_faith_tolerance,
            changed_circumstances: $changed_circumstances,
            cure_period: $cure_period,
            prohibited_bases: $prohibited_bases,
            adverse_action_notice: $adverse_action_notice,
            credit_scoring_requirements: $credit_scoring_requirements,
            spousal_signature: $spousal_signature,
            income_evaluation: $income_evaluation,
            protected_classes: $protected_classes,
            advertising_compliance: $advertising_compliance,
            appraisal_bias: $appraisal_bias,
            marketing_practices: $marketing_practices,
            complaints_procedure: $complaints_procedure,
            training_requirements: $training_requirements,
            discretionary_pricing: $discretionary_pricing,
            rate_lock_policies: $rate_lock_policies,
            exception_pricing: $exception_pricing,
            compensation_plans: $compensation_plans,
            disparate_impact: $disparate_impact,
            corrective_actions: $corrective_actions,
            covered_loans: $covered_loans,
            loan_threshold: $loan_threshold,
            data_points: $data_points,
            submission_deadline: $submission_deadline,
            public_disclosure: $public_disclosure,
            edit_checks: $edit_checks,
            verification_procedures: $verification_procedures,
            correction_deadlines: $correction_deadlines,
            resubmission_procedures: $resubmission_procedures,
            staff_training: $staff_training,
            system_controls: $system_controls,
            nmls_requirement: $nmls_requirement,
            continuing_education: $continuing_education,
            background_checks: $background_checks,
            surety_bond: $surety_bond,
            testing_requirements: $testing_requirements,
            license_maintenance: $license_maintenance,
            property_tax_disclosure: $property_tax_disclosure,
            flood_zone_disclosure: $flood_zone_disclosure,
            lead_paint_disclosure: $lead_paint_disclosure,
            homestead_exemption: $homestead_exemption,
            transfer_tax_disclosure: $transfer_tax_disclosure,
            rate_limits_applicable: $rate_limits_applicable,
            exemptions: $exemptions,
            penalty_provisions: $penalty_provisions,
            monitoring_requirements: $monitoring_requirements,
            documentation: $documentation,
            description: $description
        })
        """
        
        connection.execute_query(query, rule_params)
        logger.info(f"Created ComplianceRule: {rule['rule_id']}")
    
    logger.info(f"Loaded {len(compliance_rules)} compliance rules successfully")
