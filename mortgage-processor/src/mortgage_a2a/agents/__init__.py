"""
A2A Agents Package

Contains individual A2A agent implementations using the A2A SDK.
Each agent can run as a standalone server on different ports.
"""

from .web_search_agent import (
    LlamaStackWebSearchExecutor,
    create_web_search_agent_card,
    create_web_search_server
)

__all__ = [
    "LlamaStackWebSearchExecutor",
    "create_web_search_agent_card", 
    "create_web_search_server"
]
