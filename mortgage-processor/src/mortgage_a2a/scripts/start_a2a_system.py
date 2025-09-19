#!/usr/bin/env python3
"""
A2A System Startup Script (Startup Only)

Starts the complete mortgage A2A system including orchestrator and web search agent.
Does NOT include tests - use separate test_a2a.py for testing.
"""
import os
import sys
import asyncio
import logging
import multiprocessing
import signal
import time
from pathlib import Path

import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_orchestrator():
    """Start the A2A orchestrator agent"""
    try:
        from mortgage_a2a.orchestrator_agent import create_mortgage_orchestrator_server
        import uvicorn
        
        logger.info("🏠 Starting Mortgage A2A Orchestrator on port 8000...")
        app = create_mortgage_orchestrator_server()
        uvicorn.run(app, host="localhost", port=8000, log_level="info")
    except Exception as e:
        logger.error(f" Orchestrator error: {e}")
        raise

def start_web_search():
    """Start the web search agent"""
    try:
        from mortgage_a2a.agents.web_search_agent import create_web_search_server
        import uvicorn
        
        logger.info("🔍 Starting Web Search Agent on port 8002...")
        app = create_web_search_server()
        uvicorn.run(app, host="localhost", port=8002, log_level="info")
    except Exception as e:
        logger.error(f" Web Search error: {e}")
        raise

async def check_service_health(url, service_name):
    """Check if a service is healthy using JSON-RPC ping"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Use a simple JSON-RPC request to check if service is responsive
            ping_payload = {
                "jsonrpc": "2.0",
                "id": "health-check",
                "method": "ping",
                "params": {}
            }
            response = await client.post(url, json=ping_payload)
            # Accept both 200 (success) and 405 (method not found) as healthy
            # 405 means the server is running but doesn't support ping method
            if response.status_code in [200, 405]:
                logger.info(f" {service_name} is healthy")
                return True
            else:
                logger.warning(f"⚠️  {service_name} returned status {response.status_code}")
                return False
    except Exception as e:
        logger.warning(f"⚠️  {service_name} health check failed: {e}")
        return False

async def wait_for_services(services, timeout=60):
    """Wait for all services to be healthy"""
    logger.info("🔍 Waiting for services to be ready...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        all_healthy = True
        
        for url, name in services:
            healthy = await check_service_health(url, name)
            if not healthy:
                all_healthy = False
                break
        
        if all_healthy:
            logger.info("🎯 All services are ready!")
            return True
        
        await asyncio.sleep(2)
    
    logger.error(" Timeout waiting for services to be ready")
    return False

# Test functions removed - use separate test_a2a.py script for testing

def main():
    """Main function to start the A2A system"""
    print("🏠 Starting Mortgage Processing A2A System...")
    
    processes = []
    
    try:
        # Start orchestrator
        orchestrator_process = multiprocessing.Process(
            target=start_orchestrator,
            name="MortgageOrchestrator"
        )
        orchestrator_process.start()
        processes.append(orchestrator_process)
        logger.info("🚀 Started Mortgage A2A Orchestrator")
        
        # Give orchestrator time to start
        time.sleep(3)
        
        # Start web search agent
        web_search_process = multiprocessing.Process(
            target=start_web_search,
            name="WebSearchAgent"
        )
        web_search_process.start()
        processes.append(web_search_process)
        logger.info("🚀 Started Web Search Agent")
        
        # Wait for services to be ready
        time.sleep(5)
        
        services = [
            ("http://localhost:8000", "Mortgage A2A Orchestrator"),
            ("http://localhost:8002", "Web Search Agent")
        ]
        
        if asyncio.run(wait_for_services(services)):
            print("\n" + "="*60)
            print("🎉 MORTGAGE A2A SYSTEM READY!")
            print("="*60)
            print("📍 Orchestrator: http://localhost:8000")
            print("🔍 Web Search:   http://localhost:8002")
            print("📋 Run tests with: python test_a2a.py")
            print("📋 Test endpoint: curl -X POST http://localhost:8000 -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"method\":\"message/send\",\"params\":{\"message\":{\"parts\":[{\"type\":\"text\",\"text\":\"test\"}]}}}'")
            print("="*60)
            print("Press Ctrl+C to stop all services.")
            
            # Keep system running
            try:
                while True:
                    time.sleep(5)
                    # Check if processes are still alive
                    for process in processes:
                        if not process.is_alive():
                            logger.error(f" Process {process.name} died unexpectedly")
            except KeyboardInterrupt:
                logger.info("🛑 Shutdown requested...")
        else:
            logger.error(" Services failed to start properly")
                
    except KeyboardInterrupt:
        logger.info("🛑 Stopping A2A system...")
    except Exception as e:
        logger.error(f" Error: {e}")
    finally:
        # Clean shutdown
        for process in processes:
            if process.is_alive():
                logger.info(f"🛑 Stopping {process.name}...")
                process.terminate()
                process.join(timeout=5)
                
                if process.is_alive():
                    logger.warning(f"⚠️  Force killing {process.name}...")
                    process.kill()
                    process.join()
        
        logger.info(" All A2A services stopped")

if __name__ == "__main__":
    main()
