"""
Application Data Schema

Defines the data structures for agentic application storage and retrieval.
These schemas ensure consistent data handling across all agent tools.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MortgageApplicationData(BaseModel):
    """Complete mortgage application data structure for Neo4j storage."""
    
    # Application Metadata
    application_id: str = Field(..., description="Unique application identifier")
    received_date: str = Field(..., description="Application received timestamp")
    current_status: str = Field(default="RECEIVED", description="Current application status")
    
    # Personal Information
    first_name: str = Field(..., description="Applicant's first name")
    last_name: str = Field(..., description="Applicant's last name") 
    ssn: str = Field(..., description="Social Security Number")
    date_of_birth: str = Field(..., description="Date of birth")
    phone: str = Field(..., description="Phone number")
    email: str = Field(..., description="Email address")
    
    # Address Information
    current_street: str = Field(..., description="Current street address")
    current_city: str = Field(..., description="Current city")
    current_state: str = Field(..., description="Current state")
    current_zip: str = Field(..., description="Current ZIP code")
    years_at_address: float = Field(..., description="Years at current address")
    
    # Employment Information
    employer_name: str = Field(..., description="Current employer name")
    job_title: str = Field(..., description="Job title/position")
    years_employed: float = Field(..., description="Years with current employer")
    monthly_gross_income: float = Field(..., description="Monthly gross income")
    employment_type: str = Field(..., description="Employment type")
    
    # Loan Information
    loan_purpose: str = Field(..., description="Loan purpose")
    loan_amount: float = Field(..., description="Requested loan amount")
    property_address: str = Field(..., description="Property address")
    property_value: Optional[float] = Field(None, description="Property value estimate")
    property_type: str = Field(..., description="Property type")
    occupancy_type: str = Field(..., description="Occupancy type")
    
    # Financial Information
    credit_score: Optional[int] = Field(None, description="Credit score")
    monthly_debts: Optional[float] = Field(None, description="Monthly debt payments")
    liquid_assets: Optional[float] = Field(None, description="Liquid assets")
    down_payment: Optional[float] = Field(None, description="Down payment amount")
    
    # Special Programs
    first_time_buyer: bool = Field(default=False, description="First-time buyer flag")
    military_service: bool = Field(default=False, description="Military service flag")
    rural_property: bool = Field(default=False, description="Rural property flag")
    
    # Processing Data
    validation_status: str = Field(default="PENDING", description="Validation status")
    completion_percentage: float = Field(default=0.0, description="Completion percentage")
    next_agent: Optional[str] = Field(None, description="Next agent in workflow")
    workflow_notes: Optional[str] = Field(None, description="Workflow processing notes")


class ApplicationStatusUpdate(BaseModel):
    """Application status update for agentic tracking."""
    
    application_id: str = Field(..., description="Application ID to update")
    new_status: str = Field(..., description="New status to set")
    agent_name: str = Field(..., description="Agent making the update")
    status_notes: Optional[str] = Field(None, description="Status change notes")
    completion_percentage: Optional[float] = Field(None, description="Completion percentage")
    milestone_reached: Optional[str] = Field(None, description="Milestone reached")
    next_agent: Optional[str] = Field(None, description="Next agent in workflow")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ApplicationRetrievalResult(BaseModel):
    """Result of application data retrieval for agents."""
    
    found: bool = Field(..., description="Whether application was found")
    application_data: Optional[MortgageApplicationData] = Field(None, description="Application data if found")
    status_history: List[Dict[str, Any]] = Field(default_factory=list, description="Status change history")
    current_agent: Optional[str] = Field(None, description="Current agent handling application")
    next_steps: Optional[str] = Field(None, description="Recommended next steps")
    error_message: Optional[str] = Field(None, description="Error message if retrieval failed")


class AgenticApplicationQuery(BaseModel):
    """Query parameters for agentic application lookup."""
    
    application_id: Optional[str] = Field(None, description="Specific application ID")
    applicant_name: Optional[str] = Field(None, description="Applicant name for search")
    ssn_last_four: Optional[str] = Field(None, description="Last four digits of SSN")
    phone: Optional[str] = Field(None, description="Phone number for search")
    status: Optional[str] = Field(None, description="Filter by status")
    date_range: Optional[str] = Field(None, description="Date range filter")
    agent_name: Optional[str] = Field(None, description="Filter by agent")


class WorkflowTransition(BaseModel):
    """Workflow transition data for agent handoffs."""
    
    from_agent: str = Field(..., description="Agent passing the application")
    to_agent: str = Field(..., description="Agent receiving the application")
    application_id: str = Field(..., description="Application being transferred")
    transition_reason: str = Field(..., description="Reason for transition")
    transition_notes: Optional[str] = Field(None, description="Additional transition notes")
    completion_status: str = Field(..., description="Completion status of from_agent work")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
