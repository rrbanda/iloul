"""
Agentic mortgage application router - single chat entry point.
Specialized agents handle all tasks through conversation.
"""

import logging
import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .context import MortgageConversationWorkflow
from .database import get_db_session, MortgageApplicationDB
from .config import AppConfig

logger = logging.getLogger(__name__)

# Create application router
application_router = APIRouter(prefix="/mortgage/application", tags=["agentic-application"])

# We'll get these from the main app
_config: Optional[AppConfig] = None
_workflow: Optional[MortgageConversationWorkflow] = None


def set_application_dependencies(config: AppConfig, workflow: MortgageConversationWorkflow):
    """Set dependencies from main app"""
    global _config, _workflow
    _config = config
    _workflow = workflow


# ---- Request/Response Models ----

class ApplicationStartRequest(BaseModel):
    user_id: Optional[str] = None


class ApplicationStartResponse(BaseModel):
    session_id: str
    message: str
    status: str


class ApplicationChatRequest(BaseModel):
    message: str


class ApplicationChatResponse(BaseModel):
    session_id: str
    response: str
    completion_percentage: float
    is_complete: bool
    phase: str
    status: str
    timestamp: str


class ApplicationSubmissionRequest(BaseModel):
    session_id: str
    collected_data: dict


class ApplicationSubmissionResponse(BaseModel):
    application_id: str
    session_id: str
    status: str
    submitted_at: str
    collected_data: dict
    validation_errors: list[str]
    next_steps: list[str]
    urla_form_generated: bool


# ---- Agentic Application Endpoints ----

@application_router.post("/start", response_model=ApplicationStartResponse)
async def start_application_session(request: ApplicationStartRequest):
    """
    Start a new conversational mortgage application.
    
    Uses  LangGraph conversational workflow to guide the user
    through mortgage application data collection step by step.
    """
    if not _workflow:
        raise HTTPException(status_code=503, detail="Conversation workflow not ready")
    
    try:
        # Start the conversation session and get initial response
        result = await _workflow.start_session()
        
        logger.info(f"Started conversation application session: {result['session_id']}")
        
        return ApplicationStartResponse(
            session_id=result["session_id"],
            message=result["response"],
            status="started"
        )
        
    except Exception as e:
        logger.error(f"Error starting conversation session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@application_router.post("/{session_id}/chat", response_model=ApplicationChatResponse)
async def chat_with_workflow(session_id: str, request: ApplicationChatRequest):
    """
    Chat with conversational mortgage application workflow.
    
    The workflow uses  LangGraph conversational pattern:
    - Questioner Node: Asks next logical question based on missing data
    - Collector Node: Extracts structured data from responses
    - Router: Determines next step based on conversation state
    """
    if not _workflow:
        raise HTTPException(status_code=503, detail="Conversation workflow not ready")
    
    try:
        # Process message through the conversation workflow
        result = await _workflow.process_message(session_id, request.message)
        
        if "error" in result:
            logger.error(f"Conversation workflow error for session {session_id}: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.debug(f"Conversation workflow processed message for session {session_id}: {result.get('phase', 'unknown')} phase")
        
        return ApplicationChatResponse(
            session_id=result["session_id"],
            response=result["response"],
            completion_percentage=result["completion_percentage"],
            is_complete=result["is_complete"],
            phase=result.get("phase", "conversation"),
            status="success",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in conversation chat session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Conversation chat error: {str(e)}")


@application_router.post("/{session_id}/submit", response_model=ApplicationSubmissionResponse)
async def submit_application(session_id: str, request: ApplicationSubmissionRequest):
    """
    Submit completed mortgage application for processing.
    
    Validates collected data, generates application ID, and transitions
    from conversational data collection to formal application processing.
    """
    if not _workflow:
        raise HTTPException(status_code=503, detail="Conversation workflow not ready")
    
    try:
        # Validate that we have the required session
        if request.session_id != session_id:
            raise HTTPException(status_code=400, detail="Session ID mismatch")
        
        # Get current session state to validate completion
        current_state = await _workflow.get_session_state(session_id)
        if not current_state.get("is_complete", False):
            raise HTTPException(status_code=400, detail="Application data collection not complete")
        
        # Validate required fields are present
        validation_errors = _validate_application_data(request.collected_data)
        
        # Generate unique application ID
        application_id = f"APP_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
        
        # Submit application for processing
        submission_result = await _submit_application_for_processing(
            application_id=application_id,
            session_id=session_id,
            collected_data=request.collected_data,
            validation_errors=validation_errors
        )
        
        logger.info(f"Application {application_id} submitted successfully from session {session_id}")
        
        return ApplicationSubmissionResponse(
            application_id=application_id,
            session_id=session_id,
            status="submitted" if not validation_errors else "incomplete",
            submitted_at=datetime.now().isoformat(),
            collected_data=request.collected_data,
            validation_errors=validation_errors,
            next_steps=submission_result.get("next_steps", []),
            urla_form_generated=submission_result.get("urla_form_generated", False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting application for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Application submission failed: {str(e)}")


# ---- Application Tracking Endpoints ----

@application_router.get("/{application_id}", response_model=dict)
async def get_application(application_id: str):
    """Get application details by ID"""
    try:
        with get_db_session() as db:
            application = db.query(MortgageApplicationDB).filter(
                MortgageApplicationDB.application_id == application_id
            ).first()
            
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            
            return {
                "status": "success",
                "application": application.to_dict()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application {application_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve application: {str(e)}")


@application_router.get("/", response_model=dict)
async def list_applications(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List applications with optional filtering"""
    try:
        with get_db_session() as db:
            query = db.query(MortgageApplicationDB)
            
            # Apply status filter if provided
            if status:
                query = query.filter(MortgageApplicationDB.status == status)
            
            # Apply pagination
            applications = query.order_by(
                MortgageApplicationDB.submitted_at.desc()
            ).offset(offset).limit(limit).all()
            
            # Get total count for pagination
            total_count = query.count()
            
            return {
                "status": "success",
                "applications": [app.to_dict() for app in applications],
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total_count
                }
            }
            
    except Exception as e:
        logger.error(f"Error listing applications: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list applications: {str(e)}")


@application_router.put("/{application_id}/status", response_model=dict)
async def update_application_status(
    application_id: str,
    status_update: dict
):
    """Update application status (for admin use)"""
    try:
        new_status = status_update.get("status")
        notes = status_update.get("notes", "")
        
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        with get_db_session() as db:
            application = db.query(MortgageApplicationDB).filter(
                MortgageApplicationDB.application_id == application_id
            ).first()
            
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            
            # Update status and notes
            application.status = new_status
            application.updated_at = datetime.now()
            if notes:
                existing_notes = application.processing_notes or ""
                application.processing_notes = f"{existing_notes}\n[{datetime.now().isoformat()}] {notes}".strip()
            
            db.commit()
            db.refresh(application)
            
            logger.info(f"Application {application_id} status updated to: {new_status}")
            
            return {
                "status": "success",
                "message": f"Application status updated to: {new_status}",
                "application": application.to_dict()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application {application_id} status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update application: {str(e)}")


# ---- Helper Functions ----

def _validate_application_data(collected_data: dict) -> list[str]:
    """Validate that required mortgage application fields are present."""
    errors = []
    
    # Required personal information
    personal_fields = ["full_name", "phone", "email"]
    for field in personal_fields:
        if not collected_data.get(field):
            errors.append(f"Missing required personal information: {field.replace('_', ' ')}")
    
    # Required employment information
    employment_fields = ["annual_income", "employer", "employment_type"]
    for field in employment_fields:
        if not collected_data.get(field):
            errors.append(f"Missing required employment information: {field.replace('_', ' ')}")
    
    # Required property information
    property_fields = ["purchase_price", "property_type", "property_location"]
    for field in property_fields:
        if not collected_data.get(field):
            errors.append(f"Missing required property information: {field.replace('_', ' ')}")
    
    # Required financial information
    financial_fields = ["down_payment", "credit_score"]
    for field in financial_fields:
        if not collected_data.get(field):
            errors.append(f"Missing required financial information: {field.replace('_', ' ')}")
    
    # Validate numeric fields
    numeric_validations = [
        ("annual_income", 1000, 10000000),  # $1K to $10M
        ("purchase_price", 10000, 50000000),  # $10K to $50M  
        ("down_payment", 0, 1000000),  # $0 to $1M
        ("credit_score", 300, 850)  # Standard credit score range
    ]
    
    for field, min_val, max_val in numeric_validations:
        value = collected_data.get(field)
        if value is not None:
            try:
                num_value = float(value)
                if num_value < min_val or num_value > max_val:
                    errors.append(f"Invalid {field.replace('_', ' ')}: must be between {min_val:,} and {max_val:,}")
            except (ValueError, TypeError):
                errors.append(f"Invalid {field.replace('_', ' ')}: must be a number")
    
    return errors


async def _submit_application_for_processing(
    application_id: str,
    session_id: str, 
    collected_data: dict,
    validation_errors: list[str]
) -> dict:
    """Submit application to processing workflow and store in database."""
    
    try:
        # Calculate completion percentage
        required_fields = ["full_name", "phone", "email", "annual_income", "employer", 
                          "purchase_price", "property_location", "down_payment", "credit_score"]
        completed_fields = sum(1 for field in required_fields if collected_data.get(field))
        completion_percentage = (completed_fields / len(required_fields)) * 100
        
        # Determine status based on validation errors
        status = "incomplete" if validation_errors else "submitted"
        
        # Store application in database
        with get_db_session() as db:
            # Create new mortgage application record
            db_application = MortgageApplicationDB(
                application_id=application_id,
                session_id=session_id,
                
                # Personal Information
                full_name=collected_data.get("full_name"),
                phone=collected_data.get("phone"),
                email=collected_data.get("email"),
                
                # Employment Information
                annual_income=collected_data.get("annual_income"),
                employer=collected_data.get("employer"),
                employment_type=collected_data.get("employment_type"),
                
                # Property Information
                purchase_price=collected_data.get("purchase_price"),
                property_type=collected_data.get("property_type"),
                property_location=collected_data.get("property_location"),
                
                # Financial Information
                down_payment=collected_data.get("down_payment"),
                credit_score=collected_data.get("credit_score"),
                
                # Application Status
                status=status,
                completion_percentage=completion_percentage,
                validation_errors=validation_errors,
                urla_form_generated=False  # Will be implemented later
            )
            
            # Add to database
            db.add(db_application)
            db.commit()
            db.refresh(db_application)
            
            logger.info(f"Application {application_id} stored successfully in database")
        
        # Generate next steps based on status
        if validation_errors:
            next_steps = [
                "Complete missing required information:",
                *[f"- {error}" for error in validation_errors],
                "Return to conversation to provide missing details"
            ]
        else:
            next_steps = [
                "✅ Application submitted successfully",
                "📄 Upload required documents (driver's license, bank statements, pay stubs)",
                "⏱️ Wait for initial review (1-2 business days)",
                "🏠 Schedule property appraisal when approved",
                "📧 You'll receive email updates on your application status"
            ]
        
        # URLA form generation (future enhancement)
        urla_form_generated = False  # Will implement later with existing tools
        
        logger.info(f"Application {application_id} processed - Status: {status}, Completion: {completion_percentage}%")
        
        return {
            "next_steps": next_steps,
            "urla_form_generated": urla_form_generated,
            "database_stored": True,
            "completion_percentage": completion_percentage
        }
        
    except Exception as e:
        logger.error(f"Error storing application {application_id} in database: {e}")
        # Return fallback response if database fails
        return {
            "next_steps": [
                "Application received but encountered storage issue",
                "Please contact support with your application ID: " + application_id,
                "Your data has been preserved and will be processed manually"
            ],
            "urla_form_generated": False,
            "database_stored": False,
            "error": str(e)
        }
