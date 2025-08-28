"""
Chat API endpoints for the mortgage processing chat assistant.
These endpoints extend the existing FastAPI app with chat functionality.
"""

import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .chat_models import (
    ChatRequest, ChatResponse, ChatSession, ChatSessionSummary,
    ChatMessageRole, ChatMessageType, ChatSessionStatus, StreamingChatChunk
)
from .chat_session_manager import get_chat_session_manager
from .agent import MortgageProcessingAgent
from .config import AppConfig

logger = logging.getLogger(__name__)

# Create chat router
chat_router = APIRouter(prefix="/chat", tags=["chat"])

# We'll get these from the main app
_config: Optional[AppConfig] = None
_agent: Optional[MortgageProcessingAgent] = None


def set_chat_dependencies(config: AppConfig, agent: MortgageProcessingAgent):
    """Set dependencies from main app"""
    global _config, _agent
    _config = config
    _agent = agent


# ---- Request/Response Models ----

class ChatStartRequest(BaseModel):
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    session_context: Optional[str] = None


class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    include_history: bool = True


class ChatFileUploadRequest(BaseModel):
    session_id: str
    message: str


# ---- Chat Endpoints ----

@chat_router.post("/sessions/start", response_model=ChatSession)
async def start_chat_session(request: ChatStartRequest):
    """Start a new chat session"""
    session_manager = get_chat_session_manager()
    
    session = session_manager.create_session(
        user_id=request.user_id,
        session_name=request.session_name,
        session_context=request.session_context
    )
    
    # Add welcome message
    session_manager.add_message(
        session_id=session.session_id,
        role=ChatMessageRole.ASSISTANT,
        content="Hello! I'm your mortgage processing assistant. I can help you with loan applications, document analysis, and answer questions about the mortgage process. How can I assist you today?",
        message_type=ChatMessageType.TEXT
    )
    
    logger.info(f"Started new chat session: {session.session_id}")
    return session


@chat_router.get("/sessions", response_model=List[ChatSessionSummary])
async def list_chat_sessions(user_id: Optional[str] = None, active_only: bool = True):
    """List chat sessions"""
    session_manager = get_chat_session_manager()
    sessions = session_manager.list_sessions(user_id=user_id, active_only=active_only)
    
    return [
        ChatSessionSummary(
            session_id=s["session_id"],
            session_name=s["session_name"],
            status=s["status"],
            created_at=datetime.fromisoformat(s["created_at"]),
            last_activity=datetime.fromisoformat(s["last_activity"]),
            message_count=s["message_count"],
            has_documents=s["has_documents"],
            current_application_id=s.get("current_application_id")
        )
        for s in sessions
    ]


@chat_router.get("/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Get a specific chat session"""
    session_manager = get_chat_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@chat_router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_chat_message(session_id: str, request: ChatMessageRequest):
    """Send a message to the chat session"""
    if not all([_config, _agent]):
        raise HTTPException(status_code=503, detail="Service not ready")
    
    session_manager = get_chat_session_manager()
    
    # Get or create session
    if request.session_id:
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = session_manager.get_or_create_session(session_id=session_id)
    
    # Add user message
    user_message = session_manager.add_message(
        session_id=session.session_id,
        role=ChatMessageRole.USER,
        content=request.message,
        message_type=ChatMessageType.TEXT
    )
    
    if not user_message:
        raise HTTPException(status_code=500, detail="Failed to add user message")
    
    try:
        # Get conversation history for context
        conversation_history = session_manager.get_conversation_history(
            session_id=session.session_id,
            limit=10 if request.include_history else 1
        )
        
        # Use the actual mortgage processing agent for all queries
        try:
            # Call the agent with the user's message and conversation history
            agent_response = _agent.handle_chat_query(
                user_message=request.message,
                conversation_history=conversation_history,
                session_id=session.session_id
            )
            
            if agent_response.get("processing_successful", False):
                response_content = agent_response["response"]
                processing_result = {
                    "type": agent_response.get("type", "chat_response"),
                    "session_id": agent_response.get("session_id"),
                    "tool_calls_made": agent_response.get("tool_calls_made", [])
                }
            else:
                # Fallback if agent fails
                response_content = agent_response.get("response", "I apologize, but I'm having trouble processing your request right now. Please try again.")
                processing_result = {"type": "error", "error": agent_response.get("error")}
                
        except Exception as e:
            logger.error(f"Error calling agent for chat query: {e}", exc_info=True)
            # Fallback to simple response if agent fails
            response_content = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
            processing_result = {"type": "error", "error": str(e)}
        
        # Add assistant response
        assistant_message = session_manager.add_message(
            session_id=session.session_id,
            role=ChatMessageRole.ASSISTANT,
            content=response_content,
            message_type=ChatMessageType.TEXT,
            processing_result=processing_result
        )
        
        return ChatResponse(
            session_id=session.session_id,
            message_id=assistant_message.message_id,
            response=response_content,
            message_type=ChatMessageType.TEXT,
            processing_result=processing_result
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        
        # Add error message
        error_response = "I apologize, but I encountered an error processing your request. Please try again or contact support if the issue persists."
        session_manager.add_message(
            session_id=session.session_id,
            role=ChatMessageRole.ASSISTANT,
            content=error_response,
            message_type=ChatMessageType.ERROR
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/sessions/{session_id}/upload")
async def upload_and_process_documents(
    session_id: str,
    message: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """Upload documents and process them in chat context"""
    if not all([_config, _agent]):
        raise HTTPException(status_code=503, detail="Service not ready")
    
    session_manager = get_chat_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Add user message with file indication
        session_manager.add_message(
            session_id=session_id,
            role=ChatMessageRole.USER,
            content=f"{message} [Uploaded {len(files)} file(s)]",
            message_type=ChatMessageType.FILE_UPLOAD
        )
        
        # Process files similar to existing /mortgage/process/files endpoint
        documents = []
        for file in files:
            file_content = await file.read()
            
            # Simple text extraction (same as existing logic)
            if file.filename and file.filename.lower().endswith('.txt'):
                extracted_text = file_content.decode('utf-8')
            else:
                extracted_text = f"[File: {file.filename}, Size: {len(file_content)} bytes] - Document processing would extract text here"
            
            documents.append({
                "file_name": file.filename or "unknown",
                "content": extracted_text,
                "metadata": {
                    "mime_type": file.content_type or "application/octet-stream",
                    "file_size": len(file_content),
                    "upload_method": "chat_upload"
                }
            })
        
        # Create a simplified application data for processing
        application_data = {
            "application_id": f"CHAT_{session_id}_{uuid.uuid4().hex[:8].upper()}",
            "customer": {
                "name": "Chat User",
                "age": 35,
                "address": "Provided via chat",
                "ssn": "***-**-****",
                "loan_type": "HomeLoan",
                "authorize_credit_check": True
            }
        }
        
        # Process with existing agent
        processing_result = _agent.process_mortgage_application(
            application_data=application_data,
            documents=documents
        )
        
        # Update session context
        session_manager.update_session_context(
            session_id=session_id,
            application_id=application_data["application_id"],
            metadata={"last_upload": datetime.now().isoformat(), "documents_processed": len(documents)}
        )
        
        # Generate response based on processing results
        response_content = _format_processing_results(processing_result, len(documents))
        
        # Add assistant response
        assistant_message = session_manager.add_message(
            session_id=session_id,
            role=ChatMessageRole.ASSISTANT,
            content=response_content,
            message_type=ChatMessageType.DOCUMENT_ANALYSIS,
            processing_result=processing_result
        )
        
        return ChatResponse(
            session_id=session_id,
            message_id=assistant_message.message_id,
            response=response_content,
            message_type=ChatMessageType.DOCUMENT_ANALYSIS,
            processing_result=processing_result
        )
        
    except Exception as e:
        logger.error(f"Error processing document upload: {e}", exc_info=True)
        
        error_response = f"I encountered an error processing your documents: {str(e)}. Please try again with different files or contact support."
        session_manager.add_message(
            session_id=session_id,
            role=ChatMessageRole.ASSISTANT,
            content=error_response,
            message_type=ChatMessageType.ERROR
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/sessions/{session_id}/history")
async def get_conversation_history(session_id: str, limit: Optional[int] = None):
    """Get conversation history for a session"""
    session_manager = get_chat_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = session_manager.get_conversation_history(session_id, limit)
    return {"session_id": session_id, "messages": history}


@chat_router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session"""
    session_manager = get_chat_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # In a real implementation, you'd delete from database
    # For now, just mark as completed
    session_manager.update_session_status(session_id, ChatSessionStatus.COMPLETED)
    
    return {"message": f"Session {session_id} deleted successfully"}


@chat_router.delete("/sessions/{session_id}/messages")
async def clear_chat_messages(session_id: str):
    """Clear all messages from a chat session but keep the session active"""
    session_manager = get_chat_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Clear all messages from this session
    success = session_manager.clear_session_messages(session_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear messages")
    
    return {"message": f"Messages cleared from session {session_id}"}


# ---- Helper Functions ----

def _generate_helpful_response(user_message: str, conversation_history: List[Dict]) -> str:
    """Generate helpful responses for general mortgage questions"""
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["hello", "hi", "hey", "start"]):
        return "Hello! I'm here to help with your mortgage processing needs. I can analyze documents, answer questions about loan requirements, and guide you through the application process. What would you like to know?"
    
    elif any(word in message_lower for word in ["documents", "required", "need", "paperwork"]):
        return """For a typical home loan, you'll need these documents:

• **Identity**: Driver's license or passport
• **Income**: Recent pay stubs, tax returns (2 years), W-2 forms
• **Assets**: Bank statements (2-3 months), investment account statements
• **Employment**: Employment verification letter
• **Property**: Purchase agreement, property insurance

I can analyze these documents when you upload them. Would you like to start by uploading some documents?"""
    
    elif any(word in message_lower for word in ["qualify", "qualification", "eligible"]):
        return """Mortgage qualification typically depends on:

• **Credit Score**: Usually 620+ for conventional loans
• **Debt-to-Income Ratio**: Generally under 43%
• **Employment History**: Stable 2+ year history
• **Down Payment**: Varies by loan type (3-20%)
• **Assets**: Sufficient for down payment and closing costs

I can help analyze your documents to assess your qualification. Would you like to upload your financial documents for review?"""
    
    elif any(word in message_lower for word in ["rate", "interest", "payment"]):
        return """Interest rates vary based on:

• Credit score and financial profile
• Loan amount and down payment
• Property type and location
• Current market conditions
• Loan term (15-year, 30-year, etc.)

To get accurate rate estimates, I'd need to review your financial documents. Would you like to upload your documents so I can provide more specific guidance?"""
    
    elif any(word in message_lower for word in ["process", "timeline", "how long"]):
        return """The mortgage process typically takes:

• **Application & Initial Review**: 1-3 days
• **Document Processing**: 3-7 days
• **Underwriting**: 7-14 days
• **Final Approval & Closing**: 5-10 days

**Total timeline**: Usually 2-6 weeks

I can help expedite the document processing phase. Upload your documents and I'll analyze them immediately!"""
    
    else:
        return """I'm here to help with your mortgage needs! I can:

• **Analyze Documents**: Upload and I'll review them instantly
• **Answer Questions**: Ask about rates, requirements, or the process
• **Guide Applications**: Help you understand what you need
• **Process Applications**: Handle document review and validation

What specific aspect of your mortgage would you like help with?"""


def _format_processing_results(processing_result: Dict[str, Any], document_count: int) -> str:
    """Format processing results into a user-friendly chat response"""
    
    status = processing_result.get("processing_status", "unknown")
    valid_docs = processing_result.get("valid_documents", 0)
    invalid_docs = processing_result.get("invalid_documents", 0)
    missing_docs = processing_result.get("missing_documents", [])
    next_steps = processing_result.get("next_steps", [])
    
    response = f"📄 **Document Analysis Complete**\n\n"
    response += f"**Processed**: {document_count} documents\n"
    response += f"**Valid**: {valid_docs} documents\n"
    
    if invalid_docs > 0:
        response += f"**Issues Found**: {invalid_docs} documents need attention\n"
    
    if missing_docs:
        response += f"\n**Missing Documents**:\n"
        for doc in missing_docs:
            response += f"• {doc}\n"
    
    if status == "success":
        response += f"\n **Great news!** All documents look good. "
        if processing_result.get("urla_1003_generated"):
            response += "I've generated your URLA 1003 form."
    elif status == "partial":
        response += f"\n⚠️ **Partial Success**: Some documents need attention."
    else:
        response += f"\n **Review Needed**: Please address the issues found."
    
    if next_steps:
        response += f"\n\n**Next Steps**:\n"
        for step in next_steps:
            response += f"• {step}\n"
    
    response += f"\n💬 Ask me any questions about these results or upload additional documents!"
    
    return response
