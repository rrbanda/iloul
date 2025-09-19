#!/usr/bin/env python3
"""
Sync External Tools - Direct HTTP calls to A2A services
Provides sync versions that call A2A REST endpoints directly
"""
import requests
import json
import uuid
from langchain_core.tools import tool

def call_a2a_orchestrator(query: str) -> str:
    """Helper function to call A2A orchestrator via HTTP"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "messageId": str(uuid.uuid4()),
                    "contextId": str(uuid.uuid4()),
                    "parts": [{"type": "text", "text": query}]
                },
                "configuration": {"acceptedOutputModes": ["text"]}
            }
        }
        
        response = requests.post("http://localhost:8000", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return f"🔍 **A2A Orchestrator Results**\n\n{result['result']}"
            else:
                return f"🔍 **A2A Orchestrator Response**\n\n{result}"
        else:
            return f" A2A service returned status {response.status_code}"
    except Exception as e:
        return f" A2A services unavailable: {str(e)}\n\n💡 Make sure A2A services are running (python src/start_a2a_only.py)"

@tool
def sync_search_web_information(query: str) -> str:
    """
    Search the web for current information via A2A orchestrator.
    
    Use this tool when you need:
    - Current mortgage rates or market conditions
    - Recent real estate news or regulatory changes  
    - Up-to-date information about loan programs
    - Current economic indicators affecting mortgages
    
    Args:
        query: The search query for current information
        
    Returns:
        A2A orchestrated search results
    """
    return call_a2a_orchestrator(query)

@tool
def sync_get_current_mortgage_rates() -> str:
    """
    Get current mortgage interest rates and market conditions.
    
    Returns:
        Current mortgage rates and market information
    """
    query = "current mortgage interest rates 2024 FHA conventional VA loan rates today"
    return call_a2a_orchestrator(query)

@tool
def sync_get_mortgage_market_news() -> str:
    """
    Get recent mortgage market news and regulatory updates.
    
    Returns:
        Recent mortgage industry news and updates
    """
    query = "mortgage market news recent changes lending requirements 2024 housing market"
    return call_a2a_orchestrator(query)

@tool
def sync_use_a2a_orchestrator(query: str) -> str:
    """
    Use the A2A orchestrator for complex queries.
    
    Args:
        query: Complex query that requires A2A orchestration
        
    Returns:
        Results from the most appropriate agent via A2A orchestrator
    """
    return call_a2a_orchestrator(query)

@tool  
def sync_search_loan_program_updates(loan_type: str) -> str:
    """
    Search for recent updates to specific loan programs.
    
    Args:
        loan_type: Type of loan (FHA, VA, USDA, Conventional, etc.)
        
    Returns:
        Recent updates for the specified loan program
    """
    query = f"{loan_type} loan program updates 2024 requirements changes guidelines"
    return call_a2a_orchestrator(query)
