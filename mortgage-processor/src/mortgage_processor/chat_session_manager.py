"""
Chat session management for mortgage processing chat assistant.
Handles session persistence, conversation history, and context management using SQLite.
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .chat_models import (
    ChatSession, ChatMessage, ChatMessageRole, ChatMessageType, 
    ChatSessionStatus, ChatFileAttachment
)
from .database import (
    get_db_session, ChatSessionDB, ChatMessageDB
)

logger = logging.getLogger(__name__)


class ChatSessionManager:
    """
    Manages chat sessions with persistent conversation history using SQLite.
    Professional database persistence like tech-explorer approach.
    """
    
    def __init__(self):
        self._session_timeout_hours = 24
        logger.info("ChatSessionManager initialized with SQLite persistence")
    
    def create_session(
        self, 
        user_id: Optional[str] = None,
        session_name: Optional[str] = None,
        session_context: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session"""
        session_id = f"chat_{uuid.uuid4().hex[:12]}"
        
        try:
            with get_db_session() as db:
                # Create session metadata
                metadata = {}
                if session_context:
                    metadata['session_context'] = session_context
                
                # Create database record
                db_session = ChatSessionDB(
                    session_id=session_id,
                    user_id=user_id,
                    session_name=session_name or f"Mortgage Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    session_metadata=metadata
                )
                db.add(db_session)
                db.commit()
                db.refresh(db_session)
                
                # Convert to Pydantic model
                session_data = db_session.to_dict()
                session = ChatSession(**session_data)
                
                logger.info(f"Created new chat session: {session_id}")
                return session
        except SQLAlchemyError as e:
            logger.error(f"Database error creating session: {e}")
            raise RuntimeError(f"Failed to create session: {e}")
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve an existing chat session"""
        try:
            with get_db_session() as db:
                # Query session with messages
                db_session = db.query(ChatSessionDB).filter(
                    ChatSessionDB.session_id == session_id
                ).first()
                
                if db_session:
                    # Update last activity
                    db_session.last_activity = datetime.now()
                    db.commit()
                    
                    # Convert to Pydantic model
                    session_data = db_session.to_dict()
                    session = ChatSession(**session_data)
                    
                    logger.debug(f"Retrieved session: {session_id}")
                    return session
                else:
                    logger.warning(f"Session not found: {session_id}")
                    return None
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving session: {e}")
            return None
    
    def get_or_create_session(
        self, 
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ChatSession:
        """Get existing session or create new one"""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        
        # Create new session if not found or not provided
        return self.create_session(user_id=user_id)
    
    def add_message(
        self, 
        session_id: str, 
        role: ChatMessageRole,
        content: str,
        message_type: ChatMessageType = ChatMessageType.TEXT,
        attachments: List[ChatFileAttachment] = None,
        metadata: Dict[str, Any] = None,
        processing_result: Optional[Dict[str, Any]] = None
    ) -> Optional[ChatMessage]:
        """Add a message to the session"""
        try:
            with get_db_session() as db:
                # Check if session exists
                db_session = db.query(ChatSessionDB).filter(
                    ChatSessionDB.session_id == session_id
                ).first()
                
                if not db_session:
                    logger.error(f"Cannot add message - session not found: {session_id}")
                    return None
                
                # Create message
                message_id = f"msg_{uuid.uuid4().hex[:8]}"
                db_message = ChatMessageDB(
                    message_id=message_id,
                    session_id=session_id,
                    role=role.value,
                    content=content,
                    message_type=message_type.value,
                    attachments=[att.dict() if hasattr(att, 'dict') else att for att in (attachments or [])],
                    message_metadata=metadata or {},
                    processing_result=processing_result
                )
                
                db.add(db_message)
                
                # Update session last activity
                db_session.last_activity = datetime.now()
                db_session.updated_at = datetime.now()
                
                db.commit()
                db.refresh(db_message)
                
                # Convert to Pydantic model
                message_data = db_message.to_dict()
                message = ChatMessage(**message_data)
                
                logger.debug(f"Added {role.value} message to session {session_id}")
                return message
        except SQLAlchemyError as e:
            logger.error(f"Database error adding message: {e}")
            return None
    
    def get_conversation_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None,
        include_system: bool = False
    ) -> List[Dict[str, Any]]:
        """Get conversation history for agent context"""
        try:
            with get_db_session() as db:
                # Query messages for session
                query = db.query(ChatMessageDB).filter(
                    ChatMessageDB.session_id == session_id
                ).order_by(ChatMessageDB.timestamp)
                
                if not include_system:
                    query = query.filter(ChatMessageDB.role != "system")
                
                if limit:
                    query = query.limit(limit)
                
                messages = query.all()
                
                return [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "message_type": msg.message_type,
                        "has_attachments": len(msg.attachments or []) > 0
                    }
                    for msg in messages
                ]
        except SQLAlchemyError as e:
            logger.error(f"Database error getting conversation history: {e}")
            return []
    
    def update_session_context(
        self, 
        session_id: str, 
        application_id: Optional[str] = None,
        customer_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update session context information"""
        try:
            with get_db_session() as db:
                db_session = db.query(ChatSessionDB).filter(
                    ChatSessionDB.session_id == session_id
                ).first()
                
                if not db_session:
                    return False
                
                if application_id:
                    db_session.current_application_id = application_id
                
                if customer_context:
                    current_context = db_session.customer_context or {}
                    current_context.update(customer_context)
                    db_session.customer_context = current_context
                
                if metadata:
                    current_metadata = db_session.session_metadata or {}
                    current_metadata.update(metadata)
                    db_session.session_metadata = current_metadata
                
                db_session.updated_at = datetime.now()
                db.commit()
                
                logger.debug(f"Updated context for session {session_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database error updating session context: {e}")
            return False
    
    def list_sessions(
        self, 
        user_id: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """List sessions for a user or all sessions"""
        try:
            with get_db_session() as db:
                # Build query
                query = db.query(ChatSessionDB)
                
                if user_id:
                    query = query.filter(ChatSessionDB.user_id == user_id)
                
                if active_only:
                    query = query.filter(ChatSessionDB.status == "active")
                
                # Sort by last activity (most recent first)
                sessions = query.order_by(ChatSessionDB.last_activity.desc()).all()
                
                return [
                    {
                        "session_id": s.session_id,
                        "session_name": s.session_name,
                        "status": s.status,
                        "created_at": s.created_at.isoformat(),
                        "last_activity": s.last_activity.isoformat(),
                        "message_count": len(s.messages),
                        "has_documents": any(msg.attachments for msg in s.messages if msg.attachments),
                        "current_application_id": s.current_application_id
                    }
                    for s in sessions
                ]
        except SQLAlchemyError as e:
            logger.error(f"Database error listing sessions: {e}")
            return []
    
    def update_session_status(
        self, 
        session_id: str, 
        status: ChatSessionStatus
    ) -> bool:
        """Update session status"""
        try:
            with get_db_session() as db:
                db_session = db.query(ChatSessionDB).filter(
                    ChatSessionDB.session_id == session_id
                ).first()
                
                if not db_session:
                    return False
                
                db_session.status = status.value
                db_session.updated_at = datetime.now()
                db.commit()
                
                logger.info(f"Updated session {session_id} status to {status.value}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database error updating session status: {e}")
            return False
    
    def clear_session_messages(self, session_id: str) -> bool:
        """Clear all messages from a session but keep the session active"""
        try:
            with get_db_session() as db:
                # Check if session exists
                db_session = db.query(ChatSessionDB).filter(
                    ChatSessionDB.session_id == session_id
                ).first()
                
                if not db_session:
                    logger.warning(f"Session {session_id} not found for message clearing")
                    return False
                
                # Delete all messages for this session
                deleted_count = db.query(ChatMessageDB).filter(
                    ChatMessageDB.session_id == session_id
                ).delete()
                
                # Update session timestamp
                db_session.updated_at = datetime.now()
                db_session.last_activity = datetime.now()
                
                db.commit()
                
                logger.info(f"Cleared {deleted_count} messages from session {session_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Database error clearing session messages: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        try:
            with get_db_session() as db:
                cutoff_time = datetime.now() - timedelta(hours=self._session_timeout_hours)
                
                # Find expired sessions
                expired_sessions = db.query(ChatSessionDB).filter(
                    ChatSessionDB.last_activity < cutoff_time,
                    ChatSessionDB.status != "active"
                ).all()
                
                count = len(expired_sessions)
                
                # Delete expired sessions (messages will be cascade deleted)
                for session in expired_sessions:
                    logger.info(f"Cleaning up expired session: {session.session_id}")
                    db.delete(session)
                
                db.commit()
                
                logger.info(f"Cleaned up {count} expired sessions")
                return count
        except SQLAlchemyError as e:
            logger.error(f"Database error cleaning up sessions: {e}")
            return 0
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a session"""
        try:
            with get_db_session() as db:
                db_session = db.query(ChatSessionDB).filter(
                    ChatSessionDB.session_id == session_id
                ).first()
                
                if not db_session:
                    return None
                
                # Count messages by type
                user_count = db.query(ChatMessageDB).filter(
                    ChatMessageDB.session_id == session_id,
                    ChatMessageDB.role == "user"
                ).count()
                
                assistant_count = db.query(ChatMessageDB).filter(
                    ChatMessageDB.session_id == session_id,
                    ChatMessageDB.role == "assistant"
                ).count()
                
                total_count = len(db_session.messages)
                
                # Calculate session duration
                duration_minutes = (datetime.now() - db_session.created_at).total_seconds() / 60
                
                # Count attachments
                total_attachments = sum(
                    len(msg.attachments or []) for msg in db_session.messages
                )
                
                return {
                    "session_id": session_id,
                    "total_messages": total_count,
                    "user_messages": user_count,
                    "assistant_messages": assistant_count,
                    "session_duration_minutes": duration_minutes,
                    "has_application": db_session.current_application_id is not None,
                    "total_attachments": total_attachments,
                    "last_activity": db_session.last_activity.isoformat(),
                    "status": db_session.status
                }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting session stats: {e}")
            return None
    
    def export_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export conversation history for download or backup"""
        try:
            with get_db_session() as db:
                db_session = db.query(ChatSessionDB).filter(
                    ChatSessionDB.session_id == session_id
                ).first()
                
                if not db_session:
                    return None
                
                return {
                    "session_info": {
                        "session_id": db_session.session_id,
                        "session_name": db_session.session_name,
                        "created_at": db_session.created_at.isoformat(),
                        "exported_at": datetime.now().isoformat(),
                        "status": db_session.status
                    },
                    "conversation": [
                        {
                            "message_id": msg.message_id,
                            "timestamp": msg.timestamp.isoformat(),
                            "role": msg.role,
                            "content": msg.content,
                            "message_type": msg.message_type,
                            "attachments": [
                                {
                                    "file_name": att.get("file_name", ""),
                                    "file_size": att.get("file_size", 0),
                                    "mime_type": att.get("mime_type", "")
                                }
                                for att in (msg.attachments or [])
                            ],
                            "metadata": msg.message_metadata or {}
                        }
                        for msg in db_session.messages
                    ],
                    "context": {
                        "current_application_id": db_session.current_application_id,
                        "customer_context": db_session.customer_context or {},
                        "session_metadata": db_session.session_metadata or {}
                    }
                }
        except SQLAlchemyError as e:
            logger.error(f"Database error exporting conversation: {e}")
            return None


# Global session manager instance
chat_session_manager = ChatSessionManager()


def get_chat_session_manager() -> ChatSessionManager:
    """Get the global chat session manager instance"""
    return chat_session_manager
