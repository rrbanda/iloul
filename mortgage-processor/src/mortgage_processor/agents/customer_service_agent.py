"""
Customer Service Agent for Post-Submission Support

This agent handles customer support throughout the mortgage application lifecycle including:
- Application status tracking and updates
- Document request management  
- Issue resolution and escalation
- Communication coordination
- General customer support
"""

from mortgage_processor.utils.llm_factory import get_llm, get_supervisor_llm, get_agent_llm, get_grader_llm
from langgraph.prebuilt import create_react_agent

from ..tools.customer_service import (
    get_application_status,
    update_customer_on_status,
    request_additional_documents,
    track_document_submission,
    create_customer_issue_ticket,
    escalate_customer_issue,
    schedule_customer_callback,
    send_proactive_communication,
    provide_general_mortgage_support
)
from ..neo4j_mortgage import (
    update_application_status,
    get_application_status as get_neo4j_application_status
)
from ..state import CustomerServiceAgentState
from ..prompt_loader import load_customer_service_agent_prompt
from ..config import AppConfig


def create_customer_service_agent():
    """
    Create CustomerServiceAgent using LangGraph's prebuilt create_react_agent.
    
    This agent specializes in:
    - Application status tracking and customer updates
    - Document request management and follow-up
    - Issue resolution and escalation management
    - Proactive communication and customer engagement
    - General mortgage support and education
    
    Returns:
        Compiled LangGraph agent ready for supervisor integration
    """
    # Load configuration
    config = AppConfig.load()
    
    # Create LLM with customer service optimized settings
    llm = get_llm()  # Centralized LLM from config.yaml
    
    # Define customer service tools
    tools = [
        # Application status tools (both legacy and Neo4j)
        get_application_status,
        get_neo4j_application_status,
        update_customer_on_status,
        update_application_status,
        
        # Document management tools
        request_additional_documents,
        track_document_submission,
        
        # Issue resolution tools
        create_customer_issue_ticket,
        escalate_customer_issue,
        
        # Communication tools
        schedule_customer_callback,
        send_proactive_communication,
        
        # General support tools
        provide_general_mortgage_support
    ]
    
    # Load system prompt as messages modifier
    system_prompt = load_customer_service_agent_prompt()
    
    # Create the agent using LangGraph's prebuilt create_react_agent
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    
    return agent
