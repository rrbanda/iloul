"""
Risk Assessment Rules Module

Property and borrower risk assessment rules including:
- Property risk factors (flood zones, market conditions)
- Geographic risk assessments
- Market volatility considerations
- Environmental risk factors
"""

from .property_risk_rules import load_property_risk_rules

__all__ = [
    "load_property_risk_rules"
]
