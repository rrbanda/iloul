#!/usr/bin/env python3
"""
Simple Production Entry Point for Mortgage Processing System

Provides FastAPI server for the LangGraph workflow.
A2A system should be started separately via the unified startup script.
"""
import os
import asyncio
import logging
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .workflow_manager import MortgageConversationWorkflow
from .external_agents import get_external_agents_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global workflow manager
workflow_manager = None

# Create FastAPI app
app = FastAPI(
    title="Mortgage Processing System",
    description="LangGraph-based mortgage application processing with A2A integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the workflow manager on startup"""
    global workflow_manager
    logger.info("🏠 Initializing Mortgage Processing Workflow...")
    workflow_manager = MortgageConversationWorkflow(use_persistent_storage=True)
    logger.info("✅ Workflow manager ready")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if workflow manager is ready
        if workflow_manager is None:
            return JSONResponse(
                status_code=503,
                content={"status": "starting", "message": "Workflow manager not ready"}
            )
        
        # Check A2A system health (optional - won't fail if A2A is down)
        a2a_status = {}
        try:
            external_client = get_external_agents_client()
            agents = external_client.get_available_agents()
            a2a_status = {
                agent["name"]: "enabled" if agent["enabled"] else "disabled"
                for agent in agents
            }
        except Exception as e:
            a2a_status = {"error": f"A2A system unavailable: {str(e)}"}
        
        return {
            "status": "healthy",
            "workflow_manager": "ready",
            "a2a_agents": a2a_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mortgage Processing System API",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/chat")
async def chat_endpoint(request: dict):
    """Chat endpoint for mortgage processing"""
    try:
        if workflow_manager is None:
            raise HTTPException(status_code=503, detail="Workflow manager not ready")
        
        message = request.get("message", "")
        user_id = request.get("user_id", "default")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Process message through workflow
        response = await workflow_manager.process_message_async(
            message=message,
            user_id=user_id
        )
        
        return {
            "response": response,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Main entry point for the LangGraph API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mortgage Processing System API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting LangGraph API server on {args.host}:{args.port}")
    
    # Start the server
    uvicorn.run(
        "mortgage_processor.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()