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
    
    # Subgraph interaction tracking
    last_interaction_type: NotRequired[str]  # "react_agent", "data_agent", "info_agent"
    handoff_reason: NotRequired[str]
    
    # ReactAgent subgraph fields
    current_prompts: NotRequired[List[Dict[str, Any]]]
    guidance_steps: NotRequired[List[str]]
    
    # InfoAgent subgraph fields
    topics_discussed: NotRequired[List[str]]
    loan_types_mentioned: NotRequired[List[str]]
    user_expertise_level: NotRequired[str]  # "beginner", "intermediate", "advanced"


# ================================
# AGENT-SPECIFIC STATE SCHEMAS
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
    
    # Required by create_react_agent
    remaining_steps: NotRequired[int]

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
    
    # Required by create_react_agent
    remaining_steps: NotRequired[int]

class PropertyAgentState(MessagesState):
    """
    PropertyAgent specialized state for property analysis and valuation
    """
    # Property details
    property_address: NotRequired[str]
    purchase_price: NotRequired[float]
    property_type: NotRequired[str]
    appraised_value: NotRequired[float]
    
    # Property analysis results
    appraisal_id: NotRequired[str]
    property_value_analysis: NotRequired[Dict[str, Any]]
    compliance_status: NotRequired[str]
    property_risks: NotRequired[Dict[str, Any]]
    property_taxes: NotRequired[Dict[str, Any]]
    
    # Processing metadata
    appraisal_status: NotRequired[str]
    analysis_completion: NotRequired[float]
    property_issues: NotRequired[List[str]]
    
    # Handoff context
    handoff_reason: NotRequired[str]
    
    # Required by create_react_agent
    remaining_steps: NotRequired[int]

class UnderwritingAgentState(MessagesState):
    """
    UnderwritingAgent specialized state for risk analysis and loan decisions
    """
    # Underwriting analysis
    risk_analysis_id: NotRequired[str]
    risk_score: NotRequired[float]
    risk_level: NotRequired[str]
    loan_decision: NotRequired[str]
    
    # Analysis components
    credit_analysis: NotRequired[Dict[str, Any]]
    income_analysis: NotRequired[Dict[str, Any]]
    property_analysis: NotRequired[Dict[str, Any]]
    compliance_check: NotRequired[Dict[str, Any]]
    
    # Decision details
    approved_amount: NotRequired[float]
    interest_rate: NotRequired[float]
    approval_conditions: NotRequired[List[Dict[str, Any]]]
    loan_terms: NotRequired[Dict[str, Any]]
    
    # Processing metadata
    underwriting_stage: NotRequired[str]
    exceptions_noted: NotRequired[List[str]]
    manual_review_required: NotRequired[bool]
    
    # Handoff context
    handoff_reason: NotRequired[str]
    
    # Required by create_react_agent
    remaining_steps: NotRequired[int]

class ComplianceAgentState(MessagesState):
    """
    ComplianceAgent specialized state for regulatory compliance and audit trail
    """
    # Compliance analysis
    compliance_id: NotRequired[str]
    trid_compliance_status: NotRequired[str]
    fair_lending_status: NotRequired[str]
    documentation_status: NotRequired[str]
    regulatory_status: NotRequired[str]
    
    # Compliance details
    trid_analysis: NotRequired[Dict[str, Any]]
    fair_lending_analysis: NotRequired[Dict[str, Any]]
    documentation_review: NotRequired[Dict[str, Any]]
    regulatory_review: NotRequired[Dict[str, Any]]
    audit_trail: NotRequired[Dict[str, Any]]
    
    # Violations and issues
    compliance_violations: NotRequired[List[str]]
    compliance_warnings: NotRequired[List[str]]
    remediation_steps: NotRequired[List[str]]
    
    # Processing metadata
    compliance_score: NotRequired[float]
    review_stage: NotRequired[str]
    examiner_ready: NotRequired[bool]
    
    # Handoff context
    handoff_reason: NotRequired[str]
    
    # Required by create_react_agent
    remaining_steps: NotRequired[int]

class ClosingAgentState(MessagesState):
    """
    ClosingAgent specialized state for closing coordination and finalization
    """
    # Closing coordination
    closing_id: NotRequired[str]
    closing_date: NotRequired[str]
    closing_location: NotRequired[str]
    closing_status: NotRequired[str]
    
    # Document preparation
    document_preparation_status: NotRequired[str]
    required_documents: NotRequired[List[Dict[str, Any]]]
    document_completion_percentage: NotRequired[float]
    
    # Title and escrow
    title_work_status: NotRequired[str]
    escrow_status: NotRequired[str]
    title_issues: NotRequired[List[str]]
    
    # Closing costs
    closing_costs_calculated: NotRequired[bool]
    total_closing_costs: NotRequired[float]
    cash_to_close: NotRequired[float]
    cost_breakdown: NotRequired[Dict[str, Any]]
    
    # Closing meeting
    meeting_scheduled: NotRequired[bool]
    meeting_datetime: NotRequired[str]
    participants: NotRequired[List[str]]
    
    # Post-closing
    post_closing_tasks: NotRequired[List[Dict[str, Any]]]
    loan_delivery_status: NotRequired[str]
    recording_status: NotRequired[str]
    
    # Processing metadata
    closing_stage: NotRequired[str]
    completion_percentage: NotRequired[float]
    critical_deadlines: NotRequired[List[str]]
    
    # Handoff context
    handoff_reason: NotRequired[str]
    
    # Required by create_react_agent
    remaining_steps: NotRequired[int]


class CustomerServiceAgentState(MessagesState):
    """
    CustomerServiceAgent specialized state for post-submission customer support
    """
    # Customer communication tracking
    last_contact_date: NotRequired[str]
    preferred_contact_method: NotRequired[str]
    communication_frequency: NotRequired[str]
    customer_satisfaction_score: NotRequired[float]
    
    # Issue tracking
    active_issues: NotRequired[List[str]]
    resolved_issues: NotRequired[List[str]]
    escalated_issues: NotRequired[List[str]]
    issue_resolution_time: NotRequired[float]
    
    # Document request management
    pending_document_requests: NotRequired[List[str]]
    completed_document_requests: NotRequired[List[str]]
    document_submission_rate: NotRequired[float]
    
    # Status update tracking
    status_update_history: NotRequired[List[Dict[str, Any]]]
    next_scheduled_update: NotRequired[str]
    proactive_communication_sent: NotRequired[bool]
    
    # Support ticket management
    active_tickets: NotRequired[List[str]]
    ticket_priority_level: NotRequired[str]
    escalation_level: NotRequired[int]
    
    # Customer engagement metrics
    response_time: NotRequired[float]
    resolution_rate: NotRequired[float]
    callback_scheduled: NotRequired[bool]
    
    # Processing metadata
    service_stage: NotRequired[str]
    support_completion_percentage: NotRequired[float]
    customer_satisfaction_target: NotRequired[float]
    
    # Handoff context
    handoff_reason: NotRequired[str]
    
    # Required by create_react_agent
    remaining_steps: NotRequired[int]
