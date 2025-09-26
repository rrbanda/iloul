"""
Agentic Application Storage

Provides seamless application storage and retrieval that works transparently 
with agent tools. All functions are designed to be called automatically by 
agent tools without manual intervention.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from ..setup import get_connection
from .application_schema import (
    MortgageApplicationData,
    ApplicationStatusUpdate,
    ApplicationRetrievalResult,
    WorkflowTransition
)

logger = logging.getLogger(__name__)


def ensure_application_intake_rules() -> bool:
    """
    Ensure ApplicationIntakeRule nodes exist in Neo4j for agent tools to function.
    Called automatically when needed - no manual intervention required.
    """
    try:
        connection = get_connection()
        
        with connection.driver.session(database='mortgage') as session:
            # Check if rules already exist
            result = session.run("MATCH (r:ApplicationIntakeRule) RETURN count(r) as count")
            existing_count = result.single()['count']
            
            if existing_count > 0:
                logger.info(f"ApplicationIntakeRule nodes already exist: {existing_count}")
                return True
            
            # Create essential application intake rules that agent tools expect
            rules = [
                {
                    'rule_id': 'APP_REQ_001',
                    'category': 'ApplicationRequirements',
                    'rule_type': 'required_fields',
                    'description': 'Required fields for mortgage application intake',
                    'personal_info': ['first_name', 'last_name', 'ssn', 'date_of_birth', 'phone', 'email'],
                    'current_address': ['current_street', 'current_city', 'current_state', 'current_zip'],
                    'employment': ['employer_name', 'job_title', 'years_employed', 'monthly_gross_income'],
                    'loan_details': ['loan_purpose', 'loan_amount', 'property_address', 'property_type']
                },
                {
                    'rule_id': 'APP_VAL_001', 
                    'category': 'ValidationRules',
                    'rule_type': 'data_format_validation',
                    'description': 'Data format validation rules for application fields',
                    'ssn_pattern': '^\\d{3}-\\d{2}-\\d{4}$',
                    'phone_pattern': '^\\d{3}-\\d{3}-\\d{4}$',
                    'loan_amount_range': {'min': 50000, 'max': 5000000},
                    'income_range': {'min': 1000, 'max': 100000}
                },
                {
                    'rule_id': 'APP_STATUS_001',
                    'category': 'StatusManagement', 
                    'rule_type': 'status_tracking',
                    'description': 'Application status lifecycle and progression rules',
                    'status_progression': [
                        'RECEIVED', 'VALIDATED', 'PROCESSING', 'DOCUMENTATION', 
                        'APPRAISAL', 'UNDERWRITING', 'APPROVED', 'DENIED', 'CLOSED'
                    ],
                    'status_definitions': {
                        'RECEIVED': 'Application received and initial validation pending',
                        'VALIDATED': 'Application data validated, ready for processing',
                        'PROCESSING': 'Application in active processing workflow',
                        'DOCUMENTATION': 'Document collection and verification phase',
                        'APPRAISAL': 'Property appraisal and valuation phase',
                        'UNDERWRITING': 'Credit and risk analysis phase', 
                        'APPROVED': 'Application approved for loan funding',
                        'DENIED': 'Application denied based on criteria',
                        'CLOSED': 'Application process completed'
                    }
                },
                {
                    'rule_id': 'APP_ROUTE_001',
                    'category': 'WorkflowRouting',
                    'rule_type': 'agent_routing',
                    'description': 'Rules for routing applications between agents',
                    'routing_logic': {
                        'first_time_buyer': 'MortgageAdvisorAgent',
                        'low_credit_score': 'MortgageAdvisorAgent', 
                        'standard_application': 'DocumentAgent',
                        'complex_income': 'UnderwritingAgent',
                        'high_value_property': 'AppraisalAgent'
                    },
                    'agent_capabilities': {
                        'ApplicationAgent': ['intake', 'validation', 'routing'],
                        'MortgageAdvisorAgent': ['guidance', 'program_recommendation'],
                        'DocumentAgent': ['verification', 'document_analysis'],
                        'AppraisalAgent': ['property_valuation', 'market_analysis'],
                        'UnderwritingAgent': ['credit_analysis', 'final_decision']
                    }
                }
            ]
            
            # Create the rules
            for rule in rules:
                session.run("""
                    CREATE (r:ApplicationIntakeRule {
                        rule_id: $rule_id,
                        category: $category,
                        rule_type: $rule_type,
                        description: $description,
                        data: $data
                    })
                """, {
                    'rule_id': rule['rule_id'],
                    'category': rule['category'], 
                    'rule_type': rule['rule_type'],
                    'description': rule['description'],
                    'data': json.dumps({k: v for k, v in rule.items() if k not in ['rule_id', 'category', 'rule_type', 'description']})
                })
            
            logger.info(f"Created {len(rules)} ApplicationIntakeRule nodes for agent tools")
            return True
            
    except Exception as e:
        logger.error(f"Error ensuring application intake rules: {e}")
        return False


def store_application_data(application_data: MortgageApplicationData) -> Tuple[bool, str]:
    """
    Store mortgage application data in Neo4j for agentic access.
    Called automatically by receive_mortgage_application tool.
    
    Returns: (success, application_id or error_message)
    """
    try:
        connection = get_connection()
        
        # Ensure intake rules exist
        ensure_application_intake_rules()
        
        with connection.driver.session(database='mortgage') as session:
            # Check if application already exists
            result = session.run("""
                MATCH (app:MortgageApplication {application_id: $app_id})
                RETURN app.application_id as existing_id
            """, {'app_id': application_data.application_id})
            
            existing = result.single()
            if existing:
                logger.warning(f"Application {application_data.application_id} already exists")
                return False, f"Application {application_data.application_id} already exists"
            
            # Store the application
            app_dict = application_data.dict()
            session.run("""
                CREATE (app:MortgageApplication {
                    application_id: $application_id,
                    received_date: $received_date,
                    current_status: $current_status,
                    first_name: $first_name,
                    last_name: $last_name,
                    ssn: $ssn,
                    date_of_birth: $date_of_birth,
                    phone: $phone,
                    email: $email,
                    current_street: $current_street,
                    current_city: $current_city,
                    current_state: $current_state,
                    current_zip: $current_zip,
                    years_at_address: $years_at_address,
                    employer_name: $employer_name,
                    job_title: $job_title,
                    years_employed: $years_employed,
                    monthly_gross_income: $monthly_gross_income,
                    employment_type: $employment_type,
                    loan_purpose: $loan_purpose,
                    loan_amount: $loan_amount,
                    property_address: $property_address,
                    property_value: $property_value,
                    property_type: $property_type,
                    occupancy_type: $occupancy_type,
                    credit_score: $credit_score,
                    monthly_debts: $monthly_debts,
                    liquid_assets: $liquid_assets,
                    down_payment: $down_payment,
                    first_time_buyer: $first_time_buyer,
                    military_service: $military_service,
                    rural_property: $rural_property,
                    validation_status: $validation_status,
                    completion_percentage: $completion_percentage,
                    next_agent: $next_agent,
                    workflow_notes: $workflow_notes
                })
            """, app_dict)
            
            # Create initial status record
            session.run("""
                MATCH (app:MortgageApplication {application_id: $app_id})
                CREATE (status:ApplicationStatus {
                    application_id: $app_id,
                    status: $current_status,
                    agent_name: 'ApplicationAgent',
                    timestamp: $timestamp,
                    notes: 'Application received and stored'
                })
                CREATE (app)-[:HAS_STATUS]->(status)
            """, {
                'app_id': application_data.application_id,
                'current_status': application_data.current_status,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Stored application {application_data.application_id} in Neo4j")
            return True, application_data.application_id
            
    except Exception as e:
        logger.error(f"Error storing application data: {e}")
        return False, f"Storage error: {str(e)}"


def retrieve_application_data(application_id: str) -> ApplicationRetrievalResult:
    """
    Retrieve mortgage application data from Neo4j for agentic access.
    Called automatically by agent tools when they need application data.
    """
    try:
        connection = get_connection()
        
        with connection.driver.session(database='mortgage') as session:
            # Get application data
            result = session.run("""
                MATCH (app:MortgageApplication {application_id: $app_id})
                RETURN app
            """, {'app_id': application_id})
            
            app_record = result.single()
            if not app_record:
                return ApplicationRetrievalResult(
                    found=False,
                    error_message=f"Application {application_id} not found"
                )
            
            # Convert to MortgageApplicationData
            app_data = dict(app_record['app'])
            application_data = MortgageApplicationData(**app_data)
            
            # Get status history
            result = session.run("""
                MATCH (app:MortgageApplication {application_id: $app_id})-[:HAS_STATUS]->(status:ApplicationStatus)
                RETURN status
                ORDER BY status.timestamp DESC
            """, {'app_id': application_id})
            
            status_history = []
            for record in result:
                status_data = dict(record['status'])
                status_history.append(status_data)
            
            # Determine current agent and next steps
            current_status = application_data.current_status
            next_agent = application_data.next_agent
            
            # Get routing recommendations
            next_steps = _get_next_steps_for_status(current_status, application_data)
            
            return ApplicationRetrievalResult(
                found=True,
                application_data=application_data,
                status_history=status_history,
                current_agent=next_agent,
                next_steps=next_steps
            )
            
    except Exception as e:
        logger.error(f"Error retrieving application {application_id}: {e}")
        return ApplicationRetrievalResult(
            found=False,
            error_message=f"Retrieval error: {str(e)}"
        )


def update_application_status(status_update: ApplicationStatusUpdate) -> Tuple[bool, str]:
    """
    Update application status for agentic workflow progression.
    Called automatically by agent tools during workflow transitions.
    """
    try:
        connection = get_connection()
        
        with connection.driver.session(database='mortgage') as session:
            # Update application status
            session.run("""
                MATCH (app:MortgageApplication {application_id: $app_id})
                SET app.current_status = $new_status,
                    app.completion_percentage = coalesce($completion_percentage, app.completion_percentage),
                    app.next_agent = $next_agent,
                    app.workflow_notes = coalesce($workflow_notes, app.workflow_notes)
            """, {
                'app_id': status_update.application_id,
                'new_status': status_update.new_status,
                'completion_percentage': status_update.completion_percentage,
                'next_agent': status_update.next_agent,
                'workflow_notes': status_update.status_notes
            })
            
            # Create new status record
            session.run("""
                MATCH (app:MortgageApplication {application_id: $app_id})
                CREATE (status:ApplicationStatus {
                    application_id: $app_id,
                    status: $new_status,
                    agent_name: $agent_name,
                    timestamp: $timestamp,
                    notes: $notes,
                    milestone_reached: $milestone,
                    completion_percentage: $completion_percentage
                })
                CREATE (app)-[:HAS_STATUS]->(status)
            """, {
                'app_id': status_update.application_id,
                'new_status': status_update.new_status,
                'agent_name': status_update.agent_name,
                'timestamp': status_update.timestamp,
                'notes': status_update.status_notes,
                'milestone': status_update.milestone_reached,
                'completion_percentage': status_update.completion_percentage
            })
            
            logger.info(f"Updated application {status_update.application_id} status to {status_update.new_status}")
            return True, f"Status updated to {status_update.new_status}"
            
    except Exception as e:
        logger.error(f"Error updating application status: {e}")
        return False, f"Status update error: {str(e)}"


def get_application_history(application_id: str) -> List[Dict[str, Any]]:
    """
    Get complete application processing history for agentic review.
    Called automatically when agents need to understand application progress.
    """
    try:
        connection = get_connection()
        
        with connection.driver.session(database='mortgage') as session:
            result = session.run("""
                MATCH (app:MortgageApplication {application_id: $app_id})-[:HAS_STATUS]->(status:ApplicationStatus)
                RETURN status
                ORDER BY status.timestamp ASC
            """, {'app_id': application_id})
            
            history = []
            for record in result:
                status_data = dict(record['status'])
                history.append(status_data)
            
            return history
            
    except Exception as e:
        logger.error(f"Error getting application history: {e}")
        return []


def _get_next_steps_for_status(status: str, app_data: MortgageApplicationData) -> str:
    """
    Determine next steps based on current status and application data.
    Used internally to guide agentic workflow decisions.
    """
    if status == "RECEIVED":
        if app_data.first_time_buyer or (app_data.credit_score and app_data.credit_score < 650):
            return "Route to MortgageAdvisorAgent for guidance and program recommendation"
        else:
            return "Route to DocumentAgent for document collection and verification"
    
    elif status == "VALIDATED":
        return "Route to DocumentAgent for document collection and verification"
    
    elif status == "PROCESSING":
        return "Continue with DocumentAgent for document verification"
    
    elif status == "DOCUMENTATION":
        if app_data.property_value and app_data.property_value > 1000000:
            return "Route to AppraisalAgent for property valuation"
        else:
            return "Route to UnderwritingAgent for credit analysis"
    
    elif status == "APPRAISAL":
        return "Route to UnderwritingAgent for final credit analysis and decision"
    
    elif status == "UNDERWRITING":
        return "Await final decision from UnderwritingAgent"
    
    else:
        return f"Application in {status} status - follow standard workflow progression"
