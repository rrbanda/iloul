"""
 agentic client tools for mortgage document processing.

These tools only extract data and provide information.
The AI agent makes ALL validation decisions based on configuration rules.
"""

import logging
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from llama_stack_client.lib.agents.client_tool import client_tool
from .models import DocumentType

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