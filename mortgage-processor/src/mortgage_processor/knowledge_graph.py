"""
Knowledge Graph Construction for Mortgage Documents
Uses LangChain's LLMGraphTransformer to extract entities and relationships from mortgage documents
"""

import asyncio
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from mortgage_processor.utils.llm_factory import get_llm
from .config import AppConfig
import logging

logger = logging.getLogger(__name__)

class MortgageKnowledgeGraphExtractor:
    """Extract knowledge graphs from mortgage documents using LangChain"""
    
    def __init__(self):
        """Initialize the knowledge graph extractor"""
        self.llm = get_llm()
        self.config = AppConfig.load()
        
        # Initialize Neo4j connection for knowledge graph
        try:
            import os
            self.graph = Neo4jGraph(
                url=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                username=os.getenv("NEO4J_USERNAME", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD", "password"),
                database=os.getenv("NEO4J_DATABASE", "neo4j"),
                refresh_schema=False
            )
        except Exception as e:
            logger.warning(f"Neo4j connection failed, using fallback: {e}")
            self.graph = None
        
        # Define mortgage-specific entity types and relationships
        self.mortgage_allowed_nodes = [
            "Person",           # Applicant, co-applicant, spouse
            "Employer",         # Current and previous employers  
            "Bank",            # Financial institutions
            "Property",        # Real estate properties
            "Income",          # Salary, wages, bonuses
            "Asset",           # Bank accounts, investments, retirement
            "Debt",            # Credit cards, loans, liabilities
            "Document",        # W-2, pay stub, bank statement
            "Address",         # Residential and property addresses
            "LoanProgram",     # FHA, VA, Conventional, USDA
            "Organization"     # Government agencies, institutions
        ]
        
        # Define mortgage-specific relationships with source-relationship-target tuples
        self.mortgage_allowed_relationships = [
            # Person relationships
            ("Person", "EMPLOYED_BY", "Employer"),
            ("Person", "MARRIED_TO", "Person"),
            ("Person", "EARNS", "Income"), 
            ("Person", "OWNS", "Asset"),
            ("Person", "OWES", "Debt"),
            ("Person", "RESIDES_AT", "Address"),
            ("Person", "APPLIES_FOR", "LoanProgram"),
            
            # Employment relationships
            ("Employer", "PAYS", "Income"),
            ("Employer", "LOCATED_AT", "Address"),
            ("Employer", "ISSUES", "Document"),
            
            # Financial relationships
            ("Bank", "HOLDS", "Asset"),
            ("Bank", "ISSUES", "Document"),
            ("Bank", "PROVIDES", "Debt"),
            ("Asset", "DEPOSITED_AT", "Bank"),
            ("Income", "DEPOSITED_TO", "Asset"),
            
            # Property relationships  
            ("Property", "LOCATED_AT", "Address"),
            ("Property", "FINANCED_BY", "LoanProgram"),
            ("Person", "PURCHASING", "Property"),
            
            # Document relationships
            ("Document", "VERIFIES", "Income"),
            ("Document", "VERIFIES", "Employer"),
            ("Document", "SHOWS", "Asset"),
            ("Document", "ISSUED_BY", "Employer"),
            ("Document", "ISSUED_BY", "Bank"),
            ("Document", "BELONGS_TO", "Person")
        ]
        
        # Node properties to extract
        self.mortgage_node_properties = [
            "amount",           # Income amounts, asset values, debt balances
            "date",            # Employment dates, document dates
            "frequency",       # Income frequency (monthly, yearly)
            "type",            # Document type, income type, asset type
            "employer_name",   # Employer names
            "bank_name",       # Bank names
            "account_number",  # Account numbers (anonymized)
            "address",         # Full addresses
            "loan_amount",     # Loan amounts
            "property_value",  # Property values
            "years_employed",  # Length of employment
            "credit_score"     # Credit scores mentioned
        ]
        
        # Initialize the LLM transformer
        self.llm_transformer = LLMGraphTransformer(
            llm=self.llm,
            allowed_nodes=self.mortgage_allowed_nodes,
            allowed_relationships=self.mortgage_allowed_relationships,
            node_properties=self.mortgage_node_properties
        )
        
    async def extract_knowledge_graph(self, document_content: str, document_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract knowledge graph from document content
        
        Args:
            document_content: Raw text content of the document
            document_metadata: Document metadata (filename, type, etc.)
            
        Returns:
            Dictionary containing extracted nodes, relationships, and metadata
        """
        try:
            # Create LangChain document
            doc = Document(
                page_content=document_content,
                metadata=document_metadata
            )
            
            # Extract knowledge graph using LangChain transformer
            graph_documents = await self.llm_transformer.aconvert_to_graph_documents([doc])
            
            if not graph_documents:
                return {"nodes": [], "relationships": [], "success": False}
            
            graph_doc = graph_documents[0]
            
            # Convert to serializable format
            nodes = []
            for node in graph_doc.nodes:
                nodes.append({
                    "id": node.id,
                    "type": node.type,
                    "properties": node.properties or {}
                })
            
            relationships = []
            for rel in graph_doc.relationships:
                relationships.append({
                    "source": {
                        "id": rel.source.id,
                        "type": rel.source.type
                    },
                    "target": {
                        "id": rel.target.id, 
                        "type": rel.target.type
                    },
                    "type": rel.type,
                    "properties": rel.properties or {}
                })
            
            return {
                "nodes": nodes,
                "relationships": relationships,
                "document_metadata": document_metadata,
                "success": True,
                "extracted_entities_count": len(nodes),
                "extracted_relationships_count": len(relationships)
            }
            
        except Exception as e:
            logger.error(f"Knowledge graph extraction failed: {e}")
            return {
                "nodes": [],
                "relationships": [],
                "success": False,
                "error": str(e)
            }
    
    def store_knowledge_graph(self, knowledge_graph: Dict[str, Any], application_id: str) -> bool:
        """
        Store extracted knowledge graph in Neo4j database
        
        Args:
            knowledge_graph: Extracted knowledge graph data
            application_id: Associated mortgage application ID
            
        Returns:
            True if storage successful, False otherwise
        """
        if not self.graph or not knowledge_graph.get("success"):
            return False
            
        try:
            # Create nodes
            for node in knowledge_graph.get("nodes", []):
                node_query = f"""
                MERGE (n:{node['type']} {{id: $node_id}})
                SET n += $properties
                SET n.application_id = $application_id
                SET n.created_at = datetime()
                """
                
                self.graph.query(node_query, {
                    "node_id": node['id'],
                    "properties": node.get('properties', {}),
                    "application_id": application_id
                })
            
            # Create relationships
            for rel in knowledge_graph.get("relationships", []):
                rel_query = f"""
                MATCH (source:{rel['source']['type']} {{id: $source_id}})
                MATCH (target:{rel['target']['type']} {{id: $target_id}})
                MERGE (source)-[r:{rel['type']}]->(target)
                SET r += $properties
                SET r.application_id = $application_id
                SET r.created_at = datetime()
                """
                
                self.graph.query(rel_query, {
                    "source_id": rel['source']['id'],
                    "target_id": rel['target']['id'],
                    "properties": rel.get('properties', {}),
                    "application_id": application_id
                })
            
            # Link to application
            app_link_query = """
            MATCH (app:Application {id: $application_id})
            MATCH (n) WHERE n.application_id = $application_id
            MERGE (app)-[:HAS_KNOWLEDGE_ENTITY]->(n)
            """
            
            self.graph.query(app_link_query, {"application_id": application_id})
            
            logger.info(f"Knowledge graph stored successfully for application {application_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store knowledge graph: {e}")
            return False
    
    def query_knowledge_graph(self, application_id: str, query_type: str = "all") -> Dict[str, Any]:
        """
        Query the knowledge graph for specific application
        
        Args:
            application_id: Application to query
            query_type: Type of query (all, persons, income, assets, etc.)
            
        Returns:
            Query results
        """
        if not self.graph:
            return {"error": "Neo4j connection not available"}
            
        try:
            if query_type == "all":
                query = """
                MATCH (app:Application {id: $application_id})-[:HAS_KNOWLEDGE_ENTITY]->(n)
                OPTIONAL MATCH (n)-[r]-(connected)
                RETURN n, r, connected
                """
            elif query_type == "persons":
                query = """
                MATCH (app:Application {id: $application_id})-[:HAS_KNOWLEDGE_ENTITY]->(p:Person)
                OPTIONAL MATCH (p)-[r]-(connected)
                RETURN p, r, connected
                """
            elif query_type == "income":
                query = """
                MATCH (app:Application {id: $application_id})-[:HAS_KNOWLEDGE_ENTITY]->(i:Income)
                OPTIONAL MATCH (p:Person)-[:EARNS]->(i)
                OPTIONAL MATCH (e:Employer)-[:PAYS]->(i)
                RETURN i, p, e
                """
            elif query_type == "assets":
                query = """
                MATCH (app:Application {id: $application_id})-[:HAS_KNOWLEDGE_ENTITY]->(a:Asset)
                OPTIONAL MATCH (p:Person)-[:OWNS]->(a)
                OPTIONAL MATCH (b:Bank)-[:HOLDS]->(a)
                RETURN a, p, b
                """
            else:
                return {"error": f"Unknown query type: {query_type}"}
            
            results = self.graph.query(query, {"application_id": application_id})
            return {"results": results, "success": True}
            
        except Exception as e:
            logger.error(f"Knowledge graph query failed: {e}")
            return {"error": str(e), "success": False}

def create_mortgage_knowledge_extractor() -> MortgageKnowledgeGraphExtractor:
    """Factory function to create knowledge graph extractor"""
    return MortgageKnowledgeGraphExtractor()

# Example usage and testing
async def test_knowledge_extraction():
    """Test the knowledge graph extraction with sample mortgage document"""
    
    sample_w2_content = """
    W-2 Wage and Tax Statement for 2023
    Employee: John Smith
    SSN: ***-**-1234
    Address: 123 Oak Street, Austin, TX 78701
    
    Employer: TechCorp Solutions Inc.
    EIN: 45-1234567
    Address: 456 Business Blvd, Austin, TX 78702
    
    Wages, tips, other compensation: $85,000.00
    Federal income tax withheld: $12,750.00
    Social security wages: $85,000.00
    Medicare wages and tips: $85,000.00
    """
    
    extractor = create_mortgage_knowledge_extractor()
    
    metadata = {
        "document_type": "w2_form",
        "file_name": "john_smith_w2_2023.pdf",
        "application_id": "APP_123456",
        "upload_date": "2024-01-15"
    }
    
    knowledge_graph = await extractor.extract_knowledge_graph(sample_w2_content, metadata)
    
    print("Extracted Knowledge Graph:")
    print(f"Nodes: {len(knowledge_graph.get('nodes', []))}")
    print(f"Relationships: {len(knowledge_graph.get('relationships', []))}")
    
    for node in knowledge_graph.get('nodes', []):
        print(f"  Node: {node['id']} ({node['type']}) - {node.get('properties', {})}")
    
    for rel in knowledge_graph.get('relationships', []):
        print(f"  Relationship: {rel['source']['id']} -[{rel['type']}]-> {rel['target']['id']}")
    
    return knowledge_graph

if __name__ == "__main__":
    # Run test
    asyncio.run(test_knowledge_extraction())
