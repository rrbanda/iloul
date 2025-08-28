"""
SQLite database setup and models for chat persistence.
Simple and lightweight like tech-explorer approach.
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.types import TypeDecorator, TEXT

Base = declarative_base()


class JSONField(TypeDecorator):
    """Custom JSON field for SQLite compatibility"""
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


class ChatSessionDB(Base):
    """SQLAlchemy model for chat sessions"""
    __tablename__ = "chat_sessions"

    session_id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=True)
    session_name = Column(String(200), nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_activity = Column(DateTime, default=datetime.now)
    
    # Context data
    current_application_id = Column(String(50), nullable=True)
    customer_context = Column(JSONField, default=dict)
    session_metadata = Column(JSONField, default=dict)
    
    # Relationship to messages
    messages = relationship("ChatMessageDB", back_populates="session", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "session_name": self.session_name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "current_application_id": self.current_application_id,
            "customer_context": self.customer_context or {},
            "session_metadata": self.session_metadata or {},
            "messages": [msg.to_dict() for msg in self.messages]
        }


class ChatMessageDB(Base):
    """SQLAlchemy model for chat messages"""
    __tablename__ = "chat_messages"

    message_id = Column(String(50), primary_key=True)
    session_id = Column(String(50), ForeignKey("chat_sessions.session_id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String(30), default="text")  # text, file_upload, document_analysis, etc.
    timestamp = Column(DateTime, default=datetime.now)
    
    # Optional fields
    attachments = Column(JSONField, default=list)
    message_metadata = Column(JSONField, default=dict)
    processing_result = Column(JSONField, nullable=True)
    confidence_score = Column(String(10), nullable=True)  # Store as string to avoid float precision issues
    tool_calls = Column(JSONField, default=list)
    
    # Relationship to session
    session = relationship("ChatSessionDB", back_populates="messages")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp.isoformat(),
            "attachments": self.attachments or [],
            "metadata": self.message_metadata or {},
            "processing_result": self.processing_result,
            "confidence_score": float(self.confidence_score) if self.confidence_score else None,
            "tool_calls": self.tool_calls or []
        }


class DatabaseManager:
    """Simple database manager for SQLite"""
    
    def __init__(self, database_path: str = "data/chat_sessions.db"):
        self.database_path = database_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        
        # Create engine
        self.engine = create_engine(f"sqlite:///{database_path}", echo=False)
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self.create_tables()
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()


# Global database manager
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get or create database manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


@contextmanager
def get_db_session():
    """Get database session as context manager"""
    session = get_database_manager().get_session()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
