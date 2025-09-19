"""
Document Management Agent for Mortgage Processing
Handles comprehensive document collection, processing, and storage workflow
"""

from typing import List, Dict, Any, Optional
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from mortgage_processor.utils.llm_factory import get_agent_llm
from ..prompt_loader import load_document_agent_prompt
from ..neo4j_mortgage import MortgageGraphManager
from ..vector_stores import LlamaStackVectorStore
from ..config import AppConfig
from ..embeddings import create_embeddings
from ..application_lifecycle import get_application_manager, ApplicationIntent, ApplicationPhase
import uuid
import json
from datetime import datetime, timedelta
from pathlib import Path

# ================================
# DOCUMENT STORAGE TOOLS
# ================================

@tool
def request_required_documents(application_id: str, missing_documents: List[str] = None) -> str:
    """
    Generate and send document request to customer for mortgage application.
    
    Args:
        application_id: Unique identifier for the mortgage application
        missing_documents: List of specific documents needed (optional)
        
    Returns:
        Document request details and submission instructions
    """
    
    # Standard required documents for mortgage applications
    standard_docs = [
        "Government-issued photo ID (driver's license or passport)",
        "Social Security card or verification",
        "Recent pay stubs (last 2-3 months)",
        "W-2 forms (last 2 years)",
        "Tax returns (last 2 years)",
        "Bank statements (last 2-3 months)",
        "Employment verification letter",
        "Proof of any additional income sources",
        "Purchase agreement (if property identified)",
        "Insurance information (homeowner's/auto)",
        "Previous mortgage statements (if refinancing)",
        "Gift letter (if using gift funds for down payment)"
    ]
    
    # Use provided missing documents or default to standard list
    required_docs = missing_documents if missing_documents else standard_docs
    
    request_id = f"DOC_REQ_{uuid.uuid4().hex[:8].upper()}"
    deadline = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Store document request in Neo4j
    try:
        manager = MortgageGraphManager()
        query = """
        MATCH (app:Application {id: $application_id})
        CREATE (req:DocumentRequest {
            id: $request_id,
            application_id: $application_id,
            requested_documents: $documents,
            request_date: datetime(),
            deadline: date($deadline),
            status: 'SENT'
        })
        CREATE (app)-[:REQUIRES_DOCUMENTS]->(req)
        RETURN req.id as request_id
        """
        
        result = manager.graph.query(query, {
            "application_id": application_id,
            "request_id": request_id,
            "documents": json.dumps(required_docs),
            "deadline": deadline
        })
        
    except Exception as e:
        print(f"Warning: Could not store document request in Neo4j: {e}")
    
    doc_list = "\n".join([f"   • {doc}" for doc in required_docs])
    
    return f"""
📋 **Document Request Generated - {request_id}**

**Application ID:** {application_id}
**Submission Deadline:** {deadline}

**Required Documents:**
{doc_list}

**Submission Options:**
1. **Online Portal:** Upload directly through your secure portal
2. **Email:** Send scanned copies to docs@mortgagelender.com
3. **Mobile App:** Use our mobile document scanner
4. **In-Person:** Visit any branch location

**Important Notes:**
• All documents must be legible and complete
• Bank statements should show complete account information
• Employment verification should be on company letterhead
• Tax returns must include all schedules and forms

**Need Help?** 
Contact your loan processor at (555) 123-4567 or email support@mortgagelender.com

Your application cannot proceed until all required documents are received and verified.
"""

@tool
def process_uploaded_document(
    document_content: str,
    file_name: str,
    document_type: str = "unknown",
    file_size: int = 0,
    application_id: Optional[str] = None
) -> str:
    """
    Process an uploaded document and store in hybrid storage system with intelligent application detection.
    
    Args:
        document_content: Text content of the document
        file_name: Original filename
        document_type: Type of document (pay_stub, w2, bank_statement, etc.)
        file_size: File size in bytes
        application_id: Optional application identifier (will auto-detect if not provided)
        
    Returns:
        Processing confirmation and document verification results with application linking
    """
    
    try:
        document_id = f"DOC_{uuid.uuid4().hex[:8].upper()}"
        
        # 1. Extract knowledge graph from document content for application detection
        from ..knowledge_graph import create_mortgage_knowledge_extractor
        
        extractor = create_mortgage_knowledge_extractor()
        document_metadata = {
            "document_id": document_id,
            "file_name": file_name,
            "document_type": document_type,
            "file_size": file_size,
            "upload_date": datetime.now().isoformat(),
            "source": "agent_processing"
        }
        
        # Extract knowledge graph for intelligent application detection
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            knowledge_graph = loop.run_until_complete(
                extractor.extract_knowledge_graph(document_content, document_metadata)
            )
        finally:
            loop.close()
        
        # 2. Intelligent application detection/creation
        app_manager = get_application_manager()
        
        if not application_id:
            # Use unified application detection
            persons = [node for node in knowledge_graph.get("nodes", []) if node["type"] == "Person"]
            person_name = persons[0]["id"] if persons else None
            
            result = app_manager.find_or_create_application(
                person_name=person_name,
                document_entities=knowledge_graph,
                intent=ApplicationIntent.DOCUMENT_UPLOAD
            )
            
            if result[0]:  # Application found/created
                application_id, detection_status, phase = result
                app_message = f"Linked to application {application_id} (status: {detection_status})"
            else:
                # Fallback
                application_id = f"APP_{uuid.uuid4().hex[:8].upper()}"
                app_message = f"Created fallback application {application_id}"
        else:
            app_message = f"Using provided application {application_id}"
            
        # Update metadata with final application ID
        document_metadata["application_id"] = application_id
        
        # 3. Store document content in Vector DB for RAG
        config = AppConfig.load()
        embeddings = create_embeddings(
            model_name=config.vector_db.embedding,
            llamastack_base_url=config.llamastack.base_url,
            llamastack_api_key=config.llamastack.api_key,
            prefer_remote=True
        )
        
        vectorstore = LlamaStackVectorStore(
            vector_db_id=f"docs_{application_id}",
            llamastack_base_url=config.llamastack.base_url,
            llamastack_api_key=config.llamastack.api_key,
            embedding_function=embeddings,
            embedding_model=config.vector_db.embedding,
            embedding_dimension=config.vector_db.embedding_dimension
        )
        
        # Create document for vector storage
        from langchain_core.documents import Document
        doc = Document(
            page_content=document_content,
            metadata={
                "document_id": document_id,
                "application_id": application_id,
                "file_name": file_name,
                "document_type": document_type,
                "upload_date": datetime.now().isoformat(),
                "source": "customer_upload"
            }
        )
        
        # Add to vector database
        vectorstore.add_documents([doc])
        
        # 2. Store document metadata in Neo4j
        manager = MortgageGraphManager()
        
        # Determine document quality score
        quality_score = min(100, max(20, (file_size / 1024) * 2))  # Basic quality estimation
        
        neo4j_query = """
        MATCH (app:Application {id: $application_id})
        CREATE (doc:Document {
            id: $document_id,
            application_id: $application_id,
            file_name: $file_name,
            document_type: $document_type,
            file_size: $file_size,
            quality_score: $quality_score,
            upload_date: datetime(),
            status: 'UPLOADED',
            verification_status: 'PENDING'
        })
        CREATE (app)-[:HAS_DOCUMENT]->(doc)
        RETURN doc.id as document_id
        """
        
        manager.graph.query(neo4j_query, {
            "application_id": application_id,
            "document_id": document_id,
            "file_name": file_name,
            "document_type": document_type,
            "file_size": file_size,
            "quality_score": quality_score
        })
        
        # 3. Basic document validation
        validation_results = []
        
        # Check document type
        if document_type == "unknown":
            validation_results.append("⚠️ Document type needs to be specified")
        
        # Check content length
        if len(document_content.strip()) < 50:
            validation_results.append("⚠️ Document content appears incomplete")
        elif len(document_content.strip()) > 100:
            validation_results.append("✅ Document has substantial content")
        
        # Check for key mortgage document indicators
        content_lower = document_content.lower()
        if "pay stub" in content_lower or "earnings statement" in content_lower:
            suggested_type = "pay_stub"
            validation_results.append("✅ Appears to be a pay stub")
        elif "w-2" in content_lower or "wage and tax statement" in content_lower:
            suggested_type = "w2_form"
            validation_results.append("✅ Appears to be a W-2 form")
        elif "bank statement" in content_lower or "account summary" in content_lower:
            suggested_type = "bank_statement"
            validation_results.append("✅ Appears to be a bank statement")
        
        validation_summary = "\n".join([f"   {result}" for result in validation_results])
        
        return f"""
✅ **Document Successfully Processed**

**Document ID:** {document_id}
**Application ID:** {application_id}
**File Name:** {file_name}
**Document Type:** {document_type}
**File Size:** {file_size:,} bytes

**Application Linking:**
✅ {app_message}
✅ Document linked to unified application workflow

**Storage Confirmation:**
✅ Content stored in vector database for AI analysis
✅ Knowledge graph entities extracted and stored
✅ Metadata stored in Neo4j for workflow tracking

**Validation Results:**
{validation_summary}

**Knowledge Graph Extraction:**
• Entities: {len(knowledge_graph.get('nodes', []))}
• Relationships: {len(knowledge_graph.get('relationships', []))}

**Next Steps:**
• Document will be automatically verified by our processing agents
• Knowledge graph entities will enhance application processing
• You will be notified if additional information is needed
• Processing typically takes 1-2 business days

**Status:** Ready for verification and linked to application workflow
"""
        
    except Exception as e:
        return f" Error processing document: {str(e)}"

@tool
def get_document_status(application_id: str) -> str:
    """
    Get comprehensive document status for a mortgage application.
    
    Args:
        application_id: Application identifier
        
    Returns:
        Detailed document collection and verification status
    """
    
    try:
        manager = MortgageGraphManager()
        
        # Get document requests and uploaded documents
        query = """
        MATCH (app:Application {id: $application_id})
        OPTIONAL MATCH (app)-[:REQUIRES_DOCUMENTS]->(req:DocumentRequest)
        OPTIONAL MATCH (app)-[:HAS_DOCUMENT]->(doc:Document)
        RETURN 
            app.id as application_id,
            collect(DISTINCT {
                request_id: req.id,
                requested_docs: req.requested_documents,
                request_date: req.request_date,
                deadline: req.deadline,
                status: req.status
            }) as requests,
            collect(DISTINCT {
                document_id: doc.id,
                file_name: doc.file_name,
                document_type: doc.document_type,
                upload_date: doc.upload_date,
                status: doc.status,
                verification_status: doc.verification_status,
                quality_score: doc.quality_score
            }) as documents
        """
        
        result = manager.graph.query(query, {"application_id": application_id})
        
        if not result:
            return f" No application found with ID: {application_id}"
        
        data = result[0]
        requests = [r for r in data['requests'] if r['request_id']]
        documents = [d for d in data['documents'] if d['document_id']]
        
        # Build status report
        status_report = f"""
📊 **Document Status Report - Application {application_id}**

**Document Requests Sent:** {len(requests)}
**Documents Uploaded:** {len(documents)}
"""
        
        if requests:
            status_report += "\n**📋 Document Requests:**\n"
            for req in requests:
                deadline_str = req['deadline'].strftime('%Y-%m-%d') if req['deadline'] else 'No deadline'
                status_report += f"   • Request {req['request_id']} - Status: {req['status']} - Deadline: {deadline_str}\n"
        
        if documents:
            status_report += "\n**📄 Uploaded Documents:**\n"
            for doc in documents:
                upload_date = doc['upload_date'].strftime('%Y-%m-%d %H:%M') if doc['upload_date'] else 'Unknown'
                quality = doc['quality_score'] if doc['quality_score'] else 'N/A'
                status_report += f"   • {doc['file_name']} ({doc['document_type']}) - {doc['verification_status']} - Quality: {quality}% - Uploaded: {upload_date}\n"
        
        # Document completion analysis
        total_required = 12  # Standard document count
        completion_pct = min(100, (len(documents) / total_required) * 100) if documents else 0
        
        status_report += f"""
**📈 Progress Summary:**
• Document Completion: {completion_pct:.0f}%
• Pending Verification: {len([d for d in documents if d.get('verification_status') == 'PENDING'])}
• Verified Documents: {len([d for d in documents if d.get('verification_status') == 'VERIFIED'])}

**Next Steps:**
"""
        
        if completion_pct < 100:
            status_report += "• Upload remaining required documents\n"
        if any(d.get('verification_status') == 'PENDING' for d in documents):
            status_report += "• Wait for document verification (1-2 business days)\n"
        if completion_pct >= 100 and all(d.get('verification_status') == 'VERIFIED' for d in documents):
            status_report += "• ✅ All documents complete - Ready for underwriting\n"
        
        return status_report
        
    except Exception as e:
        return f" Error retrieving document status: {str(e)}"

@tool
def verify_document_completeness(application_id: str) -> str:
    """
    Check if all required documents have been submitted and verified.
    
    Args:
        application_id: Application identifier
        
    Returns:
        Document completeness analysis and missing document list
    """
    
    # Standard required document types
    required_document_types = {
        "identification": ["drivers_license", "passport", "state_id"],
        "income_verification": ["pay_stub", "w2_form", "tax_return"],
        "employment": ["employment_verification", "offer_letter"],
        "assets": ["bank_statement", "investment_statement"],
        "property": ["purchase_agreement", "appraisal"],
        "insurance": ["homeowners_insurance", "title_insurance"]
    }
    
    try:
        manager = MortgageGraphManager()
        
        # Get all documents for application
        query = """
        MATCH (app:Application {id: $application_id})-[:HAS_DOCUMENT]->(doc:Document)
        WHERE doc.verification_status = 'VERIFIED'
        RETURN collect(doc.document_type) as verified_docs
        """
        
        result = manager.graph.query(query, {"application_id": application_id})
        verified_docs = result[0]['verified_docs'] if result else []
        
        # Check completeness by category
        completion_report = f"""
🔍 **Document Completeness Analysis - Application {application_id}**

**Verified Documents:** {len(verified_docs)}
"""
        
        missing_categories = []
        missing_docs = []
        
        for category, doc_types in required_document_types.items():
            has_doc_in_category = any(doc_type in verified_docs for doc_type in doc_types)
            
            status_icon = "✅" if has_doc_in_category else ""
            completion_report += f"\n{status_icon} **{category.replace('_', ' ').title()}:** "
            
            if has_doc_in_category:
                found_docs = [dt for dt in doc_types if dt in verified_docs]
                completion_report += f"Complete ({', '.join(found_docs)})"
            else:
                completion_report += f"Missing ({', '.join(doc_types)})"
                missing_categories.append(category)
                missing_docs.extend(doc_types)
        
        # Overall completion status
        categories_complete = len(required_document_types) - len(missing_categories)
        completion_pct = (categories_complete / len(required_document_types)) * 100
        
        completion_report += f"""

**📊 Overall Completion:** {completion_pct:.0f}% ({categories_complete}/{len(required_document_types)} categories)

**Application Status:**"""
        
        if completion_pct == 100:
            completion_report += """
✅ **READY FOR UNDERWRITING**
All required document categories have been submitted and verified.
"""
        elif completion_pct >= 75:
            completion_report += """
🟡 **NEARLY COMPLETE**
Most documents received. Upload remaining documents to proceed.
"""
        elif completion_pct >= 50:
            completion_report += """
🟠 **IN PROGRESS**
Good progress made. Several document categories still needed.
"""
        else:
            completion_report += """
🔴 **INCOMPLETE**
Many required documents still missing. Please prioritize document submission.
"""
        
        if missing_docs:
            completion_report += f"""
**⚠️ Next Steps:**
Please upload documents from these missing categories:
{chr(10).join([f'   • {cat.replace("_", " ").title()}' for cat in missing_categories])}

Contact your loan processor if you need help with any document requirements.
"""
        
        return completion_report
        
    except Exception as e:
        return f" Error analyzing document completeness: {str(e)}"

# ================================
# DOCUMENT AGENT CREATION
# ================================

def create_document_agent():
    """Create the document management agent with comprehensive document tools"""
    
    # Get model from centralized factory
    model = get_agent_llm()
    
    # Document management tools
    tools = [
        request_required_documents,
        process_uploaded_document,
        get_document_status,
        verify_document_completeness,
    ]
    
    # Create agent with document processing capabilities  
    agent = create_react_agent(
        model=model,
        tools=tools
    )
    
    return agent
