"""
LangGraph workflow for mortgage application processing
Subgraph-based architecture with specialized agent isolation
"""

from typing import Dict, Any, Literal
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from pydantic import BaseModel

from .state import MortgageApplicationState
from .subgraphs import (
    create_assistant_agent_subgraph,
    create_data_agent_subgraph,
    AssistantAgentState,
    DataAgentState
)

# Structured output for supervisor routing
class RouterDecision(BaseModel):
    next_agent: Literal["assistant_agent", "data_agent"]
    reasoning: str

# ================================
# SUBGRAPH WRAPPER FUNCTIONS
# ================================

def call_assistant_agent_subgraph(state: MortgageApplicationState) -> Dict[str, Any]:
    """
    Wrapper function to call AssistantAgent subgraph with state transformation
    """
    # Create and compile AssistantAgent subgraph
    assistant_subgraph = create_assistant_agent_subgraph().compile()
    
    # Transform main state to AssistantAgent state
    assistant_state: AssistantAgentState = {
        "messages": state["messages"],
        # UI & Guidance context
        "ui_context": state.get("current_phase", "initial"),
        "current_prompts": state.get("current_prompts", []),
        "guidance_steps": state.get("guidance_steps", []),
        # Educational context
        "topics_discussed": state.get("topics_discussed", []),
        "loan_types_mentioned": state.get("loan_types_mentioned", []),
        "user_expertise_level": state.get("user_expertise_level", "beginner"),
        # Handoff context
        "handoff_reason": state.get("handoff_reason", "")
    }
    
    # Invoke subgraph
    result = assistant_subgraph.invoke(assistant_state)
    
    # Transform result back to main state format
    return {
        "messages": result["messages"],
        "current_prompts": result.get("current_prompts", []),
        "guidance_steps": result.get("guidance_steps", []),
        "topics_discussed": result.get("topics_discussed", []),
        "loan_types_mentioned": result.get("loan_types_mentioned", []),
        "user_expertise_level": result.get("user_expertise_level", "beginner"),
        "last_interaction_type": "assistant_agent"
    }

def call_data_agent_subgraph(state: MortgageApplicationState, config=None, *, store=None) -> Dict[str, Any]:
    """
    Wrapper function to call DataAgent subgraph with state transformation and memory
    """
    # Create and compile DataAgent subgraph 
    # Note: Checkpointing is handled by the parent graph, not individual subgraphs
    data_subgraph = create_data_agent_subgraph().compile()
    
    # Transform main state to DataAgent state
    data_state: DataAgentState = {
        "messages": state["messages"],
        # Transfer all customer data fields
        "full_name": state.get("full_name"),
        "phone": state.get("phone"),
        "email": state.get("email"),
        "annual_income": state.get("annual_income"),
        "employer": state.get("employer"),
        "employment_type": state.get("employment_type"),
        "purchase_price": state.get("purchase_price"),
        "property_type": state.get("property_type"),
        "property_location": state.get("property_location"),
        "down_payment": state.get("down_payment"),
        "credit_score": state.get("credit_score"),
        "completion_percentage": state.get("completion_percentage", 0.0),
        "handoff_reason": state.get("handoff_reason", "")
    }
    
    # Create subgraph config with user_id for memory isolation
    subgraph_config = {}
    if config:
        subgraph_config = {
            "configurable": {
                "thread_id": f"data_agent_{config.get('configurable', {}).get('thread_id', 'default')}",
                "user_id": config.get("configurable", {}).get("user_id")
            }
        }
    
    # Invoke subgraph with memory and config
    if store:
        # Pass store to subgraph for customer data persistence
        result = data_subgraph.invoke(data_state, config=subgraph_config, store=store)
    else:
        result = data_subgraph.invoke(data_state, config=subgraph_config)
    
    # Transform result back to main state format, preserving customer data
    state_update = {
        "messages": result["messages"],
        "last_interaction_type": "data_agent"
    }
    
    # Update main state with any extracted customer data
    customer_fields = [
        "full_name", "phone", "email", "annual_income", "employer", "employment_type",
        "purchase_price", "property_type", "property_location", "down_payment", "credit_score"
    ]
    
    for field in customer_fields:
        if result.get(field) is not None:
            state_update[field] = result[field]
    
    if result.get("completion_percentage") is not None:
        state_update["completion_percentage"] = result["completion_percentage"]
    
    return state_update

def supervisor_node(state: MortgageApplicationState, config=None) -> Command[Literal["assistant_agent", "data_agent"]]:
    """
    Supervisor agent that uses LLM to decide routing with context awareness
    """
    llm = ChatOpenAI(
        base_url="https://llama-4-scout-17b-16e-w4a16-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1",
        api_key="24d9922379f970918acc7ed1805b0af4",
        model="llama-4-scout-17b-16e-w4a16",
        temperature=0.2,
        max_tokens=800
    )
    
    structured_llm = llm.with_structured_output(RouterDecision)
    
    # Check completion status to inform routing decisions
    collected_fields = [
        state.get("full_name"), state.get("phone"), state.get("email"),
        state.get("annual_income"), state.get("employer"), state.get("employment_type"),
        state.get("purchase_price"), state.get("property_type"), state.get("property_location"),
        state.get("down_payment"), state.get("credit_score")
    ]
    is_complete = all(field is not None and field != "" for field in collected_fields)
    completion_percentage = (sum(1 for field in collected_fields if field) / len(collected_fields)) * 100
    
    # Get customer context from config for personalized routing
    customer_tier = config.get("configurable", {}).get("customer_tier", "standard") if config else "standard"
    communication_style = config.get("configurable", {}).get("communication_style", "detailed") if config else "detailed"
    application_type = config.get("configurable", {}).get("application_type", "purchase") if config else "purchase"
    
    completion_status = "COMPLETE" if is_complete else f"IN PROGRESS ({completion_percentage:.0f}%)"
    
    system_prompt = f"""You are a supervisor agent that routes user messages to specialist agents.

CUSTOMER CONTEXT:
- Customer Tier: {customer_tier}
- Communication Style: {communication_style}
- Application Type: {application_type}
- Data Collection Status: {completion_status}

AVAILABLE AGENTS:
- assistant_agent: Handles help, guidance, education, UI prompts, and all user assistance
- data_agent: Handles information extraction and customer data collection

COMPLETION-AWARE ROUTING:
- If data collection is COMPLETE and user says "proceed", "submit", "next steps" → assistant_agent (for submission guidance)
- If data collection is COMPLETE and user asks about process → assistant_agent (for next steps)
- If data collection is IN PROGRESS and user provides information → data_agent (for extraction)
- If user asks for help, guidance, or education → assistant_agent

ROUTING RULES:
- Help, guidance, suggestions, "what to do next" → assistant_agent
- General questions about mortgages, loan types, processes → assistant_agent  
- UI prompts, step-by-step guidance, completion instructions → assistant_agent
- Personal/financial/property information (when not complete) → data_agent
- Data like names, numbers, employment info (when not complete) → data_agent

CRITICAL: When data collection is COMPLETE, all requests should go to assistant_agent for guidance and next steps.

Choose the most appropriate agent based on the user's message intent, customer context, and completion status."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    decision = structured_llm.invoke(messages)
    
    return Command(goto=decision.next_agent)

# Removed supervisor_should_continue - using simpler one-time routing to fix infinite loop

# ================================
# SIMPLIFIED WORKFLOW WITH SUBGRAPHS
# ================================

def create_mortgage_workflow() -> StateGraph:
    """
    Create the simplified mortgage application workflow using 2-agent subgraph architecture
    - AssistantAgent: Unified guidance, education, and UI assistance
    - DataAgent: Customer data collection and extraction
    
    Fixed infinite loop issue by using one-time supervisor routing
    """
    
    workflow = StateGraph(MortgageApplicationState)
    
    # Add nodes - supervisor + simplified subgraph wrapper functions
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("assistant_agent", call_assistant_agent_subgraph)
    workflow.add_node("data_agent", call_data_agent_subgraph)
    
    # Define simplified workflow edges - supervisor routes ONCE, then agents end
    workflow.add_edge(START, "supervisor")
    
    # Agents terminate directly instead of returning to supervisor (fixes infinite loop)
    workflow.add_edge("assistant_agent", END)
    workflow.add_edge("data_agent", END)
    
    return workflow
