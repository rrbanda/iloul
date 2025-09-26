"""
Secondary Market Rules Module

Rules for selling loans to government-sponsored enterprises (GSEs)
and other secondary market investors including:
- Fannie Mae requirements
- Freddie Mac requirements  
- FHA securitization rules
- Private investor guidelines
"""

from .fannie_mae_rules import load_fannie_mae_rules

__all__ = [
    "load_fannie_mae_rules"
]
