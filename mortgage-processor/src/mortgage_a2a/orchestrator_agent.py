#!/usr/bin/env python3
"""
Smart Orchestrator Agent for Mortgage Processing A2A System
Routes requests from supervisor to appropriate specialized agents
"""
import asyncio
import logging
import uuid
from typing import Dict, TypedDict, List, Any, Optional

import httpx
import uvicorn
from langgraph.graph import StateGraph

from a2a.client import A2AClient, A2ACardResolver
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (
    AgentCard, AgentSkill, AgentCapabilities,
    InternalError, InvalidParamsError, Part, Task, TaskState, TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RouterState(TypedDict, total=False):
    """State for the orchestrator workflow"""
    request: Optional[str]
    query: Optional[str] 
    messages: Optional[List[dict]]
    selected_agent: Optional[str]
    confidence: Optional[float]
    reasoning: Optional[str]
    response: Optional[str]
    success: Optional[bool]
    agent_url: Optional[str]
    agent_skills: Optional[List[str]]
    analysis_details: Optional[str]

class MortgageA2AOrchestrator:
    """Intelligent orchestrator for mortgage processing A2A system"""
    
    def __init__(self):
        self.agents: Dict[str, AgentCard] = {}
        self.workflow = self._create_workflow()
        self._initialized = False
    
    async def initialize_agents(self):
        """Initialize with mortgage-specific agent endpoints"""
        if self._initialized:
            return
            
        default_agents = [
            "http://localhost:8002",  # Web Search Agent (LlamaStack)
            # Add more agents here as needed
        ]
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for endpoint in default_agents:
                try:
                    resolver = A2ACardResolver(client, endpoint)
                    agent_card = await resolver.get_agent_card()
                    if agent_card:
                        self.agents[agent_card.name] = agent_card
                        logger.info(f" Registered {agent_card.name} from {endpoint}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not register {endpoint}: {e}")
        
        self._initialized = True
    
    def _create_workflow(self):
        """Create LangGraph workflow for intelligent routing"""
        workflow = StateGraph(RouterState)
        workflow.add_node("analyze", self._analyze_request)
        workflow.add_node("route", self._route_to_agent)
        workflow.add_edge("analyze", "route")
        workflow.set_entry_point("analyze")
        workflow.set_finish_point("route")
        return workflow.compile()
    
    async def _analyze_request(self, state):
        """Analyze request and select best agent using mortgage-specific routing"""
        logger.info(f"🔍 Analyzing request: {state}")
        
        # Ensure agents are initialized
        await self.initialize_agents()
        
        # Extract request from multiple possible state formats
        request = self._extract_request_text(state)
        
        if not request:
            logger.error(" No request content found in state")
            request = "empty request"
        
        # Mortgage-specific intelligent routing
        best_agent = None
        best_score = 0.0
        request_lower = request.lower()
        
        logger.info(f"🎯 Analyzing: '{request_lower}' against {len(self.agents)} agents")
        
        # First try skill-based matching for registered agents
        for agent_name, agent_card in self.agents.items():
            score = 0
            matched_skills = []
            
            for skill in agent_card.skills:
                skill_score = 0
                for tag in (skill.tags or []):
                    if tag.lower() in request_lower:
                        skill_score += 1
                        matched_skills.append(tag)
                        logger.info(f" Agent '{agent_name}' matched tag '{tag}'")
                
                score += skill_score
            
            if score > best_score:
                best_score = score
                best_agent = agent_name
                logger.info(f"🏆 New best: {agent_name} (score: {score}, skills: {matched_skills})")
        
        # Enhanced mortgage-specific keyword routing
        if not best_agent or best_score == 0:
            logger.info("🔄 Using mortgage-specific keyword routing")
            
            # Web search triggers
            web_search_keywords = [
                "current", "latest", "recent", "news", "today", "2024", "2025",
                "rates", "market", "interest", "economic", "fed", "federal",
                "search", "find", "lookup", "google", "web", "internet",
                "regulations", "updates", "changes", "new"
            ]
            
            if any(keyword in request_lower for keyword in web_search_keywords):
                best_agent = "Web Search Agent"
                best_score = 0.8
                logger.info("🌐 Keyword routing to Web Search Agent")
            else:
                # Default to web search for unknown queries that might need current info
                best_agent = "Web Search Agent"
                best_score = 0.5
                logger.info("🌐 Default routing to Web Search Agent")
        
        confidence = min(best_score / 3.0, 1.0) if best_score > 0 else 0.5
        reasoning = f"Selected {best_agent} for mortgage processing query (score: {best_score})"
        
        result_state = {
            "selected_agent": best_agent,
            "confidence": confidence,
            "reasoning": reasoning,
            "request": request,
            "analysis_details": f"Analyzed {len(self.agents)} agents, best score: {best_score}"
        }
        
        state.update(result_state)
        logger.info(f" Analysis complete: {result_state}")
        return state
    
    async def _route_to_agent(self, state):
        """Route request to selected agent and get actual response"""
        selected_agent = state["selected_agent"]
        request = state["request"]
        confidence = state.get("confidence", 0)
        reasoning = state.get("reasoning", "")
        
        logger.info(f"🚀 Routing '{request}' to '{selected_agent}'")
        
        agent_card = self.agents.get(selected_agent)
        if not agent_card:
            error_msg = f" Agent {selected_agent} not available"
            logger.error(error_msg)
            state["response"] = error_msg
            state["success"] = False
            return state
        
        # Actually call the agent and get response
        try:
            if selected_agent == "Web Search Agent":
                response_text = await self._call_web_search_agent(agent_card.url, request)
            else:
                response_text = await self._call_generic_agent(agent_card.url, request)
            
            # Format final response
            final_response = f"🔍 **{selected_agent} Results**\n\n{response_text}\n\n"
            final_response += f"_Confidence: {confidence:.2f} | Reasoning: {reasoning}_"
            
            state["response"] = final_response
            state["success"] = True
            state["agent_url"] = agent_card.url
            state["agent_skills"] = [skill.name for skill in agent_card.skills]
            
            logger.info(f" Successfully got response from {selected_agent}")
            return state
            
        except Exception as e:
            error_msg = f" Error calling {selected_agent}: {str(e)}"
            logger.error(error_msg)
            state["response"] = error_msg
            state["success"] = False
            return state
    
    async def _call_web_search_agent(self, agent_url: str, query: str) -> str:
        """Call Web Search Agent via A2A protocol"""
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
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(agent_url, json=payload)
            response.raise_for_status()
            agent_result = response.json()
            
            logger.info(f"📡 Web Search Agent response: {agent_result}")
            
            # Handle task-based response (wait for completion)
            if "result" in agent_result and isinstance(agent_result["result"], dict):
                if "id" in agent_result["result"]:
                    # This is a task ID, wait for completion
                    task_id = agent_result["result"]["id"]
                    return await self._wait_for_task_completion(client, agent_url, task_id)
            
            # Extract direct response
            return self._extract_agent_response(agent_result)
    
    async def _call_generic_agent(self, agent_url: str, query: str) -> str:
        """Call any A2A agent via standard protocol"""
        return await self._call_web_search_agent(agent_url, query)  # Same protocol
    
    async def _wait_for_task_completion(self, client: httpx.AsyncClient, endpoint: str, task_id: str, max_wait: int = 30) -> str:
        """Wait for A2A task to complete"""
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
                        artifacts = task_data.get("artifacts", [])
                        for artifact in artifacts:
                            parts = artifact.get("parts", [])
                            for part in parts:
                                if part.get("kind") == "text":
                                    return part.get("text", "No response text")
                        return "Task completed but no response found"
                    elif task_state == "failed":
                        error_msg = task_data.get("status", {}).get("message", "Task failed")
                        return f" Agent error: {error_msg}"
                        
            except Exception as e:
                logger.warning(f"⚠️  Error checking task status: {e}")
                continue
        
        return "⏰ Agent timeout - no response received"
    
    def _extract_agent_response(self, agent_result: Dict) -> str:
        """Extract response text from A2A agent result"""
        try:
            # Check for artifacts
            if "result" in agent_result and "artifacts" in agent_result["result"]:
                artifacts = agent_result["result"]["artifacts"]
                for artifact in artifacts:
                    parts = artifact.get("parts", [])
                    for part in parts:
                        if part.get("kind") == "text" or part.get("type") == "text":
                            return part.get("text", "No text content")
            
            # Check for direct message content
            if "result" in agent_result and "message" in agent_result["result"]:
                message = agent_result["result"]["message"]
                if isinstance(message, dict) and "content" in message:
                    return message["content"]
            
            # Fallback
            return f"Response received: {str(agent_result)[:300]}..."
            
        except Exception as e:
            logger.warning(f"⚠️  Error extracting response: {e}")
            return "Could not extract response text"
    
    def _extract_request_text(self, state: Dict) -> str:
        """Extract request text from various state formats"""
        if "request" in state:
            return state["request"]
        elif "query" in state:
            return state["query"]
        elif "messages" in state and state["messages"]:
            last_message = state["messages"][-1]
            if isinstance(last_message, dict):
                return last_message.get("content", "")
            else:
                return getattr(last_message, 'content', "")
        else:
            return str(state)
    
    async def process_request(self, request: str) -> Dict:
        """Process request through LangGraph workflow"""
        await self.initialize_agents()
        
        logger.info(f"🎯 Processing mortgage request: {request}")
        
        try:
            initial_state: RouterState = {
                "request": request,
                "query": request,
                "messages": [{"role": "user", "content": request}]
            }
            
            final_state = await self.workflow.ainvoke(initial_state)
            
            return {
                "success": final_state.get("success", True),
                "selected_agent": final_state.get("selected_agent"),
                "confidence": final_state.get("confidence", 0),
                "reasoning": final_state.get("reasoning", ""),
                "response": final_state.get("response", "No response")
            }
            
        except Exception as e:
            logger.error(f" Workflow error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": f" Orchestrator error: {str(e)}"
            }

class MortgageOrchestratorExecutor(AgentExecutor):
    """A2A Agent Executor for the Mortgage Orchestrator"""

    def __init__(self):
        self.orchestrator = MortgageA2AOrchestrator()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        logger.info(f"🏠 Mortgage Orchestrator processing: {query}")
        
        task = context.current_task
        if not task:
            if context.message:
                task = new_task(context.message)
                await event_queue.enqueue_event(task)
            else:
                raise ServerError(error=InvalidParamsError())
        
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        
        try:
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    "🔍 Analyzing request and routing to best mortgage expert...",
                    task.context_id,
                    task.id,
                ),
            )
            
            result = await self.orchestrator.process_request(query)
            
            if result.get("success", False):
                response_text = result.get("response", "No response available")
            else:
                response_text = f" Routing Error: {result.get('error', 'Unknown error')}"
            
            await updater.add_artifact(
                [Part(root=TextPart(text=response_text))],
                name='mortgage_orchestrator_result',
            )
            await updater.complete()

        except Exception as e:
            logger.error(f' Mortgage Orchestrator error: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())

def create_mortgage_orchestrator_card(host: str = "localhost", port: int = 8000) -> AgentCard:
    """Create agent card for mortgage orchestrator"""
    skills = [
        AgentSkill(
            id="mortgage_routing",
            name="Mortgage Request Routing",
            description="Intelligent routing of mortgage-related queries to specialized agents",
            tags=["mortgage", "routing", "orchestration", "coordination"]
        ),
        AgentSkill(
            id="web_search_coordination",
            name="Web Search Coordination",
            description="Coordinating web searches for current mortgage rates and market information",
            tags=["web", "search", "current", "rates", "market", "news"]
        ),
        AgentSkill(
            id="agent_management",
            name="Agent Management",
            description="Managing and coordinating multiple mortgage processing agents",
            tags=["management", "coordination", "agents", "workflow"]
        )
    ]
    
    return AgentCard(
        name="Mortgage A2A Orchestrator",
        description="Intelligent orchestrator for mortgage processing A2A system",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=True,
            stateTransitionHistory=False
        ),
        skills=skills,
        defaultInputModes=["text"],
        defaultOutputModes=["text"]
    )

def create_mortgage_orchestrator_server(host: str = "localhost", port: int = 8000):
    """Create mortgage orchestrator A2A server"""
    agent_card = create_mortgage_orchestrator_card(host, port)
    
    request_handler = DefaultRequestHandler(
        agent_executor=MortgageOrchestratorExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    server = A2AStarletteApplication(
        agent_card=agent_card, 
        http_handler=request_handler
    )
    
    return server.build()

if __name__ == "__main__":
    print("🏠 Starting Mortgage A2A Orchestrator...")
    print("📍 Running on: http://localhost:8000")
    print("🎯 Skills: Mortgage Routing, Web Search Coordination, Agent Management")
    print("🤖 Coordinating mortgage processing agents via A2A protocol")
    
    app = create_mortgage_orchestrator_server()
    uvicorn.run(app, host="localhost", port=8000)
