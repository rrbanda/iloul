import uuid
import logging
from typing import List, Optional, Any, Dict
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
import uvicorn

from .config import AppConfig
from .models import LoanType, DocumentType
from .agent import create_mortgage_agent, MortgageProcessingAgent
from .chat_router import chat_router, set_chat_dependencies

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mortgage_processor")

# Global variables
_config: Optional[AppConfig] = None
_agent: Optional[MortgageProcessingAgent] = None

# FastAPI app
app = FastAPI(
    title="Mortgage Processing Agent API",
    version="1.0.0",
    description="Stateless AI-powered mortgage document processing using LlamaStack ReActAgent",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include chat router
app.include_router(chat_router)

# ---- Request/Response Models ----

class CustomerInput(BaseModel):
    name: str
    age: int
    address: str
    ssn: str
    loan_type: LoanType
    authorize_credit_check: bool


class DocumentInput(BaseModel):
    document_type: Optional[DocumentType] = None
    file_name: str
    content: str  # Extracted text content
    metadata: Dict[str, Any] = {}


class ProcessMortgageRequest(BaseModel):
    customer: CustomerInput
    documents: List[DocumentInput]
    application_id: Optional[str] = None  # Optional for tracking
    processing_options: Dict[str, Any] = {}


class ProcessingResponse(BaseModel):
    success: bool
    application_id: str
    processing_status: str
    documents_processed: int
    valid_documents: int
    invalid_documents: int
    missing_documents: List[str]
    document_validations: List[Dict[str, Any]]
    next_steps: List[str]
    urla_1003_generated: bool
    agent_reasoning: Optional[str] = None
    processing_timestamp: str
    session_id: str


class HealthResponse(BaseModel):
    status: str
    ready: bool
    agent_initialized: bool
    config_loaded: bool
    timestamp: str


class QuickProcessRequest(BaseModel):
    """Simplified request for quick processing with file uploads"""
    customer_name: str
    customer_age: int
    loan_type: LoanType
    authorize_credit_check: bool = True


# ---- Helper Functions ----


def _extract_text_from_file(file_content: bytes, file_name: str) -> str:
    """
    Extract text content from uploaded file.
    
    Note: This is a simplified implementation. In production, you would use:
    - PDF extraction libraries (PyPDF2, pdfplumber, etc.)
    - OCR services (Tesseract, AWS Textract, Google Vision API, etc.)
    - Document processing services
    """
    try:
        if file_name.lower().endswith('.txt'):
            return file_content.decode('utf-8')
        elif file_name.lower().endswith('.pdf'):
            # In production: Use PDF extraction libraries
            logger.info(f"PDF processing not implemented - returning placeholder for {file_name}")
            return f"[PDF TEXT EXTRACTION PLACEHOLDER]\nFile: {file_name}\nSize: {len(file_content)} bytes\nNote: Implement PDF extraction with PyPDF2 or similar"
        else:
            # In production: Use OCR services like Tesseract or cloud APIs
            logger.info(f"OCR processing not implemented - returning placeholder for {file_name}")
            return f"[OCR PLACEHOLDER]\nFile: {file_name}\nSize: {len(file_content)} bytes\nNote: Implement OCR with Tesseract, AWS Textract, or similar"
    except Exception as e:
        logger.warning(f"Error extracting text from {file_name}: {e}")
        return f"[Content extraction failed for {file_name}: {str(e)}]"


# ---- Application Lifecycle ----

@app.on_event("startup")
async def startup():
    """Initialize the application with configuration and agent."""
    global _config, _agent
    
    try:
        # Load configuration
        _config = AppConfig.load()
        logger.info("Configuration loaded successfully")
        
        # Initialize mortgage processing agent
        _agent = create_mortgage_agent(_config)
        logger.info("Mortgage processing agent initialized successfully")
        
        # Set chat dependencies
        set_chat_dependencies(_config, _agent)
        logger.info("Chat endpoints configured successfully")
        
        logger.info(" Stateless Mortgage Processing API is ready!")
        
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        _agent = None
        _config = None


@app.on_event("shutdown")
async def shutdown():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Mortgage Processing API")


# ---- Core Agent Endpoints ----

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify service status."""
    ready = all([_config, _agent])
    
    return HealthResponse(
        status="healthy" if ready else "unhealthy",
        ready=ready,
        agent_initialized=_agent is not None,
        config_loaded=_config is not None,
        timestamp=datetime.now().isoformat()
    )


@app.post("/mortgage/process", response_model=ProcessingResponse)
async def process_mortgage_documents(request: ProcessMortgageRequest):
    """
    Process mortgage application directly with AI agent (STATELESS).
    Send all customer data and documents in one request.
    """
    if not all([_config, _agent]):
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Generate application ID if not provided
        application_id = request.application_id or f"APP_{uuid.uuid4().hex[:8].upper()}"
        
        # Prepare application data for agent
        application_data = {
            "application_id": application_id,
            "customer": {
                "name": request.customer.name,
                "age": request.customer.age,
                "address": request.customer.address,
                "ssn": request.customer.ssn,
                "loan_type": request.customer.loan_type.value,
                "authorize_credit_check": request.customer.authorize_credit_check
            }
        }
        
        # Prepare documents data for agent
        documents = []
        for i, doc in enumerate(request.documents):
            documents.append({
                "document_id": f"DOC_{uuid.uuid4().hex[:8].upper()}",
                "file_name": doc.file_name,
                "file_size": len(doc.content),
                "mime_type": doc.metadata.get("mime_type", "text/plain"),
                "content_preview": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                "document_type": doc.document_type.value if doc.document_type else "unknown",
                "full_content": doc.content,
                "metadata": doc.metadata
            })
        
        logger.info(f"Processing mortgage application {application_id} for {request.customer.name}")
        logger.info(f"Documents received: {len(documents)}")
        
        # Process directly with ReActAgent
        processing_result = _agent.process_mortgage_application(
            application_data=application_data,
            documents=documents
        )
        
        # Build response
        response = ProcessingResponse(
            success=processing_result.get("processing_status") != "failed",
            application_id=application_id,
            processing_status=processing_result.get("processing_status", "success"),
            documents_processed=len(documents),
            valid_documents=processing_result.get("valid_documents", len(documents)),
            invalid_documents=processing_result.get("invalid_documents", 0),
            missing_documents=processing_result.get("missing_documents", []),
            document_validations=processing_result.get("document_validations", []),
            next_steps=processing_result.get("next_steps", []),
            urla_1003_generated=processing_result.get("urla_1003_generated", False),
            agent_reasoning=processing_result.get("agent_reasoning") if _config.response_format.include_agent_reasoning else None,
            processing_timestamp=datetime.now().isoformat(),
            session_id=processing_result.get("session_id", "unknown")
        )
        
        logger.info(f" Completed processing {application_id}: {response.processing_status}")
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing mortgage application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")



# ---- Convenience Endpoints ----

@app.post("/mortgage/process/files")
async def process_mortgage_with_files(
    customer_name: str = Form(...),
    customer_age: int = Form(...),
    loan_type: str = Form(...),
    authorize_credit_check: bool = Form(True),
    address: str = Form("123 Main Street, Anytown, CA 90210"),
    ssn: str = Form("***-**-1234"),
    files: List[UploadFile] = File(...)
):
    """
    Convenience endpoint: Upload files directly and process immediately.
    Perfect for frontend file upload integration.
    """
    if not all([_config, _agent]):
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Process uploaded files
        documents = []
        for file in files:
            # Read file content
            file_content = await file.read()
            
            # Extract text
            extracted_text = _extract_text_from_file(file_content, file.filename or "unknown")
            
            documents.append(DocumentInput(
                file_name=file.filename or "unknown",
                content=extracted_text,
                metadata={
                    "mime_type": file.content_type or "application/octet-stream",
                    "file_size": len(file_content),
                    "upload_method": "direct_upload"
                }
            ))
        
        # Create processing request
        process_request = ProcessMortgageRequest(
            customer=CustomerInput(
                name=customer_name,
                age=customer_age,
                address=address,
                ssn=ssn,
                loan_type=LoanType(loan_type),
                authorize_credit_check=authorize_credit_check
            ),
            documents=documents
        )
        
        # Process with agent
        return await process_mortgage_documents(process_request)
        
    except Exception as e:
        logger.error(f"Error processing files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")


# ---- Configuration and Demo Endpoints ----

@app.get("/mortgage/config")
async def get_mortgage_config():
    """Get mortgage processing configuration."""
    if not _config:
        raise HTTPException(status_code=503, detail="Configuration not loaded")
    
    return {
        "document_types": [doc_type.value for doc_type in DocumentType],
        "loan_types": [loan_type.value for loan_type in LoanType],
        "required_documents": _config.mortgage.required_documents,
        "validation_rules": {
            doc_type: {
                "max_days_until_expiry": rules.max_days_until_expiry,
                "max_age_months": rules.max_age_months,
                "max_age_years": rules.max_age_years,
                "acceptable_alternatives": rules.acceptable_alternatives
            }
            for doc_type, rules in _config.mortgage.validation_rules.items()
        }
    }




# ---- Main Application Entry Point ----

def main():
    """Main entry point for running the application."""
    uvicorn.run(
        "mortgage_processor.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
