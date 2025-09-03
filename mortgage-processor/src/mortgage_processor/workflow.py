"""
LangGraph workflow for mortgage application processing
Standard production implementation with autonomous agent behavior
"""

from typing import Dict, Any, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
from pydantic import BaseModel

from .state import MortgageApplicationState
from .tools import (
    extract_personal_info,
    extract_employment_info, 
    extract_property_info,
    extract_financial_info,
    analyze_application_state,
    generate_contextual_prompts,
    generate_next_step_guidance
)

# Structured output for supervisor routing
class RouterDecision(BaseModel):
    next_agent: Literal["react_agent", "data_agent", "info_agent"]
    reasoning: str

def supervisor_node(state: MortgageApplicationState, config=None) -> Command[Literal["react_agent", "data_agent", "info_agent"]]:
    """
    Supervisor agent that uses LLM to decide routing with context awareness
    """
    llm = ChatOpenAI(
        base_url="https://llama-4-scout-17b-16e-w4a16-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1",
        api_key="key",
        model="llama-4-scout-17b-16e-w4a16",
        temperature=0.2,
        max_tokens=800
    )
    
    structured_llm = llm.with_structured_output(RouterDecision)
    
    # Get customer context from config for personalized routing
    customer_tier = config.get("configurable", {}).get("customer_tier", "standard") if config else "standard"
    communication_style = config.get("configurable", {}).get("communication_style", "detailed") if config else "detailed"
    application_type = config.get("configurable", {}).get("application_type", "purchase") if config else "purchase"
    
    system_prompt = f"""You are a supervisor agent that routes user messages to specialist agents.

CUSTOMER CONTEXT:
- Customer Tier: {customer_tier}
- Communication Style: {communication_style}
- Application Type: {application_type}

AVAILABLE AGENTS:
- react_agent: Handles help requests, guidance, UI prompts generation  
- data_agent: Handles information extraction and data collection
- info_agent: Handles general mortgage questions, education, loan types

ROUTING RULES:
- If user asks for help, guidance, suggestions, or "what to do next" → react_agent
- If user is providing personal/financial/property information → data_agent  
- If user is giving data like names, numbers, employment info → data_agent
- If user asks general questions about mortgages, loan types, processes → info_agent

CONTEXT-AWARE ADJUSTMENTS:
- Premium customers: Prioritize react_agent for personalized guidance
- First-time buyers: Favor info_agent for educational content
- Refinance applications: Streamline to data_agent for efficiency
- Detailed communication style: Provide thorough reasoning

Choose the most appropriate agent based on the user's message intent and customer context."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    decision = structured_llm.invoke(messages)
    
    return Command(goto=decision.next_agent)

def react_agent_node(state: MortgageApplicationState) -> Dict[str, Any]:
    """
    React agent specialized in generating dynamic UI prompts and guidance
    """
    llm = ChatOpenAI(
        base_url="https://llama-4-scout-17b-16e-w4a16-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1",
        api_key="key",
        model="llama-4-scout-17b-16e-w4a16",
        temperature=0.3,
        max_tokens=1000
    )
    
    # React agent tools
    tools = [
        generate_contextual_prompts,
        generate_next_step_guidance,
        analyze_application_state
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """You are a React agent specialized in creating dynamic user interfaces and guidance.

YOUR MISSION: When users ask for help, guidance, or next steps, ALWAYS use your tools to generate structured responses.

YOUR TOOLS (USE THESE WHEN USERS ASK FOR HELP):
- generate_contextual_prompts: Create clickable prompts based on missing information
- generate_next_step_guidance: Provide step-by-step guidance for users  
- analyze_application_state: Check current application progress

CRITICAL INSTRUCTIONS:
1. When a user asks for help, guidance, or what to do next, IMMEDIATELY call generate_contextual_prompts
2. Use current_phase="initial", collected_data="{}", missing_fields="full_name,phone,email,annual_income,employer,employment_type,purchase_price,property_type,property_location,down_payment,credit_score"
3. ALWAYS call tools - do not provide text responses without tool calls
4. Your job is to generate UI elements, not provide conversational responses

Example: User says "I need help" → Call generate_contextual_prompts immediately"""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}

def data_agent_node(state: MortgageApplicationState, config, *, store=None) -> Dict[str, Any]:
    """
    Data collection agent specialized in extracting and processing user information
    Enhanced with customer memory storage capabilities
    """
    llm = ChatOpenAI(
        base_url="https://llama-4-scout-17b-16e-w4a16-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1",
        api_key="key",
        model="llama-4-scout-17b-16e-w4a16",
        temperature=0.4,
        max_tokens=1200
    )
    
    # Data collection tools
    tools = [
        extract_personal_info,
        extract_employment_info, 
        extract_property_info,
        extract_financial_info,
        analyze_application_state
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """You are a data collection agent specialized in gathering mortgage application information.

YOUR MISSION: Extract and process customer information for their mortgage application.

YOUR TOOLS:
- extract_personal_info: Extract name, phone, email from customer messages
- extract_employment_info: Extract income, employer, employment type  
- extract_property_info: Extract purchase price, property type, location
- extract_financial_info: Extract credit score, down payment
- analyze_application_state: Review what information you have so far

YOUR CONVERSATION FLOW:
1. When user provides information, use appropriate extraction tools
2. After tools complete, acknowledge what you extracted in natural language
3. Thank the user and continue the conversation naturally
4. Ask for the next piece of information needed

IMPORTANT: After calling tools, always respond conversationally. Never show raw tool outputs, JSON, or tool call syntax to the user.

NEVER show users:
- Raw JSON like {"name": "value"}
- Tool calls like [tool_name()]
- Technical syntax or brackets

Example Response Pattern:
"Perfect! I've got your name as [name], phone number [phone], and email [email]. Thanks for that information! 

Now let's move on to your employment details. Can you tell me about your current job - your employer name and annual income?"

Be warm, professional, and thorough in collecting all necessary information."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    # Save customer data to memory store if available
    if store and config:
        user_id = config.get("configurable", {}).get("user_id")
        if user_id:
            from datetime import datetime
            
            # Collect current application data
            customer_data = {
                "personal_info": {
                    "full_name": state.get("full_name"),
                    "phone": state.get("phone"),
                    "email": state.get("email")
                },
                "employment_info": {
                    "annual_income": state.get("annual_income"),
                    "employer": state.get("employer"),
                    "employment_type": state.get("employment_type")
                },
                "property_info": {
                    "purchase_price": state.get("purchase_price"),
                    "property_type": state.get("property_type"),
                    "property_location": state.get("property_location")
                },
                "financial_info": {
                    "down_payment": state.get("down_payment"),
                    "credit_score": state.get("credit_score")
                },
                "application_status": {
                    "completion_percentage": state.get("completion_percentage"),
                    "current_phase": state.get("current_phase"),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            # Remove None values
            customer_data = {k: {sk: sv for sk, sv in v.items() if sv is not None} 
                           for k, v in customer_data.items() if v}
            
            # Save to customer profile
            namespace = (user_id, "profile")
            store.put(namespace, "customer_profile", customer_data)
            
            # Save milestone if significant data was collected
            if any(customer_data.values()):
                milestone_namespace = (user_id, "application_history")
                milestone_id = f"data_collection_{datetime.now().timestamp()}"
                milestone_data = {
                    "event": "data_collection",
                    "agent": "data_agent", 
                    "data_collected": customer_data,
                    "timestamp": datetime.now().isoformat()
                }
                store.put(milestone_namespace, milestone_id, milestone_data)
    
    return {"messages": [response]}

def info_agent_node(state: MortgageApplicationState) -> Dict[str, Any]:
    """
    Information agent specialized in answering general mortgage questions
    """
    llm = ChatOpenAI(
        base_url="https://llama-4-scout-17b-16e-w4a16-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1",
        api_key="key",
        model="llama-4-scout-17b-16e-w4a16",
        temperature=0.6,
        max_tokens=1500
    )
    
    system_prompt = """You are a mortgage information specialist and loan officer expert.

YOUR MISSION: Answer general mortgage questions with accurate, helpful information.

YOUR EXPERTISE:
- Loan types (FHA, Conventional, VA, USDA, Jumbo)
- Mortgage process and requirements  
- Credit scores and qualification criteria
- Down payment options and assistance programs
- Interest rates and terms
- Closing costs and fees
- Pre-approval vs pre-qualification

YOUR STYLE:
- Professional but approachable
- Educational and informative
- Specific and actionable
- Always relate back to their application when relevant

Example: "What types of home loans are there?" → Explain FHA, Conventional, VA, USDA with pros/cons"""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    
    return {"messages": [response]}

def tool_node(state: MortgageApplicationState) -> Dict[str, Any]:
    """
    Tool execution node - processes tool calls and updates state
    """
    tools = [
        extract_personal_info,
        extract_employment_info, 
        extract_property_info,
        extract_financial_info,
        analyze_application_state,
        generate_contextual_prompts,
        generate_next_step_guidance
    ]
    
    tool_node = ToolNode(tools)
    result = tool_node.invoke(state)
    
    # Update state with extracted data
    state_updates = {}
    
    if result.get("messages"):
        for message in result["messages"]:
            if hasattr(message, 'content') and isinstance(message.content, str):
                # Handle state analysis request
                if message.content == "STATE_ANALYSIS_REQUESTED":
                    # Provide current state summary for agent
                    current_data = {
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
                        "credit_score": state.get("credit_score")
                    }
                    # Remove None values
                    current_data = {k: v for k, v in current_data.items() if v is not None}
                    message.content = f"CURRENT_APPLICATION_DATA: {current_data}"
                
                # Parse tool results for state updates
                try:
                    if message.content.startswith('{') and message.content.endswith('}'):
                        import json
                        parsed_data = json.loads(message.content)
                        
                        if isinstance(parsed_data, dict):
                            # Handle React agent responses (dynamic prompts)
                            if parsed_data.get("type") == "dynamic_prompts":
                                # Convert to structured format for frontend
                                message.content = f"DYNAMIC_PROMPTS: {json.dumps(parsed_data)}"
                            elif parsed_data.get("type") == "guidance":
                                # Convert guidance to structured format
                                message.content = f"GUIDANCE: {json.dumps(parsed_data)}"
                            else:
                                # Handle data extraction results
                                valid_fields = {
                                    "full_name", "phone", "email", "annual_income", 
                                    "employer", "employment_type", "purchase_price", 
                                    "property_type", "property_location", "down_payment", "credit_score"
                                }
                                for key, value in parsed_data.items():
                                    if key in valid_fields and value:
                                        state_updates[key] = value
                except json.JSONDecodeError:
                    # Try legacy ast parsing for backwards compatibility
                    try:
                        import ast
                        extracted_data = ast.literal_eval(message.content)
                        if isinstance(extracted_data, dict):
                            valid_fields = {
                                "full_name", "phone", "email", "annual_income", 
                                "employer", "employment_type", "purchase_price", 
                                "property_type", "property_location", "down_payment", "credit_score"
                            }
                            for key, value in extracted_data.items():
                                if key in valid_fields and value:
                                    state_updates[key] = value
                    except:
                        # Agent will handle raw response if parsing fails
                        pass
                except:
                    # Agent will handle raw response if parsing fails
                    pass
    
    return {**result, **state_updates}

# Remove manual routing function - using Command objects now

def should_continue(state: MortgageApplicationState) -> Literal["tools", "END"]:
    """
    Routing function - agent decides workflow continuation
    """
    if not state.get("messages"):
        return "tools"
    
    last_message = state["messages"][-1]
    
    # If agent called tools, go to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # If agent indicates completion, end workflow
    if hasattr(last_message, 'content'):
        content_lower = last_message.content.lower()
        
        # Agent-determined completion indicators
        end_indicators = [
            "application is complete",
            "we're all done", 
            "that completes",
            "application completed",
            "ready to submit",
            "process your application",
            "next steps:"
        ]
        
        if any(indicator in content_lower for indicator in end_indicators):
            return "END"
    
    # Continue conversation
    return "END"

def create_mortgage_workflow() -> StateGraph:
    """
    Create the mortgage application workflow graph with proper supervisor architecture
    """
    
    workflow = StateGraph(MortgageApplicationState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("react_agent", react_agent_node)
    workflow.add_node("data_agent", data_agent_node)
    workflow.add_node("info_agent", info_agent_node)
    workflow.add_node("tools", tool_node)
    
    # Define workflow edges
    workflow.add_edge(START, "supervisor")
    
    # Both specialist agents can use tools or end
    workflow.add_conditional_edges(
        "react_agent", 
        should_continue,
        {
            "tools": "tools",
            "END": END
        }
    )
    
    workflow.add_conditional_edges(
        "data_agent", 
        should_continue,
        {
            "tools": "tools",  
            "END": END
        }
    )
    
    # Info agent doesn't use tools, just ends
    workflow.add_edge("info_agent", END)
    
    # Tools should go back to supervisor for natural response after tool execution
    workflow.add_edge("tools", "supervisor")
    
    return workflow
