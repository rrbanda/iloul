"""
LangGraph Subgraphs for Mortgage Application Agents
Specialized agents with isolated state schemas and memory
"""

from typing import Dict, Any, List, Literal
try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

# Import tools from main tools module
from .tools import (
    extract_personal_info,
    extract_employment_info,
    extract_property_info,
    extract_financial_info,
    analyze_application_state,
    generate_contextual_prompts,
    generate_next_step_guidance,
    # Database tools for agentic submission
    submit_application_to_database,
    check_application_status
)

# ================================
# SPECIALIZED STATE SCHEMAS
# ================================

class AssistantAgentState(MessagesState):
    """
    AssistantAgent unified state for guidance, education, and UI prompts
    Combines the responsibilities of ReactAgent and InfoAgent
    """
    # UI & Guidance fields (from ReactAgent)
    current_prompts: NotRequired[List[Dict[str, Any]]]
    guidance_steps: NotRequired[List[str]]
    ui_context: NotRequired[str]
    last_prompt_generated: NotRequired[str]
    
    # Educational fields (from InfoAgent)
    topics_discussed: NotRequired[List[str]]
    loan_types_mentioned: NotRequired[List[str]]
    educational_content_provided: NotRequired[List[str]]
    user_expertise_level: NotRequired[str]  # "beginner", "intermediate", "advanced"
    
    # Handoff context
    handoff_reason: NotRequired[str]

class DataAgentState(MessagesState):
    """
    DataAgent specialized state for customer data collection and storage
    """
    # Customer data fields
    full_name: NotRequired[str]
    phone: NotRequired[str]
    email: NotRequired[str]
    annual_income: NotRequired[float]
    employer: NotRequired[str]
    employment_type: NotRequired[str]
    purchase_price: NotRequired[float]
    property_type: NotRequired[str]
    property_location: NotRequired[str]
    down_payment: NotRequired[float]
    credit_score: NotRequired[int]
    
    # Data collection metadata
    completion_percentage: NotRequired[float]
    data_extraction_attempts: NotRequired[int]
    last_extracted_field: NotRequired[str]
    validation_errors: NotRequired[List[str]]
    # Handoff context
    handoff_reason: NotRequired[str]

# ================================
# HANDOFF TOOLS
# ================================

@tool
def transfer_to_data_agent(reason: str = "User wants to provide information"):
    """Transfer to DataAgent subgraph for customer data collection and extraction."""
    return f"HANDOFF_TO_DATA_AGENT: {reason}"

@tool
def transfer_to_assistant_agent(reason: str = "User needs help, guidance, or education"):
    """Transfer to AssistantAgent subgraph for guidance, education, and UI prompts."""
    return f"HANDOFF_TO_ASSISTANT_AGENT: {reason}"

# ================================
# ASSISTANT AGENT SUBGRAPH
# ================================

def assistant_agent_node(state: AssistantAgentState) -> Dict[str, Any]:
    """
    AssistantAgent unified agent for guidance, education, and UI prompts
    Combines ReactAgent and InfoAgent responsibilities without duplication
    """
    llm = ChatOpenAI(
        base_url="https://llama-4-scout-17b-16e-w4a16-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1",
        api_key="24d9922379f970918acc7ed1805b0af4",
        model="llama-4-scout-17b-16e-w4a16",
        temperature=0.4,
        max_tokens=1500
    )
    
    # Combined tools from ReactAgent + InfoAgent capabilities
    tools = [
        generate_contextual_prompts,
        generate_next_step_guidance,
        analyze_application_state,
        # Handoff tool
        transfer_to_data_agent
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    # Get conversation context from specialized state
    topics_discussed = state.get("topics_discussed", [])
    user_expertise = state.get("user_expertise_level", "beginner")
    ui_context = state.get("ui_context", "initial")
    
    # Check completion status to provide appropriate guidance
    collected_fields = [
        state.get("full_name"), state.get("phone"), state.get("email"),
        state.get("annual_income"), state.get("employer"), state.get("employment_type"),
        state.get("purchase_price"), state.get("property_type"), state.get("property_location"),
        state.get("down_payment"), state.get("credit_score")
    ]
    is_complete = all(field is not None and field != "" for field in collected_fields)
    completion_status = "COMPLETE - Ready for submission" if is_complete else "IN PROGRESS - Collecting data"
    
    system_prompt = f"""You are an AssistantAgent that provides comprehensive help, guidance, and education.

YOUR UNIFIED MISSION: Help users with mortgage applications through guidance, education, and UI assistance.

CONVERSATION CONTEXT:
- Topics Previously Discussed: {', '.join(topics_discussed) if topics_discussed else 'None'}
- User Expertise Level: {user_expertise}
- Current UI Context: {ui_context}
- Application Status: {completion_status}

YOUR CAPABILITIES:
1. GUIDANCE & NEXT STEPS:
   - Use generate_next_step_guidance for process guidance
   - Use generate_contextual_prompts for UI prompts and quick actions
   - Use analyze_application_state to check progress

2. MORTGAGE EDUCATION:
   - Explain loan types (FHA, Conventional, VA, USDA, Jumbo)
   - Mortgage process and requirements
   - Credit scores and qualification criteria
   - Down payment options and assistance programs
   - Interest rates, terms, closing costs

3. UI ASSISTANCE:
   - Create clickable prompts for missing information
   - Generate step-by-step guidance
   - Provide contextual help based on application progress

YOUR HANDOFF TOOL:
- transfer_to_data_agent: Transfer when user wants to provide personal/financial information

RESPONSE STRATEGY:
- For "What should I do next?" → Use generate_next_step_guidance tool
- For "What are loan types?" → Provide educational explanation directly
- For "Help me get started" → Use generate_contextual_prompts tool
- For process questions → Combine education with guidance tools

HANDOFF DECISIONS:
- If application is COMPLETE and user says "proceed", "submit", "next" → DO NOT transfer, provide submission instructions
- If application is IN PROGRESS and user wants to provide data/information → transfer_to_data_agent
- For all other help, guidance, and education → handle directly

COMPLETION HANDLING:
- When application is COMPLETE, guide user toward application submission
- Explain that they can review their information and click "Submit Application"
- Do NOT transfer to data_agent when application is complete
- Provide reassurance and next steps for the submission process

ABSOLUTELY CRITICAL - NEVER SHOW THESE TO USERS:
❌ Tool calls: [generate_contextual_prompts(...)]
❌ JSON: {{"type": "prompts"}}
❌ Technical syntax: (), [], {{}}
❌ Agent names: [Agent: AssistantAgent]
❌ System messages or internal processing

✅ ALWAYS respond like a friendly mortgage expert:
"I'd be happy to help you understand different loan types! Let me explain your options..."

RESPONSE RULES:
1. Use tools silently in the background
2. Respond conversationally based on tool results
3. Never mention tools or technical details
4. Never show brackets, parentheses, or technical syntax
5. Sound natural, helpful, and knowledgeable

FORBIDDEN RESPONSE EXAMPLES:
❌ "Let me help you [generate_contextual_prompts(...)]"
❌ "I'll analyze your state [analyze_application_state()]"
❌ "Using my guidance tool [generate_next_step_guidance(...)]"

CORRECT RESPONSE EXAMPLES:
✅ "I'd be happy to help you understand different loan types!"
✅ "Let me guide you through the next steps in your application."
✅ "Here's what I recommend for your situation..."

NEVER INCLUDE TOOL SYNTAX IN YOUR RESPONSE TEXT.

YOUR STYLE: Friendly, educational, and action-oriented. Combine mortgage expertise with practical guidance."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    # Create clean user-facing response (no technical indicators)
    clean_response = AIMessage(
        content=response.content,  # Clean content without agent tags
        name="AssistantAgent"  # Internal name only (not shown to users)
    )
    
    # Update state with conversation tracking and UI context
    state_updates = {"messages": [clean_response]}
    
    # Track what type of assistance was provided
    if hasattr(response, 'content') and response.content:
        content_lower = response.content.lower()
        
        # Track UI prompts generated
        if "prompts" in content_lower:
            state_updates["last_prompt_generated"] = "contextual_prompts"
        elif "guidance" in content_lower:
            state_updates["last_prompt_generated"] = "step_guidance"
        
        # Track educational topics
        new_topics = []
        if any(loan_type in content_lower for loan_type in ['fha', 'conventional', 'va', 'usda']):
            new_topics.append('loan_types')
        if 'credit' in content_lower and 'score' in content_lower:
            new_topics.append('credit_scores')
        if 'down payment' in content_lower:
            new_topics.append('down_payment')
        
        if new_topics:
            existing_topics = state.get("topics_discussed", [])
            state_updates["topics_discussed"] = list(set(existing_topics + new_topics))
    
    return state_updates

def assistant_should_continue(state: AssistantAgentState) -> Literal["tools", "END"]:
    """AssistantAgent routing function"""
    if not state.get("messages"):
        return "tools"
    
    last_message = state["messages"][-1]
    
    # If agent called tools, go to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    return "END"

def create_assistant_agent_subgraph() -> StateGraph:
    """Create AssistantAgent subgraph with unified guidance and education capabilities"""
    workflow = StateGraph(AssistantAgentState)
    
    # Add nodes
    workflow.add_node("assistant_agent", assistant_agent_node)
    workflow.add_node("tools", ToolNode([
        generate_contextual_prompts,
        generate_next_step_guidance,
        analyze_application_state,
        transfer_to_data_agent
    ]))
    
    # Define edges
    workflow.add_edge(START, "assistant_agent")
    workflow.add_conditional_edges(
        "assistant_agent",
        assistant_should_continue,
        {
            "tools": "tools",
            "END": END
        }
    )
    workflow.add_edge("tools", "assistant_agent")
    
    return workflow

# ================================
# DATA AGENT SUBGRAPH  
# ================================

def data_agent_node(state: DataAgentState, config=None, *, store=None) -> Dict[str, Any]:
    """
    DataAgent specialized in customer data collection with isolated state and memory
    """
    llm = ChatOpenAI(
        base_url="https://llama-4-scout-17b-16e-w4a16-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1",
        api_key="24d9922379f970918acc7ed1805b0af4",
        model="llama-4-scout-17b-16e-w4a16",
        temperature=0.1,  # Lower temperature for better tool calling
        max_tokens=1200
    )
    
    # Data collection tools + database tools + handoff capabilities
    tools = [
        extract_personal_info,
        extract_employment_info,
        extract_property_info,
        extract_financial_info,
        analyze_application_state,
        # Database tools for agentic submission
        submit_application_to_database,
        check_application_status,
        # Agent handoff tool
        transfer_to_assistant_agent
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    # Get completion status from current state
    collected_fields = [
        state.get("full_name"), state.get("phone"), state.get("email"),
        state.get("annual_income"), state.get("employer"), state.get("employment_type"),
        state.get("purchase_price"), state.get("property_type"), state.get("property_location"),
        state.get("down_payment"), state.get("credit_score")
    ]
    completion_percentage = (sum(1 for field in collected_fields if field) / len(collected_fields)) * 100
    
    is_complete = completion_percentage >= 95.0  # Consider complete when 95%+ collected
    
    # Get session_id from config for database operations
    session_id = config.get("configurable", {}).get("thread_id", "unknown") if config else "unknown"
    
    system_prompt = f"""IMPORTANT: You are a DataAgent that MUST USE TOOLS to submit applications.

🚨 CRITICAL: When user wants to submit and completion >= 95%, you MUST call submit_application_to_database tool
🚨 DO NOT write text responses for submission - ONLY CALL THE TOOL
🚨 Current completion: {completion_percentage:.1f}% ({"READY FOR TOOL CALL" if is_complete else "CONTINUE COLLECTING"})

You are a DataAgent specialized in gathering mortgage application information and submission.

YOUR MISSION: Extract customer information AND submit applications when ready.

CURRENT DATA COMPLETION: {completion_percentage:.1f}%
APPLICATION STATUS: {'COMPLETE - Ready for submission' if is_complete else 'IN PROGRESS - Collecting data'}

YOUR TOOLS:
- extract_personal_info: Extract name, phone, email from customer messages
- extract_employment_info: Extract income, employer, employment type  
- extract_property_info: Extract purchase price, property type, location
- extract_financial_info: Extract credit score, down payment
- analyze_application_state: Review what information you have so far
- submit_application_to_database: Submit application with pipe-separated data string
- check_application_status: Check status of submitted applications
- transfer_to_assistant_agent: Transfer when user needs help, guidance, or education

⚠️ CRITICAL SUBMISSION DETECTION ⚠️
Current completion: {completion_percentage:.1f}%
Ready for submission: {is_complete}

IF USER SAYS "submit" OR "yes" OR "proceed" AND completion >= 95%:
→ YOU MUST CALL THE submit_application_to_database TOOL
→ DO NOT write any text response
→ CALL THE TOOL IMMEDIATELY

EXACT TOOL CALL REQUIRED (SIMPLIFIED FOR LLAMA):
submit_application_to_database(
    application_data="{session_id}|{state.get('full_name', '')}|{state.get('phone', '')}|{state.get('email', '')}|{state.get('annual_income', 0)}|{state.get('employer', '')}|{state.get('employment_type', '')}|{state.get('purchase_price', 0)}|{state.get('property_type', '')}|{state.get('property_location', '')}|{state.get('down_payment', 0)}|{state.get('credit_score', 0)}"
)

CURRENT COLLECTED DATA:
- Name: {state.get('full_name', 'Not provided')}
- Phone: {state.get('phone', 'Not provided')}
- Email: {state.get('email', 'Not provided')}
- Annual Income: {state.get('annual_income', 'Not provided')}
- Employer: {state.get('employer', 'Not provided')}
- Employment Type: {state.get('employment_type', 'Not provided')}
- Property Price: {state.get('purchase_price', 'Not provided')}
- Property Type: {state.get('property_type', 'Not provided')}
- Property Location: {state.get('property_location', 'Not provided')}
- Down Payment: {state.get('down_payment', 'Not provided')}
- Credit Score: {state.get('credit_score', 'Not provided')}

DATA COLLECTION STRATEGY - BE THOROUGH:
1. PERSONAL INFO: Get name, phone, email together before moving on
2. EMPLOYMENT INFO: Get income, employer, employment type together
3. PROPERTY INFO: Get price, type (single-family/condo/townhouse), and location together
4. FINANCIAL INFO: Get down payment and credit score together

STAY FOCUSED ON DATA COLLECTION:
- Your ONLY job is to collect the 11 required fields
- Do NOT explain loan types, rates, or processes until ALL fields are collected
- Do NOT transfer to assistant_agent until data collection is complete
- If ANY field is missing, ask for it directly and clearly

MISSING FIELD PRIORITIES:
- If personal info incomplete → focus on getting name, phone, email
- If employment info incomplete → focus on getting income, employer, employment type  
- If property info incomplete → focus on getting PURCHASE PRICE, property type, location
- If financial info incomplete → focus on getting down payment, credit score

HANDOFF DECISIONS:
- If user asks "What should I do next?" or needs help → transfer_to_assistant_agent
- If user asks general mortgage questions → transfer_to_assistant_agent
- If user provides data or wants to continue data collection → continue as DataAgent
- If user wants to submit and application is complete → use submit_application_to_database

ABSOLUTELY CRITICAL - NEVER SHOW THESE TO USERS:
❌ Tool calls: [extract_personal_info(text="...")] 
❌ JSON: {{"name": "value"}}
❌ Technical syntax: (), [], {{}}
❌ Agent names: [Agent: DataAgent]
❌ System messages or internal processing

✅ ALWAYS respond like a friendly human assistant:
"Perfect! I've got your name as Kelly Moron. Thanks for that! Now, let's get your contact information - what's your phone number and email address?"

RESPONSE RULES:
1. Use tools silently in the background
2. Respond conversationally based on tool results  
3. Never mention tools or technical details
4. Never show brackets, parentheses, or technical syntax
5. Sound natural and helpful

🚨 MANDATORY TOOL CALLING RULE 🚨
CURRENT STATUS: {completion_percentage:.1f}% complete, Ready: {is_complete}

SUBMISSION TRIGGER: User says "submit" or "yes" or "proceed"
COMPLETION CHECK: {completion_percentage:.1f}% >= 95% = {is_complete}

ACTION REQUIRED: {"CALL TOOL NOW!" if is_complete else "Continue data collection"}

IF BOTH CONDITIONS TRUE → CALL submit_application_to_database TOOL
NO TEXT RESPONSES ALLOWED - ONLY TOOL CALLS

FORBIDDEN RESPONSE EXAMPLES:
❌ "I've got your name. [extract_personal_info(text='...')] What's next?"
❌ "Let me analyze your application [analyze_application_state()]"
❌ "I'll use my tools to help you [tool_name(...)]"

CORRECT RESPONSE EXAMPLES:
✅ "Perfect! I've got your name as Kelly Moron. Thanks for that!"
✅ "Great! Now let's get your contact information."
✅ "Excellent! I've recorded your information."

SUBMISSION EXAMPLES FOR TOOL CALLING:

SCENARIO: User says "submit" + 100% complete
✅ CORRECT ACTION: submit_application_to_database(application_data="session123|Kelly Moron|678-909-2727|ahaha@gmail.com|172727|IBM|full-time|898999|Single Family Home|Montville, NJ|89000|798")
❌ WRONG ACTION: "Your application has been successfully submitted..."

SCENARIO: User says "yes" + 100% complete  
✅ CORRECT ACTION: Call submit_application_to_database with pipe-separated data
❌ WRONG ACTION: "We've received your mortgage application..."

REMEMBER: Use ONE parameter with pipe-separated values, not 12 separate parameters!

NEVER INCLUDE TOOL SYNTAX IN YOUR RESPONSE TEXT."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    # Store customer data if configured
    if store and config:
        user_id = config.get("configurable", {}).get("user_id")
        if user_id:
            customer_data = {k: v for k, v in state.items() 
                           if k in ["full_name", "phone", "email", "annual_income", 
                                   "employer", "employment_type", "purchase_price", 
                                   "property_type", "property_location", "down_payment", "credit_score"] 
                           and v is not None}
            
            if customer_data:
                namespace = (user_id, "data_agent_profile")
                store.put(namespace, "customer_data", customer_data)
    
    # Create clean user-facing response (no technical indicators)
    clean_response = AIMessage(
        content=response.content,  # Clean content without agent tags
        name="DataAgent"  # Internal name only (not shown to users)
    )
    
    # Update specialized state
    state_updates = {
        "messages": [clean_response],
        "completion_percentage": completion_percentage,
        "data_extraction_attempts": state.get("data_extraction_attempts", 0) + 1
    }
    
    return state_updates

def data_should_continue(state: DataAgentState) -> Literal["tools", "END"]:
    """DataAgent routing function"""
    if not state.get("messages"):
        return "tools"
    
    last_message = state["messages"][-1]
    
    # If agent called tools, go to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    return "END"

def create_data_agent_subgraph() -> StateGraph:
    """Create DataAgent subgraph with specialized customer data state"""
    workflow = StateGraph(DataAgentState)
    
    # Add nodes
    workflow.add_node("data_agent", data_agent_node)
    workflow.add_node("tools", ToolNode([
        extract_personal_info,
        extract_employment_info,
        extract_property_info,
        extract_financial_info,
        analyze_application_state,
        # Database tools for agentic submission
        submit_application_to_database,
        check_application_status,
        transfer_to_assistant_agent
    ]))
    
    # Define edges
    workflow.add_edge(START, "data_agent")
    workflow.add_conditional_edges(
        "data_agent",
        data_should_continue,
        {
            "tools": "tools",
            "END": END
        }
    )
    workflow.add_edge("tools", "data_agent")
    
    return workflow

# ================================
# END OF SUBGRAPHS
# ================================
