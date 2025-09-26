"""
Application Data Management

Provides agentic application storage and retrieval capabilities for the mortgage system.
All functions work transparently with agent tools - no manual intervention required.

This module enables:
- Automatic application storage when agents call receive_mortgage_application
- Seamless application retrieval when agents call track_application_status
- Cross-agent application data sharing through application IDs
- Persistent application state throughout the workflow
"""

from .application_storage import (
    store_application_data,
    retrieve_application_data, 
    update_application_status,
    get_application_history,
    ensure_application_intake_rules
)

from .application_schema import (
    MortgageApplicationData,
    ApplicationStatusUpdate,
    ApplicationRetrievalResult
)

__all__ = [
    "store_application_data",
    "retrieve_application_data", 
    "update_application_status",
    "get_application_history",
    "ensure_application_intake_rules",
    "MortgageApplicationData",
    "ApplicationStatusUpdate", 
    "ApplicationRetrievalResult"
]
