"""
 agentic client tools for mortgage document processing.

These tools only extract data and provide information.
The AI agent makes ALL validation decisions based on configuration rules.
"""

import logging
import uuid
import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from llama_stack_client.lib.agents.client_tool import client_tool
from langchain_core.tools import tool
from ..models import DocumentType
from ..database import get_db_session, MortgageApplicationDB
from ..application_lifecycle import get_application_manager, ApplicationIntent, ApplicationPhase

logger = logging.getLogger(__name__)


@client_tool
def classify_document_type(document_content: str, file_name: str) -> Dict[str, Any]:
    """
    Extract basic metadata and classify document type.
    Agent will make validation decisions based on the classification.
    
    :param document_content: Text content of the document
    :param file_name: Original filename
    :returns: Document metadata without validation decisions
    """
    content_lower = document_content.lower()
    file_lower = file_name.lower()
    
    # Simple keyword-based classification for demo
    if any(word in content_lower for word in ["driver", "license", "id"]) or "license" in file_lower:
        doc_type = DocumentType.DRIVER_LICENSE
        confidence = 0.92
    elif any(word in content_lower for word in ["bank", "statement", "account", "balance"]):
        doc_type = DocumentType.BANK_STATEMENT
        confidence = 0.88
    elif any(word in content_lower for word in ["tax", "1040", "w-2", "irs"]):
        doc_type = DocumentType.TAX_STATEMENT
        confidence = 0.85
    elif any(word in content_lower for word in ["pay", "stub", "payroll", "earnings"]):
        doc_type = DocumentType.PAY_STUB
        confidence = 0.90
    elif any(word in content_lower for word in ["passport", "united states"]):
        doc_type = DocumentType.PASSPORT
        confidence = 0.95
    else:
        doc_type = DocumentType.DRIVER_LICENSE  # Default fallback
        confidence = 0.45
    
    return {
        "document_type": doc_type.value,
        "confidence_score": confidence,
        "classification_method": "keyword_analysis",
        "file_name": file_name,
        "content_length": len(document_content),
        "timestamp": datetime.now().isoformat()
    }


@client_tool
def validate_document_expiration(document_content: str, document_type: str) -> Dict[str, Any]:
    """
    Extract date information from documents.
    Agent will determine expiration status using validation rules from config.
    
    :param document_content: Text content of the document
    :param document_type: Type of document being processed
    :returns: Raw date information for agent to validate
    """
    today = date.today()
    
    # Demo logic - simulate extracting dates from different document types
    if document_type == DocumentType.DRIVER_LICENSE.value:
        # Simulate various date scenarios for demo
        demo_scenarios = [
            {
                "issue_date": (today - timedelta(days=1825)).isoformat(),  # 5 years ago
                "expiration_date": (today + timedelta(days=45)).isoformat(),  # 45 days from now
            },
            {
                "issue_date": (today - timedelta(days=2190)).isoformat(),  # 6 years ago
                "expiration_date": (today - timedelta(days=30)).isoformat(),  # 30 days ago (expired)
            },
            {
                "issue_date": (today - timedelta(days=365)).isoformat(),  # 1 year ago
                "expiration_date": (today + timedelta(days=180)).isoformat(),  # 6 months from now
            },
        ]
        scenario = demo_scenarios[hash(document_content) % len(demo_scenarios)]
        
        return {
            "document_type": document_type,
            "issue_date": scenario["issue_date"],
            "expiration_date": scenario["expiration_date"],
            "current_date": today.isoformat(),
            "extraction_method": "demo_date_parsing",
            "confidence": 0.94,
            "timestamp": datetime.now().isoformat()
        }
    
    # For other document types that don't typically have expiration dates
    return {
        "document_type": document_type,
        "issue_date": None,
        "expiration_date": None,
        "current_date": today.isoformat(),
        "extraction_method": "no_expiration_expected",
        "confidence": 1.0,
        "timestamp": datetime.now().isoformat()
    }


@client_tool
def extract_personal_information(document_content: str, document_type: str) -> Dict[str, Any]:
    """
    Extract personal information from document content.
    Returns raw extracted data without validation.
    
    :param document_content: Text content of the document
    :param document_type: Type of document being processed
    :returns: Raw extracted personal information
    """
    # Demo extraction - in production, this would use sophisticated NLP/LLM extraction
    demo_data = {
        DocumentType.DRIVER_LICENSE.value: {
            "full_name": "John Michael Smith",
            "date_of_birth": "1985-03-15",
            "address": "123 Main Street, Anytown, CA 90210",
            "license_number": "D1234567",
            "state_issued": "CA",
            "license_class": "C"
        },
        DocumentType.PASSPORT.value: {
            "full_name": "John Michael Smith",
            "date_of_birth": "1985-03-15",
            "passport_number": "123456789",
            "nationality": "United States",
            "place_of_birth": "California, USA"
        }
    }
    
    extracted = demo_data.get(document_type, {})
    
    return {
        "document_type": document_type,
        "extracted_fields": extracted,
        "confidence_score": 0.87,
        "extraction_method": "demo_nlp_extraction",
        "fields_found": len(extracted),
        "timestamp": datetime.now().isoformat()
    }


@client_tool
def extract_income_information(document_content: str, document_type: str) -> Dict[str, Any]:
    """
    Extract financial and income information from documents.
    Returns raw financial data without validation.
    
    :param document_content: Text content of the document
    :param document_type: Type of document being processed
    :returns: Raw extracted financial information
    """
    # Demo financial extraction
    demo_financial_data = {
        DocumentType.PAY_STUB.value: {
            "gross_pay": 5500.00,
            "net_pay": 4200.00,
            "pay_period": "bi-weekly",
            "pay_date": "2024-07-15",
            "employer_name": "Tech Solutions Inc",
            "employee_id": "EMP12345",
            "ytd_gross": 71500.00,
            "ytd_taxes": 14300.00,
            "deductions": {
                "federal_tax": 825.00,
                "state_tax": 275.00,
                "social_security": 341.00,
                "medicare": 79.75
            }
        },
        DocumentType.TAX_STATEMENT.value: {
            "tax_year": 2023,
            "filing_status": "married_filing_jointly",
            "annual_gross_income": 143000.00,
            "adjusted_gross_income": 138500.00,
            "total_tax": 28600.00,
            "refund_amount": 2100.00,
            "w2_employers": ["Tech Solutions Inc"],
            "spouse_income": 65000.00
        },
        DocumentType.BANK_STATEMENT.value: {
            "account_number_masked": "****1234",
            "statement_period_start": "2024-07-01",
            "statement_period_end": "2024-07-31",
            "opening_balance": 22500.00,
            "closing_balance": 25000.00,
            "total_deposits": 8500.00,
            "total_withdrawals": 6000.00,
            "transaction_count": 47,
            "largest_deposit": 5500.00,
            "average_daily_balance": 23750.00
        }
    }
    
    financial_data = demo_financial_data.get(document_type, {})
    
    return {
        "document_type": document_type,
        "financial_information": financial_data,
        "extraction_confidence": 0.91,
        "currency": "USD",
        "extraction_timestamp": datetime.now().isoformat(),
        "data_points_extracted": len(financial_data)
    }


@client_tool
def check_document_quality(document_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract technical quality metrics from document.
    Agent will determine quality acceptability using business rules.
    
    :param document_metadata: Document metadata including file info
    :returns: Raw quality metrics for agent to evaluate
    """
    file_size = document_metadata.get("file_size", 0)
    mime_type = document_metadata.get("mime_type", "")
    file_name = document_metadata.get("file_name", "")
    
    # Extract raw quality metrics without making decisions
    quality_metrics = {
        "file_size_bytes": file_size,
        "file_size_mb": round(file_size / (1024 * 1024), 2),
        "file_size_kb": round(file_size / 1024, 2),
        "mime_type": mime_type,
        "file_name": file_name,
        "estimated_page_count": 1 if file_size > 0 else 0,
    }
    
    # For PDFs, extract additional metrics
    if "pdf" in mime_type.lower():
        quality_metrics.update({
            "is_pdf": True,
            "estimated_text_extractable": True,
            "ocr_required": False
        })
    elif "image" in mime_type.lower():
        # Simulate OCR confidence for images
        ocr_confidence = 0.88 if file_size > 100000 else 0.65  # Demo logic
        quality_metrics.update({
            "is_image": True,
            "estimated_text_extractable": ocr_confidence > 0.7,
            "ocr_required": True,
            "estimated_ocr_confidence": ocr_confidence
        })
    
    quality_metrics.update({
        "extraction_timestamp": datetime.now().isoformat(),
        "analysis_method": "demo_quality_analysis"
    })
    
    return quality_metrics


@client_tool
def authorize_credit_check(customer_id: str, authorization_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract credit check authorization information.
    Agent will determine if authorization is sufficient based on business rules.
    
    :param customer_id: Customer identifier
    :param authorization_data: Authorization details and customer consent
    :returns: Raw authorization data for agent to evaluate
    """
    # Extract authorization information without making approval decision
    authorization_info = {
        "customer_id": customer_id,
        "customer_consent": authorization_data.get("customer_consent", False),
        "terms_accepted": authorization_data.get("terms_accepted", False),
        "consent_timestamp": authorization_data.get("consent_timestamp"),
        "ip_address": authorization_data.get("ip_address"),
        "user_agent": authorization_data.get("user_agent"),
        "authorization_method": authorization_data.get("method", "online_form"),
        "consent_version": authorization_data.get("consent_version", "v1.0"),
        "additional_disclosures": authorization_data.get("additional_disclosures", []),
        "extraction_timestamp": datetime.now().isoformat()
    }
    
    return authorization_info


@client_tool
def generate_urla_1003_form(application_data: Dict[str, Any], extracted_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate data structure for URLA 1003 form.
    Returns form data structure for agent to review and validate.
    
    :param application_data: Original application data
    :param extracted_documents: All extracted document data
    :returns: URLA 1003 form data structure
    """
    customer_data = application_data.get("customer", {})
    
    # Aggregate data from extracted documents
    personal_info = {}
    financial_info = {}
    
    for doc in extracted_documents:
        if "extracted_fields" in doc:
            personal_info.update(doc["extracted_fields"])
        if "financial_information" in doc:
            financial_info.update(doc["financial_information"])
    
    urla_data = {
        "form_id": f"URLA_{uuid.uuid4().hex[:8].upper()}",
        "form_version": "1003_2023",
        "preparation_date": datetime.now().isoformat(),
        "borrower_information": {
            "name": personal_info.get("full_name", customer_data.get("name", "")),
            "date_of_birth": personal_info.get("date_of_birth"),
            "ssn": customer_data.get("ssn"),
            "current_address": personal_info.get("address"),
            "phone": customer_data.get("phone"),
            "email": customer_data.get("email")
        },
        "employment_information": {
            "current_employer": financial_info.get("employer_name"),
            "annual_income": financial_info.get("annual_gross_income"),
            "monthly_income": financial_info.get("gross_pay", 0) * 26 / 12 if financial_info.get("gross_pay") else None,
            "employment_years": "2+",  # Demo value
            "job_title": "Software Engineer"  # Demo value
        },
        "loan_information": {
            "loan_amount_requested": 350000,  # Demo amount
            "loan_purpose": "purchase",
            "property_type": "single_family",
            "occupancy": "primary_residence",
            "property_address": "456 Property Lane, Hometown, CA 90210"
        },
        "assets_and_liabilities": {
            "checking_account_balance": financial_info.get("closing_balance"),
            "savings_account_balance": 15000,  # Demo value
            "total_assets": financial_info.get("closing_balance", 0) + 15000,
            "monthly_debt_payments": 850  # Demo value
        },
        "data_sources": [doc.get("document_type") for doc in extracted_documents],
        "completion_status": "draft",
        "requires_review": True
    }
    
    return {
        "urla_1003_data": urla_data,
        "form_completeness": 0.85,  # Demo percentage
        "missing_fields": ["spouse_information", "co_borrower_details"],
        "data_confidence": 0.88,
        "generation_timestamp": datetime.now().isoformat(),
        "ready_for_submission": False
    }


@client_tool
def cross_validate_documents(documents_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Cross-reference information across multiple documents.
    Returns comparison data for agent to analyze consistency.
    
    :param documents_data: List of extracted data from multiple documents
    :returns: Cross-reference analysis for agent evaluation
    """
    if len(documents_data) < 2:
        return {
            "cross_reference_possible": False,
            "reason": "Insufficient documents for cross-referencing",
            "document_count": len(documents_data)
        }
    
    # Extract comparable fields across documents
    names_found = []
    addresses_found = []
    income_sources = []
    dates_found = []
    
    for doc_data in documents_data:
        # Extract names from various document types
        if "extracted_fields" in doc_data:
            fields = doc_data["extracted_fields"]
            if "full_name" in fields:
                names_found.append(fields["full_name"])
            if "address" in fields:
                addresses_found.append(fields["address"])
                
        # Extract income information
        if "financial_information" in doc_data:
            fin_info = doc_data["financial_information"]
            if "employer_name" in fin_info:
                income_sources.append(fin_info["employer_name"])
                
        # Extract dates
        if "expiration_date" in doc_data and doc_data["expiration_date"]:
            dates_found.append(doc_data["expiration_date"])
    
    return {
        "cross_reference_possible": True,
        "document_count": len(documents_data),
        "names_found": names_found,
        "name_consistency": len(set(names_found)) <= 1 if names_found else None,
        "addresses_found": addresses_found,
        "address_consistency": len(set(addresses_found)) <= 1 if addresses_found else None,
        "income_sources": income_sources,
        "employment_consistency": len(set(income_sources)) <= 1 if income_sources else None,
        "dates_extracted": dates_found,
        "analysis_timestamp": datetime.now().isoformat(),
        "comparison_method": "demo_cross_reference"
    }


@client_tool
def get_current_date_time() -> Dict[str, Any]:
    """
    Get current date and time for agent calculations.
    Agent uses this to calculate document expiration, age, etc.
    
    :returns: Current date and time information
    """
    now = datetime.now()
    today = date.today()
    
    return {
        "current_datetime": now.isoformat(),
        "current_date": today.isoformat(),
        "current_year": today.year,
        "current_month": today.month,
        "current_day": today.day,
        "timezone": "UTC",
        "timestamp": now.isoformat()
    }


# ============================================================================
# LangGraph Tools for Conversational Mortgage Application
# ============================================================================

from pydantic import BaseModel, Field

class PersonalInfoSchema(BaseModel):
    """Schema for extracting personal information from mortgage applicant text"""
    text: str = Field(
        description="User's message containing personal information like name, phone, or email"
    )

@tool("extract_personal_info", args_schema=PersonalInfoSchema, parse_docstring=True)
def extract_personal_info(text: str) -> Dict[str, Any]:
    """Extract personal information from mortgage applicant's message.
    
    This tool identifies and extracts personal details that are required 
    for mortgage pre-qualification including full name, phone number, and email address.
    
    Args:
        text: User's message that may contain personal information
        
    Returns:
        Dictionary with extracted personal information fields
    """
    data = {}
    
    # Name extraction with improved patterns
    name_patterns = [
        r"(?:my name is|i'm|i am|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        r"([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["full_name"] = match.group(1).strip()
            break
    
    # Phone extraction with validation
    phone_match = re.search(r"(\(?(?:\d{3})\)?[-.\s]?\d{3}[-.\s]?\d{4})", text)
    if phone_match:
        cleaned = re.sub(r'[^\d]', '', phone_match.group(1))
        if len(cleaned) == 10:
            data["phone"] = f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
    
    # Email extraction with validation
    email_match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text)
    if email_match:
        data["email"] = email_match.group(1).lower()
    
    return data

class EmploymentInfoSchema(BaseModel):
    """Schema for extracting employment information from mortgage applicant text"""
    text: str = Field(
        description="User's message containing employment details like income, employer, or job type"
    )

@tool("extract_employment_info", args_schema=EmploymentInfoSchema, parse_docstring=True)
def extract_employment_info(text: str) -> Dict[str, Any]:
    """Extract employment information from mortgage applicant's message.
    
    This tool identifies and extracts employment details required for mortgage 
    qualification including annual income, employer name, and employment type.
    
    Args:
        text: User's message that may contain employment information
        
    Returns:
        Dictionary with extracted employment information fields including:
        - annual_income: Gross annual income in USD
        - employer: Company or organization name  
        - employment_type: Type of employment (full-time, part-time, contractor, self-employed)
    """
    data = {}
    
    # Income extraction with improved validation
    income_patterns = [
        r"\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        r"(\d{5,7})"  # 5-7 digit numbers likely to be income
    ]
    for pattern in income_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match[0] else match[1]
            amount = match.replace(",", "")
            try:
                income_val = int(float(amount))
                # Validate income is in reasonable range for mortgage applicants
                if 10000 <= income_val <= 2000000:
                    data["annual_income"] = income_val
                    break
            except:
                continue
    
    # Employer extraction with enhanced patterns
    known_companies = ["IBM", "Google", "Microsoft", "Apple", "Amazon", "Meta", "Tesla", 
                      "Wells Fargo", "Bank of America", "Chase", "Citibank"]
    for company in known_companies:
        if company.lower() in text.lower():
            data["employer"] = company
            break
    
    # Generic employer patterns with better validation
    if "employer" not in data:
        employer_patterns = [
            r"work(?:\s+at|\s+for)\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s|,|$)",
            r"employed\s+(?:at|by)\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s|,|$)",
            r"company\s+(?:called|named)\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s|,|$)"
        ]
        for pattern in employer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                employer = match.group(1).strip()
                if len(employer) > 2 and len(employer) < 50:  # Reasonable company name length
                    data["employer"] = employer
                    break
    
    # Employment type classification
    if any(term in text.lower() for term in ["full time", "full-time", "fulltime"]):
        data["employment_type"] = "full-time"
    elif any(term in text.lower() for term in ["part time", "part-time", "parttime"]):
        data["employment_type"] = "part-time"
    elif any(term in text.lower() for term in ["contractor", "freelance", "consultant"]):
        data["employment_type"] = "contractor"
    elif any(term in text.lower() for term in ["self employed", "self-employed", "own business"]):
        data["employment_type"] = "self-employed"
    
    return data

@tool
def extract_property_info(text: str) -> Dict[str, Any]:
    """Extract property information from user input"""
    data = {}
    
    # Price extraction
    price_patterns = [r"\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"]
    for pattern in price_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            amount = match.replace(",", "")
            try:
                num_amount = float(amount)
                if 50000 <= num_amount <= 50000000:
                    data["purchase_price"] = int(num_amount)
                    break
            except:
                continue
    
    # Property type
    if any(word in text.lower() for word in ["house", "home", "single family"]):
        data["property_type"] = "single_family"
    elif any(word in text.lower() for word in ["condo", "condominium"]):
        data["property_type"] = "condo"
    elif any(word in text.lower() for word in ["townhouse", "townhome"]):
        data["property_type"] = "townhouse"
    
    # Location extraction
    location_patterns = [
        r"([A-Za-z\s]+,\s*[A-Z]{2})",
        r"([A-Za-z\s]+),\s*([A-Za-z\s]+)"
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 1:
                data["property_location"] = match.group(1).strip()
            else:
                data["property_location"] = f"{match.group(1).strip()}, {match.group(2).strip()}"
            break
    
    return data

@tool
def extract_financial_info(text: str) -> Dict[str, Any]:
    """Extract financial information from user input"""
    data = {}
    
    # Credit score (3-digit number between 300-850)
    credit_matches = re.findall(r"(\d{3})", text)
    for match in credit_matches:
        score = int(match)
        if 300 <= score <= 850:
            data["credit_score"] = score
            break
    
    # Down payment
    down_patterns = [
        r"(?:down|put down)\s*(?:payment)?\s*(?:of\s*)?\$?(\d{1,3}(?:,\d{3})*)",
        r"\$(\d{1,3}(?:,\d{3})*)\s*(?:down|as\s+down)"
    ]
    for pattern in down_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount = int(match.group(1).replace(",", ""))
            if amount >= 1000:
                data["down_payment"] = amount
                break
    
    # If no explicit down payment mentioned, look for large dollar amounts
    if "down_payment" not in data:
        amounts = re.findall(r"\$?(\d{1,3}(?:,\d{3})*)", text)
        for amount_str in amounts:
            try:
                amount = int(amount_str.replace(",", ""))
                if 5000 <= amount <= 500000:  # Reasonable down payment range
                    data["down_payment"] = amount
                    break
            except:
                continue
    
    return data

@tool  
def analyze_application_state() -> str:
    """Request application state analysis"""
    return "STATE_ANALYSIS_REQUESTED"

# =============================================================================
# DATABASE TOOLS - Agentic Application Submission
# =============================================================================

class ApplicationSubmissionSchema(BaseModel):
    """Schema for submitting mortgage application - simplified for Llama models"""
    application_data: str = Field(
        description="Complete application data as formatted string: 'session_id|full_name|phone|email|annual_income|employer|employment_type|purchase_price|property_type|property_location|down_payment|credit_score'"
    )

@tool("submit_application_to_database", args_schema=ApplicationSubmissionSchema, parse_docstring=True)
def submit_application_to_database(application_data: str) -> str:
    """Submit completed mortgage application to database.
    
    Use this tool when the customer wants to submit their completed application.
    This will store all collected information in the database and generate an application ID.
    
    Args:
        application_data: Pipe-separated application data string containing:
            session_id|full_name|phone|email|annual_income|employer|employment_type|purchase_price|property_type|property_location|down_payment|credit_score
        
    Returns:
        Success or error message with application ID
    """
    try:
        # Parse the application data string
        parts = application_data.split('|')
        if len(parts) != 12:
            return f" Invalid application data format. Expected 12 fields, got {len(parts)}"
        
        session_id, full_name, phone, email, annual_income_str, employer, employment_type, \
        purchase_price_str, property_type, property_location, down_payment_str, credit_score_str = parts
        
        # Convert numeric fields
        annual_income = int(annual_income_str)
        purchase_price = int(purchase_price_str)
        down_payment = int(down_payment_str)
        credit_score = int(credit_score_str)
        
        # Use unified application lifecycle management
        app_manager = get_application_manager()
        
        # Create conversation context for intent detection
        conversation_context = {
            "full_name": full_name,
            "phone": phone,
            "email": email,
            "annual_income": annual_income,
            "employer": employer,
            "employment_type": employment_type,
            "purchase_price": purchase_price,
            "property_type": property_type,
            "property_location": property_location,
            "down_payment": down_payment,
            "credit_score": credit_score,
            "completion_percentage": 100.0  # All fields provided
        }
        
        # Find or create application through unified system
        result = app_manager.find_or_create_application(
            person_name=full_name,
            conversation_context=conversation_context,
            intent=ApplicationIntent.FINAL_SUBMISSION
        )
        
        if result[0]:  # Application found/created
            application_id, detection_status, phase = result
            logger.info(f"Application {application_id} ready for submission (status: {detection_status})")
            
            # Update phase to SUBMITTED
            app_manager.update_application_phase(application_id, ApplicationPhase.SUBMITTED)
            
        else:
            # Fallback - shouldn't happen with FINAL_SUBMISSION intent
            application_id = f"APP_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
            logger.warning(f"Fallback application creation: {application_id}")
        
        # Calculate completion percentage
        completion_percentage = 100.0
        
        # Store in database
        with get_db_session() as db:
            db_application = MortgageApplicationDB(
                application_id=application_id,
                session_id=session_id,
                full_name=full_name,
                phone=phone,
                email=email,
                annual_income=annual_income,
                employer=employer,
                employment_type=employment_type,
                purchase_price=purchase_price,
                property_type=property_type,
                property_location=property_location,
                down_payment=down_payment,
                credit_score=credit_score,
                status="submitted",
                completion_percentage=completion_percentage,
                next_steps=[
                    "Application review in progress",
                    "Document verification",
                    "Credit check authorization",
                    "Property appraisal scheduling"
                ]
            )
            db.add(db_application)
            db.commit()
        
        logger.info(f"Application {application_id} submitted successfully for session {session_id}")
        
        return f" Excellent! Your mortgage application has been submitted successfully!\n\n" \
               f"**Application ID: {application_id}**\n\n" \
               f"Here's what happens next:\n" \
               f"• You'll receive email confirmations within the next hour\n" \
               f"• Our underwriting team will review your application within 1-2 business days\n" \
               f"• You'll be contacted for document uploads and verification\n" \
               f"• Property appraisal will be scheduled if initially approved\n\n" \
               f"You can reference your application using ID: **{application_id}**\n\n" \
               f"Is there anything else I can help you with regarding your mortgage application?"
    
    except Exception as e:
        logger.error(f"Error submitting application: {str(e)}")
        return f" I apologize, but there was an issue submitting your application: {str(e)}. " \
               f"Please try again in a moment, or let me know if you need assistance."

class ApplicationStatusSchema(BaseModel):
    """Schema for checking application status"""
    application_id: str = Field(description="Application ID to check status for")

@tool("check_application_status", args_schema=ApplicationStatusSchema, parse_docstring=True)
def check_application_status(application_id: str) -> str:
    """Check the status of a submitted mortgage application.
    
    Use this tool when a customer wants to check on their application status
    using their application ID.
    
    Args:
        application_id: The application ID to check status for
        
    Returns:
        Application status information or error message
    """
    try:
        with get_db_session() as db:
            app = db.query(MortgageApplicationDB).filter(
                MortgageApplicationDB.application_id == application_id
            ).first()
            
            if not app:
                return f" No application found with ID: {application_id}. " \
                       f"Please double-check the application ID and try again."
            
            # Format status information
            status_info = f"📋 **Application Status for {application_id}**\n\n" \
                         f"• **Status**: {app.status.title()}\n" \
                         f"• **Completion**: {app.completion_percentage:.1f}%\n" \
                         f"• **Submitted**: {app.submitted_at.strftime('%B %d, %Y at %I:%M %p')}\n" \
                         f"• **Last Updated**: {app.updated_at.strftime('%B %d, %Y at %I:%M %p')}\n\n"
            
            if app.next_steps:
                status_info += "**Next Steps:**\n"
                for i, step in enumerate(app.next_steps, 1):
                    status_info += f"{i}. {step}\n"
                status_info += "\n"
            
            if app.processing_notes:
                status_info += f"**Processing Notes**: {app.processing_notes}\n\n"
                
            status_info += "Is there anything specific about your application you'd like to know more about?"
            
            return status_info
    
    except Exception as e:
        logger.error(f"Error checking application status: {str(e)}")
        return f" There was an error checking the application status: {str(e)}. " \
               f"Please try again or contact support if the issue persists."


# =============================================================================
# REACT AGENT TOOLS - Dynamic UI and Prompt Generation
# =============================================================================

@tool
def generate_contextual_prompts(current_phase: str, collected_data: str, missing_fields: str) -> Dict[str, Any]:
    """
    Generate dynamic clickable prompts based on current application state.
    
    Args:
        current_phase: Current phase of application (e.g., 'personal_info', 'employment', 'property')
        collected_data: JSON string of data already collected
        missing_fields: Comma-separated list of missing required fields
    
    Returns:
        Dict with prompts structure for frontend
    """
    import json
    
    try:
        collected = json.loads(collected_data) if collected_data else {}
    except:
        collected = {}
    
    missing_list = [f.strip() for f in missing_fields.split(',') if f.strip()]
    
    prompts = []
    
    # Generate prompts based on missing fields and current phase
    if 'full_name' in missing_list or 'phone' in missing_list or 'email' in missing_list:
        prompts.extend([
            {"text": "I'll provide my personal information", "icon": "👤", "category": "personal"},
            {"text": "My name is [enter your name]", "icon": "📝", "category": "personal"},
            {"text": "My phone number is [enter phone]", "icon": "📞", "category": "personal"},
            {"text": "My email is [enter email]", "icon": "📧", "category": "personal"}
        ])
    
    if 'annual_income' in missing_list or 'employer' in missing_list:
        prompts.extend([
            {"text": "I'll share my employment details", "icon": "💼", "category": "employment"},
            {"text": "My annual income is $[amount]", "icon": "💰", "category": "employment"},
            {"text": "I work at [company name]", "icon": "🏢", "category": "employment"},
            {"text": "I'm self-employed", "icon": "👨‍💼", "category": "employment"}
        ])
    
    if 'purchase_price' in missing_list or 'property_type' in missing_list:
        prompts.extend([
            {"text": "Let me tell you about the property", "icon": "🏠", "category": "property"},
            {"text": "The purchase price is $[amount]", "icon": "🏷️", "category": "property"},
            {"text": "It's a single-family home", "icon": "🏡", "category": "property"},
            {"text": "It's a condominium", "icon": "🏢", "category": "property"}
        ])
    
    if 'down_payment' in missing_list or 'credit_score' in missing_list:
        prompts.extend([
            {"text": "I'll provide financial information", "icon": "📊", "category": "financial"},
            {"text": "My down payment will be $[amount]", "icon": "💳", "category": "financial"},
            {"text": "My credit score is [score]", "icon": "📈", "category": "financial"},
            {"text": "I need help calculating down payment", "icon": "🧮", "category": "financial"}
        ])
    
    # Add helpful prompts based on current phase
    if current_phase == 'initial':
        prompts.extend([
            {"text": "I'm ready to start my application", "icon": "🚀", "category": "action"},
            {"text": "What information do you need from me?", "icon": "❓", "category": "help"}
        ])
    elif current_phase == 'data_collection':
        prompts.extend([
            {"text": "What else do you need to know?", "icon": "❓", "category": "help"},
            {"text": "Can you check what's missing?", "icon": "🔍", "category": "help"}
        ])
    
    return {
        "type": "dynamic_prompts",
        "phase": current_phase,
        "prompts": prompts,
        "completion_status": f"{len(collected)}/11 fields collected"
    }

@tool  
def generate_next_step_guidance(current_state: str, completion_percentage: float) -> Dict[str, Any]:
    """
    Generate guidance on next steps based on application progress.
    
    Args:
        current_state: JSON string of current application state
        completion_percentage: Percentage complete (0.0 to 1.0)
    
    Returns:
        Dict with next step guidance for user
    """
    import json
    
    try:
        state = json.loads(current_state) if current_state else {}
    except:
        state = {}
    
    if completion_percentage < 0.3:
        return {
            "type": "guidance",
            "message": "Let's start with your basic information - name, phone, and email.",
            "priority": "high",
            "suggestions": [
                "Share your full name",
                "Provide your phone number", 
                "Give us your email address"
            ]
        }
    elif completion_percentage < 0.6:
        return {
            "type": "guidance", 
            "message": "Great progress! Now let's get your employment and income details.",
            "priority": "medium",
            "suggestions": [
                "Tell us about your employer",
                "Share your annual income",
                "Mention your employment type"
            ]
        }
    elif completion_percentage < 0.8:
        return {
            "type": "guidance",
            "message": "Almost there! We need property and financial information.",
            "priority": "medium", 
            "suggestions": [
                "Share the property purchase price",
                "Tell us the property type",
                "Provide your down payment amount"
            ]
        }
    else:
        return {
            "type": "guidance",
            "message": "Excellent! Your application is nearly complete. Just a few final details.",
            "priority": "low",
            "suggestions": [
                "Review your information",
                "Submit your application",
                "Schedule next steps"
            ]
        }


# =============================================================================
# MORTGAGE BUSINESS LOGIC TOOLS - Core Calculations & Assessments
# =============================================================================

@tool
def calculate_debt_to_income_ratio(monthly_income: float, monthly_debts: float) -> Dict[str, Any]:
    """
    Calculate debt-to-income ratio for mortgage qualification.
    
    Args:
        monthly_income: Gross monthly income
        monthly_debts: Total monthly debt obligations
        
    Returns:
        DTI analysis with qualification status
    """
    if monthly_income <= 0:
        return {"error": "Monthly income must be greater than 0"}
    
    dti_ratio = (monthly_debts / monthly_income) * 100
    
    # DTI qualification guidelines
    qualification_status = "excellent" if dti_ratio <= 28 else \
                          "good" if dti_ratio <= 36 else \
                          "marginal" if dti_ratio <= 43 else \
                          "high_risk"
    
    return {
        "dti_ratio": round(dti_ratio, 2),
        "monthly_income": monthly_income,
        "monthly_debts": monthly_debts,
        "qualification_status": qualification_status,
        "analysis": {
            "conventional_loans": "Qualified" if dti_ratio <= 43 else "Not Qualified",
            "fha_loans": "Qualified" if dti_ratio <= 57 else "Not Qualified", 
            "va_loans": "Qualified" if dti_ratio <= 41 else "Manual Underwriting Required"
        },
        "recommendations": [
            "Excellent DTI - Strong loan approval likelihood" if dti_ratio <= 28 else
            "Good DTI - Should qualify for most loan programs" if dti_ratio <= 36 else
            "Consider debt reduction to improve qualification" if dti_ratio > 43 else
            "DTI within acceptable range"
        ],
        "timestamp": datetime.now().isoformat()
    }

@tool
def calculate_loan_to_value_ratio(loan_amount: float, property_value: float) -> Dict[str, Any]:
    """
    Calculate loan-to-value ratio and determine PMI requirements.
    
    Args:
        loan_amount: Requested loan amount
        property_value: Appraised property value
        
    Returns:
        LTV analysis with PMI requirements
    """
    if property_value <= 0:
        return {"error": "Property value must be greater than 0"}
    
    ltv_ratio = (loan_amount / property_value) * 100
    down_payment = property_value - loan_amount
    down_payment_percentage = (down_payment / property_value) * 100
    
    # PMI requirements
    pmi_required = ltv_ratio > 80
    pmi_monthly = 0
    if pmi_required:
        # Typical PMI rates: 0.3% to 1.5% annually
        pmi_annual_rate = 0.005 if ltv_ratio <= 85 else 0.007 if ltv_ratio <= 90 else 0.01
        pmi_monthly = (loan_amount * pmi_annual_rate) / 12
    
    return {
        "ltv_ratio": round(ltv_ratio, 2),
        "loan_amount": loan_amount,
        "property_value": property_value,
        "down_payment": down_payment,
        "down_payment_percentage": round(down_payment_percentage, 2),
        "pmi_required": pmi_required,
        "pmi_monthly_cost": round(pmi_monthly, 2),
        "loan_qualification": {
            "conventional": "Qualified" if ltv_ratio <= 97 else "Not Qualified",
            "fha": "Qualified" if ltv_ratio <= 96.5 else "Not Qualified",
            "va": "Qualified" if ltv_ratio <= 100 else "Not Qualified",
            "usda": "Qualified" if ltv_ratio <= 100 else "Not Qualified"
        },
        "risk_assessment": "Low Risk" if ltv_ratio <= 80 else "Moderate Risk" if ltv_ratio <= 90 else "Higher Risk",
        "timestamp": datetime.now().isoformat()
    }

@tool
def calculate_monthly_payment(loan_amount: float, interest_rate: float, loan_term_years: int) -> Dict[str, Any]:
    """
    Calculate monthly mortgage payment with principal and interest.
    
    Args:
        loan_amount: Total loan amount
        interest_rate: Annual interest rate (e.g., 6.5 for 6.5%)
        loan_term_years: Loan term in years (typically 15 or 30)
        
    Returns:
        Payment breakdown and analysis
    """
    if loan_amount <= 0 or interest_rate < 0 or loan_term_years <= 0:
        return {"error": "Invalid input parameters"}
    
    # Convert annual rate to monthly and years to months
    monthly_rate = (interest_rate / 100) / 12
    num_payments = loan_term_years * 12
    
    # Calculate monthly payment using amortization formula
    if monthly_rate == 0:  # Handle 0% interest rate case
        monthly_payment = loan_amount / num_payments
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                         ((1 + monthly_rate) ** num_payments - 1)
    
    total_payments = monthly_payment * num_payments
    total_interest = total_payments - loan_amount
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "loan_term_years": loan_term_years,
        "total_payments": round(total_payments, 2),
        "total_interest": round(total_interest, 2),
        "interest_percentage": round((total_interest / loan_amount) * 100, 2),
        "payment_breakdown": {
            "principal_and_interest": round(monthly_payment, 2),
            "estimated_property_tax": round(loan_amount * 0.01 / 12, 2),  # 1% annually
            "estimated_insurance": round(loan_amount * 0.003 / 12, 2),     # 0.3% annually
            "estimated_hoa": 150  # Default HOA estimate
        },
        "timestamp": datetime.now().isoformat()
    }

@tool
def assess_affordability(annual_income: float, monthly_debts: float, down_payment: float, 
                        property_price: float, interest_rate: float = 6.5) -> Dict[str, Any]:
    """
    Comprehensive affordability assessment for mortgage applicant.
    
    Args:
        annual_income: Gross annual income
        monthly_debts: Existing monthly debt obligations
        down_payment: Available down payment amount
        property_price: Target property price
        interest_rate: Assumed interest rate (default 6.5%)
        
    Returns:
        Complete affordability analysis with recommendations
    """
    monthly_income = annual_income / 12
    loan_amount = property_price - down_payment
    
    # Calculate monthly payment
    payment_calc = calculate_monthly_payment.invoke({
        'loan_amount': loan_amount, 
        'interest_rate': interest_rate, 
        'loan_term_years': 30
    })
    if "error" in payment_calc:
        return payment_calc
    
    monthly_payment = payment_calc["monthly_payment"]
    
    # Add estimated taxes, insurance, PMI
    estimated_property_tax = property_price * 0.01 / 12  # 1% annually
    estimated_insurance = property_price * 0.003 / 12    # 0.3% annually
    
    # Calculate PMI if needed
    ltv_calc = calculate_loan_to_value_ratio.invoke({
        'loan_amount': loan_amount,
        'property_value': property_price
    })
    pmi_monthly = ltv_calc.get("pmi_monthly_cost", 0)
    
    total_housing_payment = monthly_payment + estimated_property_tax + estimated_insurance + pmi_monthly
    
    # Calculate ratios
    front_end_ratio = (total_housing_payment / monthly_income) * 100  # Housing ratio
    back_end_ratio = ((total_housing_payment + monthly_debts) / monthly_income) * 100  # Total DTI
    
    # Affordability assessment
    can_afford = front_end_ratio <= 28 and back_end_ratio <= 36
    qualification_level = "Strong" if front_end_ratio <= 25 and back_end_ratio <= 33 else \
                         "Good" if front_end_ratio <= 28 and back_end_ratio <= 36 else \
                         "Marginal" if front_end_ratio <= 31 and back_end_ratio <= 43 else \
                         "Challenging"
    
    # Calculate maximum affordable home price
    max_monthly_housing = monthly_income * 0.28  # 28% rule
    max_affordable_payment = max_monthly_housing - estimated_property_tax - estimated_insurance - pmi_monthly
    
    # Reverse calculate max loan amount (simplified)
    if interest_rate > 0:
        monthly_rate = (interest_rate / 100) / 12
        num_payments = 30 * 12
        max_loan_amount = max_affordable_payment * ((1 + monthly_rate) ** num_payments - 1) / \
                         (monthly_rate * (1 + monthly_rate) ** num_payments)
    else:
        max_loan_amount = max_affordable_payment * 360  # 30 years
    
    max_home_price = max_loan_amount + down_payment
    
    return {
        "affordability_assessment": {
            "can_afford": can_afford,
            "qualification_level": qualification_level,
            "confidence_score": 0.85 if can_afford else 0.45
        },
        "financial_ratios": {
            "front_end_ratio": round(front_end_ratio, 2),
            "back_end_ratio": round(back_end_ratio, 2),
            "ltv_ratio": ltv_calc.get("ltv_ratio", 0)
        },
        "payment_breakdown": {
            "principal_interest": round(monthly_payment, 2),
            "property_tax": round(estimated_property_tax, 2),
            "insurance": round(estimated_insurance, 2),
            "pmi": round(pmi_monthly, 2),
            "total_housing": round(total_housing_payment, 2)
        },
        "affordability_limits": {
            "max_home_price": round(max_home_price, 2),
            "current_target": property_price,
            "over_budget": property_price > max_home_price,
            "budget_difference": round(property_price - max_home_price, 2)
        },
        "recommendations": [
            f"Target home price of ${property_price:,.0f} is {'within' if can_afford else 'above'} your budget",
            f"Consider homes up to ${max_home_price:,.0f} for comfortable approval",
            "Increase down payment to reduce monthly costs" if pmi_monthly > 0 else "Great down payment amount",
            f"Your debt-to-income ratio is {qualification_level.lower()}"
        ],
        "timestamp": datetime.now().isoformat()
    }

@tool
def check_loan_program_eligibility(annual_income: float, credit_score: int, down_payment: float,
                                  property_price: float, military_service: bool = False) -> Dict[str, Any]:
    """
    Check eligibility for different loan programs (FHA, VA, Conventional, USDA).
    
    Args:
        annual_income: Gross annual income
        credit_score: Credit score (300-850)
        down_payment: Available down payment
        property_price: Target property price
        military_service: Whether applicant has military service
        
    Returns:
        Eligibility analysis for all loan programs
    """
    down_payment_percentage = (down_payment / property_price) * 100
    loan_amount = property_price - down_payment
    
    programs = {}
    
    # Conventional Loan
    conv_min_credit = 620
    conv_min_down = 3.0  # 3%
    conv_eligible = (credit_score >= conv_min_credit and 
                    down_payment_percentage >= conv_min_down and
                    annual_income >= 30000)
    
    programs["conventional"] = {
        "eligible": conv_eligible,
        "min_credit_score": conv_min_credit,
        "min_down_payment": f"{conv_min_down}%",
        "benefits": ["No government fees", "Can cancel PMI at 80% LTV", "Higher loan limits"],
        "limitations": ["Higher credit requirements", "Stricter DTI ratios"],
        "recommendation": "Best for borrowers with good credit and stable income"
    }
    
    # FHA Loan
    fha_min_credit = 580 if down_payment_percentage >= 3.5 else 500
    fha_min_down = 3.5
    fha_eligible = (credit_score >= fha_min_credit and 
                   down_payment_percentage >= fha_min_down and
                   loan_amount <= 472030)  # 2024 FHA limit (varies by area)
    
    programs["fha"] = {
        "eligible": fha_eligible,
        "min_credit_score": fha_min_credit,
        "min_down_payment": f"{fha_min_down}%",
        "benefits": ["Lower credit requirements", "Lower down payment", "More flexible DTI"],
        "limitations": ["MIP required for life of loan", "Lower loan limits"],
        "recommendation": "Great for first-time buyers with lower credit scores"
    }
    
    # VA Loan
    va_eligible = military_service and credit_score >= 580
    programs["va"] = {
        "eligible": va_eligible,
        "min_credit_score": 580,
        "min_down_payment": "0%",
        "benefits": ["No down payment required", "No PMI", "Competitive rates", "No prepayment penalties"],
        "limitations": ["Military service required", "VA funding fee", "Primary residence only"],
        "recommendation": "Excellent option for qualified veterans and military"
    }
    
    # USDA Rural Development
    # Simplified eligibility (actual USDA has complex income limits and geographic requirements)
    usda_eligible = (annual_income <= 115000 and  # Simplified income limit
                    credit_score >= 640 and
                    down_payment_percentage >= 0)  # Can be 0% down
    
    programs["usda"] = {
        "eligible": usda_eligible,
        "min_credit_score": 640,
        "min_down_payment": "0%",
        "benefits": ["No down payment", "Below-market interest rates", "Low mortgage insurance"],
        "limitations": ["Rural areas only", "Income limits", "Primary residence only"],
        "recommendation": "Perfect for rural property purchases"
    }
    
    # Determine best recommendations
    eligible_programs = [name for name, program in programs.items() if program["eligible"]]
    
    return {
        "loan_programs": programs,
        "eligible_programs": eligible_programs,
        "recommended_program": eligible_programs[0] if eligible_programs else None,
        "applicant_profile": {
            "credit_score": credit_score,
            "down_payment_percentage": round(down_payment_percentage, 2),
            "annual_income": annual_income,
            "military_service": military_service
        },
        "next_steps": [
            f"Apply for {prog} loan" for prog in eligible_programs[:2]
        ] if eligible_programs else [
            "Work on improving credit score",
            "Save for larger down payment",
            "Consider FHA loan options"
        ],
        "timestamp": datetime.now().isoformat()
    }

@tool
def generate_pre_approval_assessment(annual_income: float, monthly_debts: float, credit_score: int,
                                   down_payment: float, employment_years: float = 2.0) -> Dict[str, Any]:
    """
    Generate comprehensive pre-approval assessment.
    
    Args:
        annual_income: Gross annual income
        monthly_debts: Existing monthly debt payments
        credit_score: Credit score (300-850)
        down_payment: Available down payment
        employment_years: Years at current employment
        
    Returns:
        Pre-approval recommendation with loan amount and terms
    """
    monthly_income = annual_income / 12
    
    # Calculate maximum DTI-based loan payment
    max_total_payment = monthly_income * 0.36  # 36% back-end ratio
    max_housing_payment = max_total_payment - monthly_debts
    
    # Estimate max loan amount (using 6.5% rate, 30 year term)
    interest_rate = 6.5
    monthly_rate = (interest_rate / 100) / 12
    num_payments = 30 * 12
    
    # Reverse payment calculation to find max loan amount
    if monthly_rate > 0:
        max_loan_amount = max_housing_payment * ((1 + monthly_rate) ** num_payments - 1) / \
                         (monthly_rate * (1 + monthly_rate) ** num_payments)
    else:
        max_loan_amount = max_housing_payment * 360
    
    # Account for taxes, insurance, PMI (estimate 25% of payment for PITI vs PI)
    max_loan_amount *= 0.75
    
    max_purchase_price = max_loan_amount + down_payment
    
    # Pre-approval strength assessment
    credit_strength = "Excellent" if credit_score >= 740 else \
                     "Good" if credit_score >= 680 else \
                     "Fair" if credit_score >= 620 else \
                     "Poor"
    
    employment_strength = "Strong" if employment_years >= 2 else \
                         "Adequate" if employment_years >= 1 else \
                         "Weak"
    
    down_payment_strength = "Strong" if down_payment >= max_purchase_price * 0.2 else \
                           "Adequate" if down_payment >= max_purchase_price * 0.1 else \
                           "Minimal"
    
    # Overall pre-approval likelihood
    strength_scores = {
        "Excellent": 4, "Strong": 4, "Good": 3, "Adequate": 2, "Fair": 1, "Minimal": 1, "Weak": 0, "Poor": 0
    }
    
    total_score = (strength_scores[credit_strength] + 
                  strength_scores[employment_strength] + 
                  strength_scores[down_payment_strength])
    
    approval_likelihood = "Very High" if total_score >= 10 else \
                         "High" if total_score >= 8 else \
                         "Moderate" if total_score >= 6 else \
                         "Low"
    
    recommended_loan_amount = max_loan_amount * 0.9  # Conservative estimate
    
    return {
        "pre_approval_assessment": {
            "approval_likelihood": approval_likelihood,
            "confidence_score": min(95, total_score * 8),
            "estimated_timeline": "3-5 business days" if total_score >= 8 else "7-10 business days"
        },
        "loan_estimates": {
            "max_loan_amount": round(max_loan_amount, 2),
            "recommended_loan_amount": round(recommended_loan_amount, 2),
            "max_purchase_price": round(max_purchase_price, 2),
            "estimated_interest_rate": f"{interest_rate}% - {interest_rate + 0.5}%"
        },
        "strength_analysis": {
            "credit_profile": credit_strength,
            "employment_stability": employment_strength,
            "down_payment_position": down_payment_strength,
            "overall_strength": approval_likelihood
        },
        "required_documentation": [
            "Pay stubs (last 2 months)",
            "Tax returns (last 2 years)",
            "Bank statements (last 2 months)",
            "Employment verification letter",
            "Credit report authorization",
            "Down payment source documentation"
        ],
        "next_steps": [
            "Submit formal pre-approval application",
            "Gather required documentation",
            "Schedule property search",
            "Connect with real estate agent",
            "Begin shopping for homes"
        ],
        "conditions": [
            "Subject to full income verification",
            "Subject to satisfactory credit review",
            "Subject to property appraisal",
            "Subject to final underwriting approval"
        ],
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# PHASE 2: CREDIT & INCOME VERIFICATION TOOLS
# =============================================================================

@tool
def simulate_credit_check(ssn_last_4: str, full_name: str, date_of_birth: str, 
                         authorization_code: str = "DEMO_AUTH_2024") -> Dict[str, Any]:
    """
    Simulate a comprehensive credit check for mortgage qualification.
    
    Args:
        ssn_last_4: Last 4 digits of Social Security Number
        full_name: Full legal name for verification
        date_of_birth: Date of birth in YYYY-MM-DD format
        authorization_code: Credit authorization code
        
    Returns:
        Detailed credit report simulation with scores and analysis
    """
    import hashlib
    
    # Generate deterministic but realistic credit data based on inputs
    seed = f"{ssn_last_4}{full_name}{date_of_birth}".lower()
    hash_val = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    
    # Generate credit score (weighted toward realistic mortgage applicant range)
    base_score = 580 + (hash_val % 270)  # Range: 580-850
    
    # Adjust for more realistic distribution
    if base_score < 620:
        credit_score = base_score
        tier = "Subprime"
    elif base_score < 680:
        credit_score = base_score + 20  # Boost to fair range
        tier = "Fair"
    elif base_score < 740:
        credit_score = base_score + 10   # Good range
        tier = "Good" 
    else:
        credit_score = min(850, base_score)  # Excellent range
        tier = "Excellent"
    
    # Generate credit profile details
    num_accounts = 3 + (hash_val % 12)
    total_credit_limit = 15000 + (hash_val % 85000)
    current_balance = int(total_credit_limit * (0.1 + ((hash_val % 40) / 100)))
    utilization = (current_balance / total_credit_limit) * 100 if total_credit_limit > 0 else 0
    
    # Credit history factors
    oldest_account_years = 2 + (hash_val % 18)
    payment_history = 95 + (hash_val % 6) if credit_score >= 700 else 85 + (hash_val % 15)
    
    # Generate credit accounts
    account_types = ["Credit Card", "Auto Loan", "Student Loan", "Personal Loan", "Mortgage"]
    accounts = []
    
    for i in range(min(num_accounts, 8)):
        account_type = account_types[i % len(account_types)]
        account_balance = current_balance // num_accounts if num_accounts > 0 else 0
        
        accounts.append({
            "account_type": account_type,
            "creditor": f"Sample {account_type} Company",
            "account_status": "Current" if payment_history > 90 else "30 Days Late",
            "balance": account_balance + (hash_val % 1000),
            "credit_limit": (account_balance + (hash_val % 1000)) * 2 if "Card" in account_type else None,
            "monthly_payment": max(25, (account_balance + (hash_val % 1000)) // 20),
            "opened_date": f"{2024 - (i + 1)}-{((hash_val + i) % 12) + 1:02d}-01"
        })
    
    # Recent inquiries
    recent_inquiries = max(0, (hash_val % 6) - 2)
    
    return {
        "credit_report_summary": {
            "credit_score": credit_score,
            "score_range": "300-850",
            "credit_tier": tier,
            "report_date": datetime.now().isoformat(),
            "bureau": "Demo Credit Bureau"
        },
        "score_factors": {
            "payment_history": f"{payment_history}%",
            "credit_utilization": f"{utilization:.1f}%",
            "length_of_history": f"{oldest_account_years} years",
            "credit_mix": f"{len(set(acc['account_type'] for acc in accounts))} types",
            "recent_inquiries": recent_inquiries
        },
        "credit_accounts": accounts,
        "credit_summary": {
            "total_accounts": num_accounts,
            "total_credit_limit": total_credit_limit,
            "total_balance": current_balance,
            "available_credit": total_credit_limit - current_balance,
            "utilization_ratio": round(utilization, 1)
        },
        "mortgage_qualification": {
            "conventional_loans": "Qualified" if credit_score >= 620 else "Not Qualified",
            "fha_loans": "Qualified" if credit_score >= 580 else "Manual Review Required",
            "va_loans": "Qualified" if credit_score >= 580 else "Manual Review Required",
            "usda_loans": "Qualified" if credit_score >= 640 else "Not Qualified"
        },
        "recommendations": [
            "Excellent credit profile" if credit_score >= 740 else
            "Good credit for most loan programs" if credit_score >= 680 else
            "Consider improving credit before applying" if credit_score < 620 else
            "Fair credit - FHA loans recommended",
            f"Credit utilization at {utilization:.1f}% - {'excellent' if utilization < 10 else 'good' if utilization < 30 else 'consider paying down balances'}",
            f"Payment history at {payment_history}% - {'excellent' if payment_history >= 95 else 'good' if payment_history >= 90 else 'needs improvement'}"
        ],
        "next_steps": [
            "Pre-approval with strong terms available" if credit_score >= 720 else
            "Standard pre-approval process" if credit_score >= 620 else
            "Work on credit improvement before applying"
        ],
        "timestamp": datetime.now().isoformat()
    }

@tool
def verify_employment_history(employer_name: str, job_title: str, employment_years: float,
                            employment_type: str = "full-time", hr_phone: str = None) -> Dict[str, Any]:
    """
    Simulate employment verification for mortgage qualification.
    
    Args:
        employer_name: Current employer company name
        job_title: Current job title/position
        employment_years: Years at current employer
        employment_type: Type of employment (full-time, part-time, contractor, self-employed)
        hr_phone: HR department phone number for verification
        
    Returns:
        Employment verification results and stability assessment
    """
    import random
    
    # Simulate verification process
    verification_successful = True
    
    # Employment stability scoring
    stability_score = 0
    stability_factors = []
    
    if employment_years >= 2:
        stability_score += 40
        stability_factors.append("2+ years at current employer")
    elif employment_years >= 1:
        stability_score += 25
        stability_factors.append("1+ year at current employer")
    else:
        stability_score += 10
        stability_factors.append("Less than 1 year at current employer")
    
    if employment_type == "full-time":
        stability_score += 30
        stability_factors.append("Full-time employment")
    elif employment_type == "part-time":
        stability_score += 15
        stability_factors.append("Part-time employment")
    elif employment_type == "contractor":
        stability_score += 10
        stability_factors.append("Contract employment")
    elif employment_type == "self-employed":
        stability_score += 5
        stability_factors.append("Self-employed")
    
    # Industry stability (simplified simulation)
    stable_industries = ["healthcare", "education", "government", "technology", "finance"]
    if any(industry in employer_name.lower() for industry in stable_industries):
        stability_score += 20
        stability_factors.append("Stable industry sector")
    
    # Job title stability indicators
    management_titles = ["manager", "director", "senior", "lead", "supervisor"]
    if any(title in job_title.lower() for title in management_titles):
        stability_score += 10
        stability_factors.append("Management/senior position")
    
    stability_score = min(100, stability_score)
    
    # Employment verification status
    verification_method = "Automated HR System" if hr_phone else "Manual Verification"
    
    # Generate employment details
    employment_details = {
        "employer_verified": True,
        "position_verified": True,
        "start_date_verified": True,
        "employment_status": "Active" if employment_type != "contractor" else "Contract Active",
        "eligible_for_rehire": True,
        "disciplinary_actions": False
    }
    
    # Risk assessment based on employment type and tenure
    if stability_score >= 80:
        risk_level = "Low Risk"
        loan_impact = "Positive - Strong employment profile"
    elif stability_score >= 60:
        risk_level = "Moderate Risk"
        loan_impact = "Neutral - Standard verification required"
    else:
        risk_level = "Higher Risk"
        loan_impact = "May require additional documentation"
    
    return {
        "verification_summary": {
            "verification_successful": verification_successful,
            "verification_method": verification_method,
            "verification_date": datetime.now().isoformat(),
            "hr_contact_confirmed": hr_phone is not None
        },
        "employment_details": employment_details,
        "stability_assessment": {
            "stability_score": stability_score,
            "risk_level": risk_level,
            "employment_tenure": f"{employment_years} years",
            "employment_type": employment_type,
            "stability_factors": stability_factors
        },
        "mortgage_impact": {
            "loan_qualification_impact": loan_impact,
            "documentation_requirements": [
                "Pay stubs (last 2 months)",
                "Employment verification letter",
                "W-2 forms (last 2 years)" if employment_type == "full-time" else "1099 forms (last 2 years)",
                "Tax returns (last 2 years)" if employment_type in ["self-employed", "contractor"] else None
            ],
            "additional_requirements": [
                "Profit & Loss statements" if employment_type == "self-employed" else None,
                "Contract agreements" if employment_type == "contractor" else None,
                "Business license verification" if employment_type == "self-employed" else None
            ]
        },
        "recommendations": [
            "Strong employment profile for lending" if stability_score >= 80 else
            "Stable employment, standard processing" if stability_score >= 60 else
            "Consider waiting for more tenure or providing additional documentation",
            f"Employment type ({employment_type}) is {'well-suited' if employment_type == 'full-time' else 'acceptable'} for mortgage lending",
            f"Industry stability is {'strong' if any(industry in employer_name.lower() for industry in stable_industries) else 'standard'}"
        ],
        "timestamp": datetime.now().isoformat()
    }

@tool
def validate_income_sources(primary_income: float, secondary_income: float = 0,
                          rental_income: float = 0, investment_income: float = 0,
                          income_documentation: List[str] = None) -> Dict[str, Any]:
    """
    Validate and analyze multiple income sources for mortgage qualification.
    
    Args:
        primary_income: Primary employment income (annual)
        secondary_income: Secondary income source (annual)
        rental_income: Rental property income (annual)
        investment_income: Investment/dividend income (annual)
        income_documentation: List of provided documentation types
        
    Returns:
        Income validation results with qualification analysis
    """
    if income_documentation is None:
        income_documentation = []
    
    total_income = primary_income + secondary_income + rental_income + investment_income
    
    # Income source analysis
    income_sources = []
    
    if primary_income > 0:
        income_sources.append({
            "source_type": "Primary Employment",
            "annual_amount": primary_income,
            "monthly_amount": primary_income / 12,
            "percentage_of_total": (primary_income / total_income) * 100,
            "stability_rating": "High",
            "lender_acceptance": "100% usable"
        })
    
    if secondary_income > 0:
        income_sources.append({
            "source_type": "Secondary Employment",
            "annual_amount": secondary_income,
            "monthly_amount": secondary_income / 12,
            "percentage_of_total": (secondary_income / total_income) * 100,
            "stability_rating": "Moderate",
            "lender_acceptance": "Typically 100% usable with 2-year history"
        })
    
    if rental_income > 0:
        # Lenders typically use 75% of rental income
        usable_rental = rental_income * 0.75
        income_sources.append({
            "source_type": "Rental Income",
            "annual_amount": rental_income,
            "monthly_amount": rental_income / 12,
            "usable_amount": usable_rental,
            "percentage_of_total": (rental_income / total_income) * 100,
            "stability_rating": "Variable",
            "lender_acceptance": "75% usable with property management documentation"
        })
    
    if investment_income > 0:
        income_sources.append({
            "source_type": "Investment Income",
            "annual_amount": investment_income,
            "monthly_amount": investment_income / 12,
            "percentage_of_total": (investment_income / total_income) * 100,
            "stability_rating": "Variable",
            "lender_acceptance": "Averaged over 2 years, may be discounted"
        })
    
    # Calculate qualifying income (what lenders will actually use)
    qualifying_income = primary_income + secondary_income + (rental_income * 0.75) + (investment_income * 0.8)
    
    # Income diversity analysis
    primary_percentage = (primary_income / total_income) * 100
    if primary_percentage >= 80:
        income_diversity = "Low - Heavily dependent on primary income"
        diversity_risk = "Moderate"
    elif primary_percentage >= 60:
        income_diversity = "Moderate - Good primary income with supplemental sources"
        diversity_risk = "Low"
    else:
        income_diversity = "High - Multiple significant income sources"
        diversity_risk = "Low"
    
    # Documentation completeness
    required_docs = ["pay_stubs", "tax_returns", "employment_verification"]
    if secondary_income > 0:
        required_docs.extend(["secondary_employment_docs"])
    if rental_income > 0:
        required_docs.extend(["lease_agreements", "rental_history"])
    if investment_income > 0:
        required_docs.extend(["investment_statements", "tax_schedules"])
    
    provided_docs = set(income_documentation)
    missing_docs = [doc for doc in required_docs if doc not in provided_docs]
    documentation_complete = len(missing_docs) == 0
    
    # Income qualification levels for different loan amounts
    loan_qualifications = {
        "conservative_estimate": qualifying_income * 3,  # 3x income
        "standard_estimate": qualifying_income * 4,     # 4x income
        "aggressive_estimate": qualifying_income * 5    # 5x income (with excellent credit)
    }
    
    return {
        "income_summary": {
            "total_gross_income": total_income,
            "qualifying_income": qualifying_income,
            "monthly_qualifying": qualifying_income / 12,
            "income_reduction": total_income - qualifying_income,
            "reduction_percentage": ((total_income - qualifying_income) / total_income) * 100
        },
        "income_sources": income_sources,
        "income_analysis": {
            "primary_income_percentage": round(primary_percentage, 1),
            "income_diversity": income_diversity,
            "diversity_risk_level": diversity_risk,
            "number_of_sources": len(income_sources)
        },
        "documentation_status": {
            "documentation_complete": documentation_complete,
            "provided_documents": list(provided_docs),
            "missing_documents": missing_docs,
            "completeness_percentage": ((len(required_docs) - len(missing_docs)) / len(required_docs)) * 100
        },
        "loan_qualification_estimates": loan_qualifications,
        "underwriting_considerations": [
            "Strong single-source income" if primary_percentage >= 80 else "Good income diversification",
            "Standard documentation required" if documentation_complete else f"Missing {len(missing_docs)} document types",
            "Rental income subject to vacancy factor" if rental_income > 0 else None,
            "Investment income requires 2-year average" if investment_income > 0 else None,
            "Secondary income strengthens profile" if secondary_income > 0 else None
        ],
        "recommendations": [
            f"Qualifying income of ${qualifying_income:,.0f} supports loan amounts up to ${loan_qualifications['standard_estimate']:,.0f}",
            "Provide complete documentation for all income sources",
            "Consider investment income volatility in loan planning" if investment_income > 0 else None,
            "Rental income adds qualification strength with proper documentation" if rental_income > 0 else None
        ],
        "timestamp": datetime.now().isoformat()
    }

@tool
def analyze_bank_statements(account_type: str, average_balance: float, deposit_frequency: str,
                          large_deposits: List[float] = None, overdrafts: int = 0) -> Dict[str, Any]:
    """
    Analyze bank statement patterns for mortgage qualification.
    
    Args:
        account_type: Type of account (checking, savings, investment)
        average_balance: Average monthly balance
        deposit_frequency: How often deposits occur (weekly, bi-weekly, monthly)
        large_deposits: List of large deposit amounts for verification
        overdrafts: Number of overdrafts in the review period
        
    Returns:
        Bank statement analysis with financial stability assessment
    """
    if large_deposits is None:
        large_deposits = []
    
    # Financial stability scoring
    stability_score = 0
    stability_factors = []
    
    # Balance analysis
    if average_balance >= 10000:
        stability_score += 30
        balance_rating = "Excellent"
        stability_factors.append("Strong account balances")
    elif average_balance >= 5000:
        stability_score += 25
        balance_rating = "Good"
        stability_factors.append("Good account balances")
    elif average_balance >= 2000:
        stability_score += 15
        balance_rating = "Fair"
        stability_factors.append("Adequate account balances")
    else:
        stability_score += 5
        balance_rating = "Low"
        stability_factors.append("Limited account balances")
    
    # Deposit pattern analysis
    if deposit_frequency in ["weekly", "bi-weekly"]:
        stability_score += 20
        deposit_pattern = "Regular employment deposits"
        stability_factors.append("Consistent deposit pattern")
    elif deposit_frequency == "monthly":
        stability_score += 15
        deposit_pattern = "Monthly income pattern"
        stability_factors.append("Regular monthly deposits")
    else:
        stability_score += 5
        deposit_pattern = "Irregular deposit pattern"
        stability_factors.append("Irregular deposit timing")
    
    # Overdraft analysis
    if overdrafts == 0:
        stability_score += 25
        overdraft_status = "No overdrafts"
        stability_factors.append("No overdraft history")
    elif overdrafts <= 2:
        stability_score += 10
        overdraft_status = "Minimal overdrafts"
        stability_factors.append("Occasional overdrafts")
    else:
        stability_score -= 10
        overdraft_status = "Frequent overdrafts"
        stability_factors.append("Concerning overdraft pattern")
    
    # Large deposit analysis
    suspicious_deposits = [dep for dep in large_deposits if dep > average_balance * 2]
    
    stability_score = min(100, max(0, stability_score))
    
    # Overall assessment
    if stability_score >= 80:
        financial_stability = "Excellent"
        loan_impact = "Positive impact on loan approval"
    elif stability_score >= 60:
        financial_stability = "Good"
        loan_impact = "Standard processing expected"
    elif stability_score >= 40:
        financial_stability = "Fair"
        loan_impact = "May require additional documentation"
    else:
        financial_stability = "Concerning"
        loan_impact = "Likely to impact loan approval negatively"
    
    return {
        "account_analysis": {
            "account_type": account_type,
            "average_balance": average_balance,
            "balance_rating": balance_rating,
            "deposit_pattern": deposit_pattern,
            "overdraft_status": overdraft_status
        },
        "stability_assessment": {
            "stability_score": stability_score,
            "financial_stability": financial_stability,
            "stability_factors": stability_factors
        },
        "deposit_analysis": {
            "deposit_frequency": deposit_frequency,
            "large_deposits_count": len(large_deposits),
            "suspicious_deposits": suspicious_deposits,
            "verification_required": len(suspicious_deposits) > 0
        },
        "mortgage_impact": {
            "loan_qualification_impact": loan_impact,
            "down_payment_verification": "Source of funds verified" if average_balance >= 20000 else "Additional verification may be required",
            "reserve_requirements": "Meets reserve requirements" if average_balance >= 5000 else "May not meet reserve requirements"
        },
        "recommendations": [
            f"Account shows {financial_stability.lower()} financial management",
            "Maintain consistent deposit patterns" if deposit_frequency != "regular" else "Continue current deposit pattern",
            "Avoid overdrafts before closing" if overdrafts > 0 else "Excellent account management",
            f"Large deposits require explanation" if suspicious_deposits else "No concerning deposit patterns",
            "Build reserves for closing costs" if average_balance < 10000 else "Strong reserves for closing"
        ],
        "required_documentation": [
            f"Bank statements for {account_type} account",
            "Explanation letters for large deposits" if suspicious_deposits else None,
            "Source of funds documentation" if average_balance >= 50000 else None,
            "Gift letter if applicable" if any(dep > 10000 for dep in large_deposits) else None
        ],
        "timestamp": datetime.now().isoformat()
    }