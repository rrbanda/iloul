"""
Core Mortgage Data Module

Contains the fundamental mortgage entities that form the foundation
of the mortgage knowledge graph.

Entities:
- Loan Programs: FHA, VA, USDA, Conventional, Jumbo
- Borrower Profiles: First-time buyer, Military, High-income, etc.
- Process Steps: Mortgage workflow guidance
- Qualification Requirements: Basic qualification criteria
"""

from .loan_programs import load_loan_programs

__all__ = [
    "load_loan_programs"
]
