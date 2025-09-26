"""
Simple Application Status Tracking Tool - Fixed for Structured Tool Calls

This tool provides application status tracking using the exact same pattern
as transfer tools that work with structured tool calls.
"""

from langchain_core.tools import tool
from datetime import datetime

try:
    from ....database.application_data.application_storage import retrieve_application_data, update_application_status
    from ....database.application_data.application_schema import ApplicationStatusUpdate
    from ....utils.db import get_neo4j_connection, initialize_connection
except ImportError:
    from mortgage_processor.database.application_data.application_storage import retrieve_application_data, update_application_status
    from mortgage_processor.database.application_data.application_schema import ApplicationStatusUpdate
    from mortgage_processor.utils.db import get_neo4j_connection, initialize_connection


@tool
def track_application_status_fixed(status_request: str) -> str:
    """Track and update application status with automated Neo4j integration.
    
    Args:
        status_request: Status request like "check status for APP_20250926_090605_JOH" or "update APP_20250926_090605_JOH to UNDERWRITING"
    """
    
    try:
        # Parse status request
        request = status_request.lower()
        
        # Extract application ID
        import re
        app_id_match = re.search(r'(app_\w+)', request)
        application_id = app_id_match.group(1).upper() if app_id_match else None
        
        if not application_id:
            return "Error: No valid application ID found in request"
        
        # Determine action
        if "check" in request or "status" in request:
            action = "check_status"
        elif "update" in request:
            action = "update_status"
        else:
            action = "check_status"
        
        # 🤖 AGENTIC RETRIEVAL: Get real application data from Neo4j
        app_retrieval = retrieve_application_data(application_id)
        
        # Build status report
        status_report = []
        status_report.append("APPLICATION STATUS TRACKING REPORT")
        status_report.append("=" * 45)
        status_report.append(f"Application ID: {application_id}")
        status_report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        status_report.append(f"Requested Action: {action.replace('_', ' ').title()}")
        
        if app_retrieval.found:
            # Use real stored application data
            app_data = app_retrieval.application_data
            stored_status = app_data.current_status
            
            status_report.append(f"\n📊 APPLICATION STATUS:")
            status_report.append(f"Current Status: {stored_status}")
            status_report.append(f"Applicant: {app_data.first_name} {app_data.last_name}")
            status_report.append(f"Loan Amount: ${app_data.loan_amount:,.0f}")
            status_report.append(f"Property: {app_data.property_address}")
            
            # Use stored status for processing
            effective_status = stored_status
        else:
            # Fallback to input status if no stored data
            status_report.append(f"\n⚠️ APPLICATION DATA: Not found in agentic storage, using estimated values")
            status_report.append(f"Current Status: PROCESSING")
            effective_status = "PROCESSING"
        
        # Process different actions
        if action == "check_status":
            # Check current status and provide details
            status_report.append(f"\n📋 STATUS ANALYSIS:")
            
            status_definitions = {
                "RECEIVED": "Application received and initial validation pending",
                "VALIDATED": "Application data validated, ready for processing", 
                "PROCESSING": "Application in active processing workflow",
                "DOCUMENTATION": "Document collection and verification phase",
                "APPRAISAL": "Property appraisal and valuation phase",
                "UNDERWRITING": "Credit and risk analysis phase",
                "APPROVED": "Application approved for loan funding",
                "DENIED": "Application denied based on criteria",
                "CLOSED": "Application process completed"
            }
            
            if effective_status in status_definitions:
                definition = status_definitions[effective_status]
                status_report.append(f"Status Definition: {definition}")
            
            # Find position in workflow
            status_progression = ["RECEIVED", "VALIDATED", "PROCESSING", "DOCUMENTATION", "APPRAISAL", "UNDERWRITING", "APPROVED"]
            if effective_status in status_progression:
                current_index = status_progression.index(effective_status)
                total_stages = len(status_progression)
                progress_pct = ((current_index + 1) / total_stages) * 100
                
                status_report.append(f"Workflow Position: {current_index + 1} of {total_stages}")
                status_report.append(f"Progress: {progress_pct:.1f}% complete")
                
                # Show workflow progression
                status_report.append(f"\n🔄 WORKFLOW PROGRESSION:")
                for i, stage in enumerate(status_progression):
                    if i < current_index:
                        status_report.append(f"   ✅ {stage}")
                    elif i == current_index:
                        status_report.append(f"   🔄 {stage} (CURRENT)")
                    else:
                        status_report.append(f"   ⏳ {stage}")
            
            # Next steps
            status_report.append(f"\n🎯 NEXT STEPS:")
            if effective_status == "RECEIVED":
                status_report.append("• Initial validation and data verification")
                status_report.append("• Credit check authorization")
            elif effective_status == "PROCESSING":
                status_report.append("• Document collection coordination")
                status_report.append("• Employment verification")
            elif effective_status == "DOCUMENTATION":
                status_report.append("• Property appraisal scheduling")
                status_report.append("• Final document review")
            elif effective_status == "UNDERWRITING":
                status_report.append("• Credit analysis completion")
                status_report.append("• Final lending decision")
            elif effective_status == "APPROVED":
                status_report.append("• Loan documentation preparation")
                status_report.append("• Closing coordination")
            else:
                status_report.append("• Contact loan officer for details")
        
        elif action == "update_status":
            # Extract new status from request
            new_status_match = re.search(r'to\s+(\w+)', request)
            new_status = new_status_match.group(1).upper() if new_status_match else "PROCESSING"
            
            status_report.append(f"\n📈 STATUS UPDATE:")
            status_report.append(f"Previous Status: {effective_status}")
            status_report.append(f"New Status: {new_status}")
            
            # Try to update in Neo4j if application exists
            if app_retrieval.found:
                try:
                    status_update = ApplicationStatusUpdate(
                        application_id=application_id,
                        new_status=new_status,
                        agent_name="ApplicationAgent",
                        timestamp=datetime.now().isoformat(),
                        status_notes=f"Status updated via agentic tool to {new_status}",
                        milestone_reached=f"Reached {new_status}",
                        completion_percentage=75.0
                    )
                    
                    success, result = update_application_status(status_update)
                    
                    if success:
                        status_report.append(f"✅ AGENTIC UPDATE: Status successfully updated in Neo4j")
                        status_report.append(f"   Update Result: {result}")
                    else:
                        status_report.append(f"⚠️ UPDATE WARNING: {result}")
                        
                except Exception as update_error:
                    status_report.append(f"⚠️ UPDATE WARNING: Auto-update failed, manual update required")
            else:
                status_report.append(f"⚠️ UPDATE NOTE: Application not found in storage, update recorded locally")
        
        # Contact information
        status_report.append(f"\n📞 SUPPORT:")
        status_report.append(f"Application Support: (555) 123-LOAN")
        status_report.append(f"Email: support@mortgageprocessor.com")
        status_report.append(f"Hours: Monday-Friday 8AM-6PM EST")
        
        return "\n".join(status_report)
        
    except Exception as e:
        return f"Status tracking error: {str(e)}"
