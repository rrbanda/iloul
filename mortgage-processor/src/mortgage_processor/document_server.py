"""
Document Management Server with Knowledge Graph Extraction
FastAPI server for handling document uploads and knowledge graph construction
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from .api.document_api import router as document_router
from .config import AppConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Mortgage Document Management API",
    description="""
    Advanced document management system for mortgage processing with:
    
    - **Smart Document Upload**: Multi-format file upload (PDF, Word, Images, Text) with NO APPLICATION ID REQUIRED
    - **Intelligent Application Detection**: Automatically detects or creates applications based on document content
    - **Knowledge Graph Extraction**: Automatic entity and relationship extraction using LangChain
    - **Hybrid Storage**: Vector database for RAG + Neo4j for knowledge graphs
    - **Document Status Tracking**: Real-time processing and verification status
    - **Knowledge Graph Queries**: Rich querying of extracted entities and relationships
    
    ## Features
    
    ### 🔄 Triple Storage Architecture
    - **Vector Database**: Document content for semantic search and RAG
    - **Neo4j Knowledge Graph**: Extracted entities (Person, Income, Asset, etc.) and relationships
    - **Neo4j Metadata**: Document workflow status and tracking
    
    ### 🧠 Knowledge Graph Entities
    - **Person**: Applicants, co-applicants, spouses
    - **Employer**: Current and previous employers
    - **Income**: Salary, wages, bonuses, benefits
    - **Asset**: Bank accounts, investments, retirement funds
    - **Debt**: Credit cards, loans, liabilities
    - **Property**: Real estate properties
    - **Document**: W-2s, pay stubs, bank statements
    
    ### 🔗 Relationship Types
    - Person → EMPLOYED_BY → Employer
    - Person → EARNS → Income
    - Person → OWNS → Asset
    - Person → RESIDES_AT → Address
    - Document → VERIFIES → Income/Employment
    - And many more...
    
    ### 📄 Supported Document Types
    - **W-2 Forms**: Tax documents from employers
    - **Pay Stubs**: Recent earnings statements
    - **Bank Statements**: Account summaries and transaction history
    - **Tax Returns**: Complete tax filings
    - **Employment Verification**: VOE letters
    - **Property Documents**: Appraisals, purchase agreements
    
    ### 🔍 Query Capabilities
    - All entities and relationships for an application
    - Person-specific data (applicants, employment)
    - Income and asset analysis
    - Document verification status
    - Knowledge graph visualization data
    """,
    version="1.0.0",
    contact={
        "name": "Mortgage Processing Team",
        "email": "support@mortgageprocessing.com",
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include document management router
app.include_router(document_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Mortgage Document Management API",
        "version": "1.0.0",
        "description": "Document upload and knowledge graph extraction for mortgage processing",
        "features": [
            "Multi-format document upload",
            "Automatic knowledge graph extraction",
            "Triple storage architecture (Vector DB + Neo4j)",
            "Real-time document status tracking",
            "Rich knowledge graph queries"
        ],
        "endpoints": {
            "upload": "/api/documents/upload",
            "status": "/api/documents/status/{document_id}",
            "knowledge_graph": "/api/documents/knowledge-graph/{application_id}",
            "list_documents": "/api/documents/applications/{application_id}/documents",
            "health": "/api/documents/health"
        },
        "documentation": {
            "interactive": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check for all services"""
    
    health_status = {
        "status": "healthy",
        "service": "document_management_api",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Check configuration
    try:
        config = AppConfig.load()
        health_status["components"]["config"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["config"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # Check Neo4j connection (basic check)
    try:
        from .neo4j_mortgage import MortgageGraphManager
        neo4j_manager = MortgageGraphManager()
        # Simple query to test connection
        neo4j_manager.execute_query("RETURN 1 as test", {})
        health_status["components"]["neo4j"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["neo4j"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check knowledge graph extractor
    try:
        from .knowledge_graph import create_mortgage_knowledge_extractor
        extractor = create_mortgage_knowledge_extractor()
        health_status["components"]["knowledge_extractor"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["knowledge_extractor"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check vector store (basic check)
    try:
        from .vector_stores import LlamaStackVectorStore
        health_status["components"]["vector_store"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["vector_store"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    return health_status

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path),
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Mortgage Document Management API")
    logger.info("📄 Document upload and knowledge graph extraction ready")
    logger.info("🔗 Triple storage architecture: Vector DB + Neo4j")
    logger.info("✅ API server ready for requests")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Mortgage Document Management API")

def run_server(host: str = "0.0.0.0", port: int = 8001, reload: bool = False):
    """Run the document management server"""
    logger.info(f"🌐 Starting server on {host}:{port}")
    uvicorn.run(
        "src.mortgage_processor.document_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    # Run with development settings
    run_server(reload=True)
