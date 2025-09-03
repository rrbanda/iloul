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

class IngestMortgageDocsResponse(BaseModel):
    status: str
    message: str
    processed_count: int
    document_ids: List[str]

class QueryMortgageKnowledgeRequest(BaseModel):
    query: str
    customer_id: Optional[str] = None
    document_types: Optional[List[str]] = None
    max_chunks: Optional[int] = 5

class QueryMortgageKnowledgeResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float

# We'll get these from the main app
_config: Optional[AppConfig] = None
_client = None

def set_rag_dependencies(config: AppConfig, client):
    """Set dependencies from main app"""
    global _config, _client
    _config = config
    _client = client

@router.post("/ingest", response_model=IngestMortgageDocsResponse)
async def ingest_mortgage_documents(request: IngestMortgageDocsRequest):
    """
    Ingest mortgage documents into vector database for semantic search.
    """
    if not _client:
        raise HTTPException(status_code=500, detail="RAG client not initialized")
    
    try:
        # Convert mortgage documents to RAG documents
        rag_documents = []
        document_ids = []
        
        for doc in request.documents:
            doc_id = str(uuid.uuid4())
            document_ids.append(doc_id)
            
            # Create RAG document with proper metadata
            rag_doc = RAGDocument(
                document_id=doc_id,
                content=doc.content,
                mime_type=doc.mime_type,
                metadata={
                    "customer_id": doc.customer_id,
                    "application_id": doc.application_id,
                    "document_type": doc.document_type,
                    "file_name": doc.file_name,
                    **(doc.metadata or {})
                }
            )
            rag_documents.append(rag_doc)
        
        # Ingest documents using LlamaStack client
        response = await _client.post_rag_documents(
            bank_id=_config.llamastack.rag_bank_id,
            documents=rag_documents,
            chunk_size_in_tokens=request.chunk_size_in_tokens
        )
        
        logger.info(f"Successfully ingested {len(rag_documents)} documents for RAG")
        
        return IngestMortgageDocsResponse(
            status="success",
            message=f"Successfully processed {len(rag_documents)} documents",
            processed_count=len(rag_documents),
            document_ids=document_ids
        )
        
    except Exception as e:
        logger.error(f"Failed to ingest documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest documents: {str(e)}")

@router.post("/query", response_model=QueryMortgageKnowledgeResponse)
async def query_mortgage_knowledge(request: QueryMortgageKnowledgeRequest):
    """
    Query the mortgage knowledge base using RAG.
    """
    if not _client:
        raise HTTPException(status_code=500, detail="RAG client not initialized")
    
    try:
        # Build filter based on customer and document types
        filters = {}
        if request.customer_id:
            filters["customer_id"] = request.customer_id
        if request.document_types:
            filters["document_type"] = {"$in": request.document_types}
        
        # Query the RAG system
        response = await _client.query_rag(
            bank_id=_config.llamastack.rag_bank_id,
            query=request.query,
            filters=filters,
            max_chunks=request.max_chunks or 5
        )
        
        # Process response
        answer = response.get("answer", "No relevant information found.")
        sources = response.get("sources", [])
        confidence = response.get("confidence", 0.0)
        
        return QueryMortgageKnowledgeResponse(
            answer=answer,
            sources=sources,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Failed to query knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to query knowledge base: {str(e)}")

@router.get("/health")
async def rag_health_check():
    """Health check for RAG endpoints"""
    if not _client:
        raise HTTPException(status_code=500, detail="RAG client not initialized")
    
    try:
        # Simple health check
        return {
            "status": "healthy",
            "rag_bank_id": _config.llamastack.rag_bank_id if _config else None,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG health check failed: {str(e)}")

# For backward compatibility with existing imports
async def ingest_documents(documents: List[MortgageDocument], chunk_size: int = 512):
    """Legacy function for document ingestion"""
    request = IngestMortgageDocsRequest(
        documents=documents,
        chunk_size_in_tokens=chunk_size
    )
    return await ingest_mortgage_documents(request)

async def query_knowledge_base(query: str, customer_id: str = None, max_chunks: int = 5):
    """Legacy function for knowledge base queries"""
    request = QueryMortgageKnowledgeRequest(
        query=query,
        customer_id=customer_id,
        max_chunks=max_chunks
    )
    return await query_mortgage_knowledge(request)
