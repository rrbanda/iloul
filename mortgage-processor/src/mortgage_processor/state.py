"""
State schema for the mortgage application workflow
"""

from typing import Dict, List, Any, Annotated
from typing_extensions import TypedDict, NotRequired
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState

class MortgageApplicationState(MessagesState):
    """
    Enhanced state schema inheriting from LangGraph's MessagesState.
    This provides built-in message handling with add_messages reducer.
    """
    # Personal Information
    full_name: NotRequired[str]
    phone: NotRequired[str]
    email: NotRequired[str]
    
    # Employment Information  
    annual_income: NotRequired[int]
    employer: NotRequired[str]
    employment_type: NotRequired[str]
    
    # Property Information
    purchase_price: NotRequired[int]
    property_type: NotRequired[str]
    property_location: NotRequired[str]
    
    # Financial Information
    down_payment: NotRequired[int]
    credit_score: NotRequired[int]
    
    # Application Status
    completion_percentage: NotRequired[float]
    current_phase: NotRequired[str]
    
    # Enhanced fields for production
    application_id: NotRequired[str]
    risk_assessment: NotRequired[str]
    approval_status: NotRequired[str]
