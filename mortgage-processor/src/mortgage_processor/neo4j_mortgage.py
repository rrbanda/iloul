"""
Neo4j integration for mortgage application processing.

"""

import os
import uuid
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain_neo4j.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from mortgage_processor.utils.llm_factory import get_llm, get_supervisor_llm, get_agent_llm, get_grader_llm
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .config import AppConfig


class MortgageEntities(BaseModel):
    """Identifying mortgage-related entities from text."""
    
    applicants: List[str] = Field(
        default_factory=list,
        description="Names of mortgage applicants or borrowers mentioned in the text."
    )
    properties: List[str] = Field(
        default_factory=list, 
        description="Property addresses or property identifiers mentioned."
    )
    employers: List[str] = Field(
        default_factory=list,
        description="Employer names or companies mentioned."
    )
    financial_institutions: List[str] = Field(
        default_factory=list,
        description="Banks, lenders, or financial institutions mentioned."
    )
    loan_programs: List[str] = Field(
        default_factory=list,
        description="Loan types or programs mentioned (FHA, VA, Conventional, etc.)."
    )


class MortgageGraphManager:
    """
    Manages Neo4j connections and operations for mortgage applications.
    Adapted from IBM Watsonx example for mortgage-specific use cases.
    """
    
    def __init__(self):
        self.config = AppConfig.load()
        
        # Initialize Neo4j connection (using local Neo4j Desktop)
        self.graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
            database=os.getenv("NEO4J_DATABASE", "neo4j")
        )
        
        # Initialize LLM for entity extraction - centralized config
        self.llm = get_llm()  # Uses config.yaml settings
        
        # Initialize embeddings for vector search
        # Note: You may want to use a different embedding model
        # self.embeddings = OpenAIEmbeddings()
        
        # Initialize graph schema
        self._setup_graph_schema()
    
    def _setup_graph_schema(self):
        """Set up Neo4j schema for mortgage applications."""
        
        # Create constraints and indexes for mortgage entities
        schema_queries = [
            # Constraints for uniqueness
            "CREATE CONSTRAINT applicant_id IF NOT EXISTS FOR (a:Applicant) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT application_id IF NOT EXISTS FOR (app:Application) REQUIRE app.id IS UNIQUE", 
            "CREATE CONSTRAINT property_id IF NOT EXISTS FOR (p:Property) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT employer_id IF NOT EXISTS FOR (e:Employer) REQUIRE e.id IS UNIQUE",
            
            # Full-text search indexes for entity matching
            "CREATE FULLTEXT INDEX applicant_search IF NOT EXISTS FOR (a:Applicant) ON EACH [a.first_name, a.last_name, a.full_name]",
            "CREATE FULLTEXT INDEX property_search IF NOT EXISTS FOR (p:Property) ON EACH [p.address, p.city, p.state]",
            "CREATE FULLTEXT INDEX employer_search IF NOT EXISTS FOR (e:Employer) ON EACH [e.name, e.industry]",
        ]
        
        for query in schema_queries:
            try:
                self.graph.query(query)
            except Exception as e:
                # Constraint may already exist
                pass
    
    def extract_mortgage_entities(self, text: str) -> MortgageEntities:
        """Extract mortgage-related entities from text using LLM."""
        
        chat_prompt = ChatPromptTemplate.from_messages([
            {
                "role": "system", 
                "content": (
                    "You are an expert at extracting mortgage-related entities from text. "
                    "Extract applicant names, property addresses, employer names, "
                    "financial institutions, and loan program types mentioned in the text."
                )
            },
            {
                "role": "user",
                "content": "Extract mortgage entities from this text: {text}"
            }
        ])
        
        entity_chain = chat_prompt | self.llm.with_structured_output(MortgageEntities)
        return entity_chain.invoke({"text": text})
    
    def _generate_full_text_query(self, input_text: str) -> str:
        """Generate full-text search query (from IBM example)."""
        full_text_query = ""
        words = remove_lucene_chars(input_text).split()
        if not words:
            return ""
            
        for word in words[:-1]:
            full_text_query += f" {word}~2 AND"
        full_text_query += f" {words[-1]}~2"
        return full_text_query.strip()
    
    def search_mortgage_relationships(self, entities: MortgageEntities) -> str:
        """Search for relationships between mortgage entities in the graph."""
        
        result = ""
        
        # Search for applicant relationships
        for applicant in entities.applicants:
            if not applicant.strip():
                continue
                
            query = """
            CALL db.index.fulltext.queryNodes('applicant_search', $query, {limit:3})
            YIELD node, score
            CALL {
                WITH node
                MATCH (node)-[r]->(neighbor)
                RETURN node.full_name + ' - ' + type(r) + ' -> ' + 
                       COALESCE(neighbor.name, neighbor.address, neighbor.id) AS output
                UNION
                WITH node  
                MATCH (node)<-[r]-(neighbor)
                RETURN COALESCE(neighbor.name, neighbor.address, neighbor.id) + 
                       ' - ' + type(r) + ' -> ' + node.full_name AS output
            }
            RETURN output LIMIT 10
            """
            
            try:
                response = self.graph.query(query, {
                    "query": self._generate_full_text_query(applicant)
                })
                result += f"\n=== {applicant} Relationships ===\n"
                result += "\n".join([el["output"] for el in response]) + "\n"
            except Exception as e:
                continue
        
        # Search for property relationships
        for property_addr in entities.properties:
            if not property_addr.strip():
                continue
                
            query = """
            CALL db.index.fulltext.queryNodes('property_search', $query, {limit:2})
            YIELD node, score
            CALL {
                WITH node
                MATCH (node)-[r]->(neighbor)
                RETURN node.address + ' - ' + type(r) + ' -> ' + 
                       COALESCE(neighbor.full_name, neighbor.name, neighbor.id) AS output
                UNION
                WITH node
                MATCH (node)<-[r]-(neighbor) 
                RETURN COALESCE(neighbor.full_name, neighbor.name, neighbor.id) + 
                       ' - ' + type(r) + ' -> ' + node.address AS output
            }
            RETURN output LIMIT 10
            """
            
            try:
                response = self.graph.query(query, {
                    "query": self._generate_full_text_query(property_addr)
                })
                result += f"\n=== {property_addr} Relationships ===\n"
                result += "\n".join([el["output"] for el in response]) + "\n"
            except Exception as e:
                continue
        
        return result if result.strip() else "No existing relationships found in graph."
    
    def create_application_nodes(self, application_data: Dict[str, Any]) -> str:
        """Create nodes and relationships for a new mortgage application."""
        
        application_id = application_data.get("application_id", str(uuid.uuid4()))
        
        # Create Application node
        app_query = """
        CREATE (app:Application {
            id: $app_id,
            status: $status,
            created_date: $created_date,
            loan_amount: $loan_amount,
            loan_program: $loan_program,
            property_value: $property_value
        })
        RETURN app.id as application_id
        """
        
        app_result = self.graph.query(app_query, {
            "app_id": application_id,
            "status": application_data.get("status", "SUBMITTED"),
            "created_date": datetime.now().isoformat(),
            "loan_amount": application_data.get("loan_amount"),
            "loan_program": application_data.get("loan_program"),
            "property_value": application_data.get("property_value")
        })
        
        # Create Applicant node(s)
        applicants = application_data.get("applicants", [])
        for applicant in applicants:
            applicant_query = """
            MERGE (a:Applicant {
                id: $applicant_id
            })
            SET a.first_name = $first_name,
                a.last_name = $last_name,
                a.full_name = $full_name,
                a.email = $email,
                a.phone = $phone,
                a.annual_income = $annual_income
            WITH a
            MATCH (app:Application {id: $app_id})
            MERGE (a)-[:SUBMITS]->(app)
            RETURN a.id as applicant_id
            """
            
            applicant_id = applicant.get("id", str(uuid.uuid4()))
            
            params = {
                "applicant_id": applicant_id,
                "first_name": applicant.get("first_name"),
                "last_name": applicant.get("last_name"), 
                "full_name": applicant.get("full_name", ""),
                "email": applicant.get("email"),
                "phone": applicant.get("phone"),
                "annual_income": applicant.get("annual_income"),
                "app_id": application_id
            }
            
            self.graph.query(applicant_query, params)
        
        # Create Property node(s)
        properties = application_data.get("properties", [])
        for property_data in properties:
            property_query = """
            MERGE (p:Property {
                id: $property_id
            })
            SET p.address = $address,
                p.city = $city,
                p.state = $state,
                p.zip_code = $zip_code,
                p.property_type = $property_type,
                p.estimated_value = $estimated_value,
                p.purchase_price = $purchase_price,
                p.market_value = $market_value
            WITH p
            MATCH (app:Application {id: $app_id})
            MERGE (app)-[:FOR]->(p)
            RETURN p.id as property_id
            """
            
            property_id = property_data.get("id", str(uuid.uuid4()))
            
            property_params = {
                "property_id": property_id,
                "address": property_data.get("address"),
                "city": property_data.get("city"),
                "state": property_data.get("state"),
                "zip_code": property_data.get("zip_code"),
                "property_type": property_data.get("property_type"),
                "estimated_value": property_data.get("estimated_value"),
                "purchase_price": property_data.get("purchase_price"),
                "market_value": property_data.get("market_value"),
                "app_id": application_id
            }
            
            self.graph.query(property_query, property_params)
        
        # Create Employment relationships
        for applicant in applicants:
            if employment := applicant.get("employment"):
                emp_query = """
                MERGE (e:Employer {
                    id: $employer_id
                })
                SET e.name = $employer_name,
                    e.industry = $industry,
                    e.address = $employer_address
                WITH e
                MATCH (a:Applicant {id: $applicant_id})
                MERGE (a)-[w:WORKS_AT]->(e)
                SET w.position = $position,
                    w.start_date = $start_date,
                    w.monthly_income = $monthly_income,
                    w.employment_type = $employment_type
                RETURN e.id as employer_id
                """
                
                employer_id = employment.get("employer_id", str(uuid.uuid4()))
                
                emp_params = {
                    "employer_id": employer_id,
                    "employer_name": employment.get("employer_name"),
                    "industry": employment.get("industry"),
                    "employer_address": employment.get("employer_address"),
                    "applicant_id": applicant.get("id"),
                    "position": employment.get("position"),
                    "start_date": employment.get("start_date"),
                    "monthly_income": employment.get("monthly_income"),
                    "employment_type": employment.get("employment_type")
                }
                
                self.graph.query(emp_query, emp_params)
        
        return f"Successfully created application {application_id} with all relationships in Neo4j graph."


# Global instance
_graph_manager: Optional[MortgageGraphManager] = None

def get_mortgage_graph_manager() -> MortgageGraphManager:
    """Get or create the global mortgage graph manager instance."""
    global _graph_manager
    if _graph_manager is None:
        _graph_manager = MortgageGraphManager()
    return _graph_manager


# Tools for use in agents
@tool
def search_applicant_history(applicant_name: str) -> str:
    """Search for an applicant's mortgage history and relationships in the graph database."""
    graph_manager = get_mortgage_graph_manager()
    entities = MortgageEntities(applicants=[applicant_name])
    return graph_manager.search_mortgage_relationships(entities)


@tool  
def search_property_history(property_address: str) -> str:
    """Search for a property's mortgage history and relationships in the graph database."""
    graph_manager = get_mortgage_graph_manager()
    entities = MortgageEntities(properties=[property_address])
    return graph_manager.search_mortgage_relationships(entities)


def transform_flat_application_data(flat_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform flat application data from ApplicationAgent into nested structure for storage."""
    
    # Extract applicant info
    applicant_name = flat_data.get("applicant_name", "")
    name_parts = applicant_name.split(" ", 1)
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    # Create employment data nested within applicant
    employment_data = {
        "employer_id": str(uuid.uuid4()),
        "employer_name": flat_data.get("employer"),
        "position": "Employee",  # Default since not provided
        "monthly_income": flat_data.get("annual_income", 0) / 12 if flat_data.get("annual_income") else None,
        "employment_type": flat_data.get("employment_type")
    }
    
    applicant = {
        "id": str(uuid.uuid4()),
        "first_name": first_name,
        "last_name": last_name,
        "full_name": applicant_name,
        "email": flat_data.get("email"),
        "phone": flat_data.get("phone"),
        "annual_income": flat_data.get("annual_income"),
        "employment_type": flat_data.get("employment_type"),
        "employment": employment_data if flat_data.get("employer") else None
    }
    
    # Extract property info
    property_data = {
        "id": str(uuid.uuid4()),
        "address": flat_data.get("property_location"),
        "property_type": flat_data.get("property_type"),
        "purchase_price": flat_data.get("purchase_price"),
        "market_value": flat_data.get("purchase_price")  # Use purchase price as market value
    }
    
    # Extract employer info
    employer_data = {
        "id": str(uuid.uuid4()),
        "name": flat_data.get("employer"),
        "employment_type": flat_data.get("employment_type")
    }
    
    # Extract financial info
    financial_data = {
        "credit_score": flat_data.get("credit_score"),
        "down_payment": flat_data.get("down_payment"),
        "monthly_income": flat_data.get("annual_income", 0) / 12 if flat_data.get("annual_income") else None
    }
    
    # Create structured data
    structured_data = {
        "application_id": str(uuid.uuid4()),
        "status": "SUBMITTED",
        "loan_program": flat_data.get("loan_program"),
        "loan_amount": flat_data.get("purchase_price", 0) - flat_data.get("down_payment", 0) if flat_data.get("purchase_price") and flat_data.get("down_payment") else None,
        "property_value": flat_data.get("purchase_price"),
        
        # Nested structures expected by create_application_nodes
        "applicants": [applicant] if applicant_name else [],
        "properties": [property_data] if flat_data.get("property_location") else [],
        "employers": [employer_data] if flat_data.get("employer") else [],
        "financial_info": financial_data
    }
    
    return structured_data

@tool
def store_mortgage_application(application_data: Dict[str, Any]) -> str:
    """Store a complete mortgage application in the Neo4j graph database."""
    graph_manager = get_mortgage_graph_manager()
    
    # Transform flat data from ApplicationAgent into nested structure
    structured_data = transform_flat_application_data(application_data)
    
    return graph_manager.create_application_nodes(structured_data)


@tool
def analyze_mortgage_relationships(query_text: str) -> str:
    """Analyze mortgage-related relationships by extracting entities and searching the graph."""
    graph_manager = get_mortgage_graph_manager()
    entities = graph_manager.extract_mortgage_entities(query_text)
    return graph_manager.search_mortgage_relationships(entities)


@tool
def update_application_status(application_id: str, status: str, notes: str = "", agent_name: str = "") -> str:
    """
    Update application status and add processing notes.
    
    Args:
        application_id: Unique application identifier
        status: New status (SUBMITTED, PROCESSING, UNDERWRITING, APPROVED, DENIED, CONDITIONAL)
        notes: Processing notes or reason for status change
        agent_name: Agent making the update
        
    Returns:
        Confirmation message
    """
    graph_manager = get_mortgage_graph_manager()
    
    # Update application status with timestamp
    update_query = """
    MATCH (app:Application {id: $application_id})
    SET app.status = $status,
        app.last_updated = datetime(),
        app.processing_notes = CASE 
            WHEN app.processing_notes IS NULL THEN $notes
            ELSE app.processing_notes + " | " + $notes
        END
    WITH app
    CREATE (app)-[:STATUS_CHANGE]->(s:StatusHistory {
        id: randomUUID(),
        status: $status,
        timestamp: datetime(),
        notes: $notes,
        updated_by: $agent_name
    })
    RETURN app.id as application_id, app.status as new_status
    """
    
    params = {
        "application_id": application_id,
        "status": status,
        "notes": f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}",
        "agent_name": agent_name
    }
    
    try:
        result = graph_manager.graph.query(update_query, params)
        if result:
            return f"✅ Application {application_id} status updated to {status}. Notes: {notes}"
        else:
            return f" Application {application_id} not found"
    except Exception as e:
        return f" Error updating status: {str(e)}"


@tool
def get_application_status(application_id: str) -> str:
    """
    Get current application status and processing history.
    
    Args:
        application_id: Unique application identifier
        
    Returns:
        Current status and recent processing history
    """
    graph_manager = get_mortgage_graph_manager()
    
    status_query = """
    MATCH (app:Application {id: $application_id})
    OPTIONAL MATCH (app)-[:STATUS_CHANGE]->(s:StatusHistory)
    RETURN app.id as application_id,
           app.status as current_status,
           app.loan_program as loan_program,
           app.loan_amount as loan_amount,
           app.last_updated as last_updated,
           app.processing_notes as notes,
           collect({
               status: s.status,
               timestamp: s.timestamp,
               notes: s.notes,
               updated_by: s.updated_by
           }) as status_history
    ORDER BY s.timestamp DESC
    """
    
    try:
        result = graph_manager.graph.query(status_query, {"application_id": application_id})
        if result:
            app = result[0]
            loan_amount_str = f"${app['loan_amount']:,.2f}" if app['loan_amount'] else 'N/A'
            status_info = f"""
📋 **Application Status Report**
Application ID: {app['application_id']}
Current Status: {app['current_status']}
Loan Program: {app['loan_program']}
Loan Amount: {loan_amount_str}
Last Updated: {app['last_updated']}

📝 **Processing Notes:**
{app['notes'] if app['notes'] else 'No notes available'}

📊 **Status History:**"""
            
            for entry in app['status_history'][:5]:  # Show last 5 status changes
                if entry['status']:  # Skip null entries
                    status_info += f"\n• {entry['status']} - {entry['timestamp']} ({entry['updated_by']})"
                    if entry['notes']:
                        status_info += f"\n  Notes: {entry['notes']}"
            
            return status_info
        else:
            return f" Application {application_id} not found"
    except Exception as e:
        return f" Error retrieving status: {str(e)}"


@tool
def store_loan_decision(application_id: str, decision_data: Dict[str, Any]) -> str:
    """
    Store final loan decision and conditions in Neo4j.
    
    Args:
        application_id: Unique application identifier
        decision_data: Decision details from underwriting agent
        
    Returns:
        Confirmation message
    """
    graph_manager = get_mortgage_graph_manager()
    
    # Extract decision details
    decision = decision_data.get("decision", "PENDING")
    risk_score = decision_data.get("risk_score", 0)
    conditions = decision_data.get("conditions", [])
    interest_rate = decision_data.get("interest_rate", 0)
    reasoning = decision_data.get("reasoning", "")
    
    # Store decision in Neo4j
    decision_query = """
    MATCH (app:Application {id: $application_id})
    CREATE (app)-[:HAS_DECISION]->(d:LoanDecision {
        id: randomUUID(),
        decision: $decision,
        risk_score: $risk_score,
        interest_rate: $interest_rate,
        reasoning: $reasoning,
        conditions: $conditions,
        decision_date: datetime(),
        decision_by: "UnderwritingAgent"
    })
    SET app.final_decision = $decision,
        app.decision_date = datetime(),
        app.status = CASE $decision
            WHEN "Approved" THEN "APPROVED"
            WHEN "Approved with Conditions" THEN "CONDITIONAL"
            WHEN "Counter-Offer" THEN "COUNTER_OFFER"
            ELSE "DENIED"
        END
    RETURN d.id as decision_id, app.status as final_status
    """
    
    params = {
        "application_id": application_id,
        "decision": decision,
        "risk_score": risk_score,
        "interest_rate": interest_rate,
        "reasoning": reasoning,
        "conditions": conditions
    }
    
    try:
        result = graph_manager.graph.query(decision_query, params)
        if result:
            # Update application status
            status_update = f"Final decision: {decision}. Risk score: {risk_score}/10"
            update_application_status(application_id, f"DECISION_{decision.upper().replace(' ', '_')}", 
                                    status_update, "UnderwritingAgent")
            
            return f"✅ Loan decision stored for application {application_id}: {decision}"
        else:
            return f" Application {application_id} not found for decision storage"
    except Exception as e:
        return f" Error storing decision: {str(e)}"


@tool
def initiate_processing_workflow(application_id: str) -> str:
    """
    Initiate automated processing workflow after application submission.
    
    Args:
        application_id: Unique application identifier
        
    Returns:
        Workflow initiation confirmation and next steps
    """
    # Update status to processing
    update_result = update_application_status(
        application_id, 
        "PROCESSING", 
        "Application submitted successfully. Initiating automated processing workflow.",
        "ProcessingWorkflow"
    )
    
    # Return next steps for the workflow
    return f"""
{update_result}

🔄 **Processing Workflow Initiated for Application {application_id}**

**Next Steps:**
1. **Data Validation** - DataAgent will verify all submitted information
2. **Property Analysis** - PropertyAgent will assess property value and risks  
3. **Credit & Income Verification** - DataAgent will perform comprehensive checks
4. **Risk Analysis** - UnderwritingAgent will analyze all risk factors
5. **Compliance Review** - ComplianceAgent will ensure regulatory compliance
6. **Final Decision** - UnderwritingAgent will make approval/denial decision

**Estimated Processing Time:** 2-5 business days
**Status Updates:** Available via application status check

The system will now coordinate between specialized agents to process your application. You can check status anytime by asking "What's the status of my application?"
"""
