"""
ComplianceAgent using LangGraph prebuilt create_react_agent
Handles regulatory compliance, TRID compliance, and audit trail management
"""

from mortgage_processor.utils.llm_factory import get_llm, get_supervisor_llm, get_agent_llm, get_grader_llm
from langgraph.prebuilt import create_react_agent

from ..tools.compliance import (
    trid_compliance_check,
    fair_lending_analysis,
    documentation_completeness_check,
    regulatory_validation,
    audit_trail_generator
)
from ..state import ComplianceAgentState
from ..prompt_loader import load_compliance_agent_prompt
from ..config import AppConfig


def create_compliance_agent():
    """
    Create ComplianceAgent using LangGraph's prebuilt create_react_agent
    
    This agent specializes in regulatory compliance including TRID compliance,
    fair lending analysis, documentation completeness, and audit trail management.
    """
    
    # Load configuration
    config = AppConfig.load()
    
    # Create the LLM using config
    llm = get_llm()  # Centralized LLM from config.yaml
    
    # Tools for compliance agent
    tools = [
        trid_compliance_check,
        fair_lending_analysis,
        documentation_completeness_check,
        regulatory_validation,
        audit_trail_generator
        # Note: Handoff tools will be provided automatically by supervisor
    ]
    
    # Load system prompt as messages modifier
    system_prompt = load_compliance_agent_prompt()

    # Create the prebuilt ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    
    return agent
