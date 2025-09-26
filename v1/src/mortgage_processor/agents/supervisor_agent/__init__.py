"""
SupervisorAgent Package

This package provides the main coordination layer for the V1 production mortgage
processing system using LangGraph's built-in supervisor pattern.

The SupervisorAgent orchestrates all 5 specialized mortgage processing agents:
- ApplicationAgent (application intake & URLA generation)
- MortgageAdvisorAgent (customer guidance & recommendations)
- DocumentAgent (document verification & ID validation)  
- AppraisalAgent (property valuation & market analysis)
- UnderwritingAgent (credit analysis & final decisions)

Features:
- End-to-end mortgage workflow coordination
- Intelligent routing based on customer needs
- Seamless handoffs between specialized agents
- Production-grade state management and error handling
- Customer-facing interface (users don't need to know about individual agents)

Usage:
    from mortgage_processor.agents.supervisor_agent import create_supervisor_agent
    
    supervisor = create_supervisor_agent()
    response = supervisor.invoke({
        "messages": [("user", "I want to apply for a mortgage")]
    })
    
Example Workflows:
    - Complete Application: "I want to apply for a mortgage" → Full workflow
    - Loan Guidance: "What loans am I eligible for?" → MortgageAdvisorAgent
    - Document Help: "I need to upload documents" → DocumentAgent
    - Property Questions: "What's my house worth?" → AppraisalAgent
    - Decision Status: "Will I get approved?" → UnderwritingAgent
"""

from .agent import create_supervisor_agent, get_supervised_agents_info

# Export main functions for external use
__all__ = [
    "create_supervisor_agent",
    "get_supervised_agents_info"
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Mortgage Processor V1 Team"

# Agent information
AGENT_NAME = "supervisor_agent"
AGENT_PURPOSE = "End-to-end mortgage workflow coordination and intelligent agent routing"
SUPERVISED_AGENTS_COUNT = 5
WORKFLOW_STAGES = [
    "Application Intake",
    "Loan Guidance", 
    "Document Verification",
    "Property Appraisal",
    "Credit Underwriting"
]

def validate_supervisor_agent() -> bool:
    """
    Validate that the supervisor agent can be created successfully.
    
    Returns:
        bool: True if supervisor agent creation succeeds, False otherwise
    """
    try:
        supervisor = create_supervisor_agent()
        # Basic validation - supervisor should be a compiled graph
        supervisor_type = str(type(supervisor))
        return "CompiledStateGraph" in supervisor_type
    except Exception as e:
        print(f"Supervisor agent validation failed: {e}")
        return False

def get_supervisor_capabilities() -> dict:
    """
    Get comprehensive information about supervisor capabilities.
    
    Returns:
        dict: Supervisor capabilities and configuration information
    """
    return {
        "agent_name": AGENT_NAME,
        "purpose": AGENT_PURPOSE,
        "supervised_agents_count": SUPERVISED_AGENTS_COUNT,
        "workflow_stages": WORKFLOW_STAGES,
        "coordination_pattern": "LangGraph Built-in Supervisor",
        "handoff_management": "Automatic with message history",
        "state_management": "Full conversation context maintained",
        "routing_intelligence": "Context-aware agent selection",
        "user_experience": "Single interface for complete mortgage processing",
        "production_ready": True,
        "agent_details": get_supervised_agents_info()
    }
