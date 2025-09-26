"""
Property Appraisal Rules

This module contains comprehensive property appraisal rules for mortgage processing.
All rules are stored as Neo4j nodes to maintain the 100% data-driven approach.

Categories:
- Property Type Requirements
- Appraisal Standards
- Value Analysis Rules
- Property Condition Requirements
- Market Analysis Rules
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_property_appraisal_rules(connection):
    """Load comprehensive property appraisal rules into Neo4j."""
    
    property_rules = [
        # Property Type Rules
        {
            "rule_id": "PROPERTY_SINGLE_FAMILY",
            "category": "PropertyType",
            "property_type": "single_family_detached",
            "appraisal_approach": "sales_comparison_primary",
            "comparable_requirements": "3_minimum_closed_sales",
            "distance_limit_miles": 1.0,
            "age_limit_months": 12,
            "adjustment_limits": '{"total": 0.25, "individual": 0.10}',
            "special_requirements": [],
            "description": "Single family detached property appraisal requirements"
        },
        {
            "rule_id": "PROPERTY_CONDOMINIUM",
            "category": "PropertyType", 
            "property_type": "condominium",
            "appraisal_approach": "sales_comparison_primary",
            "comparable_requirements": "3_minimum_same_project_preferred",
            "distance_limit_miles": 5.0,
            "age_limit_months": 12,
            "hoa_analysis_required": True,
            "condo_certification": "warrantability_review_required",
            "special_requirements": ["hoa_budget_review", "reserve_analysis"],
            "description": "Condominium property appraisal requirements"
        },
        {
            "rule_id": "PROPERTY_TOWNHOUSE",
            "category": "PropertyType",
            "property_type": "townhouse",
            "appraisal_approach": "sales_comparison_primary", 
            "comparable_requirements": "3_minimum_similar_style",
            "distance_limit_miles": 3.0,
            "age_limit_months": 12,
            "attachment_consideration": "attached_vs_detached_comparison",
            "hoa_requirements": "if_applicable",
            "description": "Townhouse property appraisal requirements"
        },
        
        # Appraisal Standards Rules
        {
            "rule_id": "APPRAISAL_USPAP_COMPLIANCE",
            "category": "AppraisalStandards",
            "standard_type": "uspap_compliance",
            "appraiser_license": "state_licensed_certified_required",
            "independence_requirements": "no_financial_interest",
            "competency_requirements": "geographic_property_type_competent",
            "reporting_format": "urar_form_1004",
            "effective_date": "within_120_days",
            "description": "USPAP compliance requirements for residential appraisals"
        },
        {
            "rule_id": "APPRAISAL_GSE_REQUIREMENTS",
            "category": "AppraisalStandards",
            "standard_type": "gse_compliance",
            "appraisal_forms": ["URAR_1004", "Exterior_2055", "Desktop_2065"],
            "quality_control": "collateral_underwriter_review",
            "data_verification": "mls_public_records_confirmation",
            "photo_requirements": "street_front_rear_interior",
            "sketch_requirements": "building_sketch_with_calculations",
            "description": "GSE (Fannie Mae/Freddie Mac) appraisal requirements"
        },
        
        # Value Analysis Rules
        {
            "rule_id": "VALUE_SALES_COMPARISON",
            "category": "ValueAnalysis",
            "approach_type": "sales_comparison",
            "comparable_count": 3,
            "adjustment_categories": ["location", "site", "view", "design", "quality", "age", "condition", "room_count", "gross_living_area"],
            "gross_adjustment_limit": 0.25,
            "net_adjustment_limit": 0.15,
            "data_sources": ["mls", "public_records", "appraiser_verification"],
            "verification_requirements": "all_comparables_verified",
            "description": "Sales comparison approach value analysis"
        },
        {
            "rule_id": "VALUE_COST_APPROACH",
            "category": "ValueAnalysis",
            "approach_type": "cost_approach",
            "when_required": ["new_construction", "unique_properties", "gse_requirement"],
            "land_value_method": "comparable_land_sales",
            "improvement_cost": "current_local_construction_costs",
            "depreciation_analysis": "physical_functional_external",
            "cost_sources": "marshall_swift_local_builders",
            "description": "Cost approach value analysis requirements"
        },
        {
            "rule_id": "VALUE_INCOME_APPROACH", 
            "category": "ValueAnalysis",
            "approach_type": "income_approach",
            "when_required": ["2_4_unit_properties", "investment_properties"],
            "rental_analysis": "market_rent_comparable_rentals",
            "capitalization_rate": "market_derived_rate",
            "expense_ratio": "market_typical_expenses",
            "vacancy_factor": "market_area_vacancy",
            "description": "Income approach value analysis for income properties"
        },
        
        # Property Condition Rules
        {
            "rule_id": "CONDITION_HEALTH_SAFETY",
            "category": "PropertyCondition",
            "condition_type": "health_safety",
            "required_systems": ["heating", "cooling", "electrical", "plumbing", "structural"],
            "safety_requirements": ["smoke_detectors", "handrails", "egress_windows"],
            "health_hazards": ["lead_paint", "asbestos", "mold", "radon"],
            "repair_requirements": "completion_prior_to_closing",
            "inspection_depth": "readily_observable_conditions",
            "description": "Health and safety property condition requirements"
        },
        {
            "rule_id": "CONDITION_STRUCTURAL_INTEGRITY",
            "category": "PropertyCondition",
            "condition_type": "structural",
            "foundation_requirements": "sound_adequate_support",
            "roof_requirements": "weather_tight_remaining_life",
            "structural_elements": ["foundation", "framing", "roof_structure"],
            "red_flag_conditions": ["settling", "cracking", "sagging", "water_damage"],
            "engineer_referral": "if_structural_concerns_observed",
            "description": "Structural integrity condition requirements"
        },
        
        # Market Analysis Rules  
        {
            "rule_id": "MARKET_ANALYSIS_STANDARD",
            "category": "MarketAnalysis",
            "analysis_type": "neighborhood_market_conditions",
            "market_indicators": ["price_trends", "marketing_time", "supply_demand"],
            "data_period": "12_months_minimum",
            "geographic_scope": "subject_neighborhood_competitive_area",
            "trend_analysis": "stable_increasing_decreasing",
            "market_acceptance": "typical_buyer_appeal",
            "description": "Standard neighborhood and market analysis"
        },
        {
            "rule_id": "MARKET_DECLINING_CONDITIONS",
            "category": "MarketAnalysis", 
            "analysis_type": "declining_market",
            "decline_indicators": ["price_decrease_10_percent", "marketing_time_increase", "foreclosure_activity"],
            "additional_requirements": ["expanded_comparable_search", "market_data_analysis"],
            "adjustment_considerations": "market_decline_impact",
            "lender_notification": "declining_market_noted",
            "description": "Declining market condition analysis requirements"
        },
        
        # Special Property Rules
        {
            "rule_id": "SPECIAL_NEW_CONSTRUCTION",
            "category": "SpecialProperty",
            "property_type": "new_construction",
            "completion_requirements": "certificate_of_occupancy",
            "comparable_preferences": "new_construction_comparables",
            "cost_approach": "required_as_support",
            "builder_reputation": "consideration_factor",
            "warranty_information": "builder_warranty_details",
            "description": "New construction property appraisal requirements"
        },
        {
            "rule_id": "SPECIAL_RURAL_PROPERTY",
            "category": "SpecialProperty",
            "property_type": "rural",
            "comparable_search_radius": "expanded_radius_acceptable",
            "age_limit_extended": "24_months_if_necessary",
            "unique_features": "acreage_outbuildings_wells",
            "access_requirements": "legal_access_documented",
            "utility_availability": "verify_utilities_available",
            "description": "Rural property appraisal special requirements"
        },
        {
            "rule_id": "SPECIAL_MANUFACTURED_HOME",
            "category": "SpecialProperty",
            "property_type": "manufactured_home",
            "foundation_requirements": "permanent_foundation_required",
            "hud_certification": "hud_certification_plate_required",
            "comparable_requirements": "manufactured_home_comparables_preferred",
            "personal_vs_real_property": "real_property_classification_required",
            "age_considerations": "age_condition_marketability",
            "description": "Manufactured home appraisal requirements"
        }
    ]
    
    for rule in property_rules:
        # Ensure all parameters are explicitly set
        rule_params = {key: rule.get(key) for key in [
            "rule_id", "category", "property_type", "appraisal_approach", "comparable_requirements", 
            "distance_limit_miles", "age_limit_months", "adjustment_limits", "special_requirements",
            "hoa_analysis_required", "condo_certification", "attachment_consideration", "hoa_requirements",
            "standard_type", "appraiser_license", "independence_requirements", "competency_requirements", 
            "reporting_format", "effective_date", "appraisal_forms", "quality_control", "data_verification",
            "photo_requirements", "sketch_requirements", "approach_type", "comparable_count", 
            "adjustment_categories", "gross_adjustment_limit", "net_adjustment_limit", "data_sources",
            "verification_requirements", "when_required", "land_value_method", "improvement_cost",
            "depreciation_analysis", "cost_sources", "rental_analysis", "capitalization_rate",
            "expense_ratio", "vacancy_factor", "condition_type", "required_systems", "safety_requirements",
            "health_hazards", "repair_requirements", "inspection_depth", "foundation_requirements",
            "roof_requirements", "structural_elements", "red_flag_conditions", "engineer_referral",
            "analysis_type", "market_indicators", "data_period", "geographic_scope", "trend_analysis",
            "market_acceptance", "decline_indicators", "additional_requirements", "adjustment_considerations",
            "lender_notification", "completion_requirements", "comparable_preferences", "cost_approach",
            "builder_reputation", "warranty_information", "comparable_search_radius", "age_limit_extended",
            "unique_features", "access_requirements", "utility_availability", "hud_certification",
            "personal_vs_real_property", "age_considerations", "description"
        ]}
        query = """
        CREATE (par:PropertyAppraisalRule {
            rule_id: $rule_id,
            category: $category,
            property_type: $property_type,
            appraisal_approach: $appraisal_approach,
            comparable_requirements: $comparable_requirements,
            distance_limit_miles: $distance_limit_miles,
            age_limit_months: $age_limit_months,
            adjustment_limits: $adjustment_limits,
            special_requirements: $special_requirements,
            hoa_analysis_required: $hoa_analysis_required,
            condo_certification: $condo_certification,
            attachment_consideration: $attachment_consideration,
            hoa_requirements: $hoa_requirements,
            standard_type: $standard_type,
            appraiser_license: $appraiser_license,
            independence_requirements: $independence_requirements,
            competency_requirements: $competency_requirements,
            reporting_format: $reporting_format,
            effective_date: $effective_date,
            appraisal_forms: $appraisal_forms,
            quality_control: $quality_control,
            data_verification: $data_verification,
            photo_requirements: $photo_requirements,
            sketch_requirements: $sketch_requirements,
            approach_type: $approach_type,
            comparable_count: $comparable_count,
            adjustment_categories: $adjustment_categories,
            gross_adjustment_limit: $gross_adjustment_limit,
            net_adjustment_limit: $net_adjustment_limit,
            data_sources: $data_sources,
            verification_requirements: $verification_requirements,
            when_required: $when_required,
            land_value_method: $land_value_method,
            improvement_cost: $improvement_cost,
            depreciation_analysis: $depreciation_analysis,
            cost_sources: $cost_sources,
            rental_analysis: $rental_analysis,
            capitalization_rate: $capitalization_rate,
            expense_ratio: $expense_ratio,
            vacancy_factor: $vacancy_factor,
            condition_type: $condition_type,
            required_systems: $required_systems,
            safety_requirements: $safety_requirements,
            health_hazards: $health_hazards,
            repair_requirements: $repair_requirements,
            inspection_depth: $inspection_depth,
            foundation_requirements: $foundation_requirements,
            roof_requirements: $roof_requirements,
            structural_elements: $structural_elements,
            red_flag_conditions: $red_flag_conditions,
            engineer_referral: $engineer_referral,
            analysis_type: $analysis_type,
            market_indicators: $market_indicators,
            data_period: $data_period,
            geographic_scope: $geographic_scope,
            trend_analysis: $trend_analysis,
            market_acceptance: $market_acceptance,
            decline_indicators: $decline_indicators,
            additional_requirements: $additional_requirements,
            adjustment_considerations: $adjustment_considerations,
            lender_notification: $lender_notification,
            completion_requirements: $completion_requirements,
            comparable_preferences: $comparable_preferences,
            cost_approach: $cost_approach,
            builder_reputation: $builder_reputation,
            warranty_information: $warranty_information,
            comparable_search_radius: $comparable_search_radius,
            age_limit_extended: $age_limit_extended,
            unique_features: $unique_features,
            access_requirements: $access_requirements,
            utility_availability: $utility_availability,
            foundation_requirements: $foundation_requirements,
            hud_certification: $hud_certification,
            personal_vs_real_property: $personal_vs_real_property,
            age_considerations: $age_considerations,
            description: $description
        })
        """
        
        connection.execute_query(query, rule_params)
        logger.info(f"Created PropertyAppraisalRule: {rule['rule_id']}")
    
    logger.info(f"Loaded {len(property_rules)} property appraisal rules successfully")
