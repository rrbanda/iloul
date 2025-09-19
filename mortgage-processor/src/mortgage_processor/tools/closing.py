"""
Closing tools for closing coordination and finalization
Handles closing document preparation, coordination, and post-closing activities
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
import random

logger = logging.getLogger(__name__)


@tool
def prepare_closing_documents(loan_data: Dict[str, Any], property_data: Dict[str, Any] = None,
                            borrower_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Prepare all required closing documents for the loan.
    
    Args:
        loan_data: Complete loan information including terms and conditions
        property_data: Property information including title and insurance
        borrower_data: Borrower information for document preparation
        
    Returns:
        Closing document preparation status and checklist
    """
    preparation_id = f"CLOSE_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    if property_data is None:
        property_data = {}
    if borrower_data is None:
        borrower_data = {}
    
    # Required closing documents
    required_documents = [
        {
            "document": "Closing Disclosure",
            "description": "Final loan terms and closing costs",
            "responsible_party": "Lender",
            "deadline": (datetime.now() + timedelta(days=3)).isoformat(),
            "status": "In Preparation"
        },
        {
            "document": "Promissory Note",
            "description": "Borrower's promise to repay the loan",
            "responsible_party": "Lender",
            "deadline": (datetime.now() + timedelta(days=5)).isoformat(),
            "status": "Not Started"
        },
        {
            "document": "Deed of Trust/Mortgage",
            "description": "Security instrument for the loan",
            "responsible_party": "Lender",
            "deadline": (datetime.now() + timedelta(days=5)).isoformat(),
            "status": "Not Started"
        },
        {
            "document": "Title Insurance Policy",
            "description": "Protection against title defects",
            "responsible_party": "Title Company",
            "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
            "status": "Ordered"
        },
        {
            "document": "Property Insurance Binder",
            "description": "Evidence of property insurance coverage",
            "responsible_party": "Borrower",
            "deadline": (datetime.now() + timedelta(days=1)).isoformat(),
            "status": "Pending"
        },
        {
            "document": "Final Walkthrough Report",
            "description": "Property condition verification",
            "responsible_party": "Real Estate Agent",
            "deadline": (datetime.now() + timedelta(days=14)).isoformat(),
            "status": "Scheduled"
        },
        {
            "document": "Funding Authorization",
            "description": "Authorization to fund the loan",
            "responsible_party": "Lender",
            "deadline": (datetime.now() + timedelta(days=14)).isoformat(),
            "status": "Pending Approval"
        }
    ]
    
    # Add loan-specific documents
    loan_type = loan_data.get("loan_type", "conventional")
    if loan_type.lower() == "va":
        required_documents.append({
            "document": "VA Funding Fee Disclosure",
            "description": "VA funding fee calculation and disclosure",
            "responsible_party": "Lender",
            "deadline": (datetime.now() + timedelta(days=3)).isoformat(),
            "status": "Not Started"
        })
    elif loan_type.lower() == "fha":
        required_documents.append({
            "document": "FHA Mortgage Insurance Disclosure",
            "description": "FHA mortgage insurance requirements",
            "responsible_party": "Lender",
            "deadline": (datetime.now() + timedelta(days=3)).isoformat(),
            "status": "Not Started"
        })
    
    # Calculate preparation status
    total_docs = len(required_documents)
    completed_docs = len([doc for doc in required_documents if doc["status"] == "Complete"])
    in_progress_docs = len([doc for doc in required_documents if doc["status"] in ["In Preparation", "Ordered", "Scheduled"]])
    
    preparation_percentage = (completed_docs + (in_progress_docs * 0.5)) / total_docs * 100
    
    return {
        "preparation_id": preparation_id,
        "document_summary": {
            "total_documents": total_docs,
            "completed": completed_docs,
            "in_progress": in_progress_docs,
            "not_started": total_docs - completed_docs - in_progress_docs,
            "preparation_percentage": round(preparation_percentage, 1)
        },
        "required_documents": required_documents,
        "preparation_timeline": {
            "estimated_completion": (datetime.now() + timedelta(days=14)).isoformat(),
            "critical_path_items": [
                doc["document"] for doc in required_documents 
                if datetime.fromisoformat(doc["deadline"]) <= datetime.now() + timedelta(days=3)
            ]
        },
        "loan_details": {
            "loan_amount": loan_data.get("loan_amount", 0),
            "loan_type": loan_type,
            "interest_rate": loan_data.get("interest_rate", 0),
            "property_address": property_data.get("address", "Not provided")
        },
        "next_steps": [
            "Complete Closing Disclosure preparation",
            "Coordinate with title company for title insurance",
            "Obtain borrower insurance binder",
            "Schedule final walkthrough",
            "Prepare loan documents for execution"
        ],
        "responsible_parties": {
            "lender": len([doc for doc in required_documents if doc["responsible_party"] == "Lender"]),
            "borrower": len([doc for doc in required_documents if doc["responsible_party"] == "Borrower"]),
            "title_company": len([doc for doc in required_documents if doc["responsible_party"] == "Title Company"]),
            "other": len([doc for doc in required_documents if doc["responsible_party"] not in ["Lender", "Borrower", "Title Company"]])
        },
        "timestamp": datetime.now().isoformat()
    }


@tool
def coordinate_title_escrow(property_address: str, loan_amount: float, 
                          title_company: str = None, escrow_instructions: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Coordinate title and escrow services for the closing.
    
    Args:
        property_address: Complete property address
        loan_amount: Loan amount for escrow calculations
        title_company: Selected title company name
        escrow_instructions: Special escrow instructions
        
    Returns:
        Title and escrow coordination status
    """
    coordination_id = f"TITLE_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    if title_company is None:
        title_company = "Demo Title & Escrow Company"
    if escrow_instructions is None:
        escrow_instructions = {}
    
    # Title work components
    title_work = [
        {
            "component": "Title Search",
            "description": "Research property ownership history",
            "status": "In Progress",
            "estimated_completion": (datetime.now() + timedelta(days=5)).isoformat(),
            "cost": 150.00
        },
        {
            "component": "Title Examination",
            "description": "Review title search results for issues",
            "status": "Pending",
            "estimated_completion": (datetime.now() + timedelta(days=7)).isoformat(),
            "cost": 200.00
        },
        {
            "component": "Title Insurance Commitment",
            "description": "Issue title insurance commitment",
            "status": "Pending",
            "estimated_completion": (datetime.now() + timedelta(days=9)).isoformat(),
            "cost": loan_amount * 0.0006  # 0.06% of loan amount
        },
        {
            "component": "Survey Review",
            "description": "Review property survey for boundary issues",
            "status": "Ordered",
            "estimated_completion": (datetime.now() + timedelta(days=10)).isoformat(),
            "cost": 350.00
        }
    ]
    
    # Escrow services
    escrow_services = [
        {
            "service": "Escrow Account Setup",
            "description": "Establish neutral escrow account",
            "status": "Complete",
            "cost": 250.00
        },
        {
            "service": "Document Preparation",
            "description": "Prepare closing and recording documents",
            "status": "In Progress",
            "cost": 300.00
        },
        {
            "service": "Closing Coordination",
            "description": "Schedule and coordinate closing meeting",
            "status": "Pending",
            "cost": 150.00
        },
        {
            "service": "Recording Services",
            "description": "Record documents with county recorder",
            "status": "Pending",
            "cost": 85.00
        }
    ]
    
    # Calculate total costs
    title_costs = sum(item["cost"] for item in title_work)
    escrow_costs = sum(item["cost"] for item in escrow_services)
    total_costs = title_costs + escrow_costs
    
    # Identify potential issues
    potential_issues = []
    
    # Simulate common title issues
    if random.choice([True, False]):
        potential_issues.append({
            "issue": "Unpaid Property Taxes",
            "description": "Outstanding property taxes must be paid at closing",
            "severity": "Medium",
            "resolution": "Calculate and collect tax prorations at closing"
        })
    
    if random.choice([True, False]):
        potential_issues.append({
            "issue": "Easement on Property",
            "description": "Utility easement identified in title search",
            "severity": "Low",
            "resolution": "Verify easement doesn't affect property use"
        })
    
    return {
        "coordination_id": coordination_id,
        "title_company": title_company,
        "property_address": property_address,
        "coordination_summary": {
            "title_work_progress": len([item for item in title_work if item["status"] == "Complete"]) / len(title_work) * 100,
            "escrow_progress": len([item for item in escrow_services if item["status"] == "Complete"]) / len(escrow_services) * 100,
            "estimated_completion": (datetime.now() + timedelta(days=12)).isoformat(),
            "total_estimated_costs": round(total_costs, 2)
        },
        "title_work": title_work,
        "escrow_services": escrow_services,
        "cost_breakdown": {
            "title_work_costs": round(title_costs, 2),
            "escrow_service_costs": round(escrow_costs, 2),
            "total_costs": round(total_costs, 2),
            "lender_paid": round(total_costs * 0.3, 2),  # Lender typically pays some costs
            "borrower_paid": round(total_costs * 0.7, 2)
        },
        "potential_issues": potential_issues,
        "next_actions": [
            "Complete title search and examination",
            "Resolve any title issues identified",
            "Prepare title insurance commitment",
            "Schedule closing date and time",
            "Coordinate document signing"
        ],
        "contact_information": {
            "title_officer": "Jane Smith, Senior Title Officer",
            "escrow_officer": "Bob Johnson, Escrow Officer",
            "phone": "(555) 123-4567",
            "email": "closing@demotitle.com"
        },
        "timestamp": datetime.now().isoformat()
    }


@tool
def calculate_closing_costs(loan_data: Dict[str, Any], property_data: Dict[str, Any] = None,
                          cost_selections: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Calculate detailed closing costs breakdown for the loan.
    
    Args:
        loan_data: Complete loan information including amount and terms
        property_data: Property information for cost calculations
        cost_selections: Borrower selections for optional services
        
    Returns:
        Detailed closing costs calculation
    """
    calculation_id = f"COSTS_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    if property_data is None:
        property_data = {}
    if cost_selections is None:
        cost_selections = {}
    
    loan_amount = loan_data.get("loan_amount", 0)
    property_value = property_data.get("value", loan_amount * 1.2)  # Assume 20% down if not provided
    loan_type = loan_data.get("loan_type", "conventional")
    interest_rate = loan_data.get("interest_rate", 6.5)
    
    # Origination charges (A. Origination Charges)
    origination_charges = {
        "origination_fee": loan_amount * 0.01,  # 1% of loan amount
        "discount_points": loan_amount * cost_selections.get("points_purchased", 0) * 0.01,
        "processing_fee": 795.00,
        "underwriting_fee": 850.00,
        "application_fee": 500.00
    }
    
    # Services borrower cannot shop for (B. Services You Cannot Shop For)
    cannot_shop_services = {
        "appraisal_fee": 650.00,
        "credit_report_fee": 75.00,
        "flood_certification": 25.00,
        "tax_monitoring": 95.00,
        "tax_status_research": 85.00
    }
    
    # Services borrower can shop for (C. Services You Can Shop For)
    can_shop_services = {
        "survey_fee": 350.00,
        "title_insurance": property_value * 0.006,
        "title_search": 200.00,
        "attorney_fees": 750.00,
        "home_inspection": cost_selections.get("home_inspection", 0) or 450.00
    }
    
    # Government recording and transfer charges (E. Taxes and Government Fees)
    government_fees = {
        "recording_fees": 125.00,
        "transfer_tax": property_value * 0.001,  # 0.1% of property value
        "city_tax": property_value * 0.0005 if property_data.get("city_tax_applicable", True) else 0
    }
    
    # Prepaids (F. Prepaids)
    monthly_payment = loan_data.get("monthly_payment", loan_amount * (interest_rate/100/12) * 1.2)  # Estimate
    prepaids = {
        "homeowners_insurance": 1200.00,  # Annual premium
        "mortgage_insurance": loan_amount * 0.005 if loan_amount/property_value > 0.8 else 0,  # Annual MIP
        "prepaid_interest": (loan_amount * interest_rate/100/365) * 15,  # 15 days interest
        "property_tax_reserves": (property_value * 0.012) / 12 * 3,  # 3 months taxes
        "insurance_reserves": 1200.00 / 12 * 2  # 2 months insurance
    }
    
    # Initial escrow payment (G. Initial Escrow Payment at Closing)
    escrow_payment = {
        "property_taxes": property_value * 0.012 / 12 * 6,  # 6 months
        "homeowners_insurance": 1200.00 / 12 * 6,  # 6 months
        "mortgage_insurance": (loan_amount * 0.005 / 12 * 6) if loan_amount/property_value > 0.8 else 0
    }
    
    # Other costs (H. Other)
    other_costs = {
        "home_warranty": cost_selections.get("home_warranty", 0) or 450.00,
        "pest_inspection": 125.00,
        "hoa_transfer_fee": 150.00 if property_data.get("hoa_applicable", False) else 0
    }
    
    # Loan-specific fees
    if loan_type.lower() == "va":
        origination_charges["va_funding_fee"] = loan_amount * 0.023  # 2.3% for first-time use
    elif loan_type.lower() == "fha":
        origination_charges["fha_upfront_mip"] = loan_amount * 0.0175  # 1.75% upfront MIP
    
    # Calculate totals
    section_totals = {
        "origination_charges": sum(origination_charges.values()),
        "cannot_shop_services": sum(cannot_shop_services.values()),
        "can_shop_services": sum(can_shop_services.values()),
        "government_fees": sum(government_fees.values()),
        "prepaids": sum(prepaids.values()),
        "escrow_payment": sum(escrow_payment.values()),
        "other_costs": sum(other_costs.values())
    }
    
    total_closing_costs = sum(section_totals.values())
    
    # Cash to close calculation
    down_payment = property_value - loan_amount
    cash_to_close = total_closing_costs + down_payment
    
    return {
        "calculation_id": calculation_id,
        "loan_details": {
            "loan_amount": loan_amount,
            "property_value": property_value,
            "loan_type": loan_type,
            "interest_rate": interest_rate
        },
        "closing_cost_breakdown": {
            "A_origination_charges": {
                "items": origination_charges,
                "total": round(section_totals["origination_charges"], 2)
            },
            "B_cannot_shop_services": {
                "items": cannot_shop_services,
                "total": round(section_totals["cannot_shop_services"], 2)
            },
            "C_can_shop_services": {
                "items": can_shop_services,
                "total": round(section_totals["can_shop_services"], 2)
            },
            "E_government_fees": {
                "items": government_fees,
                "total": round(section_totals["government_fees"], 2)
            },
            "F_prepaids": {
                "items": prepaids,
                "total": round(section_totals["prepaids"], 2)
            },
            "G_escrow_payment": {
                "items": escrow_payment,
                "total": round(section_totals["escrow_payment"], 2)
            },
            "H_other_costs": {
                "items": other_costs,
                "total": round(section_totals["other_costs"], 2)
            }
        },
        "cost_summary": {
            "total_closing_costs": round(total_closing_costs, 2),
            "down_payment": round(down_payment, 2),
            "cash_to_close": round(cash_to_close, 2),
            "closing_costs_percentage": round((total_closing_costs / loan_amount) * 100, 2)
        },
        "cost_comparison": {
            "national_average": round(loan_amount * 0.025, 2),  # 2.5% average
            "compared_to_average": "Below Average" if total_closing_costs < loan_amount * 0.025 else "Above Average",
            "variance": round(total_closing_costs - (loan_amount * 0.025), 2)
        },
        "shopping_opportunities": [
            f"Title insurance: Shop for competitive rates (current: ${can_shop_services['title_insurance']:.2f})",
            f"Attorney fees: Compare local attorney rates (current: ${can_shop_services['attorney_fees']:.2f})",
            f"Home inspection: Optional service (current: ${can_shop_services.get('home_inspection', 450):.2f})"
        ],
        "payment_timeline": {
            "due_at_application": round(origination_charges.get("application_fee", 0), 2),
            "due_before_closing": round(section_totals["cannot_shop_services"] + section_totals["can_shop_services"], 2),
            "due_at_closing": round(total_closing_costs - origination_charges.get("application_fee", 0), 2)
        },
        "timestamp": datetime.now().isoformat()
    }


@tool
def schedule_closing_meeting(participants: List[str], preferred_date: str = None,
                           location_preference: str = None) -> Dict[str, Any]:
    """
    Schedule the closing meeting with all required participants.
    
    Args:
        participants: List of participants (borrower, seller, agents, etc.)
        preferred_date: Preferred closing date (YYYY-MM-DD format)
        location_preference: Preferred location (title_company, lender, attorney)
        
    Returns:
        Closing meeting scheduling details
    """
    scheduling_id = f"SCHED_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    # Default participants if not provided
    if not participants:
        participants = ["borrower", "seller", "borrower_agent", "listing_agent", "title_officer"]
    
    # Default preferred date (7-14 days from now)
    if preferred_date is None:
        preferred_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    
    if location_preference is None:
        location_preference = "title_company"
    
    # Generate available time slots
    available_slots = []
    base_date = datetime.strptime(preferred_date, '%Y-%m-%d')
    
    for day_offset in [-2, -1, 0, 1, 2]:  # 5 day window around preferred date
        slot_date = base_date + timedelta(days=day_offset)
        
        # Skip weekends
        if slot_date.weekday() >= 5:
            continue
            
        # Morning and afternoon slots
        for hour in [9, 10, 11, 14, 15, 16]:
            slot_time = slot_date.replace(hour=hour, minute=0)
            available_slots.append({
                "datetime": slot_time.isoformat(),
                "date": slot_time.strftime('%Y-%m-%d'),
                "time": slot_time.strftime('%I:%M %p'),
                "day_of_week": slot_time.strftime('%A'),
                "available": random.choice([True, True, True, False])  # Most slots available
            })
    
    # Filter to available slots
    available_slots = [slot for slot in available_slots if slot["available"]]
    
    # Recommend best slot (closest to preferred date and time)
    if available_slots:
        recommended_slot = min(available_slots, 
                             key=lambda x: abs((datetime.fromisoformat(x["datetime"]) - base_date).total_seconds()))
    else:
        recommended_slot = None
    
    # Participant coordination
    participant_details = []
    for participant in participants:
        participant_details.append({
            "role": participant,
            "required": participant in ["borrower", "seller", "title_officer"],
            "contact_method": "email_and_phone",
            "confirmation_status": "pending",
            "special_requirements": "None"
        })
    
    # Location details
    location_details = {
        "title_company": {
            "name": "Demo Title & Escrow Company",
            "address": "123 Title Plaza, Suite 200, Anytown, ST 12345",
            "phone": "(555) 123-4567",
            "parking": "Free parking available",
            "amenities": ["Conference room", "Notary services", "Document copies"]
        },
        "lender": {
            "name": "Demo Mortgage Lender",
            "address": "456 Lending Lane, Financial District, Anytown, ST 12345",
            "phone": "(555) 234-5678",
            "parking": "Validated parking",
            "amenities": ["Conference room", "Refreshments", "Wi-Fi"]
        },
        "attorney": {
            "name": "Demo Legal Services",
            "address": "789 Law Street, Legal District, Anytown, ST 12345",
            "phone": "(555) 345-6789",
            "parking": "Street parking",
            "amenities": ["Private office", "Notary services"]
        }
    }
    
    selected_location = location_details.get(location_preference, location_details["title_company"])
    
    return {
        "scheduling_id": scheduling_id,
        "scheduling_summary": {
            "preferred_date": preferred_date,
            "available_slots_count": len(available_slots),
            "recommended_slot": recommended_slot,
            "total_participants": len(participants),
            "location": location_preference
        },
        "recommended_appointment": recommended_slot,
        "available_time_slots": available_slots[:8],  # Show first 8 available slots
        "participants": participant_details,
        "location_details": selected_location,
        "preparation_requirements": [
            "All participants must bring valid photo ID",
            "Borrower must bring certified funds for closing costs",
            "Final walkthrough must be completed before closing",
            "All loan conditions must be satisfied",
            "Insurance binder must be provided"
        ],
        "estimated_duration": "45-90 minutes",
        "coordination_notes": [
            "Confirm all participants 24 hours before closing",
            "Review closing disclosure with borrower before meeting",
            "Ensure all documents are prepared and reviewed",
            "Coordinate fund transfer timing",
            "Plan for document recording after signing"
        ],
        "backup_options": [
            "Remote/mobile closing available",
            "Evening appointments by special arrangement",
            "Weekend closings for urgent situations"
        ],
        "contact_information": {
            "closing_coordinator": "Sarah Wilson",
            "phone": selected_location["phone"],
            "email": "closings@demotitle.com",
            "emergency_contact": "(555) 999-0000"
        },
        "timestamp": datetime.now().isoformat()
    }


@tool
def post_closing_coordination(loan_id: str, closing_date: str, 
                            recording_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Coordinate post-closing activities and loan delivery.
    
    Args:
        loan_id: Unique loan identifier
        closing_date: Date the loan was closed (YYYY-MM-DD format)
        recording_info: Document recording information
        
    Returns:
        Post-closing coordination status and next steps
    """
    coordination_id = f"POST_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    if recording_info is None:
        recording_info = {}
    
    closing_datetime = datetime.strptime(closing_date, '%Y-%m-%d')
    
    # Post-closing checklist
    post_closing_tasks = [
        {
            "task": "Document Recording",
            "description": "Record deed and mortgage with county recorder",
            "responsible_party": "Title Company",
            "due_date": (closing_datetime + timedelta(days=1)).isoformat(),
            "status": recording_info.get("recording_status", "In Progress"),
            "priority": "Critical"
        },
        {
            "task": "Loan Funding Confirmation",
            "description": "Confirm loan funds have been disbursed",
            "responsible_party": "Lender",
            "due_date": closing_datetime.isoformat(),
            "status": "Complete",
            "priority": "Critical"
        },
        {
            "task": "Title Insurance Policy Issuance",
            "description": "Issue final title insurance policy",
            "responsible_party": "Title Company",
            "due_date": (closing_datetime + timedelta(days=30)).isoformat(),
            "status": "Pending",
            "priority": "High"
        },
        {
            "task": "Loan Delivery to Investor",
            "description": "Deliver loan package to secondary market investor",
            "responsible_party": "Lender",
            "due_date": (closing_datetime + timedelta(days=60)).isoformat(),
            "status": "Not Started",
            "priority": "High"
        },
        {
            "task": "Escrow Account Setup",
            "description": "Establish escrow account for taxes and insurance",
            "responsible_party": "Loan Servicer",
            "due_date": (closing_datetime + timedelta(days=45)).isoformat(),
            "status": "In Progress",
            "priority": "Medium"
        },
        {
            "task": "Welcome Package to Borrower",
            "description": "Send loan servicing information to borrower",
            "responsible_party": "Loan Servicer",
            "due_date": (closing_datetime + timedelta(days=10)).isoformat(),
            "status": "Scheduled",
            "priority": "Medium"
        },
        {
            "task": "Quality Control Review",
            "description": "Post-closing quality control audit",
            "responsible_party": "Lender",
            "due_date": (closing_datetime + timedelta(days=30)).isoformat(),
            "status": "Scheduled",
            "priority": "Medium"
        }
    ]
    
    # Calculate completion status
    completed_tasks = len([task for task in post_closing_tasks if task["status"] == "Complete"])
    in_progress_tasks = len([task for task in post_closing_tasks if task["status"] == "In Progress"])
    critical_pending = len([task for task in post_closing_tasks if task["priority"] == "Critical" and task["status"] != "Complete"])
    
    completion_percentage = (completed_tasks + (in_progress_tasks * 0.5)) / len(post_closing_tasks) * 100
    
    # Loan delivery preparation
    loan_delivery_items = [
        "Original promissory note",
        "Recorded deed of trust/mortgage",
        "Closing disclosure",
        "Title insurance policy",
        "Property appraisal",
        "Income and employment verification",
        "Credit report",
        "Property insurance evidence",
        "Compliance certifications"
    ]
    
    # Quality control checkpoints
    qc_checkpoints = [
        {
            "checkpoint": "Document Completeness",
            "description": "Verify all required documents are in loan file",
            "status": "Pending",
            "due_date": (closing_datetime + timedelta(days=15)).isoformat()
        },
        {
            "checkpoint": "Compliance Review",
            "description": "Verify regulatory compliance requirements met",
            "status": "Pending",
            "due_date": (closing_datetime + timedelta(days=20)).isoformat()
        },
        {
            "checkpoint": "Funding Verification",
            "description": "Confirm proper loan funding and disbursement",
            "status": "Complete",
            "due_date": closing_datetime.isoformat()
        }
    ]
    
    return {
        "coordination_id": coordination_id,
        "loan_id": loan_id,
        "closing_date": closing_date,
        "post_closing_summary": {
            "completion_percentage": round(completion_percentage, 1),
            "total_tasks": len(post_closing_tasks),
            "completed_tasks": completed_tasks,
            "critical_pending": critical_pending,
            "estimated_completion": (closing_datetime + timedelta(days=60)).isoformat()
        },
        "post_closing_tasks": post_closing_tasks,
        "loan_delivery": {
            "delivery_deadline": (closing_datetime + timedelta(days=60)).isoformat(),
            "required_documents": loan_delivery_items,
            "investor_requirements": "Standard agency delivery requirements",
            "delivery_method": "Electronic via investor portal"
        },
        "quality_control": {
            "qc_checkpoints": qc_checkpoints,
            "qc_completion_deadline": (closing_datetime + timedelta(days=30)).isoformat(),
            "audit_requirements": "Standard post-closing audit procedures"
        },
        "borrower_communications": {
            "welcome_package_sent": "Scheduled for " + (closing_datetime + timedelta(days=10)).strftime('%Y-%m-%d'),
            "first_payment_due": (closing_datetime + timedelta(days=30)).strftime('%Y-%m-%d'),
            "servicing_contact": "Demo Loan Servicing - (555) 123-9999",
            "online_account_setup": "Available at www.demoloanservicing.com"
        },
        "critical_deadlines": [
            {
                "deadline": "Document recording",
                "date": (closing_datetime + timedelta(days=1)).isoformat(),
                "status": recording_info.get("recording_status", "In Progress")
            },
            {
                "deadline": "Loan delivery to investor",
                "date": (closing_datetime + timedelta(days=60)).isoformat(),
                "status": "Pending"
            }
        ],
        "next_actions": [
            "Confirm document recording completion",
            "Begin loan delivery package preparation",
            "Schedule quality control review",
            "Monitor critical task completion",
            "Coordinate with loan servicer for borrower communications"
        ],
        "timestamp": datetime.now().isoformat()
    }
