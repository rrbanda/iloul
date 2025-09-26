"""
Compliance Rules Module

Regulatory compliance rules for mortgage processing including:
- QM (Qualified Mortgage) requirements
- TRID (Truth in Lending) rules
- CFPB consumer protection guidelines
"""

from .qm_rules import load_qm_rules

__all__ = [
    "load_qm_rules"
]
