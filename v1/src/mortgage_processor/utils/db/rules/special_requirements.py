"""
Special Requirements for Loan Programs

This module contains the special requirements for each loan program
used by the MortgageAdvisorAgent for qualification analysis.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_special_requirements(connection):
    """Load special requirements for each loan program into Neo4j."""
    
    special_requirements = [
        # VA Loan Special Requirements
        {
            "program_name": "VA",
            "requirement_type": "military_eligibility",
            "required": True,
            "description": "Must be eligible veteran, active duty, or qualified spouse",
            "eligibility_criteria": ["active_duty", "veteran", "spouse"],
            "gap_message": "Must establish VA loan eligibility",
            "verification_steps": [
                "Obtain Certificate of Eligibility (COE)",
                "Gather military service records",
                "Contact VA-approved lender",
                "Verify entitlement amount"
            ]
        },
        {
            "program_name": "VA",
            "requirement_type": "va_benefits",
            "required": False,
            "description": "VA loan benefits for eligible borrowers",
            "benefit_details": "No down payment required, no PMI",
            "additional_info": "VA funding fee may apply"
        },
        # USDA Loan Special Requirements
        {
            "program_name": "USDA",
            "requirement_type": "property_location",
            "required": True,
            "description": "Property must be in USDA-eligible rural area",
            "eligibility_criteria": ["rural"],
            "gap_message": "Property must be in USDA-eligible area",
            "verification_steps": [
                "Use USDA property eligibility map",
                "Work with realtor familiar with USDA areas",
                "Verify property eligibility before making offers",
                "Consider suburban areas near rural zones"
            ]
        },
        {
            "program_name": "USDA",
            "requirement_type": "income_limits",
            "required": True,
            "description": "Household income must not exceed 115% of area median income",
            "additional_info": "Income limits vary by location and household size"
        },
        # FHA Loan Special Requirements
        {
            "program_name": "FHA",
            "requirement_type": "property_standards",
            "required": True,
            "description": "Property must meet FHA minimum property standards",
            "additional_info": "Includes safety, security, and soundness requirements"
        },
        {
            "program_name": "FHA",
            "requirement_type": "mortgage_insurance",
            "required": True,
            "description": "Mortgage insurance required for life of loan",
            "additional_info": "Upfront and annual mortgage insurance premiums apply"
        },
        # Conventional Loan Special Requirements
        {
            "program_name": "Conventional",
            "requirement_type": "private_mortgage_insurance",
            "required": True,
            "description": "PMI required if down payment is less than 20%",
            "additional_info": "PMI can be removed once 20% equity is reached"
        },
        {
            "program_name": "Conventional",
            "requirement_type": "loan_limits",
            "required": True,
            "description": "Must be within conforming loan limits",
            "additional_info": "Limits vary by county and are updated annually"
        },
        # Jumbo Loan Special Requirements
        {
            "program_name": "Jumbo",
            "requirement_type": "loan_amount",
            "required": True,
            "description": "Loan amount exceeds conforming loan limits",
            "additional_info": "Higher credit scores and reserves typically required"
        }
    ]
    
    for req in special_requirements:
        # Handle optional parameters
        req_params = {
            "program_name": req.get("program_name"),
            "requirement_type": req.get("requirement_type"),
            "required": req.get("required", True),
            "description": req.get("description", ""),
            "eligibility_criteria": req.get("eligibility_criteria"),
            "gap_message": req.get("gap_message"),
            "verification_steps": req.get("verification_steps"),
            "benefit_details": req.get("benefit_details"),
            "additional_info": req.get("additional_info")
        }
        
        query = """
        CREATE (sr:SpecialRequirement {
            program_name: $program_name,
            requirement_type: $requirement_type,
            required: $required,
            description: $description,
            eligibility_criteria: $eligibility_criteria,
            gap_message: $gap_message,
            verification_steps: $verification_steps,
            benefit_details: $benefit_details,
            additional_info: $additional_info
        })
        """
        
        connection.execute_query(query, req_params)
        logger.info(f"Created SpecialRequirement: {req['program_name']} - {req['requirement_type']}")
    
    logger.info(f"Loaded {len(special_requirements)} special requirements successfully")
