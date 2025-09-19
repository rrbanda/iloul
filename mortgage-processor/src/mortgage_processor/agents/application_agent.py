"""
ApplicationAgent for interactive mortgage application processing with Neo4j integration.
Adapted from IBM Watsonx LangGraph-Graph-RAG pattern.
"""

import uuid
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime

from mortgage_processor.utils.llm_factory import get_llm
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from ..application_lifecycle import get_application_manager, ApplicationIntent, ApplicationPhase

from ..tools.core import (
    assess_affordability,
    check_loan_program_eligibility,
    calculate_debt_to_income_ratio
)
from ..neo4j_mortgage import (
    get_mortgage_graph_manager,
    store_mortgage_application,
    search_applicant_history,
    analyze_mortgage_relationships,
    update_application_status,
    get_application_status,
    initiate_processing_workflow
)
from ..state import MessagesState
from ..prompt_loader import load_application_agent_prompt
from ..config import AppConfig


class ApplicationRouting(BaseModel):
    """Routing decisions for application processing."""
    
    route: Literal["collect_data", "graph_search", "submit_application", "final_answer"] = Field(
        description=(
            "Route determines the next action: "
            "'collect_data' - need more information from user, "
            "'graph_search' - search existing relationships in graph, "
            "'submit_application' - ready to submit complete application, "
            "'final_answer' - provide final response to user"
        )
    )
    reasoning: str = Field(description="Explanation for the routing decision")


class ApplicationAgentState(MessagesState):
    """
    Enhanced state for ApplicationAgent with graph data.
    Based on IBM Watsonx Graph-RAG pattern.
    """
    # Current application data being collected
    current_application: Optional[Dict[str, Any]] = None
    application_id: Optional[str] = None
    
    # Graph search results  
    structured_graph_data: str = ""
    relationship_context: str = ""
    
    # Application progress
    current_step: str = "initial"
    completion_percentage: float = 0.0
    required_fields: List[str] = []
    collected_fields: List[str] = []
    
    # Routing decision
    route: Optional[str] = None
    
    # Validation
    validation_errors: List[str] = []
    
    # Required by create_react_agent
    remaining_steps: int = 10


class ApplicationCollector:
    """Handles step-by-step application data collection."""
    
    REQUIRED_SECTIONS = {
        "personal_info": ["first_name", "last_name", "ssn_last_4", "email", "phone", "date_of_birth"],
        "employment": ["employer_name", "position", "annual_income", "employment_type", "start_date"],
        "property": ["address", "city", "state", "zip_code", "property_type", "purchase_price"],
        "financial": ["monthly_debts", "assets", "down_payment_amount"],
        "loan_details": ["loan_amount", "loan_program", "loan_term"]
    }
    
    def __init__(self):
        self.graph_manager = get_mortgage_graph_manager()
    
    def get_next_question(self, application_data: Dict[str, Any], current_step: str) -> tuple[str, str]:
        """Get the next question to ask the user."""
        
        # Determine current section
        if current_step == "initial" or not application_data.get("personal_info"):
            return self._get_personal_info_question(application_data)
        elif not application_data.get("employment"):
            return self._get_employment_question(application_data) 
        elif not application_data.get("property"):
            return self._get_property_question(application_data)
        elif not application_data.get("financial"):
            return self._get_financial_question(application_data)
        elif not application_data.get("loan_details"):
            return self._get_loan_details_question(application_data)
        else:
            return "complete", "Ready to submit your application!"
    
    def _get_personal_info_question(self, app_data: Dict[str, Any]) -> tuple[str, str]:
        """Get next personal information question."""
        personal = app_data.get("personal_info", {})
        
        if not personal.get("first_name"):
            return "personal_info", "Let's start with your personal information. What's your first name?"
        elif not personal.get("last_name"):
            return "personal_info", "What's your last name?"
        elif not personal.get("email"):
            return "personal_info", "What's your email address?"
        elif not personal.get("phone"):
            return "personal_info", "What's your phone number?"
        elif not personal.get("ssn_last_4"):
            return "personal_info", "For identity verification, what are the last 4 digits of your Social Security Number?"
        elif not personal.get("date_of_birth"):
            return "personal_info", "What's your date of birth? (MM/DD/YYYY format)"
        else:
            return "employment", "Great! Now let's talk about your employment."
    
    def _get_employment_question(self, app_data: Dict[str, Any]) -> tuple[str, str]:
        """Get next employment question.""" 
        employment = app_data.get("employment", {})
        
        if not employment.get("employer_name"):
            return "employment", "What's the name of your current employer?"
        elif not employment.get("position"):
            return "employment", "What's your job title or position?"
        elif not employment.get("annual_income"):
            return "employment", "What's your annual gross income? (before taxes)"
        elif not employment.get("employment_type"):
            return "employment", "Are you employed full-time, part-time, or self-employed?"
        elif not employment.get("start_date"):
            return "employment", "When did you start working at this company? (MM/YYYY format)"
        else:
            return "property", "Perfect! Now let's discuss the property you're purchasing."
    
    def _get_property_question(self, app_data: Dict[str, Any]) -> tuple[str, str]:
        """Get next property question."""
        property_info = app_data.get("property", {})
        
        if not property_info.get("address"):
            return "property", "What's the full address of the property you want to purchase?"
        elif not property_info.get("city"):
            return "property", "What city is the property in?"
        elif not property_info.get("state"):
            return "property", "What state is the property in?"
        elif not property_info.get("zip_code"):
            return "property", "What's the ZIP code?"
        elif not property_info.get("property_type"):
            return "property", "What type of property is this? (Single Family, Condo, Townhouse, etc.)"
        elif not property_info.get("purchase_price"):
            return "property", "What's the purchase price of the property?"
        else:
            return "financial", "Excellent! Now I need some financial information."
    
    def _get_financial_question(self, app_data: Dict[str, Any]) -> tuple[str, str]:
        """Get next financial question."""
        financial = app_data.get("financial", {})
        
        if not financial.get("down_payment_amount"):
            return "financial", "How much are you planning to put down as a down payment?"
        elif not financial.get("monthly_debts"):
            return "financial", "What are your total monthly debt payments? (credit cards, car loans, student loans, etc.)"
        elif not financial.get("assets"):
            return "financial", "What's the total value of your savings and assets available for this purchase?"
        else:
            return "loan_details", "Almost done! Let's finalize your loan preferences."
    
    def _get_loan_details_question(self, app_data: Dict[str, Any]) -> tuple[str, str]:
        """Get next loan details question."""
        loan = app_data.get("loan_details", {})
        
        if not loan.get("loan_amount"):
            purchase_price = app_data.get("property", {}).get("purchase_price", 0)
            down_payment = app_data.get("financial", {}).get("down_payment_amount", 0)
            if purchase_price and down_payment:
                suggested_amount = purchase_price - down_payment
                return "loan_details", f"Based on your purchase price and down payment, you'll need a loan of ${suggested_amount:,}. Does this look correct?"
            else:
                return "loan_details", "What loan amount do you need?"
        elif not loan.get("loan_program"):
            return "loan_details", "What type of loan program interests you? (Conventional, FHA, VA, USDA, or let me recommend based on your profile)"
        elif not loan.get("loan_term"):
            return "loan_details", "What loan term do you prefer? (15 years, 30 years, or other)"
        else:
            return "complete", "Perfect! I have all the information needed for your application."
    
    def calculate_completion_percentage(self, application_data: Dict[str, Any]) -> float:
        """Calculate application completion percentage."""
        total_fields = sum(len(fields) for fields in self.REQUIRED_SECTIONS.values())
        completed_fields = 0
        
        for section, fields in self.REQUIRED_SECTIONS.items():
            section_data = application_data.get(section, {})
            for field in fields:
                if section_data.get(field):
                    completed_fields += 1
        
        return (completed_fields / total_fields) * 100


# LLM factory functions moved to mortgage_processor.utils.llm_factory

def create_application_agent():
    """Create the ApplicationAgent with Neo4j integration - WORKING VERSION."""
    
    # Tools for application processing
    tools = [
        # Core mortgage tools
        assess_affordability,
        check_loan_program_eligibility, 
        calculate_debt_to_income_ratio,
        
        # Neo4j graph tools
        store_mortgage_application,
        search_applicant_history,
        analyze_mortgage_relationships,
        
        # Application status and workflow management
        update_application_status,
        get_application_status,
        initiate_processing_workflow,
    ]
    
    # Create agent with system message
    system_message = (
        "You are a mortgage application processing expert specializing in interactive application collection and submission.\n\n"
        
        "## Your Primary Responsibilities ##\n"
        "1. **Collect Application Data**: Guide users through step-by-step data collection for mortgage applications\n"
        "2. **Store Applications**: When complete data is provided, immediately execute store_mortgage_application\n"
        "3. **Initiate Processing**: After successful storage, automatically trigger initiate_processing_workflow\n"
        "4. **Status Updates**: Help users track their application status using get_application_status\n\n"
        
        "## Complete Application Data Includes ##\n"
        "- Personal: applicant name, email, phone, date of birth\n"
        "- Employment: employer, position, annual income, employment type\n"
        "- Property: address, city, state, zip, property type, purchase price\n"
        "- Financial: monthly debts, assets, down payment amount, credit score\n"
        "- Loan: loan amount, loan program (FHA/VA/Conventional), loan term\n\n"
        
        "## Workflow After Application Submission ##\n"
        "When a user provides complete data:\n"
        "1. IMMEDIATELY execute store_mortgage_application with their data\n"
        "2. IF storage is successful, IMMEDIATELY execute initiate_processing_workflow with the application_id\n"
        "3. Provide the user with their application ID and next steps\n\n"
        
        "## Available Tools ##\n"
        "- assess_affordability: Calculate affordability based on income/debts\n"
        "- check_loan_program_eligibility: Determine eligible loan programs\n"
        "- calculate_debt_to_income_ratio: Calculate DTI for qualification\n"
        "- store_mortgage_application: Store complete application in database\n"
        "- initiate_processing_workflow: Start automated processing after submission\n"
        "- get_application_status: Check current status of submitted applications\n"
        "- search_applicant_history: Look up previous applications\n\n"
        
        "You are a TOOL-EXECUTING AGENT. Always execute tools rather than just describing what you would do.\n"
        "Focus on ACTION, not explanation."
    )
    
    agent = create_react_agent(
        model=get_llm(),
        tools=tools
    )
    
    return agent


def application_router(state: ApplicationAgentState) -> ApplicationAgentState:
    """
    Route application processing based on current state.
    Adapted from IBM Watsonx routing pattern.
    """
    
    config = AppConfig.load()
    llm = ChatOpenAI(
        base_url=config.llamastack.base_url,
        api_key=config.llamastack.api_key,
        model=config.llamastack.default_model,
        temperature=0.1
    )
    
    # Get last user message
    messages = state.get("messages", [])
    if not messages:
        return state
    
    last_message = messages[-1]
    user_query = last_message.content if hasattr(last_message, 'content') else ""
    
    # Determine routing based on application state and user input
    system_message = SystemMessage(content=(
        "You are a mortgage application routing assistant. "
        "Based on the user's message and current application state, determine the next action: "
        "'collect_data' if more information is needed, "
        "'graph_search' if you should check existing relationships, "
        "'submit_application' if the application is complete, "
        "'final_answer' for general responses."
    ))
    
    current_app = state.get("current_application", {})
    completion = state.get("completion_percentage", 0)
    
    context_message = HumanMessage(content=(
        f"User message: {user_query}\n"
        f"Application completion: {completion}%\n"
        f"Current step: {state.get('current_step', 'initial')}\n"
        f"Has application data: {bool(current_app)}"
    ))
    
    llm_with_tool = llm.bind_tools([ApplicationRouting], tool_choice="ApplicationRouting")
    response = llm_with_tool.invoke([system_message, context_message])
    
    if response.tool_calls:
        route_decision = response.tool_calls[0]["args"]["route"]
        return {**state, "route": route_decision}
    
    return {**state, "route": "final_answer"}


def application_data_collector(state: ApplicationAgentState) -> ApplicationAgentState:
    """Collect application data step by step."""
    
    collector = ApplicationCollector()
    current_app = state.get("current_application", {})
    current_step = state.get("current_step", "initial")
    
    # Get next question
    next_step, question = collector.get_next_question(current_app, current_step)
    
    # Calculate completion
    completion = collector.calculate_completion_percentage(current_app)
    
    # Generate response message
    if next_step == "complete":
        response_content = (
            f"🎉 **Application Complete!** (100% done)\n\n"
            f"{question}\n\n"
            f"**Application Summary:**\n"
            f"- Applicant: {current_app.get('personal_info', {}).get('first_name', '')} {current_app.get('personal_info', {}).get('last_name', '')}\n"
            f"- Property: {current_app.get('property', {}).get('address', 'N/A')}\n"
            f"- Loan Amount: ${current_app.get('loan_details', {}).get('loan_amount', 0):,}\n"
            f"- Program: {current_app.get('loan_details', {}).get('loan_program', 'N/A')}\n\n"
            f"Would you like me to submit this application?"
        )
        route = "submit_application"
    else:
        response_content = (
            f"📋 **Mortgage Application** ({completion:.0f}% complete)\n\n"
            f"{question}\n\n"
            f"*I'll guide you through each step - no guessing required!*"
        )
        route = "collect_data"
    
    ai_message = AIMessage(content=response_content)
    
    return {
        **state,
        "messages": state.get("messages", []) + [ai_message],
        "current_step": next_step,
        "completion_percentage": completion,
        "route": route
    }


def graph_search_node(state: ApplicationAgentState) -> ApplicationAgentState:
    """Search Neo4j graph for relevant mortgage relationships."""
    
    graph_manager = get_mortgage_graph_manager()
    messages = state.get("messages", [])
    
    if not messages:
        return state
    
    # Extract entities from recent messages
    recent_text = " ".join([
        msg.content for msg in messages[-3:] 
        if hasattr(msg, 'content') and msg.content
    ])
    
    entities = graph_manager.extract_mortgage_entities(recent_text)
    relationship_data = graph_manager.search_mortgage_relationships(entities)
    
    # Create context message about found relationships
    if relationship_data and relationship_data.strip() != "No existing relationships found in graph.":
        context_content = (
            f"📊 **Found Related Information:**\n\n"
            f"I found some relevant information in our database:\n\n"
            f"```\n{relationship_data}\n```\n\n"
            f"This might help with your application. Let me continue collecting your information."
        )
    else:
        context_content = "I'll help you with a fresh application. Let's get started!"
    
    context_message = AIMessage(content=context_content)
    
    return {
        **state,
        "structured_graph_data": relationship_data,
        "relationship_context": context_content,
        "messages": state.get("messages", []) + [context_message],
        "route": "collect_data"
    }


def submit_application_node(state: ApplicationAgentState) -> ApplicationAgentState:
    """Submit the completed application to Neo4j."""
    
    current_app = state.get("current_application", {})
    
    if not current_app:
        error_message = AIMessage(content=" No application data found. Please start over.")
        return {
            **state,
            "messages": state.get("messages", []) + [error_message],
            "route": "final_answer"
        }
    
    # Generate application ID
    app_id = f"MORT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Prepare application data for Neo4j
    app_data = {
        "application_id": app_id,
        "status": "SUBMITTED",
        "applicants": [{
            "id": str(uuid.uuid4()),
            **current_app.get("personal_info", {}),
            "employment": current_app.get("employment", {})
        }],
        "property": {
            "id": str(uuid.uuid4()),
            **current_app.get("property", {})
        },
        **current_app.get("financial", {}),
        **current_app.get("loan_details", {})
    }
    
    try:
        # Store in Neo4j
        graph_manager = get_mortgage_graph_manager()
        result = graph_manager.create_application_nodes(app_data)
        
        success_message = AIMessage(content=(
            f"✅ **Application Submitted Successfully!**\n\n"
            f"**Application ID: {app_id}**\n\n"
            f"Your mortgage application has been submitted and stored in our system. "
            f"You can reference your application using the ID above.\n\n"
            f"**Next Steps:**\n"
            f"1. Our underwriting team will review your application\n"
            f"2. You'll receive updates via email and phone\n"
            f"3. We may request additional documentation\n\n"
            f"Thank you for choosing us for your mortgage needs!"
        ))
        
        return {
            **state,
            "application_id": app_id,
            "messages": state.get("messages", []) + [success_message],
            "route": "final_answer"
        }
        
    except Exception as e:
        error_message = AIMessage(content=(
            f" **Submission Error**\n\n"
            f"There was an issue submitting your application: {str(e)}\n\n"
            f"Please try again or contact support."
        ))
        
        return {
            **state,
            "messages": state.get("messages", []) + [error_message],
            "route": "final_answer"
        }
