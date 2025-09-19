#!/usr/bin/env python3
"""
A2A Agents Launcher for Mortgage Processing System

Comprehensive launcher for all A2A agents including orchestrator and specialized agents.
"""
import asyncio
import logging
import multiprocessing
import signal
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_orchestrator_agent():
    """Start the Mortgage A2A Orchestrator agent"""
    try:
        from .orchestrator_agent import create_mortgage_orchestrator_server
        import uvicorn
        
        logger.info("🏠 Starting Mortgage A2A Orchestrator on port 8000...")
        app = create_mortgage_orchestrator_server(host="localhost", port=8000)
        uvicorn.run(app, host="localhost", port=8000)
    except KeyboardInterrupt:
        logger.info("🛑 Orchestrator agent stopped")
    except Exception as e:
        logger.error(f" Orchestrator agent error: {e}")

def start_web_search_agent():
    """Start the LlamaStack web search A2A agent"""
    try:
        from .agents.web_search_agent import create_web_search_server
        import uvicorn
        
        logger.info("🔍 Starting LlamaStack Web Search Agent on port 8002...")
        app = create_web_search_server(host="localhost", port=8002)
        uvicorn.run(app, host="localhost", port=8002)
    except KeyboardInterrupt:
        logger.info("🛑 Web search agent stopped")
    except Exception as e:
        logger.error(f" Web search agent error: {e}")

def start_all_agents():
    """Start all A2A agents in separate processes"""
    logger.info("🚀 Starting Mortgage Processing A2A System...")
    
    processes = []
    
    try:
        # Start orchestrator agent first
        orchestrator_process = multiprocessing.Process(
            target=start_orchestrator_agent,
            name="MortgageOrchestrator"
        )
        orchestrator_process.start()
        processes.append(orchestrator_process)
        logger.info(" Mortgage A2A Orchestrator started on port 8000")
        
        # Give orchestrator time to start
        time.sleep(2)
        
        # Start web search agent
        web_search_process = multiprocessing.Process(
            target=start_web_search_agent,
            name="WebSearchAgent"
        )
        web_search_process.start()
        processes.append(web_search_process)
        logger.info(" Web Search Agent started on port 8002")
        
        # Wait a moment for agents to initialize
        time.sleep(3)
        
        logger.info("🎯 Mortgage A2A System is ready!")
        logger.info("📍 Orchestrator: http://localhost:8000")
        logger.info("🔍 Web Search:   http://localhost:8002")
        logger.info("Press Ctrl+C to stop all agents.")
        
        # Keep main process alive
        while True:
            time.sleep(1)
            
            # Check if any process died
            for process in processes:
                if not process.is_alive():
                    logger.error(f" Process {process.name} died unexpectedly")
                    
    except KeyboardInterrupt:
        logger.info("🛑 Stopping Mortgage A2A System...")
        
        # Terminate all processes gracefully
        for process in processes:
            if process.is_alive():
                logger.info(f"🛑 Stopping {process.name}...")
                process.terminate()
                process.join(timeout=5)
                
                if process.is_alive():
                    logger.warning(f"⚠️  Force killing {process.name}...")
                    process.kill()
                    process.join()
        
        logger.info(" All A2A agents stopped")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f" Error in A2A system: {e}")
        sys.exit(1)

def start_orchestrator_only():
    """Start only the orchestrator (for testing)"""
    logger.info("🏠 Starting Orchestrator Only...")
    start_orchestrator_agent()

def start_web_search_only():
    """Start only the web search agent (for testing)"""
    logger.info("🔍 Starting Web Search Only...")
    start_web_search_agent()

if __name__ == "__main__":
    print("🏠 Mortgage Processing A2A System Launcher")
    print("=" * 50)
    print("Available components:")
    print("  🏠 Mortgage A2A Orchestrator (port 8000)")
    print("  🔍 Web Search Agent         (port 8002)")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "orchestrator":
            start_orchestrator_only()
        elif command == "websearch":
            start_web_search_only()
        else:
            print(f" Unknown command: {command}")
            print("Usage: python launcher.py [orchestrator|websearch]")
            sys.exit(1)
    else:
        start_all_agents()
