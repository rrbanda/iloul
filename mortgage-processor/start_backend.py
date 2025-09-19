#!/usr/bin/env python3
"""
Unified Backend Startup Script

Starts the complete mortgage processing backend with one command:
- A2A System (Orchestrator + Web Search Agent)
- LangGraph API Server (FastAPI with mortgage workflow)

Usage:
    python start_backend.py                    # Start everything
    python start_backend.py --dev              # Development mode with auto-reload
    python start_backend.py --a2a-only         # Start only A2A system
    python start_backend.py --api-only         # Start only API server
"""
import os
import sys
import time
import signal
import asyncio
import logging
import argparse
import multiprocessing
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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

def start_langgraph_api(host="0.0.0.0", port=8080, reload=False):
    """Start the LangGraph API server"""
    try:
        from mortgage_processor.app import app
        import uvicorn
        
        logger.info(f"🤖 Starting LangGraph API on {host}:{port}...")
        uvicorn.run(
            "mortgage_processor.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        logger.error(f" LangGraph API error: {e}")
        raise

def check_port_available(port):
    """Check if a port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
        return True
    except OSError:
        return False

async def wait_for_services():
    """Wait for all services to be ready"""
    import httpx
    
    services = [
        ("http://localhost:8000", "A2A Orchestrator"),
        ("http://localhost:8002", "Web Search Agent"),
        ("http://localhost:8080/health", "LangGraph API")
    ]
    
    logger.info("🔍 Waiting for services to be ready...")
    
    for i in range(30):  # Wait up to 60 seconds
        all_ready = True
        
        for url, name in services:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(url)
                    if response.status_code not in [200, 405]:  # 405 is OK for A2A services
                        all_ready = False
                        break
            except:
                all_ready = False
                break
        
        if all_ready:
            logger.info("🎯 All services are ready!")
            return True
        
        await asyncio.sleep(2)
        logger.info(f"⏳ Waiting for services... ({i+1}/30)")
    
    logger.error(" Timeout waiting for services")
    return False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Shutdown signal received...")
    cleanup_processes()
    sys.exit(0)

def cleanup_processes():
    """Clean up all spawned processes"""
    global processes
    
    logger.info("🧹 Cleaning up processes...")
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
    logger.info("✅ All processes stopped")

def main():
    """Main entry point"""
    global processes
    
    parser = argparse.ArgumentParser(description="Unified Backend Startup")
    parser.add_argument("--dev", action="store_true", help="Development mode with auto-reload")
    parser.add_argument("--a2a-only", action="store_true", help="Start only A2A system")
    parser.add_argument("--api-only", action="store_true", help="Start only API server")
    parser.add_argument("--host", default="0.0.0.0", help="API server host")
    parser.add_argument("--port", type=int, default=8080, help="API server port")
    
    args = parser.parse_args()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("🚀 Starting Mortgage Processing Backend...")
        print("=" * 60)
        
        # Check port availability
        if not args.api_only:
            if not check_port_available(8000):
                logger.error(" Port 8000 (A2A Orchestrator) is already in use")
                return
            if not check_port_available(8002):
                logger.error(" Port 8002 (Web Search Agent) is already in use")
                return
        
        if not args.a2a_only:
            if not check_port_available(args.port):
                logger.error(f" Port {args.port} (LangGraph API) is already in use")
                return
        
        # Start A2A system
        if not args.api_only:
            logger.info("🏠 Starting A2A System...")
            
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
            
            time.sleep(3)  # Give web search time to start
        
        # Start LangGraph API
        if not args.a2a_only:
            logger.info("🤖 Starting LangGraph API...")
            
            api_process = multiprocessing.Process(
                target=start_langgraph_api,
                args=(args.host, args.port, args.dev),
                name="LangGraph-API"
            )
            api_process.start()
            processes.append(api_process)
            logger.info("✅ LangGraph API starting...")
        
        # Wait for services to be ready
        time.sleep(5)
        
        if asyncio.run(wait_for_services()):
            print("\n" + "=" * 60)
            print("🎉 MORTGAGE PROCESSING BACKEND READY!")
            print("=" * 60)
            if not args.api_only:
                print("🏠 A2A Orchestrator:  http://localhost:8000")
                print("🔍 Web Search Agent:  http://localhost:8002")
            if not args.a2a_only:
                print(f"🤖 LangGraph API:     http://localhost:{args.port}")
                print(f"📋 API Docs:          http://localhost:{args.port}/docs")
                print(f"❤️  Health Check:     http://localhost:{args.port}/health")
            print("=" * 60)
            print("Press Ctrl+C to stop all services.")
            print("=" * 60)
            
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
        else:
            logger.error(" Failed to start all services")
            cleanup_processes()
            return
            
    except Exception as e:
        logger.error(f" Error: {e}")
        cleanup_processes()
        return
    finally:
        cleanup_processes()

if __name__ == "__main__":
    main()
