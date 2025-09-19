"""
Compliance tools for regulatory compliance and audit trail management
Handles TRID compliance, fair lending analysis, and documentation completeness
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
import random

logger = logging.getLogger(__name__)


@tool
def trid_compliance_check(loan_application: Dict[str, Any], loan_estimate_data: Dict[str, Any] = None,
                         closing_disclosure_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Check TRID (TILA-RESPA Integrated Disclosure) compliance for the loan.
    
    Args:
        loan_application: Complete loan application data
        loan_estimate_data: Loan Estimate (LE) form data
        closing_disclosure_data: Closing Disclosure (CD) form data
        
    Returns:
        TRID compliance analysis with any violations
    """
    compliance_id = f"TRID_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    if loan_estimate_data is None:
        loan_estimate_data = {}
    if closing_disclosure_data is None:
        closing_disclosure_data = {}
    
    violations = []
    warnings = []
    
    # Loan Estimate compliance checks
    le_issues = []
    
    # LE must be provided within 3 business days of application
    application_date = loan_application.get("application_date", datetime.now().isoformat())
    app_datetime = datetime.fromisoformat(application_date.replace('Z', '+00:00').replace('+00:00', ''))
    le_due_date = app_datetime + timedelta(days=3)
    
    if not loan_estimate_data:
        le_issues.append("Loan Estimate not yet provided")
    elif "issue_date" in loan_estimate_data:
        le_issue_date = datetime.fromisoformat(loan_estimate_data["issue_date"])
        if le_issue_date > le_due_date:
            violations.append("Loan Estimate provided after 3-business day requirement")
    
    # LE accuracy requirements
    if loan_estimate_data:
        loan_amount = loan_application.get("loan_amount", 0)
        le_loan_amount = loan_estimate_data.get("loan_amount", 0)
        
        if abs(loan_amount - le_loan_amount) > loan_amount * 0.02:  # 2% tolerance
            warnings.append("Loan amount variance between application and LE exceeds 2%")
    
    # Closing Disclosure compliance checks
    cd_issues = []
    
    if closing_disclosure_data:
        # CD must be provided at least 3 business days before closing
        closing_date = loan_application.get("closing_date")
        cd_issue_date = closing_disclosure_data.get("issue_date")
        
        if closing_date and cd_issue_date:
            close_datetime = datetime.fromisoformat(closing_date)
            cd_datetime = datetime.fromisoformat(cd_issue_date)
            required_advance = timedelta(days=3)
            
            if (close_datetime - cd_datetime) < required_advance:
                violations.append("Closing Disclosure not provided 3 business days before closing")
    
    # Fee tolerance analysis
    fee_violations = []
    if loan_estimate_data and closing_disclosure_data:
        # Zero tolerance fees (cannot increase from LE to CD)
        zero_tolerance_fees = ["origination_charges", "credit_report_fee", "appraisal_fee"]
        
        for fee in zero_tolerance_fees:
            le_amount = loan_estimate_data.get(fee, 0)
            cd_amount = closing_disclosure_data.get(fee, 0)
            
            if cd_amount > le_amount:
                fee_violations.append(f"{fee}: Increased from ${le_amount} to ${cd_amount} (zero tolerance)")
        
        # 10% tolerance fees
        ten_percent_fees = ["title_services", "recording_fees", "survey_fee"]
        total_10_percent_increase = 0
        
        for fee in ten_percent_fees:
            le_amount = loan_estimate_data.get(fee, 0)
            cd_amount = closing_disclosure_data.get(fee, 0)
            
            if cd_amount > le_amount:
                total_10_percent_increase += (cd_amount - le_amount)
        
        # Check if total 10% tolerance fees exceed 10% of original estimate
        total_10_percent_le = sum(loan_estimate_data.get(fee, 0) for fee in ten_percent_fees)
        if total_10_percent_increase > total_10_percent_le * 0.10:
            fee_violations.append(f"10% tolerance fees exceeded by ${total_10_percent_increase - (total_10_percent_le * 0.10):.2f}")
    
    # Calculate overall compliance score
    total_checks = 10  # Total number of compliance checks
    violations_count = len(violations) + len(fee_violations)
    warnings_count = len(warnings)
    
    compliance_score = max(0, (total_checks - violations_count * 2 - warnings_count) / total_checks * 100)
    
    return {
        "compliance_id": compliance_id,
        "trid_compliance": {
            "overall_score": round(compliance_score, 1),
            "status": "Compliant" if violations_count == 0 and warnings_count <= 1 else 
                     "Minor Issues" if violations_count <= 1 and warnings_count <= 2 else 
                     "Non-Compliant",
            "violations_count": violations_count,
            "warnings_count": warnings_count
        },
        "loan_estimate_compliance": {
            "timing_compliant": "Loan Estimate provided after 3-business day requirement" not in violations,
            "accuracy_compliant": len([w for w in warnings if "LE" in w or "Loan Estimate" in w]) == 0,
            "issues": le_issues
        },
        "closing_disclosure_compliance": {
            "timing_compliant": "Closing Disclosure not provided 3 business days before closing" not in violations,
            "fee_tolerance_compliant": len(fee_violations) == 0,
            "issues": cd_issues + fee_violations
        },
        "violations": violations,
        "warnings": warnings,
        "remediation_steps": [
            "Correct fee disclosures and reissue forms" if fee_violations else None,
            "Adjust closing timeline to meet disclosure requirements" if any("business days" in v for v in violations) else None,
            "Update loan estimate for accuracy" if any("variance" in w for w in warnings) else None,
            "Document compliance measures in loan file" if compliance_score < 100 else None
        ],
        "next_review_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "timestamp": datetime.now().isoformat()
    }


@tool
def fair_lending_analysis(loan_application: Dict[str, Any], decision_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Perform fair lending analysis to ensure compliance with fair lending laws.
    
    Args:
        loan_application: Complete loan application data
        decision_data: Loan decision and terms data
        
    Returns:
        Fair lending analysis with risk assessment
    """
    analysis_id = f"FL_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    if decision_data is None:
        decision_data = {}
    
    # Extract protected class information (if provided)
    protected_characteristics = {}
    
    # Race/ethnicity analysis
    race_ethnicity = loan_application.get("race_ethnicity", "Not Provided")
    protected_characteristics["race_ethnicity"] = race_ethnicity
    
    # Gender analysis
    gender = loan_application.get("gender", "Not Provided")
    protected_characteristics["gender"] = gender
    
    # Age analysis (if birth date provided)
    birth_date = loan_application.get("date_of_birth")
    age_group = "Unknown"
    if birth_date:
        try:
            birth_datetime = datetime.fromisoformat(birth_date)
            age = (datetime.now() - birth_datetime).days // 365
            if age >= 62:
                age_group = "62+"
            elif age >= 35:
                age_group = "35-61"
            else:
                age_group = "Under 35"
        except:
            age_group = "Unknown"
    
    protected_characteristics["age_group"] = age_group
    
    # Geographic analysis
    property_zip = loan_application.get("property_zip_code", "Unknown")
    protected_characteristics["geographic_area"] = property_zip
    
    # Decision analysis
    decision = decision_data.get("decision", "Pending")
    interest_rate = decision_data.get("interest_rate", 0)
    loan_amount = decision_data.get("loan_amount", 0)
    
    # Risk factors for fair lending violations
    risk_factors = []
    risk_score = 0
    
    # Analyze decision patterns (simulated - in real implementation would compare against portfolio)
    if decision == "Declined":
        risk_score += 3
        risk_factors.append("Loan application declined - requires fair lending documentation")
    
    if interest_rate > 7.0:  # Assuming 7% as above-average rate
        risk_score += 2
        risk_factors.append("Above-average interest rate pricing")
    
    # Geographic concentration risk (simplified)
    if property_zip in ["90210", "10001", "60601"]:  # Example high-value areas
        risk_score += 1
        risk_factors.append("Geographic concentration in high-value area")
    
    # Age-related risks (for protected class)
    if age_group == "62+":
        risk_score += 1
        risk_factors.append("Older applicant - monitor for age discrimination")
    
    # Calculate overall fair lending risk
    risk_level = "Low Risk" if risk_score <= 2 else \
                "Moderate Risk" if risk_score <= 5 else \
                "High Risk"
    
    return {
        "analysis_id": analysis_id,
        "fair_lending_assessment": {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "compliance_status": "Compliant" if risk_score <= 3 else "Review Required",
            "requires_additional_documentation": risk_score > 5
        },
        "protected_characteristics": protected_characteristics,
        "decision_analysis": {
            "decision": decision,
            "interest_rate": interest_rate,
            "loan_amount": loan_amount,
            "pricing_justification_required": interest_rate > 6.5,
            "decision_justification_required": decision == "Declined"
        },
        "risk_factors": risk_factors,
        "monitoring_requirements": [
            "Document business justification for decision" if decision == "Declined" else None,
            "Provide pricing rationale for above-market rates" if interest_rate > 7.0 else None,
            "Monitor for geographic lending patterns" if "Geographic" in str(risk_factors) else None,
            "Review for age-related disparate impact" if age_group == "62+" else None
        ],
        "compliance_actions": [
            "Include fair lending analysis in loan file",
            "Document legitimate business reasons for all decisions",
            "Ensure consistent application of underwriting guidelines",
            "Monitor portfolio for disparate impact patterns"
        ],
        "review_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "timestamp": datetime.now().isoformat()
    }


@tool
def documentation_completeness_check(loan_file_contents: Dict[str, Any], 
                                   loan_type: str = "conventional") -> Dict[str, Any]:
    """
    Check completeness of loan documentation for regulatory compliance.
    
    Args:
        loan_file_contents: Dictionary of documents and data in the loan file
        loan_type: Type of loan (conventional, fha, va, usda)
        
    Returns:
        Documentation completeness analysis
    """
    check_id = f"DOC_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    # Required documents by loan type
    required_docs = {
        "conventional": [
            "loan_application", "credit_report", "income_verification", 
            "employment_verification", "bank_statements", "appraisal_report",
            "title_commitment", "insurance_binder", "closing_disclosure",
            "loan_estimate", "intent_to_proceed"
        ],
        "fha": [
            "loan_application", "credit_report", "income_verification",
            "employment_verification", "bank_statements", "fha_appraisal",
            "title_commitment", "insurance_binder", "closing_disclosure",
            "loan_estimate", "intent_to_proceed", "fha_certifications",
            "mortgage_insurance_certificate"
        ],
        "va": [
            "loan_application", "credit_report", "income_verification",
            "employment_verification", "bank_statements", "va_appraisal",
            "certificate_of_eligibility", "title_commitment", "insurance_binder",
            "closing_disclosure", "loan_estimate", "intent_to_proceed",
            "va_funding_fee_calculation"
        ]
    }
    
    required_for_loan_type = required_docs.get(loan_type, required_docs["conventional"])
    provided_docs = list(loan_file_contents.keys())
    
    # Check document completeness
    missing_docs = [doc for doc in required_for_loan_type if doc not in provided_docs]
    extra_docs = [doc for doc in provided_docs if doc not in required_for_loan_type]
    
    # Document quality analysis
    quality_issues = []
    
    for doc_name, doc_data in loan_file_contents.items():
        if isinstance(doc_data, dict):
            # Check document timestamps
            if "date" in doc_data:
                try:
                    doc_date = datetime.fromisoformat(doc_data["date"])
                    if (datetime.now() - doc_date).days > 120:  # 4 months old
                        quality_issues.append(f"{doc_name}: Document may be outdated (over 4 months old)")
                except:
                    quality_issues.append(f"{doc_name}: Invalid or missing date")
            
            # Check document completeness
            if "complete" in doc_data and not doc_data["complete"]:
                quality_issues.append(f"{doc_name}: Document marked as incomplete")
            
            # Check signatures
            if "signed" in doc_data and not doc_data["signed"]:
                quality_issues.append(f"{doc_name}: Document not signed")
    
    # Calculate completeness percentage
    completeness_percentage = ((len(required_for_loan_type) - len(missing_docs)) / 
                              len(required_for_loan_type)) * 100
    
    # Regulatory compliance assessment
    critical_missing = []
    for doc in missing_docs:
        if doc in ["loan_application", "credit_report", "appraisal_report", "closing_disclosure"]:
            critical_missing.append(doc)
    
    compliance_status = "Compliant" if len(missing_docs) == 0 and len(quality_issues) == 0 else \
                       "Minor Issues" if len(critical_missing) == 0 and len(quality_issues) <= 2 else \
                       "Non-Compliant"
    
    return {
        "check_id": check_id,
        "loan_type": loan_type,
        "documentation_summary": {
            "completeness_percentage": round(completeness_percentage, 1),
            "compliance_status": compliance_status,
            "total_required": len(required_for_loan_type),
            "total_provided": len(provided_docs),
            "missing_count": len(missing_docs),
            "quality_issues_count": len(quality_issues)
        },
        "missing_documents": missing_docs,
        "critical_missing": critical_missing,
        "extra_documents": extra_docs,
        "quality_issues": quality_issues,
        "completion_requirements": [
            f"Obtain {doc.replace('_', ' ').title()}" for doc in missing_docs
        ],
        "quality_improvements": [
            "Update outdated documents" if any("outdated" in issue for issue in quality_issues) else None,
            "Complete partial documents" if any("incomplete" in issue for issue in quality_issues) else None,
            "Obtain missing signatures" if any("not signed" in issue for issue in quality_issues) else None
        ],
        "regulatory_notes": [
            "All critical documents must be present before closing",
            "Document dates must be current and valid",
            "All required signatures must be obtained",
            f"Loan type {loan_type} has specific documentation requirements"
        ],
        "estimated_completion_time": len(missing_docs) * 2 + len(quality_issues),  # Days
        "timestamp": datetime.now().isoformat()
    }


@tool
def regulatory_validation(loan_data: Dict[str, Any], regulation_type: str = "all") -> Dict[str, Any]:
    """
    Validate loan compliance with various regulations.
    
    Args:
        loan_data: Complete loan application and decision data
        regulation_type: Specific regulation to check (all, qm, hpml, hoepa)
        
    Returns:
        Regulatory validation results
    """
    validation_id = f"REG_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    regulations_checked = []
    violations = []
    warnings = []
    
    loan_amount = loan_data.get("loan_amount", 0)
    annual_income = loan_data.get("annual_income", 0)
    interest_rate = loan_data.get("interest_rate", 0)
    monthly_payment = loan_data.get("monthly_payment", 0)
    monthly_income = annual_income / 12 if annual_income > 0 else 0
    
    # Qualified Mortgage (QM) Rule
    if regulation_type in ["all", "qm"]:
        regulations_checked.append("Qualified Mortgage (QM)")
        
        # DTI requirement (43% max for QM)
        monthly_debts = loan_data.get("monthly_debts", 0)
        total_monthly_obligations = monthly_payment + monthly_debts
        dti_ratio = (total_monthly_obligations / monthly_income * 100) if monthly_income > 0 else 100
        
        if dti_ratio > 43:
            violations.append(f"QM DTI ratio exceeds 43% (current: {dti_ratio:.1f}%)")
        
        # Loan term restriction (30 years max for QM safe harbor)
        loan_term = loan_data.get("loan_term_years", 30)
        if loan_term > 30:
            warnings.append(f"Loan term exceeds 30 years QM safe harbor ({loan_term} years)")
        
        # Points and fees limitation
        points_and_fees = loan_data.get("points_and_fees", 0)
        pf_threshold = min(loan_amount * 0.03, 1057) if loan_amount >= 105000 else loan_amount * 0.05
        
        if points_and_fees > pf_threshold:
            violations.append(f"Points and fees exceed QM threshold (${points_and_fees} > ${pf_threshold})")
    
    # Higher-Priced Mortgage Loan (HPML)
    if regulation_type in ["all", "hpml"]:
        regulations_checked.append("Higher-Priced Mortgage Loan (HPML)")
        
        # APOR comparison (simplified - using 6.5% as average prime offer rate)
        apor = 6.5  # Average Prime Offer Rate (simplified)
        hpml_threshold = apor + 1.5  # 1.5% above APOR for first lien
        
        if interest_rate > hpml_threshold:
            warnings.append(f"Loan qualifies as HPML (rate {interest_rate}% > threshold {hpml_threshold}%)")
            
            # Additional HPML requirements
            escrow_required = loan_data.get("escrow_required", False)
            if not escrow_required:
                violations.append("HPML requires escrow for taxes and insurance")
    
    # Home Ownership and Equity Protection Act (HOEPA)
    if regulation_type in ["all", "hoepa"]:
        regulations_checked.append("Home Ownership and Equity Protection Act (HOEPA)")
        
        # HOEPA APR threshold (8% above APOR)
        apor = 6.5
        hoepa_apr_threshold = apor + 8.0
        
        if interest_rate > hoepa_apr_threshold:
            violations.append(f"Loan exceeds HOEPA APR threshold (rate {interest_rate}% > {hoepa_apr_threshold}%)")
        
        # HOEPA points and fees threshold (5% of loan amount)
        points_and_fees = loan_data.get("points_and_fees", 0)
        hoepa_pf_threshold = loan_amount * 0.05
        
        if points_and_fees > hoepa_pf_threshold:
            violations.append(f"Points and fees exceed HOEPA threshold (${points_and_fees} > ${hoepa_pf_threshold})")
    
    # Calculate compliance score
    total_checks = len(regulations_checked) * 3  # Average 3 checks per regulation
    violations_count = len(violations)
    warnings_count = len(warnings)
    
    compliance_score = max(0, (total_checks - violations_count * 3 - warnings_count) / total_checks * 100)
    
    return {
        "validation_id": validation_id,
        "regulatory_compliance": {
            "overall_score": round(compliance_score, 1),
            "compliance_status": "Compliant" if violations_count == 0 else "Non-Compliant",
            "regulations_checked": regulations_checked,
            "violations_count": violations_count,
            "warnings_count": warnings_count
        },
        "violations": violations,
        "warnings": warnings,
        "loan_characteristics": {
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "dti_ratio": round(dti_ratio, 1) if 'dti_ratio' in locals() else None,
            "loan_term": loan_data.get("loan_term_years", 30),
            "points_and_fees": loan_data.get("points_and_fees", 0)
        },
        "required_actions": [
            "Reduce DTI ratio or document compensating factors" if any("DTI" in v for v in violations) else None,
            "Implement HPML requirements" if any("HPML" in str(warnings)) else None,
            "Review loan structure for regulatory compliance" if violations_count > 1 else None,
            "Document compliance analysis in loan file" if compliance_score < 100 else None
        ],
        "compliance_certification_required": violations_count == 0,
        "timestamp": datetime.now().isoformat()
    }


@tool
def audit_trail_generator(loan_id: str, actions_log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate comprehensive audit trail for regulatory compliance.
    
    Args:
        loan_id: Unique loan identifier
        actions_log: List of all actions taken on the loan
        
    Returns:
        Comprehensive audit trail report
    """
    audit_id = f"AUDIT_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    # Process actions log
    audit_events = []
    decision_points = []
    compliance_checkpoints = []
    
    for action in actions_log:
        action_type = action.get("action_type", "unknown")
        timestamp = action.get("timestamp", datetime.now().isoformat())
        user = action.get("user", "system")
        details = action.get("details", {})
        
        audit_event = {
            "timestamp": timestamp,
            "action_type": action_type,
            "user": user,
            "details": details,
            "compliance_relevant": action_type in ["decision", "approval", "denial", "exception", "override"]
        }
        
        audit_events.append(audit_event)
        
        # Track decision points
        if action_type in ["approval", "denial", "conditional_approval"]:
            decision_points.append({
                "decision": action_type,
                "timestamp": timestamp,
                "decision_maker": user,
                "rationale": details.get("rationale", "Not provided")
            })
        
        # Track compliance checkpoints
        if action_type in ["compliance_check", "trid_review", "fair_lending_review"]:
            compliance_checkpoints.append({
                "checkpoint_type": action_type,
                "timestamp": timestamp,
                "result": details.get("result", "Unknown"),
                "reviewer": user
            })
    
    # Generate audit summary
    total_events = len(audit_events)
    compliance_events = len([e for e in audit_events if e["compliance_relevant"]])
    
    # Timeline analysis
    if audit_events:
        first_event = min(audit_events, key=lambda x: x["timestamp"])
        last_event = max(audit_events, key=lambda x: x["timestamp"])
        
        start_time = datetime.fromisoformat(first_event["timestamp"])
        end_time = datetime.fromisoformat(last_event["timestamp"])
        processing_duration = (end_time - start_time).days
    else:
        processing_duration = 0
        start_time = datetime.now()
        end_time = datetime.now()
    
    return {
        "audit_id": audit_id,
        "loan_id": loan_id,
        "audit_summary": {
            "total_events": total_events,
            "compliance_events": compliance_events,
            "decision_points": len(decision_points),
            "compliance_checkpoints": len(compliance_checkpoints),
            "processing_duration_days": processing_duration,
            "audit_completeness": "Complete" if compliance_events >= 3 else "Incomplete"
        },
        "timeline": {
            "loan_start_date": start_time.isoformat(),
            "audit_end_date": end_time.isoformat(),
            "key_milestones": [
                {
                    "milestone": "Application Received",
                    "date": first_event["timestamp"] if audit_events else datetime.now().isoformat()
                },
                {
                    "milestone": "Final Decision",
                    "date": decision_points[-1]["timestamp"] if decision_points else "Pending"
                }
            ]
        },
        "audit_events": audit_events,
        "decision_points": decision_points,
        "compliance_checkpoints": compliance_checkpoints,
        "regulatory_compliance": {
            "trid_compliance_documented": any("trid" in cp["checkpoint_type"] for cp in compliance_checkpoints),
            "fair_lending_reviewed": any("fair_lending" in cp["checkpoint_type"] for cp in compliance_checkpoints),
            "decision_rationale_documented": all("rationale" in dp and dp["rationale"] != "Not provided" for dp in decision_points),
            "audit_trail_complete": total_events >= 5 and compliance_events >= 2
        },
        "audit_certification": {
            "audit_complete": compliance_events >= 3 and len(decision_points) >= 1,
            "regulatory_ready": all([
                any("trid" in cp["checkpoint_type"] for cp in compliance_checkpoints),
                len(decision_points) >= 1,
                total_events >= 5
            ]),
            "examiner_ready": True  # Simplified for demo
        },
        "recommendations": [
            "Document additional compliance checkpoints" if compliance_events < 3 else None,
            "Provide decision rationale for all approval/denial actions" if any("rationale" not in dp or dp["rationale"] == "Not provided" for dp in decision_points) else None,
            "Complete TRID compliance documentation" if not any("trid" in cp["checkpoint_type"] for cp in compliance_checkpoints) else None,
            "Audit trail meets regulatory standards" if compliance_events >= 3 and len(decision_points) >= 1 else None
        ],
        "timestamp": datetime.now().isoformat()
    }
