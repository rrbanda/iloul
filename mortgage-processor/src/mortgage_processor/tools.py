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
from .models import DocumentType
from .database import get_db_session, MortgageApplicationDB

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
            return f"❌ Invalid application data format. Expected 12 fields, got {len(parts)}"
        
        session_id, full_name, phone, email, annual_income_str, employer, employment_type, \
        purchase_price_str, property_type, property_location, down_payment_str, credit_score_str = parts
        
        # Convert numeric fields
        annual_income = int(annual_income_str)
        purchase_price = int(purchase_price_str)
        down_payment = int(down_payment_str)
        credit_score = int(credit_score_str)
        
        # Generate unique application ID
        application_id = f"APP_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate completion percentage (assume all fields are now provided)
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
        
        return f"✅ Excellent! Your mortgage application has been submitted successfully!\n\n" \
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
        return f"❌ I apologize, but there was an issue submitting your application: {str(e)}. " \
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
                return f"❌ No application found with ID: {application_id}. " \
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
        return f"❌ There was an error checking the application status: {str(e)}. " \
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