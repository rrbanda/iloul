"""
Mortgage Rules Package

This package contains all mortgage business rules organized by category.
Each rule type is in its own module for better maintainability.

Structure:
- document_verification/: Document verification rules
- income_calculation/: Income calculation rules  
- property_appraisal/: Property appraisal rules
- underwriting/: Underwriting decision rules
- compliance/: Regulatory compliance rules
- rate_pricing/: Rate and pricing rules

All rules are stored as Neo4j nodes (data-driven, not hardcoded).
"""

# Core rules (original MortgageAdvisorAgent rules)
from .business_rules import load_business_rules
from .scoring_rules import load_scoring_rules
from .qualification_thresholds import load_qualification_thresholds
from .special_requirements import load_special_requirements
from .improvement_strategies import load_improvement_strategies

# Comprehensive end-to-end processing rules
from .document_verification import load_document_verification_rules
from .income_calculation import load_income_calculation_rules
from .property_appraisal import load_property_appraisal_rules
from .underwriting import load_underwriting_rules
from .compliance import load_compliance_rules
from .rate_pricing import load_rate_pricing_rules

# Identity verification rules
from .id_verification import load_id_verification_rules

# Application intake rules
from .application_intake import load_application_intake_rules

# URLA Form 1003 rules
from .urla_1003 import load_urla_1003_rules

__all__ = [
    # Core rules
    "load_business_rules",
    "load_scoring_rules",
    "load_qualification_thresholds",
    "load_special_requirements",
    "load_improvement_strategies",

    # End-to-end processing rules
    "load_document_verification_rules",
    "load_income_calculation_rules",
    "load_property_appraisal_rules",
    "load_underwriting_rules",
    "load_compliance_rules",
    "load_rate_pricing_rules",

    # Identity verification rules
    "load_id_verification_rules",

    # Application intake rules
    "load_application_intake_rules",

    # URLA Form 1003 rules
    "load_urla_1003_rules"
]
