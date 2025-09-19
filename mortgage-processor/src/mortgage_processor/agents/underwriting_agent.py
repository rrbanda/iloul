"""
UnderwritingAgent using LangGraph prebuilt create_react_agent
Handles comprehensive risk analysis, loan decisions, and compliance verification
"""

from mortgage_processor.utils.llm_factory import get_llm, get_supervisor_llm, get_agent_llm, get_grader_llm
from langgraph.prebuilt import create_react_agent

from ..tools.underwriting import (
    comprehensive_risk_analysis,
    loan_decision_engine,
    guideline_compliance_check,
    generate_approval_conditions,
    exception_analysis
)
# Also include some tools from other modules that underwriting needs
from ..tools import (
    simulate_credit_check,
    verify_employment_history,
    validate_income_sources,
    assess_affordability,
    check_loan_program_eligibility
)
from ..neo4j_mortgage import (
    update_application_status,
    get_application_status,
    store_loan_decision
)
from ..state import UnderwritingAgentState
from ..prompt_loader import load_underwriting_agent_prompt
from ..config import AppConfig


def create_underwriting_agent():
    """
    Create UnderwritingAgent using LangGraph's prebuilt create_react_agent
    
    This agent specializes in underwriting tasks including risk analysis,
    loan decision making, compliance checking, and exception processing.
    """
    
    # Load configuration
    config = AppConfig.load()
    
    # Create the LLM using config
    llm = get_llm()  # Centralized LLM from config.yaml
    
    # Tools for underwriting agent
    tools = [
        # Core underwriting tools
        comprehensive_risk_analysis,
        loan_decision_engine,
        guideline_compliance_check,
        generate_approval_conditions,
        exception_analysis,
        
        # Supporting analysis tools from other modules
        simulate_credit_check,
        verify_employment_history,
        validate_income_sources,
        assess_affordability,
        check_loan_program_eligibility,
        
        # Status management and decision persistence
        update_application_status,
        get_application_status,
        store_loan_decision
        
        # Note: Handoff tools will be provided automatically by supervisor
    ]
    
    # Load system prompt as messages modifier
    system_prompt = load_underwriting_agent_prompt()

    # Create the prebuilt ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    
    return agent
