from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, date
from enum import Enum


class DocumentType(str, Enum):
    DRIVER_LICENSE = "driver_license"
    BANK_STATEMENT = "bank_statement"
    TAX_STATEMENT = "tax_statement"
    PAY_STUB = "pay_stub"
    PASSPORT = "passport"


class LoanType(str, Enum):
    HOME_LOAN = "HomeLoan"
    WORKING_CAPITAL = "WorkingCapital"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    NEEDS_REPLACEMENT = "needs_replacement"


class ValidationIssue(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    issue_type: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    suggested_action: Optional[str] = None


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    file_name: str
    file_size: int
    upload_timestamp: datetime
    mime_type: str
    document_type: DocumentType


class DocumentValidationResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    document_id: str
    document_type: DocumentType
    status: DocumentStatus
    is_expired: bool
    expiration_date: Optional[date] = None
    scan_quality_score: float  # 0.0 to 1.0
    issues_found: List[ValidationIssue] = []
    extracted_data: Dict[str, Any] = {}
    confidence_score: float  # 0.0 to 1.0


class Customer(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    cust_id: str = Field(..., description="Customer ID")
    name: str = Field(..., description="Customer full name")
    age: int = Field(..., ge=18, le=120, description="Customer age")
    address: str = Field(..., description="Customer address")
    ssn: str = Field(..., description="Social Security Number")
    loan_type: LoanType = Field(..., description="Type of loan requested")
    authorize_credit_check: bool = Field(..., description="Credit check authorization")
    created_at: datetime = Field(default_factory=datetime.now)


class DocumentRequirement(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    document_type: DocumentType
    required: bool
    quantity_needed: int = 1
    description: str


class MortgageApplication(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    application_id: str
    customer: Customer
    documents_required: List[DocumentRequirement]
    documents_uploaded: List[DocumentValidationResult] = []
    overall_status: Literal["incomplete", "under_review", "approved", "rejected"] = "incomplete"
    processing_notes: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ProcessingResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    application_id: str
    processing_status: Literal["success", "partial", "failed"]
    documents_processed: int
    valid_documents: int
    invalid_documents: int
    missing_documents: List[DocumentType] = []
    next_steps: List[str] = []
    estimated_completion: Optional[str] = None
    urla_1003_generated: bool = False


class ExtractedPersonalInfo(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    ssn_last_four: Optional[str] = None
    address: Optional[str] = None
    license_number: Optional[str] = None
    license_expiration: Optional[date] = None


class ExtractedIncomeInfo(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    annual_income: Optional[float] = None
    monthly_income: Optional[float] = None
    employer_name: Optional[str] = None
    employment_duration: Optional[str] = None
    income_source: Optional[str] = None
    pay_period: Optional[str] = None


class CreditCheckAuthorization(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    authorized: bool
    authorization_date: datetime
    customer_signature: Optional[str] = None
    terms_accepted: bool = False
