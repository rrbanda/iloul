"""
Property Risk Assessment Rules

Rules for evaluating property-specific risks that may affect
loan eligibility, pricing, or require additional conditions.

Risk Categories:
- Environmental risks (flood, earthquake, wildfire)
- Market risks (declining values, oversupply)
- Property condition risks
- Geographic risks
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_property_risk_rules(connection) -> bool:
    """
    Load property risk assessment rules into Neo4j.
    
    Args:
        connection: Neo4j connection instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Loading property risk assessment rules...")
    
    property_risk_rules = [
        # Flood Zone Risk Assessment
        {
            "rule_id": "PROPERTY_RISK_FLOOD_ZONE_A",
            "rule_type": "PropertyRisk",
            "category": "EnvironmentalRisk",
            "risk_factor": "flood_zone",
            "flood_zone": "A",
            "risk_level": "high",
            "flood_insurance_required": True,
            "additional_requirements": ["elevated_foundation", "flood_certificate"],
            "loan_restrictions": ["no_basement_finished_areas"],
            "description": "High flood risk areas require flood insurance and elevated construction",
            "impact_on_lending": "additional_conditions_required"
        },
        {
            "rule_id": "PROPERTY_RISK_FLOOD_ZONE_X",
            "rule_type": "PropertyRisk",
            "category": "EnvironmentalRisk",
            "risk_factor": "flood_zone",
            "flood_zone": "X",
            "risk_level": "low",
            "flood_insurance_required": False,
            "additional_requirements": [],
            "loan_restrictions": [],
            "description": "Minimal flood risk areas with no special requirements",
            "impact_on_lending": "no_impact"
        },
        
        # Wildfire Risk Assessment
        {
            "rule_id": "PROPERTY_RISK_WILDFIRE_HIGH",
            "rule_type": "PropertyRisk",
            "category": "EnvironmentalRisk",
            "risk_factor": "wildfire_risk",
            "risk_level": "high",
            "affected_states": ["CA", "CO", "OR", "WA", "AZ", "NV"],
            "insurance_requirements": ["fire_insurance", "additional_coverage"],
            "property_requirements": ["defensible_space", "fire_resistant_materials"],
            "rate_adjustment": 0.125,  # 12.5 basis points
            "description": "High wildfire risk areas require additional insurance and property protections",
            "seasonal_restrictions": "no_closings_during_fire_season_without_inspection"
        },
        
        # Earthquake Risk Assessment
        {
            "rule_id": "PROPERTY_RISK_EARTHQUAKE_HIGH",
            "rule_type": "PropertyRisk",
            "category": "EnvironmentalRisk",
            "risk_factor": "earthquake_risk",
            "risk_level": "high",
            "affected_states": ["CA", "AK", "WA", "OR"],
            "seismic_zone": ["4", "3"],
            "building_code_requirements": ["seismic_retrofitting", "foundation_bolting"],
            "insurance_recommendations": ["earthquake_insurance"],
            "inspection_requirements": ["structural_engineer_review"],
            "description": "High seismic activity areas require enhanced building standards"
        },
        
        # Market Risk Assessment
        {
            "rule_id": "PROPERTY_RISK_DECLINING_MARKET",
            "rule_type": "PropertyRisk",
            "category": "MarketRisk",
            "risk_factor": "market_conditions",
            "risk_level": "moderate",
            "market_indicators": ["declining_home_values", "high_inventory", "job_losses"],
            "ltv_restrictions": {"max_ltv": 0.80},
            "appraisal_requirements": ["recent_comparable_sales", "market_analysis"],
            "reserve_requirements": "additional_reserves_recommended",
            "description": "Declining market areas require conservative LTV and additional reserves",
            "monitoring_required": True
        },
        {
            "rule_id": "PROPERTY_RISK_OVERSUPPLY_MARKET",
            "rule_type": "PropertyRisk",
            "category": "MarketRisk",
            "risk_factor": "market_conditions",
            "risk_level": "moderate",
            "market_indicators": ["new_construction_oversupply", "extended_days_on_market"],
            "property_restrictions": ["no_spec_homes", "completion_required"],
            "appraisal_requirements": ["absorption_analysis", "supply_demand_study"],
            "loan_program_restrictions": ["conventional_preferred"],
            "description": "Markets with oversupply require completed properties and enhanced analysis"
        },
        
        # Property Condition Risk
        {
            "rule_id": "PROPERTY_RISK_AGE_CONDITION",
            "rule_type": "PropertyRisk",
            "category": "PropertyCondition",
            "risk_factor": "property_age",
            "property_age_threshold": 50,
            "inspection_requirements": ["home_inspection", "major_systems_evaluation"],
            "potential_issues": ["outdated_electrical", "plumbing_concerns", "roof_replacement"],
            "reserve_recommendations": "maintenance_reserves",
            "description": "Properties over 50 years old require enhanced inspection and reserves",
            "appraisal_considerations": ["remaining_economic_life", "deferred_maintenance"]
        },
        {
            "rule_id": "PROPERTY_RISK_FOUNDATION_ISSUES",
            "rule_type": "PropertyRisk",
            "category": "PropertyCondition",
            "risk_factor": "structural_integrity",
            "risk_level": "high",
            "required_inspections": ["structural_engineer", "foundation_specialist"],
            "repair_requirements": ["documented_repairs", "warranty_required"],
            "loan_hold_conditions": ["repairs_completed_before_funding"],
            "description": "Foundation issues require expert evaluation and completion of repairs",
            "follow_up_required": "post_repair_inspection"
        },
        
        # Geographic Risk Factors
        {
            "rule_id": "PROPERTY_RISK_RURAL_LOCATION",
            "rule_type": "PropertyRisk",
            "category": "GeographicRisk",
            "risk_factor": "location_isolation",
            "location_type": "rural",
            "distance_to_services": "> 30 miles",
            "appraisal_challenges": ["limited_comparables", "extended_marketing_time"],
            "loan_program_suitability": ["USDA_preferred", "conventional_caution"],
            "rate_considerations": "rural_rate_adjustment_possible",
            "description": "Rural properties may have limited marketability and fewer comparables"
        },
        {
            "rule_id": "PROPERTY_RISK_URBAN_DECLINING",
            "rule_type": "PropertyRisk",
            "category": "GeographicRisk", 
            "risk_factor": "neighborhood_decline",
            "location_type": "urban",
            "risk_indicators": ["population_decline", "business_closures", "crime_increase"],
            "ltv_restrictions": {"max_ltv": 0.85},
            "appraisal_requirements": ["neighborhood_analysis", "trend_evaluation"],
            "monitoring_requirements": "ongoing_market_monitoring",
            "description": "Declining urban areas require conservative lending and ongoing monitoring"
        },
        
        # Environmental Contamination
        {
            "rule_id": "PROPERTY_RISK_ENVIRONMENTAL_CONTAMINATION",
            "rule_type": "PropertyRisk",
            "category": "EnvironmentalRisk",
            "risk_factor": "soil_contamination",
            "contamination_sources": ["former_gas_stations", "industrial_sites", "dry_cleaners"],
            "testing_requirements": ["phase_1_environmental", "soil_testing"],
            "remediation_requirements": ["cleanup_completion", "regulatory_clearance"],
            "loan_eligibility": "conditional_upon_clean_certification",
            "description": "Properties with potential contamination require environmental clearance",
            "liability_considerations": "lender_liability_assessment"
        }
    ]
    
    try:
        # Clear existing property risk rules
        with connection.driver.session(database=connection.database) as session:
            session.run("MATCH (n:PropertyRisk_Rule) DELETE n")
            logger.info("Cleared existing property risk rules")
        
        # Create property risk rule nodes
        for rule in property_risk_rules:
            # Build dynamic query based on available fields
            fields = []
            params = {}
            
            # Core fields that should always be present
            core_fields = ["rule_id", "rule_type", "category", "risk_factor", "description"]
            
            for field in core_fields:
                if field in rule:
                    fields.append(f"{field}: ${field}")
                    params[field] = rule[field]
            
            # Optional fields - only add if present and not None
            all_optional_fields = list(rule.keys())
            for field in all_optional_fields:
                if field not in core_fields and field in rule and rule[field] is not None:
                    value = rule[field]
                    # Convert dictionaries to JSON strings for Neo4j compatibility
                    if isinstance(value, dict):
                        import json
                        value = json.dumps(value)
                    fields.append(f"{field}: ${field}")
                    params[field] = value
            
            # Add timestamps
            fields.extend(["created_at: datetime()", "updated_at: datetime()"])
            
            query = f"""
            CREATE (pr:PropertyRisk_Rule {{
                {', '.join(fields)}
            }})
            """
            
            with connection.driver.session(database=connection.database) as session:
                session.run(query, params)
                logger.info(f" Created Property Risk Rule: {rule['rule_id']}")
        
        logger.info(f"Successfully loaded {len(property_risk_rules)} property risk rules")
        return True
        
    except Exception as e:
        logger.error(f" Error loading property risk rules: {e}")
        return False


def create_property_risk_relationships(connection) -> bool:
    """
    Create relationships between property risk rules and loan programs.
    
    Args:
        connection: Neo4j connection instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Creating property risk rule relationships...")
    
    try:
        relationship_queries = [
            # Connect flood risk to all loan programs
            """
            MATCH (pr:PropertyRisk_Rule)
            WHERE pr.risk_factor = 'flood_zone'
            MATCH (lp:LoanProgram)
            CREATE (lp)-[:SUBJECT_TO_PROPERTY_RISK]->(pr)
            """,
            
            # Connect environmental risks to loan programs
            """
            MATCH (pr:PropertyRisk_Rule)
            WHERE pr.category = 'EnvironmentalRisk'
            MATCH (lp:LoanProgram)
            CREATE (lp)-[:EVALUATED_FOR_ENVIRONMENTAL_RISK]->(pr)
            """,
            
            # Connect market risks to conventional loans primarily
            """
            MATCH (pr:PropertyRisk_Rule)
            WHERE pr.category = 'MarketRisk'
            MATCH (lp:LoanProgram {name: 'Conventional'})
            CREATE (lp)-[:AFFECTED_BY_MARKET_RISK]->(pr)
            """,
            
            # Connect property condition risks to all programs
            """
            MATCH (pr:PropertyRisk_Rule)
            WHERE pr.category = 'PropertyCondition'
            MATCH (lp:LoanProgram)
            CREATE (lp)-[:REQUIRES_CONDITION_ASSESSMENT]->(pr)
            """
        ]
        
        relationships_created = 0
        with connection.driver.session(database=connection.database) as session:
            for query in relationship_queries:
                result = session.run(query)
                summary = result.consume()
                relationships_created += summary.counters.relationships_created
        
        logger.info(f" Created {relationships_created} property risk rule relationships")
        return True
        
    except Exception as e:
        logger.error(f" Error creating property risk relationships: {e}")
        return False
