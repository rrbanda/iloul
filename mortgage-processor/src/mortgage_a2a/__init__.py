"""
A2A (Agent-to-Agent) Integration Module

This module contains all A2A related functionality for the mortgage processing system,
including agent executors and server implementations using the A2A SDK.
"""

from .agents import *
from .orchestrator_agent import (
    MortgageA2AOrchestrator,
    MortgageOrchestratorExecutor,
    create_mortgage_orchestrator_card,
    create_mortgage_orchestrator_server
)

__version__ = "1.0.0"

__all__ = [
    # Orchestrator
    "MortgageA2AOrchestrator",
    "MortgageOrchestratorExecutor", 
    "create_mortgage_orchestrator_card",
    "create_mortgage_orchestrator_server",
    # Agents (imported from agents package)
    "LlamaStackWebSearchExecutor",
    "create_web_search_agent_card",
    "create_web_search_server"
]
