#!/usr/bin/env python3
"""
External A2A Agents Client
Provides integration with external A2A agents like LlamaStack web search
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import httpx
from langchain_core.tools import tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class A2AAgent:
    """Configuration for an external A2A agent"""
    name: str
    url: str
    description: str
    skills: List[str]
    enabled: bool = True


class ExternalAgentsClient:
    """Client for calling external A2A agents"""
    
    def __init__(self):
        """Initialize the external agents client"""
        self.agents = self._load_default_agents()
        self.timeout = 60.0
        
    def _load_default_agents(self) -> Dict[str, A2AAgent]:
        """Load default external agent configurations"""
        return {
            # A2A Orchestrator for intelligent routing (preferred method)
            "orchestrator": A2AAgent(
                name="Mortgage A2A Orchestrator",
                url="http://localhost:8000",
                description="Intelligent orchestrator for mortgage processing that routes queries to specialized agents",
                skills=["mortgage", "routing", "orchestration", "web", "search", "current", "rates", "market"],
                enabled=True  # Primary routing agent
            ),
            # Direct LlamaStack web search agent
            "web_search": A2AAgent(
                name="Web Search Agent",
                url="http://localhost:8002",
                description="Real-time web search and current information using LlamaStack",
                skills=["web", "search", "current", "news", "latest", "internet", "market", "rates"],
                enabled=True  # Web search functionality via A2A
            )
        }
    
    
    async def call_orchestrator(self, query: str) -> Dict[str, Any]:
        """Call the A2A orchestrator for intelligent routing (REQUIRED - no fallbacks)"""
        agent = self.agents.get("orchestrator")
        if not agent or not agent.enabled:
            return {
                "success": False,
                "error": "A2A Orchestrator is not available or disabled - no fallback allowed",
                "response": ""
            }
        
        logger.info(f"🏠 Calling A2A Orchestrator with query: {query}")
        
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
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(agent.url, json=payload)
                response.raise_for_status()
                agent_result = response.json()
                
                logger.info(f"📡 Orchestrator response: {agent_result}")
                
                # Handle both task-based and direct responses
                if "result" in agent_result:
                    result_data = agent_result["result"]
                    
                    # Check if it's a task (async processing)
                    if isinstance(result_data, dict) and "id" in result_data:
                        task_id = result_data["id"]
                        logger.info(f"⏳ Waiting for orchestrator task {task_id} to complete...")
                        
                        response_text = await self._wait_for_task_completion(client, agent.url, task_id)
                        
                        return {
                            "success": True,
                            "agent_name": agent.name,
                            "response": response_text,
                            "raw_result": agent_result,
                            "routing_type": "orchestrator_async"
                        }
                    else:
                        # Direct response
                        response_text = self._extract_response_text(agent_result)
                        
                        return {
                            "success": True,
                            "agent_name": agent.name,
                            "response": response_text,
                            "raw_result": agent_result,
                            "routing_type": "orchestrator_direct"
                        }
                else:
                    return {
                        "success": False,
                        "error": "No result in orchestrator response",
                        "response": ""
                    }
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code} error calling orchestrator: {e.response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "response": ""
            }
            
        except Exception as e:
            error_msg = f"Error calling orchestrator: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "response": ""
            }
    
    async def _wait_for_task_completion(self, client: httpx.AsyncClient, endpoint: str, task_id: str, max_wait: int = 30) -> str:
        """Wait for A2A task to complete and return result"""
        for attempt in range(max_wait):
            await asyncio.sleep(1)
            
            get_payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tasks/get",
                "params": {"id": task_id}
            }
            
            try:
                response = await client.post(endpoint, json=get_payload)
                response.raise_for_status()
                result = response.json()
                
                if "result" in result and result["result"]:
                    task_data = result["result"]
                    task_state = task_data.get("status", {}).get("state")
                    
                    if task_state == "completed":
                        # Extract actual response text
                        artifacts = task_data.get("artifacts", [])
                        for artifact in artifacts:
                            parts = artifact.get("parts", [])
                            for part in parts:
                                if part.get("kind") == "text":
                                    return part.get("text", "Task completed but no response")
                        return "Task completed but no response found"
                    elif task_state == "failed":
                        error_msg = task_data.get("status", {}).get("message", "Task failed")
                        return f" Orchestrator task failed: {error_msg}"
                        
            except Exception as e:
                logger.warning(f"⚠️  Error checking task status: {e}")
                continue
        
        return "⏰ Orchestrator timeout - no response received"

    async def call_agent(self, agent_key: str, query: str) -> Dict[str, Any]:
        """Call an external A2A agent (fallback method)"""
        agent = self.agents.get(agent_key)
        if not agent or not agent.enabled:
            return {
                "success": False,
                "error": f"Agent '{agent_key}' not available or disabled",
                "response": ""
            }
        
        logger.info(f"Calling external agent '{agent.name}' with query: {query}")
        
        # Use A2A protocol for all agents - no fallbacks allowed
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
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(agent.url, json=payload)
                response.raise_for_status()
                agent_result = response.json()
                
                logger.info(f"Received response from '{agent.name}': {agent_result}")
                
                # Extract the actual result from the A2A response
                response_text = self._extract_response_text(agent_result)
                
                return {
                    "success": True,
                    "agent_name": agent.name,
                    "response": response_text,
                    "raw_result": agent_result,
                    "routing_type": "direct_a2a"
                }
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code} error calling {agent.name}: {e.response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "response": ""
            }
        except Exception as e:
            error_msg = f"Error calling {agent.name}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "response": ""
            }
    
    def _extract_response_text(self, agent_result: Dict) -> str:
        """Extract response text from A2A agent result"""
        try:
            # Check for artifacts in the result
            if "result" in agent_result and "artifacts" in agent_result["result"]:
                artifacts = agent_result["result"]["artifacts"]
                for artifact in artifacts:
                    parts = artifact.get("parts", [])
                    for part in parts:
                        if part.get("kind") == "text" or part.get("type") == "text":
                            text_content = part.get("text", "")
                            if text_content:
                                return text_content
            
            # Fallback: check for direct message content
            if "result" in agent_result and "message" in agent_result["result"]:
                message = agent_result["result"]["message"]
                if isinstance(message, dict) and "content" in message:
                    return message["content"]
            
            # Fallback: return string representation
            return str(agent_result).replace("'", '"')[:500] + "..."
            
        except Exception as e:
            logger.warning(f"Error extracting response text: {e}")
            return "Response received but could not extract text content"
    
    def get_available_agents(self) -> List[Dict[str, str]]:
        """Get list of available external agents"""
        return [
            {
                "key": key,
                "name": agent.name,
                "description": agent.description,
                "skills": ", ".join(agent.skills),
                "enabled": agent.enabled,
                "url": agent.url
            }
            for key, agent in self.agents.items()
        ]


# Global client instance
_external_agents_client = None


def get_external_agents_client() -> ExternalAgentsClient:
    """Get the global external agents client"""
    global _external_agents_client
    if _external_agents_client is None:
        _external_agents_client = ExternalAgentsClient()
    return _external_agents_client


# LangChain tools for external agents
@tool
async def search_web_information(query: str) -> str:
    """
    Search the web for current information, news, market data, or recent developments.
    
    This tool ONLY uses A2A orchestration - no fallbacks allowed.
    The orchestrator will intelligently route your query to the best available agent.
    
    Use this tool when you need:
    - Current mortgage rates or market conditions
    - Recent real estate news or regulatory changes  
    - Up-to-date information about loan programs
    - Current economic indicators affecting mortgages
    - Recent changes in lending requirements
    - Latest housing market trends
    
    Args:
        query: The search query for current information
        
    Returns:
        A2A orchestrated search results or error if A2A system unavailable
    """
    client = get_external_agents_client()
    
    # Use A2A orchestrator only - no fallbacks
    result = await client.call_orchestrator(query)
    
    if result["success"]:
        routing_info = result.get("routing_type", "a2a_orchestrator")
        agent_name = result.get("agent_name", "A2A Orchestrator")
        
        response = f"🔍 **{agent_name} Results**\n\n{result['response']}"
        response += f"\n\n_Routed via A2A Orchestrator - No Fallbacks Used_"
        
        return response
    else:
        return f" A2A Orchestrator Error: {result['error']}\n\n⚠️ No fallback mechanisms available - A2A system required."


@tool
async def get_current_mortgage_rates() -> str:
    """
    Get current mortgage interest rates and market conditions via A2A orchestrator.
    
    Returns:
        Current mortgage rates and market information (A2A only - no fallbacks)
    """
    query = "current mortgage interest rates 2024 FHA conventional VA loan rates today"
    return await search_web_information(query)


@tool
async def get_mortgage_market_news() -> str:
    """
    Get recent mortgage market news and regulatory updates via A2A orchestrator.
    
    Returns:
        Recent mortgage industry news and updates (A2A only - no fallbacks)
    """
    query = "mortgage market news recent changes lending requirements 2024 housing market"
    return await search_web_information(query)


@tool
async def search_loan_program_updates(loan_type: str) -> str:
    """
    Search for recent updates to specific loan programs via A2A orchestrator.
    
    Args:
        loan_type: Type of loan (FHA, VA, USDA, Conventional, etc.)
        
    Returns:
        Recent updates for the specified loan program (A2A only - no fallbacks)
    """
    query = f"{loan_type} loan program updates 2024 requirements changes guidelines"
    return await search_web_information(query)


@tool
async def use_a2a_orchestrator(query: str) -> str:
    """
    Use the A2A orchestrator to intelligently route complex queries to specialized agents.
    
    This tool provides strict A2A routing with NO fallbacks:
    - Multiple agent coordination via A2A protocol
    - Context-aware agent selection using LangGraph
    - Real-time web search via A2A agents only
    - Fails if A2A system unavailable (no fallbacks)
    
    Args:
        query: Complex query that requires A2A orchestration
        
    Returns:
        Results from the most appropriate agent via A2A orchestrator or error
    """
    client = get_external_agents_client()
    result = await client.call_orchestrator(query)
    
    if result["success"]:
        routing_info = result.get("routing_type", "a2a_orchestrator")
        agent_name = result.get("agent_name", "A2A Agent")
        
        response = f"🏠 **A2A Orchestrator → {agent_name}**\n\n{result['response']}"
        response += f"\n\n_Strict A2A Routing: {routing_info} (No Fallbacks)_"
        
        return response
    else:
        return f" A2A Orchestrator Error: {result['error']}\n\n⚠️ No fallback mechanisms available - A2A system required."

@tool
def list_available_external_agents() -> str:
    """
    List all available A2A agents and their capabilities (NO fallback mechanisms).
    
    Returns:
        Information about available A2A agents - orchestrator required for routing
    """
    client = get_external_agents_client()
    agents = client.get_available_agents()
    
    if not agents:
        return " No A2A agents are currently available - system requires A2A orchestrator."
    
    result = "🤖 **Available A2A Agents (Strict A2A Only)**\n\n"
    
    # Highlight orchestrator first
    orchestrator = next((agent for agent in agents if agent["key"] == "orchestrator"), None)
    if orchestrator:
        status = "✅ Enabled" if orchestrator["enabled"] else " Disabled"
        result += f"🏠 **{orchestrator['name']}** ({status}) - REQUIRED ROUTER\n"
        result += f"📝 {orchestrator['description']}\n"
        result += f"🌐 URL: {orchestrator['url']}\n"
        result += f"🏷️ Skills: {orchestrator['skills']}\n\n"
    
    # List other agents
    for agent in agents:
        if agent["key"] != "orchestrator":
            status = "✅ Enabled" if agent["enabled"] else " Disabled"
            result += f"**{agent['name']}** ({status})\n"
            result += f"📝 {agent['description']}\n"
            result += f"🌐 URL: {agent['url']}\n"
            result += f"🏷️ Skills: {agent['skills']}\n\n"
    
    result += "⚠️ **No Fallback Mechanisms** - All routing requires A2A system to be running."
    
    return result


# Export the tools for use in agents
__all__ = [
    "ExternalAgentsClient",
    "get_external_agents_client", 
    "search_web_information",
    "use_a2a_orchestrator",
    "get_current_mortgage_rates",
    "get_mortgage_market_news",
    "search_loan_program_updates",
    "list_available_external_agents"
]
