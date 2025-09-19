"""
PropertyAgent using LangGraph prebuilt create_react_agent
Handles property valuation, appraisal coordination, and compliance checking
"""

from mortgage_processor.utils.llm_factory import get_llm, get_supervisor_llm, get_agent_llm, get_grader_llm
from langgraph.prebuilt import create_react_agent

from ..tools.property import (
    request_property_appraisal,
    analyze_property_value,
    check_property_compliance,
    calculate_property_taxes,
    assess_property_risks
)
from ..state import PropertyAgentState
from ..prompt_loader import load_property_agent_prompt
from ..config import AppConfig


def create_property_agent():
    """
    Create PropertyAgent using LangGraph's prebuilt create_react_agent
    
    This agent specializes in property-related tasks including valuation,
    appraisal coordination, compliance checking, and risk assessment.
    """
    
    # Load configuration
    config = AppConfig.load()
    
    # Create the LLM using config
    llm = get_llm()  # Centralized LLM from config.yaml
    
    # Tools for property agent
    tools = [
        request_property_appraisal,
        analyze_property_value,
        check_property_compliance,
        calculate_property_taxes,
        assess_property_risks
        # Note: Handoff tools will be provided automatically by supervisor
    ]
    
    # Load system prompt as messages modifier
    system_prompt = load_property_agent_prompt()

    # Create the prebuilt ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    
    return agent
