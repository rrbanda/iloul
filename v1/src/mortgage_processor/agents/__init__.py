"""
Production Agents Package - V1

Contains 6 production-ready components for complete mortgage processing:

**Specialized Agents (5):**
- ApplicationAgent: Application intake & URLA generation
- MortgageAdvisorAgent: Customer guidance & recommendations 
- DocumentAgent: Document verification & ID validation
- AppraisalAgent: Property valuation & market analysis
- UnderwritingAgent: Credit analysis & lending decisions

**Coordination Layer (1):**
- SupervisorAgent: End-to-end workflow orchestration using LangGraph supervisor pattern

All specialized agents use LangGraph ReAct architecture with Neo4j-powered tools.
The supervisor coordinates all agents for seamless user experience.
"""

from .application_agent import create_application_agent
from .mortgage_advisor_agent import create_mortgage_advisor_agent
from .document_agent import create_document_agent
from .appraisal_agent import create_appraisal_agent
from .underwriting_agent import create_underwriting_agent
from .supervisor_agent import create_supervisor_agent

# Import validation functions where available
try:
    from .application_agent import validate_all_tools as validate_application_tools
except ImportError:
    validate_application_tools = None

try:
    from .mortgage_advisor_agent import validate_all_tools as validate_advisor_tools
except ImportError:
    validate_advisor_tools = None

try:
    from .document_agent import validate_all_tools as validate_document_tools
except ImportError:
    validate_document_tools = None

try:
    from .appraisal_agent import validate_all_tools as validate_appraisal_tools
except ImportError:
    validate_appraisal_tools = None

try:
    from .underwriting_agent import validate_all_tools as validate_underwriting_tools
except ImportError:
    validate_underwriting_tools = None

try:
    from .supervisor_agent import validate_supervisor_agent
except ImportError:
    validate_supervisor_agent = None

# Build __all__ list with 5 specialized agents + 1 supervisor
__all__ = [
    # Production-ready agent creators (5 specialized agents)
    "create_application_agent",
    "create_mortgage_advisor_agent", 
    "create_document_agent",
    "create_appraisal_agent",
    "create_underwriting_agent",
    
    # Coordination layer (1 supervisor)
    "create_supervisor_agent"
]

# Add validation functions that are available
if validate_application_tools is not None:
    __all__.append("validate_application_tools")
if validate_advisor_tools is not None:
    __all__.append("validate_advisor_tools")
if validate_document_tools is not None:
    __all__.append("validate_document_tools")
if validate_appraisal_tools is not None:
    __all__.append("validate_appraisal_tools")
if validate_underwriting_tools is not None:
    __all__.append("validate_underwriting_tools")
if validate_supervisor_agent is not None:
    __all__.append("validate_supervisor_agent")
