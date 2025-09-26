"""
SupervisorAgent Implementation using Built-in LangGraph Supervisor

This agent uses the official langgraph-supervisor package to coordinate all specialized 
mortgage processing agents with proper handoff mechanisms and transfer tools.

The SupervisorAgent uses LangGraph's built-in supervisor pattern for:
- Professional multi-agent coordination using transfer tools
- Intelligent routing between specialized agents based on context
- Seamless handoffs with proper state management
- Production-grade coordination using official LangGraph supervisor
"""

from pathlib import Path
from langgraph_supervisor import create_supervisor
from langchain_core.language_models import BaseChatModel

try:
    from mortgage_processor.utils.llm_factory import get_supervisor_llm
except ImportError:
    # Fallback for relative imports during testing
    from ...utils.llm_factory import get_supervisor_llm

from ..shared.prompt_loader import load_agent_prompt


def create_supervisor_agent():
    """
    Create SupervisorAgent using the official LangGraph supervisor pattern.
    
    This creates a production-ready supervisor that coordinates all 5 mortgage processing
    agents using LangGraph's built-in supervisor implementation with transfer tools.
    
    Features:
    - Built-in multi-agent coordination and handoffs using transfer tools
    - Intelligent workflow routing based on mortgage process stages
    - Automatic state management and message history
    - Production-grade error handling and recovery
    - Seamless end-to-end user experience
    - Official LangGraph supervisor pattern compliance
    
    Workflow Coordination:
    1. ApplicationAgent - Mortgage application intake and URLA generation
    2. MortgageAdvisorAgent - Loan guidance and recommendations  
    3. DocumentAgent - Document verification and ID validation
    4. AppraisalAgent - Property valuation and market analysis
    5. UnderwritingAgent - Final credit analysis and lending decisions
    
    Returns:
        Compiled LangGraph supervisor ready for end-to-end mortgage processing
    """
    
    # Import all specialized agents (avoid circular imports)
    from ..application_agent import create_application_agent
    from ..mortgage_advisor_agent import create_mortgage_advisor_agent
    from ..document_agent import create_document_agent
    from ..appraisal_agent import create_appraisal_agent
    from ..underwriting_agent import create_underwriting_agent
    
    # Create all 5 specialized mortgage processing agents
    application_agent = create_application_agent()
    mortgage_advisor_agent = create_mortgage_advisor_agent()
    document_agent = create_document_agent()
    appraisal_agent = create_appraisal_agent()
    underwriting_agent = create_underwriting_agent()
    
    # Get centralized LLM from factory
    llm = get_supervisor_llm()
    
    # Load supervisor system prompt from YAML using shared prompt loader
    agent_dir = Path(__file__).parent  # Current directory (supervisor_agent/)
    system_prompt = load_agent_prompt("supervisor_agent", agent_dir)
    
    # Create supervisor using built-in LangGraph supervisor
    supervisor = create_supervisor(
        model=llm,
        agents=[
            application_agent,
            mortgage_advisor_agent, 
            document_agent,
            appraisal_agent,
            underwriting_agent
        ],
        prompt=(
            f"{system_prompt}\n\n"
            "You are a supervisor managing five specialized mortgage processing agents:\n"
            "- application_agent: Mortgage application intake and URLA Form 1003 generation\n"
            "- mortgage_advisor_agent: Customer guidance and loan program recommendations\n" 
            "- document_agent: Document verification and ID validation\n"
            "- appraisal_agent: Property valuation and market analysis\n"
            "- underwriting_agent: Credit analysis and final lending decisions\n\n"
            "IMPORTANT: Before transferring, check if an agent already handled the request completely.\n"
            "If an agent already provided a comprehensive response, acknowledge their work and offer next steps instead of transferring again.\n"
            "Only transfer when the customer has a NEW question requiring specialist expertise.\n\n"
            "Assign work to one agent at a time based on the customer's needs.\n"
            "Do not call agents in parallel.\n"
            "Do not do any work yourself - delegate to the appropriate specialist."
        ),
        add_handoff_back_messages=True,
        output_mode="full_history",
    ).compile()
    
    return supervisor


def get_supervised_agents_info():
    """
    Get information about all agents managed by the supervisor.
    
    Returns:
        Dict with agent information for documentation and debugging
    """
    return {
        "supervisor_type": "Built-in LangGraph Supervisor (langgraph-supervisor)",
        "total_agents": 5,
        "agents": [
            {
                "name": "application_agent",
                "purpose": "Mortgage application intake and URLA Form 1003 generation",
                "tools_count": 6,
                "key_capabilities": ["Application intake", "URLA generation", "Initial qualification", "Workflow routing"]
            },
            {
                "name": "mortgage_advisor_agent", 
                "purpose": "Customer guidance and loan program recommendations",
                "tools_count": 4,
                "key_capabilities": ["Loan program matching", "Qualification analysis", "Educational guidance", "Next steps"]
            },
            {
                "name": "document_agent",
                "purpose": "Document verification and ID validation",
                "tools_count": 6,
                "key_capabilities": ["Document verification", "ID validation", "OCR processing", "Completeness checking"]
            },
            {
                "name": "appraisal_agent",
                "purpose": "Property valuation and market analysis", 
                "tools_count": 5,
                "key_capabilities": ["Property valuation", "Market analysis", "Comparable sales", "Appraisal review"]
            },
            {
                "name": "underwriting_agent",
                "purpose": "Credit analysis and final lending decisions",
                "tools_count": 4,
                "key_capabilities": ["Credit risk analysis", "DTI calculations", "Income verification", "Final decisions"]
            }
        ],
        "workflow": [
            "Customer Application → ApplicationAgent",
            "Loan Guidance → MortgageAdvisorAgent", 
            "Document Verification → DocumentAgent",
            "Property Valuation → AppraisalAgent",
            "Final Decision → UnderwritingAgent"
        ],
        "features": [
            "Built-in transfer tools",
            "Automatic handoff mechanisms", 
            "Full message history tracking",
            "Production-grade error handling",
            "Official LangGraph supervisor compliance"
        ]
    }