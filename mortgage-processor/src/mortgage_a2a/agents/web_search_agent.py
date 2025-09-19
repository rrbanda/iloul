#!/usr/bin/env python3
"""
LlamaStack A2A Agent using proper A2A SDK
"""
import asyncio
import json
import logging
import httpx
import uvicorn

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

class LlamaStackWebSearchExecutor(AgentExecutor):
    """LlamaStack Agent Executor for web search using correct endpoint"""
    
    def __init__(self):
        # LlamaStack configuration from working curl command
        self.base_url = "https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com/v1"
        self.agent_id = "b35d9295-552a-4b75-8fd9-8a4b9e1bef26"
        
    async def create_session(self, client: httpx.AsyncClient) -> str:
        """Create a new session for the LlamaStack agent"""
        session_url = f"{self.base_url}/agents/{self.agent_id}/session"
        
        session_payload = {
            "session_name": "mortgage_a2a_session"
        }
        
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = await client.post(session_url, headers=headers, json=session_payload)
        response.raise_for_status()
        
        session_data = response.json()
        session_id = session_data.get("session_id")
        
        if not session_id:
            raise Exception(f"Failed to get session_id from response: {session_data}")
            
        logger.info(f"Created LlamaStack session: {session_id}")
        return session_id

    async def call_llamastack(self, query: str) -> str:
        """Call LlamaStack Responses API with built-in web search"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Use Responses API instead of Agents API
                responses_url = f"{self.base_url}/openai/v1/responses"
                
                headers = {
                    "accept": "application/json",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "llama-4-scout-17b-16e-w4a16",  # Use actual model from your Llama Stack
                    "input": query,
                    "instructions": "You are a web search agent. Use web search to find relevant, current information to answer the user's query thoroughly.",
                    "tools": [
                        {
                            "type": "web_search",
                            "search_context_size": "medium"
                        }
                    ],
                    "stream": False,  # Start with non-streaming for simplicity
                    "max_infer_iters": 5
                }
                
                logger.info(f"Sending query to LlamaStack Responses API: {query}")
                
                response = await client.post(responses_url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                return self._extract_response_content(result)
                    
        except httpx.HTTPStatusError as e:
            return f"LlamaStack HTTP error {e.response.status_code}: {e.response.text}"
        except Exception as e:
            logger.error(f"LlamaStack error: {e}")
            return f"Web search error: {str(e)}"

    def _extract_response_content(self, result: dict) -> str:
        """Extract content from Responses API result"""
        try:
            # Handle the Responses API output format
            if "output" in result:
                content = result["output"].get("content", "")
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # Handle content array format
                    text_parts = []
                    for item in content:
                        if item.get("type") == "output_text":
                            text_parts.append(item.get("text", ""))
                    return "".join(text_parts)
            
            # Fallback to direct content if structure is different
            if "content" in result:
                return str(result["content"])
                
            return "No content found in response"
            
        except Exception as e:
            logger.warning(f"Error extracting response content: {e}")
            return f"Error processing web search results: {str(e)}"

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        logger.info(f"Processing web search query: {query}")
        
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
                    "Searching the web...",
                    task.context_id,
                    task.id,
                ),
            )
            
            search_result = await self.call_llamastack(query)
            
            await updater.add_artifact(
                [Part(root=TextPart(text=search_result))],
                name='web_search_result',
            )
            await updater.complete()

        except Exception as e:
            logger.error(f'Error processing web search: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())

def create_web_search_agent_card(host: str = "localhost", port: int = 8002) -> AgentCard:
    """Create agent card for LlamaStack web search"""
    skills = [
        AgentSkill(
            id="web_search",
            name="Web Search",
            description="Real-time web search and current information",
            tags=["web", "search", "current", "news", "latest", "internet"]
        ),
        AgentSkill(
            id="current_events", 
            name="Current Events",
            description="Latest news and current events information",
            tags=["news", "current", "events", "recent", "today"]
        ),
        AgentSkill(
            id="market_data",
            name="Market Data",
            description="Current market rates and financial information",
            tags=["rates", "market", "finance", "economy"]
        )
    ]
    
    return AgentCard(
        name="Web Search Agent",
        description="Real-time web search using LlamaStack for mortgage and market information",
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

def create_web_search_server(host: str = "localhost", port: int = 8002):
    """Create LlamaStack web search A2A server"""
    agent_card = create_web_search_agent_card(host, port)
    
    request_handler = DefaultRequestHandler(
        agent_executor=LlamaStackWebSearchExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    server = A2AStarletteApplication(
        agent_card=agent_card, 
        http_handler=request_handler
    )
    
    return server.build()

if __name__ == "__main__":
    print("🚀 Starting LlamaStack Web Search A2A Agent...")
    print("📍 Running on: http://localhost:8002")
    print("🔍 Skills: Web Search, Current Events, Market Data")
    print("💡 Using real LlamaStack endpoint for web search")
    
    app = create_web_search_server()
    uvicorn.run(app, host="localhost", port=8002)
