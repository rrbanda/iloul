"""
Underwriting tools for comprehensive loan decision making
Handles risk analysis, guideline compliance, and loan approval decisions
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
import random

logger = logging.getLogger(__name__)


@tool
def comprehensive_risk_analysis(application_data: Dict[str, Any], credit_data: Dict[str, Any],
                               property_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Perform comprehensive risk analysis for loan underwriting.
    
    Args:
        application_data: Complete application information
        credit_data: Credit report and analysis data
        property_data: Property assessment and appraisal data
        
    Returns:
        Detailed risk analysis with scoring
    """
    if property_data is None:
        property_data = {}
    
    risk_analysis_id = f"RISK_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    # Credit risk factors
    credit_score = credit_data.get("credit_score", 650)
    credit_risk_score = 0
    if credit_score >= 740:
        credit_risk_score = 10
    elif credit_score >= 680:
        credit_risk_score = 8
    elif credit_score >= 620:
        credit_risk_score = 6
    else:
        credit_risk_score = 3
    
    # Income stability risk
    employment_years = application_data.get("employment_years", 2)
    employment_type = application_data.get("employment_type", "full-time")
    
    income_risk_score = 0
    if employment_type == "full-time" and employment_years >= 2:
        income_risk_score = 10
    elif employment_type == "full-time" and employment_years >= 1:
        income_risk_score = 8
    elif employment_type in ["part-time", "contractor"] and employment_years >= 2:
        income_risk_score = 6
    else:
        income_risk_score = 4
    
    # Property risk factors
    property_risk_score = property_data.get("risk_score", 7)  # Default moderate risk
    
    # Debt-to-income risk
    annual_income = application_data.get("annual_income", 75000)
    monthly_debts = application_data.get("monthly_debts", 800)
    monthly_income = annual_income / 12
    dti_ratio = (monthly_debts / monthly_income) * 100 if monthly_income > 0 else 50
    
    dti_risk_score = 0
    if dti_ratio <= 28:
        dti_risk_score = 10
    elif dti_ratio <= 36:
        dti_risk_score = 8
    elif dti_ratio <= 43:
        dti_risk_score = 6
    else:
        dti_risk_score = 3
    
    # Loan-to-value risk
    purchase_price = application_data.get("purchase_price", 300000)
    down_payment = application_data.get("down_payment", 60000)
    loan_amount = purchase_price - down_payment
    ltv_ratio = (loan_amount / purchase_price) * 100
    
    ltv_risk_score = 0
    if ltv_ratio <= 80:
        ltv_risk_score = 10
    elif ltv_ratio <= 90:
        ltv_risk_score = 8
    elif ltv_ratio <= 95:
        ltv_risk_score = 6
    else:
        ltv_risk_score = 4
    
    # Calculate overall risk score
    total_risk_score = (credit_risk_score + income_risk_score + dti_risk_score + ltv_risk_score + property_risk_score) / 5
    
    risk_level = "Low Risk" if total_risk_score >= 8 else \
                "Moderate Risk" if total_risk_score >= 6 else \
                "High Risk"
    
    return {
        "analysis_id": risk_analysis_id,
        "overall_assessment": {
            "risk_level": risk_level,
            "risk_score": round(total_risk_score, 2),
            "approval_recommendation": "Approve" if total_risk_score >= 7 else "Approve with Conditions" if total_risk_score >= 5 else "Decline"
        },
        "risk_factors": {
            "credit_risk": {
                "score": credit_risk_score,
                "credit_score": credit_score,
                "assessment": "Excellent" if credit_risk_score >= 9 else "Good" if credit_risk_score >= 7 else "Fair" if credit_risk_score >= 5 else "Poor"
            },
            "income_stability": {
                "score": income_risk_score,
                "employment_years": employment_years,
                "employment_type": employment_type,
                "assessment": "Strong" if income_risk_score >= 8 else "Adequate" if income_risk_score >= 6 else "Weak"
            },
            "debt_to_income": {
                "score": dti_risk_score,
                "dti_ratio": round(dti_ratio, 2),
                "assessment": "Excellent" if dti_risk_score >= 9 else "Good" if dti_risk_score >= 7 else "Marginal" if dti_risk_score >= 5 else "High"
            },
            "loan_to_value": {
                "score": ltv_risk_score,
                "ltv_ratio": round(ltv_ratio, 2),
                "assessment": "Conservative" if ltv_risk_score >= 9 else "Standard" if ltv_risk_score >= 7 else "Aggressive"
            },
            "property_risk": {
                "score": property_risk_score,
                "assessment": "Low Risk" if property_risk_score >= 8 else "Moderate Risk" if property_risk_score >= 6 else "High Risk"
            }
        },
        "mitigating_factors": [
            "Strong credit history" if credit_risk_score >= 8 else None,
            "Stable employment" if income_risk_score >= 8 else None,
            "Conservative LTV" if ltv_risk_score >= 8 else None,
            "Low DTI ratio" if dti_risk_score >= 8 else None
        ],
        "risk_mitigations": [
            "Require PMI" if ltv_ratio > 80 else None,
            "Additional income verification" if income_risk_score < 7 else None,
            "Property insurance requirements" if property_risk_score < 7 else None,
            "Co-signer consideration" if total_risk_score < 6 else None
        ],
        "timestamp": datetime.now().isoformat()
    }


@tool
def loan_decision_engine(risk_analysis: Dict[str, Any], loan_type: str = "conventional",
                        loan_amount: float = 300000) -> Dict[str, Any]:
    """
    Make loan approval decision based on risk analysis and guidelines.
    
    Args:
        risk_analysis: Output from comprehensive_risk_analysis
        loan_type: Type of loan (conventional, fha, va, usda)
        loan_amount: Requested loan amount
        
    Returns:
        Loan decision with conditions and terms
    """
    decision_id = f"DEC_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    risk_score = risk_analysis.get("overall_assessment", {}).get("risk_score", 5)
    risk_level = risk_analysis.get("overall_assessment", {}).get("risk_level", "Moderate Risk")
    
    # Decision logic based on risk score and loan type
    if risk_score >= 8:
        decision = "Approved"
        conditions = ["Standard loan conditions"]
        interest_rate_adjustment = 0.0
    elif risk_score >= 6:
        decision = "Approved with Conditions"
        conditions = [
            "Additional income verification required",
            "Property appraisal review",
            "Final employment verification"
        ]
        interest_rate_adjustment = 0.125  # +0.125%
    elif risk_score >= 4:
        decision = "Counter-Offer"
        conditions = [
            "Reduced loan amount recommended",
            "Higher down payment required",
            "Co-signer required",
            "Additional reserves required"
        ]
        interest_rate_adjustment = 0.25  # +0.25%
    else:
        decision = "Declined"
        conditions = [
            "Credit score below minimum requirements",
            "Debt-to-income ratio too high",
            "Insufficient income stability"
        ]
        interest_rate_adjustment = 0.0
    
    # Loan type specific adjustments
    base_rate = 6.5  # Current market rate
    loan_type_adjustments = {
        "conventional": 0.0,
        "fha": -0.25,
        "va": -0.125,
        "usda": -0.375
    }
    
    final_rate = base_rate + loan_type_adjustments.get(loan_type, 0.0) + interest_rate_adjustment
    
    # Calculate loan terms
    monthly_payment = 0
    if decision in ["Approved", "Approved with Conditions", "Counter-Offer"]:
        if decision == "Counter-Offer":
            loan_amount *= 0.9  # Reduce loan amount by 10%
        
        monthly_rate = final_rate / 100 / 12
        num_payments = 30 * 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    
    return {
        "decision_id": decision_id,
        "loan_decision": {
            "decision": decision,
            "decision_date": datetime.now().isoformat(),
            "risk_assessment": risk_level,
            "confidence_level": random.uniform(0.85, 0.98)
        },
        "loan_terms": {
            "approved_amount": loan_amount if decision != "Declined" else 0,
            "interest_rate": round(final_rate, 3),
            "loan_term_years": 30,
            "monthly_payment": round(monthly_payment, 2),
            "loan_type": loan_type
        },
        "conditions": conditions,
        "expiration_date": (datetime.now() + timedelta(days=60)).isoformat(),
        "next_steps": [
            "Provide requested documentation" if decision == "Approved with Conditions" else None,
            "Consider loan modifications" if decision == "Counter-Offer" else None,
            "Proceed to closing" if decision == "Approved" else None,
            "Work on credit improvement" if decision == "Declined" else None,
            "Lock interest rate within 30 days" if decision in ["Approved", "Approved with Conditions"] else None
        ],
        "underwriter_notes": f"Decision based on risk score of {risk_score}/10. {risk_level} profile.",
        "timestamp": datetime.now().isoformat()
    }


@tool
def guideline_compliance_check(application_data: Dict[str, Any], loan_type: str = "conventional") -> Dict[str, Any]:
    """
    Check application compliance with loan program guidelines.
    
    Args:
        application_data: Complete application data
        loan_type: Type of loan program to check against
        
    Returns:
        Compliance check results with any violations
    """
    compliance_id = f"COMP_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    violations = []
    warnings = []
    compliance_score = 0
    total_checks = 0
    
    # Common compliance checks
    credit_score = application_data.get("credit_score", 650)
    annual_income = application_data.get("annual_income", 75000)
    employment_years = application_data.get("employment_years", 2)
    purchase_price = application_data.get("purchase_price", 300000)
    down_payment = application_data.get("down_payment", 60000)
    monthly_debts = application_data.get("monthly_debts", 800)
    
    loan_amount = purchase_price - down_payment
    ltv_ratio = (loan_amount / purchase_price) * 100
    dti_ratio = (monthly_debts / (annual_income / 12)) * 100
    
    # Loan type specific guidelines
    if loan_type.lower() == "conventional":
        total_checks = 6
        
        # Credit score requirement
        if credit_score >= 620:
            compliance_score += 1
        else:
            violations.append("Credit score below 620 minimum for conventional loans")
        
        # DTI requirement
        if dti_ratio <= 43:
            compliance_score += 1
        else:
            violations.append("Debt-to-income ratio exceeds 43% maximum")
        
        # LTV requirement
        if ltv_ratio <= 97:
            compliance_score += 1
        else:
            violations.append("Loan-to-value ratio exceeds 97% maximum")
        
        # Employment history
        if employment_years >= 2:
            compliance_score += 1
        else:
            warnings.append("Employment history less than 2 years")
            compliance_score += 0.5
        
        # Income requirements
        if annual_income >= 25000:
            compliance_score += 1
        else:
            violations.append("Income below minimum threshold")
        
        # Down payment requirements
        if down_payment >= purchase_price * 0.03:
            compliance_score += 1
        else:
            violations.append("Down payment below 3% minimum")
    
    elif loan_type.lower() == "fha":
        total_checks = 6
        
        # Credit score requirement
        if credit_score >= 580:
            compliance_score += 1
        elif credit_score >= 500:
            compliance_score += 0.5
            warnings.append("Credit score requires 10% down payment")
        else:
            violations.append("Credit score below 500 minimum for FHA loans")
        
        # DTI requirement
        if dti_ratio <= 57:
            compliance_score += 1
        else:
            violations.append("Debt-to-income ratio exceeds 57% maximum for FHA")
        
        # LTV requirement
        if ltv_ratio <= 96.5:
            compliance_score += 1
        else:
            violations.append("Loan-to-value ratio exceeds 96.5% maximum for FHA")
        
        # Employment history
        if employment_years >= 1:
            compliance_score += 1
        else:
            warnings.append("Employment history less than 1 year")
            compliance_score += 0.5
        
        # Income requirements
        if annual_income >= 20000:
            compliance_score += 1
        else:
            violations.append("Income below minimum threshold for FHA")
        
        # Down payment requirements
        min_down = 0.035 if credit_score >= 580 else 0.10
        if down_payment >= purchase_price * min_down:
            compliance_score += 1
        else:
            violations.append(f"Down payment below {min_down*100}% minimum for FHA")
    
    # Add more loan types as needed...
    
    compliance_percentage = (compliance_score / total_checks) * 100 if total_checks > 0 else 0
    
    return {
        "compliance_id": compliance_id,
        "loan_type": loan_type,
        "compliance_summary": {
            "compliance_percentage": round(compliance_percentage, 1),
            "status": "Compliant" if compliance_percentage >= 90 and len(violations) == 0 else 
                     "Minor Issues" if compliance_percentage >= 80 else 
                     "Non-Compliant",
            "violations_count": len(violations),
            "warnings_count": len(warnings)
        },
        "violations": violations,
        "warnings": warnings,
        "compliance_details": {
            "checks_passed": int(compliance_score),
            "total_checks": total_checks,
            "credit_score_check": credit_score,
            "dti_ratio_check": round(dti_ratio, 2),
            "ltv_ratio_check": round(ltv_ratio, 2),
            "employment_check": employment_years,
            "income_check": annual_income,
            "down_payment_check": down_payment
        },
        "recommendations": [
            "Address all violations before proceeding" if violations else None,
            "Consider alternative loan programs" if len(violations) > 2 else None,
            "Manual underwriting may be required" if warnings else None,
            "Standard processing recommended" if compliance_percentage >= 90 and len(violations) == 0 else None
        ],
        "timestamp": datetime.now().isoformat()
    }


@tool
def generate_approval_conditions(risk_analysis: Dict[str, Any], compliance_check: Dict[str, Any],
                               property_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate specific approval conditions based on analysis results.
    
    Args:
        risk_analysis: Risk analysis results
        compliance_check: Compliance check results  
        property_data: Property assessment data
        
    Returns:
        Detailed approval conditions and requirements
    """
    if property_data is None:
        property_data = {}
    
    conditions_id = f"COND_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    conditions = []
    
    # Risk-based conditions
    risk_score = risk_analysis.get("overall_assessment", {}).get("risk_score", 5)
    risk_factors = risk_analysis.get("risk_factors", {})
    
    if risk_factors.get("credit_risk", {}).get("score", 5) < 7:
        conditions.append({
            "condition": "Credit Verification",
            "description": "Provide explanation letter for any credit issues",
            "required_documents": ["Credit explanation letter"],
            "deadline": (datetime.now() + timedelta(days=10)).isoformat()
        })
    
    if risk_factors.get("income_stability", {}).get("score", 5) < 7:
        conditions.append({
            "condition": "Employment Verification",
            "description": "Verbal verification of employment (VVOE) required",
            "required_documents": ["Employment verification form", "Recent pay stub"],
            "deadline": (datetime.now() + timedelta(days=5)).isoformat()
        })
    
    if risk_factors.get("debt_to_income", {}).get("score", 5) < 7:
        conditions.append({
            "condition": "Income Documentation",
            "description": "Provide additional income documentation",
            "required_documents": ["Bank statements (3 months)", "Bonus/overtime history"],
            "deadline": (datetime.now() + timedelta(days=7)).isoformat()
        })
    
    # Compliance-based conditions
    violations = compliance_check.get("violations", [])
    warnings = compliance_check.get("warnings", [])
    
    if violations:
        conditions.append({
            "condition": "Guideline Compliance",
            "description": "Address all guideline violations",
            "required_documents": ["Updated application with corrections"],
            "deadline": (datetime.now() + timedelta(days=15)).isoformat()
        })
    
    # Property-based conditions
    if property_data:
        property_risk = property_data.get("risk_level", "Moderate Risk")
        if property_risk == "High Risk":
            conditions.append({
                "condition": "Property Assessment",
                "description": "Additional property inspections required",
                "required_documents": ["Professional inspection report"],
                "deadline": (datetime.now() + timedelta(days=21)).isoformat()
            })
    
    # Standard conditions
    conditions.extend([
        {
            "condition": "Property Appraisal",
            "description": "Property must appraise at or above purchase price",
            "required_documents": ["Completed appraisal report"],
            "deadline": (datetime.now() + timedelta(days=14)).isoformat()
        },
        {
            "condition": "Title Insurance",
            "description": "Clear title required with title insurance",
            "required_documents": ["Title commitment", "Title insurance policy"],
            "deadline": (datetime.now() + timedelta(days=30)).isoformat()
        },
        {
            "condition": "Property Insurance",
            "description": "Homeowner's insurance with lender as mortgagee",
            "required_documents": ["Insurance binder", "Proof of payment"],
            "deadline": (datetime.now() + timedelta(days=30)).isoformat()
        }
    ])
    
    return {
        "conditions_id": conditions_id,
        "approval_conditions": conditions,
        "conditions_summary": {
            "total_conditions": len(conditions),
            "standard_conditions": len([c for c in conditions if c["condition"] in ["Property Appraisal", "Title Insurance", "Property Insurance"]]),
            "risk_based_conditions": len(conditions) - 3,
            "earliest_deadline": min([c["deadline"] for c in conditions]),
            "latest_deadline": max([c["deadline"] for c in conditions])
        },
        "condition_categories": {
            "documentation": len([c for c in conditions if "documentation" in c["description"].lower()]),
            "verification": len([c for c in conditions if "verification" in c["description"].lower()]),
            "property": len([c for c in conditions if "property" in c["description"].lower() or "appraisal" in c["description"].lower()]),
            "insurance": len([c for c in conditions if "insurance" in c["description"].lower()])
        },
        "completion_instructions": [
            "All conditions must be satisfied prior to closing",
            "Submit documents in order of deadline priority",
            "Contact underwriter with questions about specific conditions",
            "Conditional approval expires in 60 days from issue date"
        ],
        "timestamp": datetime.now().isoformat()
    }


@tool
def exception_analysis(application_data: Dict[str, Any], guideline_violations: List[str]) -> Dict[str, Any]:
    """
    Analyze exceptions and determine if manual underwriting is warranted.
    
    Args:
        application_data: Complete application data
        guideline_violations: List of guideline violations
        
    Returns:
        Exception analysis with manual underwriting recommendation
    """
    exception_id = f"EXC_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    # Analyze compensating factors
    compensating_factors = []
    
    credit_score = application_data.get("credit_score", 650)
    annual_income = application_data.get("annual_income", 75000)
    employment_years = application_data.get("employment_years", 2)
    down_payment = application_data.get("down_payment", 60000)
    purchase_price = application_data.get("purchase_price", 300000)
    assets = application_data.get("assets_savings", 50000)
    
    down_payment_percentage = (down_payment / purchase_price) * 100
    
    # Strong compensating factors
    if down_payment_percentage >= 20:
        compensating_factors.append("Large down payment (20%+ reduces lender risk)")
    
    if assets >= down_payment * 2:
        compensating_factors.append("Significant reserves (2+ months of payments)")
    
    if employment_years >= 5:
        compensating_factors.append("Long-term employment stability (5+ years)")
    
    if annual_income >= 100000:
        compensating_factors.append("High income level reduces payment burden")
    
    if credit_score >= 700:
        compensating_factors.append("Strong credit history despite other factors")
    
    # Evaluate exception potential
    exception_score = len(compensating_factors) * 2 - len(guideline_violations)
    
    manual_underwriting_recommendation = "Recommended" if exception_score >= 2 else \
                                       "Consider" if exception_score >= 0 else \
                                       "Not Recommended"
    
    return {
        "exception_id": exception_id,
        "exception_analysis": {
            "manual_underwriting_recommendation": manual_underwriting_recommendation,
            "exception_score": exception_score,
            "violation_count": len(guideline_violations),
            "compensating_factor_count": len(compensating_factors)
        },
        "guideline_violations": guideline_violations,
        "compensating_factors": compensating_factors,
        "manual_underwriting_rationale": [
            f"Strong compensating factors: {len(compensating_factors)}" if compensating_factors else "Limited compensating factors",
            f"Guideline violations: {len(guideline_violations)}",
            "Exception may be warranted based on overall risk profile" if exception_score >= 2 else "Standard guidelines should be followed"
        ],
        "required_documentation": [
            "Detailed explanation letter from borrower" if guideline_violations else None,
            "Additional financial documentation" if manual_underwriting_recommendation == "Recommended" else None,
            "Character reference letters" if exception_score < 0 else None,
            "Enhanced property documentation" if "property" in str(guideline_violations).lower() else None
        ],
        "approval_likelihood": "High" if exception_score >= 3 else \
                              "Moderate" if exception_score >= 1 else \
                              "Low",
        "timestamp": datetime.now().isoformat()
    }
