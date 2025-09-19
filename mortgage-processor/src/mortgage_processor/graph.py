"""
Main Graph Construction for Mortgage Processing Application

This module constructs the main LangGraph workflow using a supervisor pattern
to coordinate between different specialized agents for mortgage processing.
Uses LangGraph's built-in supervisor functionality with Command and handoff tools.
"""

from typing import Annotated
from mortgage_processor.utils.llm_factory import get_llm, get_supervisor_llm, get_agent_llm, get_grader_llm
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.graph.message import add_messages

from .state import MortgageApplicationState
from .subgraphs import (
    create_compiled_assistant_agent,
    create_compiled_data_agent,
    create_compiled_property_agent,
    create_compiled_underwriting_agent,
    create_compiled_compliance_agent,
    create_compiled_closing_agent,
    create_compiled_customer_service_agent,
    create_compiled_application_agent,
    create_compiled_document_agent
)
from .prompt_loader import load_supervisor_prompt
from .config import AppConfig
from .sync_external_tools import sync_search_web_information

# ================================
# HANDOFF TOOLS FOR SUPERVISOR
# ================================

def create_handoff_tool(*, agent_name: str, description: str):
    """Create a handoff tool for transferring control to a specific agent."""
    name = f"transfer_to_{agent_name}"
    
    @tool(name, description=description)
    def handoff_tool() -> str:
        """Handoff tool that indicates transfer to specific agent."""
        return f"Transferring to {agent_name} for specialized assistance."
    
    return handoff_tool

# Create handoff tools for each agent
transfer_to_assistant_agent = create_handoff_tool(
    agent_name="assistant_agent",
    description="Transfer to AssistantAgent for customer guidance, education, and general mortgage assistance."
)

transfer_to_data_agent = create_handoff_tool(
    agent_name="data_agent",
    description="Transfer to DataAgent for data extraction, validation, and processing tasks."
)

transfer_to_property_agent = create_handoff_tool(
    agent_name="property_agent",
    description="Transfer to PropertyAgent for property valuation, appraisal coordination, and property-related tasks."
)

transfer_to_underwriting_agent = create_handoff_tool(
    agent_name="underwriting_agent",
    description="Transfer to UnderwritingAgent for risk analysis, loan decisions, and underwriting tasks."
)

transfer_to_compliance_agent = create_handoff_tool(
    agent_name="compliance_agent",
    description="Transfer to ComplianceAgent for regulatory compliance, TRID compliance, and audit trail management."
)

transfer_to_closing_agent = create_handoff_tool(
    agent_name="closing_agent", 
    description="Transfer to ClosingAgent for closing coordination, document preparation, and cost calculations."
)

transfer_to_customer_service_agent = create_handoff_tool(
    agent_name="customer_service_agent",
    description="Transfer to CustomerServiceAgent for application status tracking, issue resolution, and customer support."
)

transfer_to_application_agent = create_handoff_tool(
    agent_name="application_agent",
    description="Transfer to ApplicationAgent for interactive mortgage application processing and data collection."
)

transfer_to_document_agent = create_handoff_tool(
    agent_name="document_agent",
    description="Transfer to DocumentAgent for document collection, processing, verification, and status tracking."
)

# ================================
# SUPERVISOR AGENT
# ================================

def create_supervisor_agent():
    """Create the supervisor agent with handoff tools."""
    # Use centralized LLM factory - all config comes from config.yaml
    supervisor_model = get_supervisor_llm()
    
    # Handoff tools for all agents + Google A2A external routing
    handoff_tools = [
        transfer_to_assistant_agent,
        transfer_to_data_agent,
        transfer_to_property_agent,
        transfer_to_underwriting_agent,
        transfer_to_compliance_agent,
        transfer_to_closing_agent,
        transfer_to_customer_service_agent,
        transfer_to_application_agent,
        transfer_to_document_agent,
        # Google A2A external agent routing - using sync wrapper to avoid async issues
        sync_search_web_information  # Routes to Google A2A orchestrator
    ]
    
    # Load supervisor system prompt
    system_prompt = load_supervisor_prompt()
    
    # Bind tools to the model with explicit tool choice
    model_with_tools = supervisor_model.bind_tools(handoff_tools, tool_choice="any")
    
    # Create supervisor agent using LangGraph's built-in supervisor functionality
    supervisor = create_react_agent(
        model=supervisor_model,
        tools=handoff_tools
    )
    
    return supervisor

# ================================
# HELPER FUNCTIONS
# ================================

def should_continue(state: MessagesState) -> bool:
    """
    Determine if the conversation should continue to supervisor or end.
    
    Returns True if should return to supervisor, False if should end.
    """
    messages = state.get("messages", [])
    if not messages:
        return True
        
    last_message = messages[-1]
    
    # If the last message is from an AI agent and contains substantial content,
    # consider it a complete response and end the conversation
    if hasattr(last_message, 'content') and last_message.content:
        content = last_message.content.lower()
        
        # Check if it's a complete response (contains helpful information)
        if (len(content) > 50 and  # Substantial content
            ('document' in content or 'mortgage' in content or 'loan' in content or 
             'application' in content or 'qualify' in content or 'require' in content)):
            return False  # End conversation
    
    return True  # Continue to supervisor

# ================================
# MAIN GRAPH CONSTRUCTION
# ================================

def create_mortgage_graph() -> StateGraph:
    """
    Create the complete mortgage application workflow using built-in LangGraph supervisor pattern.
    
    This creates a 9-agent system with built-in LangGraph supervisor:
    - AssistantAgent: Customer guidance and education
    - DataAgent: Data collection and processing
    - PropertyAgent: Property valuation and analysis
    - UnderwritingAgent: Risk analysis and loan decisions
    - ComplianceAgent: Regulatory compliance
    - ClosingAgent: Closing coordination
    - CustomerServiceAgent: Post-submission support
    - ApplicationAgent: Interactive mortgage application processing with Neo4j
    - DocumentAgent: Document collection, processing, and verification
    
    Uses Command-based handoffs for seamless agent-to-agent communication.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    
    # Create all agent instances
    supervisor_agent = create_supervisor_agent()
    assistant_agent = create_compiled_assistant_agent()
    data_agent = create_compiled_data_agent()
    property_agent = create_compiled_property_agent()
    underwriting_agent = create_compiled_underwriting_agent()
    compliance_agent = create_compiled_compliance_agent()
    closing_agent = create_compiled_closing_agent()
    customer_service_agent = create_compiled_customer_service_agent()
    application_agent = create_compiled_application_agent()
    document_agent = create_compiled_document_agent()
    
    # Build the complete supervisor graph with all agents
    workflow = StateGraph(MessagesState)
    
    # Add supervisor as the central coordinator
    workflow.add_node("supervisor", supervisor_agent)
    
    # Add all specialized worker agents
    workflow.add_node("assistant_agent", assistant_agent)
    workflow.add_node("data_agent", data_agent)
    workflow.add_node("property_agent", property_agent)
    workflow.add_node("underwriting_agent", underwriting_agent)
    workflow.add_node("compliance_agent", compliance_agent)
    workflow.add_node("closing_agent", closing_agent)
    workflow.add_node("customer_service_agent", customer_service_agent)
    workflow.add_node("application_agent", application_agent)
    workflow.add_node("document_agent", document_agent)
    
    # Set entry point
    workflow.add_edge(START, "supervisor")
    
    # Create a simple routing function for supervisor decisions
    def route_supervisor_decision(state):
        """Route supervisor decisions to appropriate agents based on last message content."""
        messages = state.get("messages", [])
        if not messages:
            return "assistant_agent"  # Default
            
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            content = last_message.content.lower()
            
            # Route based on content keywords and tool calls
            if any(word in content for word in ["transfer_to_assistant", "guidance", "education", "help", "question"]):
                return "assistant_agent"
            elif any(word in content for word in ["transfer_to_data", "data", "extract", "validation", "processing"]):
                return "data_agent"
            elif any(word in content for word in ["transfer_to_property", "property", "appraisal", "valuation"]):
                return "property_agent"
            elif any(word in content for word in ["transfer_to_underwriting", "underwriting", "risk", "decision", "approval"]):
                return "underwriting_agent"
            elif any(word in content for word in ["transfer_to_compliance", "compliance", "regulatory", "trid"]):
                return "compliance_agent"
            elif any(word in content for word in ["transfer_to_closing", "closing", "documents", "coordination"]):
                return "closing_agent"
            elif any(word in content for word in ["transfer_to_customer_service", "status", "support", "issue"]):
                return "customer_service_agent"
            elif any(word in content for word in ["transfer_to_application", "application", "apply", "submit"]):
                return "application_agent"
            elif any(word in content for word in ["transfer_to_document", "document", "upload", "docs", "paperwork", "verification"]):
                return "document_agent"
            else:
                return "assistant_agent"  # Default to assistant for general queries
        
        return "assistant_agent"  # Default fallback
    
    # Add conditional edges from supervisor to all agents
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor_decision,
        {
            "assistant_agent": "assistant_agent",
            "data_agent": "data_agent", 
            "property_agent": "property_agent",
            "underwriting_agent": "underwriting_agent",
            "compliance_agent": "compliance_agent",
            "closing_agent": "closing_agent",
            "customer_service_agent": "customer_service_agent",
            "application_agent": "application_agent",
            "document_agent": "document_agent"
        }
    )
    
    # All worker agents end the conversation (simplified for now)
    # In a full implementation, agents could route back to supervisor
    workflow.add_edge("assistant_agent", END)
    workflow.add_edge("data_agent", END)
    workflow.add_edge("property_agent", END)
    workflow.add_edge("underwriting_agent", END)
    workflow.add_edge("compliance_agent", END)
    workflow.add_edge("closing_agent", END)
    workflow.add_edge("customer_service_agent", END)
    workflow.add_edge("application_agent", END)
    workflow.add_edge("document_agent", END)
    
    # Compile the graph
    return workflow.compile()