#!/usr/bin/env python3
"""
A2A System Only Startup Script
Starts only the A2A orchestrator and web search agents
"""
import os
import sys
import time
import signal
import logging
import multiprocessing
from pathlib import Path

# Add src to Python path
sys.path.insert(0, '/app/src')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global process tracking
processes = []

def start_a2a_orchestrator():
    """Start the A2A orchestrator agent"""
    try:
        from mortgage_a2a.orchestrator_agent import create_mortgage_orchestrator_server
        import uvicorn
        
        logger.info("🏠 Starting Mortgage A2A Orchestrator on port 8000...")
        app = create_mortgage_orchestrator_server()
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        logger.error(f" Orchestrator error: {e}")
        raise

def start_a2a_web_search():
    """Start the A2A web search agent"""
    try:
        from mortgage_a2a.agents.web_search_agent import create_web_search_server
        import uvicorn
        
        logger.info("🔍 Starting Web Search Agent on port 8002...")
        app = create_web_search_server()
        uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
    except Exception as e:
        logger.error(f" Web Search error: {e}")
        raise

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 A2A shutdown signal received...")
    cleanup_processes()
    sys.exit(0)

def cleanup_processes():
    """Clean up all spawned processes"""
    global processes
    
    logger.info("🧹 Cleaning up A2A processes...")
    for process in processes:
        if process.is_alive():
            logger.info(f"Stopping {process.name}...")
            process.terminate()
            process.join(timeout=5)
            
            if process.is_alive():
                logger.warning(f"Force killing {process.name}...")
                process.kill()
                process.join()
    
    processes.clear()
    logger.info("✅ All A2A processes stopped")

def main():
    """Main entry point for A2A system"""
    global processes
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("🏠 Starting A2A System...")
        print("=" * 50)
        
        # Start orchestrator
        orchestrator_process = multiprocessing.Process(
            target=start_a2a_orchestrator,
            name="A2A-Orchestrator"
        )
        orchestrator_process.start()
        processes.append(orchestrator_process)
        logger.info("✅ A2A Orchestrator starting...")
        
        time.sleep(3)  # Give orchestrator time to start
        
        # Start web search agent
        web_search_process = multiprocessing.Process(
            target=start_a2a_web_search,
            name="A2A-WebSearch"
        )
        web_search_process.start()
        processes.append(web_search_process)
        logger.info("✅ A2A Web Search Agent starting...")
        
        time.sleep(3)
        
        print("=" * 50)
        print("🎉 A2A SYSTEM READY!")
        print("=" * 50)
        print("🏠 A2A Orchestrator:  http://0.0.0.0:8000")
        print("🔍 Web Search Agent:  http://0.0.0.0:8002")
        print("=" * 50)
        print("Press Ctrl+C to stop all services.")
        print("=" * 50)
        
        # Keep running and monitor processes
        try:
            while True:
                time.sleep(5)
                # Check if any process died
                for process in processes:
                    if not process.is_alive():
                        logger.error(f" Process {process.name} died unexpectedly")
                        cleanup_processes()
                        return
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
            
    except Exception as e:
        logger.error(f" Error: {e}")
        cleanup_processes()
        return
    finally:
        cleanup_processes()

if __name__ == "__main__":
    main()
