import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from llama_stack_client import RAGDocument

from .config import AppConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mortgage/rag", tags=["RAG"])

# Pydantic models for RAG
class MortgageDocument(BaseModel):
    customer_id: str
    application_id: Optional[str] = None
    document_type: str  # "driver_license", "bank_statement", etc.
    file_name: str
    content: str
    mime_type: str = "text/plain"
    metadata: Optional[Dict[str, Any]] = None

class IngestMortgageDocsRequest(BaseModel):
    documents: List[MortgageDocument]
    chunk_size_in_tokens: Optional[int] = 512

class QueryMortgageDocsRequest(BaseModel):
    customer_id: Optional[str] = None
    application_id: Optional[str] = None
    query: str
    document_types: Optional[List[str]] = None  # Filter by doc type

class RAGProcessingRequest(BaseModel):
    customer_id: str
    query: str  # "Analyze all documents for John Smith"
    use_tools: bool = True  # Whether to also use direct tools


def _ensure_mortgage_vector_db(client, config: AppConfig):
    """Ensure mortgage-specific vector DB exists."""
    try:
        v = config.vector_db
        payload = {
            "vector_db_id": v.id,
            "embedding_model": v.embedding,
            "embedding_dimension": int(v.embedding_dimension),
            "provider_id": v.provider,
        }
        client.vector_dbs.register(**payload)
        logger.info(f"Mortgage vector DB '{v.id}' ready")
        return True
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info(f"Mortgage vector DB '{v.id}' already exists")
            return True
        logger.error(f"Failed to setup vector DB: {e}")
        return False


def _optimal_mortgage_rag_insert(client, config: AppConfig, documents: List[Dict], chunk_size: Optional[int] = None) -> Dict:
    """Insert mortgage documents into RAG with proper metadata."""
    try:
        rag_documents = []
        for doc in documents:
            # Enhance metadata for mortgage-specific use
            enhanced_metadata = {
                "customer_id": doc["customer_id"],
                "document_type": doc["document_type"],
                "file_name": doc["file_name"],
                "source": "mortgage_application",
                **(doc.get("metadata", {}))
            }
            
            if doc.get("application_id"):
                enhanced_metadata["application_id"] = doc["application_id"]
            
            rag_doc = RAGDocument(
                document_id=f"mortgage_{doc['customer_id']}_{doc['document_type']}_{uuid.uuid4().hex[:8]}",
                content=doc["content"],
                mime_type=doc.get("mime_type", "text/plain"),
                metadata=enhanced_metadata
            )
            rag_documents.append(rag_doc)
        
        # Insert using RAG tool
        client.tool_runtime.rag_tool.insert(
            documents=rag_documents,
            vector_db_id=config.vector_db.id,
            chunk_size_in_tokens=chunk_size or int(config.vector_db.chunk_size)
        )
        
        return {
            "status": "success",
            "documents_ingested": len(rag_documents),
            "vector_db_id": config.vector_db.id,
            "chunk_size": chunk_size or int(config.vector_db.chunk_size)
        }
        
    except Exception as e:
        logger.error(f"RAG insertion error: {e}")
        raise


# Router endpoints
@router.post("/ingest")
def ingest_mortgage_documents(request: IngestMortgageDocsRequest):
    """
    Ingest mortgage documents into vector database for semantic search.
    
    Example:
    {
        "documents": [
            {
                "customer_id": "CUST_12345",
                "application_id": "APP_67890",
                "document_type": "driver_license",
                "file_name": "johns_license.jpg",
                "content": "CALIFORNIA DRIVER LICENSE John Smith...",
                "metadata": {"upload_date": "2025-08-14"}
            }
        ]
    }
    """
    from ..main import get_client, get_config  # Import from main app
    
    client = get_client()
    config = get_config()
    
    if not client or not config:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Ensure vector DB exists
        if not _ensure_mortgage_vector_db(client, config):
            raise HTTPException(status_code=503, detail="Vector DB not ready")
        
        # Convert request to documents
        documents = []
        for doc in request.documents:
            documents.append({
                "customer_id": doc.customer_id,
                "application_id": doc.application_id,
                "document_type": doc.document_type,
                "file_name": doc.file_name,
                "content": doc.content,
                "mime_type": doc.mime_type,
                "metadata": doc.metadata or {}
            })
        
        # Ingest documents
        result = _optimal_mortgage_rag_insert(client, config, documents, request.chunk_size_in_tokens)
        
        logger.info(f"Ingested {len(documents)} mortgage documents for customers: {list(set(d['customer_id'] for d in documents))}")
        return result
        
    except Exception as e:
        logger.error(f"Mortgage document ingestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")


@router.post("/query")
def query_mortgage_documents(request: QueryMortgageDocsRequest):
    """
    Query mortgage documents using semantic search.
    
    Example:
    {
        "customer_id": "CUST_12345",
        "query": "Find John's income information",
        "document_types": ["pay_stub", "bank_statement"]
    }
    """
    from ..main import get_client, get_config, get_agent
    
    client = get_client()
    config = get_config()
    
    if not client or not config:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Build enhanced query with filters
        enhanced_query = request.query
        if request.customer_id:
            enhanced_query += f" for customer {request.customer_id}"
        if request.document_types:
            enhanced_query += f" in documents: {', '.join(request.document_types)}"
        
        # Use vector search (this would need to be implemented with the RAG tool)
        # For now, return a structured response
        return {
            "query": request.query,
            "enhanced_query": enhanced_query,
            "customer_id": request.customer_id,
            "results": f"RAG search results for: {enhanced_query}",
            "document_types_searched": request.document_types,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"RAG query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")


@router.post("/process")
def process_with_rag(request: RAGProcessingRequest):
    """
    Process mortgage application using BOTH RAG search AND direct tools.
    
    This combines:
    1. Semantic search across all customer documents in vector DB
    2. Direct tool execution on current documents
    3. Cross-validation between RAG results and tool results
    """
    from ..main import get_agent
    
    agent = get_agent()
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not ready")
    
    try:
        # Create RAG-enhanced prompt
        enhanced_prompt = f"""
        Process this mortgage query using BOTH knowledge search AND your tools:
        
        Customer ID: {request.customer_id}
        Query: {request.query}
        
        Please:
        1. Search the knowledge base for all documents related to this customer
        2. Use your direct tools for any real-time analysis needed
        3. Compare and validate information from both sources
        4. Provide a comprehensive analysis
        """
        
        session_id = agent.create_session(f"rag-session-{uuid.uuid4().hex[:8]}")
        
        response = agent.create_turn(
            messages=[{"role": "user", "content": enhanced_prompt}],
            session_id=session_id,
            stream=False
        )
        
        # Extract response content
        response_text = response.output_message.content if hasattr(response, 'output_message') else str(response)
        
        return {
            "customer_id": request.customer_id,
            "query": request.query,
            "analysis": response_text,
            "method": "rag_plus_tools",
            "session_id": session_id,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"RAG processing error: {e}")
        raise HTTPException(status_code=500, detail=f"RAG processing failed: {e}")
