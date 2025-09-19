"""
AssistantAgent using LangGraph prebuilt create_react_agent
Handles guidance, education, UI prompts, and user assistance
"""

from mortgage_processor.utils.llm_factory import get_llm, get_supervisor_llm, get_agent_llm, get_grader_llm
from langgraph.prebuilt import create_react_agent

from ..tools import (
    generate_contextual_prompts,
    generate_next_step_guidance,
    analyze_application_state,
    # Mortgage business logic tools
    calculate_debt_to_income_ratio,
    calculate_loan_to_value_ratio,
    calculate_monthly_payment,
    assess_affordability,
    check_loan_program_eligibility,
    generate_pre_approval_assessment,
    # Credit & income verification tools
    simulate_credit_check,
    verify_employment_history,
    validate_income_sources,
    analyze_bank_statements
)
from ..rag_tools import get_mortgage_retriever_tool
from ..external_agents import list_available_external_agents
from ..sync_external_tools import (
    # Sync wrappers for A2A tools (avoid async tool issues in create_react_agent)
    sync_search_web_information,
    sync_use_a2a_orchestrator, 
    sync_get_current_mortgage_rates,
    sync_get_mortgage_market_news,
    sync_search_loan_program_updates
)
from ..state import AssistantAgentState
from ..prompt_loader import load_assistant_prompt
from ..config import AppConfig


def create_assistant_agent():
    """
    Create AssistantAgent using LangGraph's prebuilt create_react_agent
    
    This replaces the custom assistant_agent_node with a proper LangGraph agent
    that includes built-in memory, streaming, and human-in-the-loop capabilities.
    """
    
    # Load configuration
    config = AppConfig.load()
    
    # Create the LLM using config
    llm = get_llm()  # Centralized LLM from config.yaml
    
    # Tools for assistant agent - FULL SET RESTORED (supervisor async tool issue fixed!)
    tools = [
        # Core guidance tools
        generate_contextual_prompts,
        generate_next_step_guidance,
        analyze_application_state,
        
        # Mortgage business logic & calculations
        calculate_debt_to_income_ratio,
        calculate_loan_to_value_ratio,
        calculate_monthly_payment,
        assess_affordability,
        check_loan_program_eligibility,
        generate_pre_approval_assessment,
        
        # Credit & income verification tools
        simulate_credit_check,
        verify_employment_history,
        validate_income_sources,
        analyze_bank_statements,
        
        # External A2A agents - sync wrappers for full functionality
        list_available_external_agents,
        sync_search_web_information,
        sync_use_a2a_orchestrator,
        sync_get_current_mortgage_rates,
        sync_get_mortgage_market_news,
        sync_search_loan_program_updates
        
        # Note: Handoff tools will be provided automatically by supervisor
    ]
    
    # Load system prompt as messages modifier
    system_prompt = load_assistant_prompt()

    # Create the prebuilt ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    
    return agent
