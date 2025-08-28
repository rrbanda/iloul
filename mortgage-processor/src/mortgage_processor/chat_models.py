"""
Chat-specific models and data structures for the mortgage processing chat assistant.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime
from enum import Enum
from .models import MortgageBaseModel


class ChatMessageRole(str, Enum):
    """Roles for chat messages"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessageType(str, Enum):
    """Types of chat messages"""
    TEXT = "text"
    FILE_UPLOAD = "file_upload"
    DOCUMENT_ANALYSIS = "document_analysis"
    PROCESSING_RESULT = "processing_result"
    ERROR = "error"


class ChatFileAttachment(BaseModel):
    """File attachment in chat messages"""
    model_config = ConfigDict(protected_namespaces=())
    
    file_id: str
    file_name: str
    file_size: int
    mime_type: str
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    processing_status: Literal["pending", "processing", "completed", "error"] = "pending"


class ChatMessage(BaseModel):
    """Individual chat message"""
    model_config = ConfigDict(protected_namespaces=())
    
    message_id: str
    session_id: str
    role: ChatMessageRole
    content: str
    message_type: ChatMessageType = ChatMessageType.TEXT
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Optional fields for rich content
    attachments: List[ChatFileAttachment] = []
    metadata: Dict[str, Any] = {}
    
    # For assistant messages - processing results
    processing_result: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    tool_calls: List[Dict[str, Any]] = []


class ChatSessionStatus(str, Enum):
    """Chat session status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class ChatSession(BaseModel):
    """Chat session with conversation history"""
    model_config = ConfigDict(protected_namespaces=())
    
    session_id: str
    user_id: Optional[str] = None
    session_name: str = "Mortgage Processing Chat"
    status: ChatSessionStatus = ChatSessionStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    
    # Session context
    current_application_id: Optional[str] = None
    customer_context: Dict[str, Any] = {}
    session_metadata: Dict[str, Any] = {}
    
    # Conversation history
    messages: List[ChatMessage] = []
    
    @property
    def session_context(self) -> Optional[str]:
        """Get session context from metadata"""
        return self.session_metadata.get('session_context')
    
    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the session"""
        self.messages.append(message)
        self.updated_at = datetime.now()
        self.last_activity = datetime.now()
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history in format suitable for agent"""
        messages = self.messages[-limit:] if limit else self.messages
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]


class ChatRequest(BaseModel):
    """Request to send a chat message"""
    model_config = ConfigDict(protected_namespaces=())
    
    session_id: Optional[str] = None
    message: str
    message_type: ChatMessageType = ChatMessageType.TEXT
    attachments: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    model_config = ConfigDict(protected_namespaces=())
    
    session_id: str
    message_id: str
    response: str
    message_type: ChatMessageType
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Processing metadata
    processing_time_ms: Optional[int] = None
    tool_calls_made: List[str] = []
    confidence_score: Optional[float] = None
    
    # Attachments or results
    attachments: List[ChatFileAttachment] = []
    processing_result: Optional[Dict[str, Any]] = None


class ChatSessionSummary(BaseModel):
    """Summary of chat session for listing"""
    model_config = ConfigDict(protected_namespaces=())
    
    session_id: str
    session_name: str
    status: ChatSessionStatus
    created_at: datetime
    last_activity: datetime
    message_count: int
    has_documents: bool
    current_application_id: Optional[str] = None


class StreamingChatChunk(BaseModel):
    """Chunk for streaming chat responses"""
    model_config = ConfigDict(protected_namespaces=())
    
    session_id: str
    chunk_id: str
    content: str
    is_final: bool = False
    chunk_type: Literal["text", "tool_call", "result", "error"] = "text"
    metadata: Dict[str, Any] = {}
