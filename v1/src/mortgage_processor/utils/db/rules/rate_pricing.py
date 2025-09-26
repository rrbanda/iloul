"""
Rate Pricing Rules

This module contains comprehensive rate pricing rules for mortgage processing.
All rules are stored as Neo4j nodes to maintain the 100% data-driven approach.

Categories:
- Base Rate Rules
- Credit Score Adjustments
- LTV Adjustments
- Loan Program Adjustments
- Property Type Adjustments
- Cash-Out Adjustments
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_rate_pricing_rules(connection):
    """Load comprehensive rate pricing rules into Neo4j."""
    
    pricing_rules = [
        # Base Rate Rules
        {
            "rule_id": "BASE_RATE_30_YEAR_FIXED",
            "category": "BaseRates",
            "loan_term": 360,
            "loan_type": "fixed_rate",
            "base_rate": 7.125,
            "rate_lock_periods": '{"15_day": 0.0, "30_day": 0.125, "45_day": 0.25, "60_day": 0.375}',
            "market_conditions": "current_market_base",
            "investor_type": "agency_conforming",
            "effective_date": "2024_rates",
            "description": "30-year fixed rate base pricing"
        },
        {
            "rule_id": "BASE_RATE_15_YEAR_FIXED",
            "category": "BaseRates",
            "loan_term": 180,
            "loan_type": "fixed_rate", 
            "base_rate": 6.625,
            "rate_lock_periods": '{"15_day": 0.0, "30_day": 0.125, "45_day": 0.25, "60_day": 0.375}',
            "market_conditions": "current_market_base",
            "investor_type": "agency_conforming",
            "discount_to_30_year": 0.50,
            "description": "15-year fixed rate base pricing"
        },
        {
            "rule_id": "BASE_RATE_JUMBO",
            "category": "BaseRates",
            "loan_term": 360,
            "loan_type": "jumbo_fixed_rate",
            "base_rate": 7.250,
            "rate_lock_periods": '{"15_day": 0.0, "30_day": 0.125, "45_day": 0.25, "60_day": 0.375}',
            "market_conditions": "jumbo_market_premium",
            "investor_type": "portfolio_jumbo",
            "premium_to_conforming": 0.125,
            "description": "Jumbo loan base pricing"
        },
        
        # Credit Score Adjustments
        {
            "rule_id": "CREDIT_SCORE_ADJUSTMENTS",
            "category": "CreditAdjustments",
            "adjustment_type": "credit_score_based",
            "score_ranges": '{"760_plus": 0.0, "740_759": 0.125, "720_739": 0.25, "700_719": 0.375, "680_699": 0.50, "660_679": 0.75, "640_659": 1.0, "620_639": 1.25, "600_619": 1.50, "580_599": 1.75}',
            "loan_programs": ["conventional", "jumbo"],
            "ltv_interaction": "see_ltv_credit_matrix",
            "description": "Credit score-based rate adjustments"
        },
        {
            "rule_id": "CREDIT_LTV_MATRIX",
            "category": "CreditAdjustments",
            "adjustment_type": "credit_ltv_matrix",
            "high_ltv_high_credit_penalty": "additional_0.25_if_ltv_over_90_credit_under_740",
            "low_ltv_low_credit_benefit": "reduced_penalty_if_ltv_under_80",
            "matrix_applicable": "conventional_loans_only",
            "fha_va_exempt": "government_loans_use_standard_adjustments",
            "description": "Combined credit score and LTV adjustments"
        },
        
        # LTV Adjustments
        {
            "rule_id": "LTV_ADJUSTMENTS_CONVENTIONAL",
            "category": "LTVAdjustments",
            "loan_program": "conventional",
            "adjustment_type": "ltv_based",
            "ltv_ranges": '{"0_to_60": 0.0, "60.01_to_70": 0.0, "70.01_to_75": 0.125, "75.01_to_80": 0.25, "80.01_to_85": 0.375, "85.01_to_90": 0.50, "90.01_to_95": 0.75, "95.01_to_97": 1.0}',
            "maximum_ltv": 0.97,
            "pmi_required": "ltv_over_80_percent",
            "description": "Conventional loan LTV-based rate adjustments"
        },
        {
            "rule_id": "LTV_ADJUSTMENTS_JUMBO",
            "category": "LTVAdjustments",
            "loan_program": "jumbo",
            "adjustment_type": "ltv_based",
            "ltv_ranges": '{"0_to_60": 0.0, "60.01_to_70": 0.125, "70.01_to_75": 0.25, "75.01_to_80": 0.375, "80.01_to_85": 0.75, "85.01_to_90": 1.25}',
            "maximum_ltv": 0.90,
            "higher_adjustments": "jumbo_loans_higher_ltv_penalties",
            "description": "Jumbo loan LTV-based rate adjustments"
        },
        
        # Loan Program Adjustments
        {
            "rule_id": "PROGRAM_ADJUSTMENTS_FHA",
            "category": "ProgramAdjustments",
            "loan_program": "fha",
            "base_adjustment": 0.25,
            "credit_score_tiers": '{"580_plus": 0.25, "500_579": 0.50}',
            "mip_requirement": "upfront_and_annual_mip",
            "ltv_maximum": 0.965,
            "special_pricing": "streamline_refinance_discount_0.125",
            "description": "FHA loan program pricing adjustments"
        },
        {
            "rule_id": "PROGRAM_ADJUSTMENTS_VA",
            "category": "ProgramAdjustments",
            "loan_program": "va",
            "base_adjustment": -0.125,
            "credit_score_minimum": 580,
            "funding_fee": "percentage_of_loan_amount",
            "ltv_maximum": 1.0,
            "no_pmi_benefit": "no_mortgage_insurance_required",
            "irrrl_pricing": "interest_rate_reduction_loan_discount_0.25",
            "description": "VA loan program pricing adjustments"
        },
        {
            "rule_id": "PROGRAM_ADJUSTMENTS_USDA",
            "category": "ProgramAdjustments",
            "loan_program": "usda",
            "base_adjustment": 0.125,
            "credit_score_tiers": '{"640_plus": 0.125, "580_639": 0.375}',
            "guarantee_fee": "upfront_and_annual_fees",
            "ltv_maximum": 1.0,
            "geographic_restriction": "eligible_rural_areas_only",
            "description": "USDA loan program pricing adjustments"
        },
        
        # Property Type Adjustments
        {
            "rule_id": "PROPERTY_TYPE_ADJUSTMENTS",
            "category": "PropertyTypeAdjustments",
            "adjustment_type": "property_based",
            "property_types": '{"single_family_detached": 0.0, "single_family_attached": 0.125, "condominium": 0.25, "2_unit": 0.25, "3_unit": 0.375, "4_unit": 0.50, "manufactured_home": 0.75}',
            "warrantability_review": "condominiums_require_project_approval",
            "occupancy_impact": "see_occupancy_adjustments",
            "description": "Property type-based rate adjustments"
        },
        {
            "rule_id": "OCCUPANCY_ADJUSTMENTS",
            "category": "OccupancyAdjustments",
            "adjustment_type": "occupancy_based",
            "occupancy_types": '{"primary_residence": 0.0, "second_home": 0.375, "investment_property": 0.75}',
            "documentation_requirements": "occupancy_certification_required",
            "verification_methods": "utility_bills_voter_registration",
            "fraud_prevention": "occupancy_fraud_monitoring",
            "description": "Occupancy type-based rate adjustments"
        },
        
        # Cash-Out and Transaction Type Adjustments
        {
            "rule_id": "CASH_OUT_ADJUSTMENTS",
            "category": "CashOutAdjustments",
            "transaction_type": "cash_out_refinance",
            "adjustment_amount": 0.375,
            "ltv_limitations": "lower_maximum_ltv_than_rate_term",
            "cash_out_threshold": "increased_loan_amount_2000_plus",
            "documentation_enhanced": "additional_asset_verification",
            "seasoning_requirements": "property_ownership_6_months",
            "description": "Cash-out refinance rate adjustments"
        },
        {
            "rule_id": "TRANSACTION_TYPE_ADJUSTMENTS",
            "category": "TransactionAdjustments",
            "adjustment_type": "transaction_based",
            "transaction_types": '{"purchase": 0.0, "rate_term_refinance": 0.0, "cash_out_refinance": 0.375, "construction_to_perm": 0.50, "renovation_loan": 0.625}',
            "streamline_discounts": "va_fha_streamline_0.125_discount",
            "portfolio_retention": "portfolio_loans_custom_pricing",
            "description": "Transaction type-based rate adjustments"
        },
        
        # Points and Fees Rules
        {
            "rule_id": "DISCOUNT_POINTS_PRICING",
            "category": "PointsPricing",
            "pricing_type": "discount_points",
            "point_value": 0.25,
            "maximum_points": 4.0,
            "point_increments": 0.125,
            "break_even_analysis": "required_disclosure",
            "prepayment_consideration": "points_benefit_long_term_ownership",
            "tax_implications": "points_tax_deductibility",
            "description": "Discount points pricing and value"
        },
        {
            "rule_id": "ORIGINATION_FEES",
            "category": "OriginationFees",
            "fee_type": "origination_points",
            "standard_fee": 1.0,
            "fee_variations": '{"jumbo_loans": 1.25, "government_loans": 1.0, "portfolio_loans": 0.75}',
            "negotiability": "fees_may_be_negotiated",
            "qm_limitations": "points_and_fees_qm_limits_apply",
            "description": "Loan origination fee structure"
        }
    ]
    
    for rule in pricing_rules:
        # Ensure all parameters are explicitly set
        rule_params = {key: rule.get(key) for key in [
            "rule_id", "category", "loan_term", "loan_type", "base_rate", "rate_lock_periods",
            "market_conditions", "investor_type", "effective_date", "discount_to_30_year",
            "premium_to_conforming", "adjustment_type", "score_ranges", "loan_programs",
            "ltv_interaction", "high_ltv_high_credit_penalty", "low_ltv_low_credit_benefit",
            "matrix_applicable", "fha_va_exempt", "loan_program", "ltv_ranges", "maximum_ltv",
            "pmi_required", "higher_adjustments", "base_adjustment", "credit_score_tiers",
            "mip_requirement", "special_pricing", "credit_score_minimum", "funding_fee",
            "no_pmi_benefit", "irrrl_pricing", "guarantee_fee", "geographic_restriction",
            "property_types", "warrantability_review", "occupancy_impact", "occupancy_types",
            "documentation_requirements", "verification_methods", "fraud_prevention",
            "transaction_type", "adjustment_amount", "ltv_limitations", "cash_out_threshold",
            "documentation_enhanced", "seasoning_requirements", "transaction_types",
            "streamline_discounts", "portfolio_retention", "pricing_type", "point_value",
            "maximum_points", "point_increments", "break_even_analysis", "prepayment_consideration",
            "tax_implications", "fee_type", "standard_fee", "fee_variations", "negotiability",
            "qm_limitations", "description"
        ]}
        query = """
        CREATE (rpr:RatePricingRule {
            rule_id: $rule_id,
            category: $category,
            loan_term: $loan_term,
            loan_type: $loan_type,
            base_rate: $base_rate,
            rate_lock_periods: $rate_lock_periods,
            market_conditions: $market_conditions,
            investor_type: $investor_type,
            effective_date: $effective_date,
            discount_to_30_year: $discount_to_30_year,
            premium_to_conforming: $premium_to_conforming,
            adjustment_type: $adjustment_type,
            score_ranges: $score_ranges,
            loan_programs: $loan_programs,
            ltv_interaction: $ltv_interaction,
            high_ltv_high_credit_penalty: $high_ltv_high_credit_penalty,
            low_ltv_low_credit_benefit: $low_ltv_low_credit_benefit,
            matrix_applicable: $matrix_applicable,
            fha_va_exempt: $fha_va_exempt,
            loan_program: $loan_program,
            ltv_ranges: $ltv_ranges,
            maximum_ltv: $maximum_ltv,
            pmi_required: $pmi_required,
            higher_adjustments: $higher_adjustments,
            base_adjustment: $base_adjustment,
            credit_score_tiers: $credit_score_tiers,
            mip_requirement: $mip_requirement,
            special_pricing: $special_pricing,
            credit_score_minimum: $credit_score_minimum,
            funding_fee: $funding_fee,
            no_pmi_benefit: $no_pmi_benefit,
            irrrl_pricing: $irrrl_pricing,
            guarantee_fee: $guarantee_fee,
            geographic_restriction: $geographic_restriction,
            property_types: $property_types,
            warrantability_review: $warrantability_review,
            occupancy_impact: $occupancy_impact,
            occupancy_types: $occupancy_types,
            documentation_requirements: $documentation_requirements,
            verification_methods: $verification_methods,
            fraud_prevention: $fraud_prevention,
            transaction_type: $transaction_type,
            adjustment_amount: $adjustment_amount,
            ltv_limitations: $ltv_limitations,
            cash_out_threshold: $cash_out_threshold,
            documentation_enhanced: $documentation_enhanced,
            seasoning_requirements: $seasoning_requirements,
            transaction_types: $transaction_types,
            streamline_discounts: $streamline_discounts,
            portfolio_retention: $portfolio_retention,
            pricing_type: $pricing_type,
            point_value: $point_value,
            maximum_points: $maximum_points,
            point_increments: $point_increments,
            break_even_analysis: $break_even_analysis,
            prepayment_consideration: $prepayment_consideration,
            tax_implications: $tax_implications,
            fee_type: $fee_type,
            standard_fee: $standard_fee,
            fee_variations: $fee_variations,
            negotiability: $negotiability,
            qm_limitations: $qm_limitations,
            description: $description
        })
        """
        
        connection.execute_query(query, rule_params)
        logger.info(f"Created RatePricingRule: {rule['rule_id']}")
    
    logger.info(f"Loaded {len(pricing_rules)} rate pricing rules successfully")
