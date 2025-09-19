"""
ClosingAgent using LangGraph prebuilt create_react_agent
Handles closing coordination, document preparation, and post-closing activities
"""

from mortgage_processor.utils.llm_factory import get_llm, get_supervisor_llm, get_agent_llm, get_grader_llm
from langgraph.prebuilt import create_react_agent

from ..tools.closing import (
    prepare_closing_documents,
    coordinate_title_escrow,
    calculate_closing_costs,
    schedule_closing_meeting,
    post_closing_coordination
)
from ..state import ClosingAgentState
from ..prompt_loader import load_closing_agent_prompt
from ..config import AppConfig


def create_closing_agent():
    """
    Create ClosingAgent using LangGraph's prebuilt create_react_agent
    
    This agent specializes in closing coordination including document preparation,
    title and escrow coordination, cost calculations, and post-closing activities.
    """
    
    # Load configuration
    config = AppConfig.load()
    
    # Create the LLM using config
    llm = get_llm()  # Centralized LLM from config.yaml
    
    # Tools for closing agent
    tools = [
        prepare_closing_documents,
        coordinate_title_escrow,
        calculate_closing_costs,
        schedule_closing_meeting,
        post_closing_coordination
        # Note: Handoff tools will be provided automatically by supervisor
    ]
    
    # Load system prompt as messages modifier
    system_prompt = load_closing_agent_prompt()

    # Create the prebuilt ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    
    return agent
