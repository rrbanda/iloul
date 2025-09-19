"""
DataAgent using LangGraph prebuilt create_react_agent
Handles customer data collection, extraction, and application submission
"""

from mortgage_processor.utils.llm_factory import get_llm, get_supervisor_llm, get_agent_llm, get_grader_llm
from langgraph.prebuilt import create_react_agent

from ..tools import (
    extract_personal_info,
    extract_employment_info,
    extract_property_info,
    extract_financial_info,
    analyze_application_state,
    submit_application_to_database,
    check_application_status,
    # Mortgage assessment tools for validation
    assess_affordability,
    check_loan_program_eligibility,
    generate_pre_approval_assessment,
    # Verification tools for data validation
    simulate_credit_check,
    verify_employment_history,
    validate_income_sources,
    analyze_bank_statements
)
from ..neo4j_mortgage import (
    update_application_status,
    get_application_status
)
from ..state import DataAgentState
from ..prompt_loader import load_data_agent_prompt
from ..config import AppConfig


def create_data_agent():
    """
    Create DataAgent using LangGraph's prebuilt create_react_agent
    
    This replaces the custom data_agent_node with a proper LangGraph agent
    that includes built-in memory, streaming, and human-in-the-loop capabilities.
    """
    
    # Load configuration
    config = AppConfig.load()
    
    # Create the LLM using config
    llm = get_llm()  # Centralized LLM from config.yaml
    
    # Tools for data agent
    tools = [
        extract_personal_info,
        extract_employment_info,
        extract_property_info,
        extract_financial_info,
        analyze_application_state,
        # Mortgage assessment tools for validation
        assess_affordability,
        check_loan_program_eligibility,
        generate_pre_approval_assessment,
        # Verification tools for comprehensive data validation
        simulate_credit_check,
        verify_employment_history,
        validate_income_sources,
        analyze_bank_statements,
        # Database tools for agentic submission
        submit_application_to_database,
        check_application_status,
        # Status management tools
        update_application_status,
        get_application_status
        # Note: Handoff tools will be provided automatically by supervisor
    ]
    
    # Load system prompt as messages modifier
    system_prompt = load_data_agent_prompt()

    # Create the prebuilt ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    
    return agent
