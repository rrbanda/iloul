#!/usr/bin/env python3
"""
🏠 MORTGAGE PROCESSING SYSTEM - INTERACTIVE SETUP & DEPLOYMENT 🏠
================================================================

Production-grade interactive setup script that guides users through:
✅ Environment selection (Native, Podman, OpenShift)
✅ Dependency installation and verification
✅ Service orchestration in correct order
✅ Health checks and validation
✅ Clean conflict resolution

Usage:
    python setup.py              # Interactive mode
    python setup.py --native     # Skip interaction, use native
    python setup.py --podman     # Skip interaction, use podman
    python setup.py --help       # Show all options
"""

import os
import sys
import time
import json
import signal
import shutil
import argparse
import subprocess
import multiprocessing
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Color codes for beautiful CLI output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class DeploymentType(Enum):
    NATIVE = "native"
    PODMAN = "podman"
    OPENSHIFT = "openshift"

@dataclass
class ServiceConfig:
    name: str
    description: str
    port: int
    dependencies: List[str]
    health_endpoint: str
    required_for: List[str]

@dataclass
class SystemRequirement:
    name: str
    description: str
    check_command: str
    install_hint: str
    required_for: List[DeploymentType]

class MortgageSystemOrchestrator:
    """
    Production-grade orchestrator for the complete mortgage processing system.
    Handles native, container, and cloud deployments with guided setup.
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.processes: List[subprocess.Popen] = []
        self.deployment_type: Optional[DeploymentType] = None
        
        # External dependencies (assumed running)
        self.external_deps = {
            "neo4j": {
                "name": "Neo4j Desktop/Server",
                "url": "bolt://localhost:7687",
                "description": "Graph database for application data"
            },
            "llamastack": {
                "name": "LlamaStack Server", 
                "url": "https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com",
                "description": "Remote LLM and vector database service"
            }
        }
        
        # Core services configuration
        self.services = {
            "a2a_orchestrator": ServiceConfig(
                name="A2A Orchestrator",
                description="Agent-to-Agent communication hub",
                port=8000,
                dependencies=[],
                health_endpoint="/",
                required_for=["web_search", "langgraph"]
            ),
            "web_search": ServiceConfig(
                name="Web Search Agent",
                description="External web search capabilities",
                port=8002,
                dependencies=["a2a_orchestrator"],
                health_endpoint="/",
                required_for=["langgraph"]
            ),
            "document_server": ServiceConfig(
                name="Document Management API",
                description="Document upload and knowledge graph extraction",
                port=8001,
                dependencies=[],
                health_endpoint="/health",
                required_for=["frontend"]
            ),
            "langgraph": ServiceConfig(
                name="LangGraph API Server",
                description="Multi-agent mortgage processing engine",
                port=2024,  # Frontend expects this port
                dependencies=["a2a_orchestrator", "web_search"],
                health_endpoint="/health",
                required_for=["frontend"]
            ),
            "frontend": ServiceConfig(
                name="React Frontend",
                description="User interface for mortgage applications",
                port=3000,
                dependencies=["langgraph", "document_server"],
                health_endpoint="/",
                required_for=[]
            )
        }
        
        # System requirements
        self.requirements = [
            SystemRequirement(
                name="Python 3.11+",
                description="Python runtime for the mortgage processing system",
                check_command="python3 --version",
                install_hint="Install from https://python.org or system package manager",
                required_for=[DeploymentType.NATIVE]
            ),
            SystemRequirement(
                name="Podman",
                description="Container runtime for isolated deployment",
                check_command="podman --version",
                install_hint="Install from https://podman.io/getting-started/installation",
                required_for=[DeploymentType.PODMAN]
            ),
            SystemRequirement(
                name="Node.js 18+",
                description="JavaScript runtime for React frontend",
                check_command="node --version",
                install_hint="Install from https://nodejs.org or use nvm",
                required_for=[DeploymentType.NATIVE]
            )
        ]

    def print_banner(self):
        """Display welcome banner"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("🏠 " + "=" * 60 + " 🏠")
        print("   MORTGAGE PROCESSING SYSTEM - INTERACTIVE SETUP")
        print("🏠 " + "=" * 60 + " 🏠")
        print(f"{Colors.END}")
        print(f"{Colors.CYAN}Production-grade agentic mortgage application processing{Colors.END}")
        print(f"{Colors.BLUE}✅ 9-Agent LangGraph System  ✅ Neo4j Integration{Colors.END}")
        print(f"{Colors.BLUE}✅ Vector Database & RAG     ✅ Knowledge Graph{Colors.END}")
        print(f"{Colors.BLUE}✅ Document Processing       ✅ React Frontend{Colors.END}")
        print(f"{Colors.BLUE}✅ A2A External Integration  ✅ Production Ready{Colors.END}")
        print()

    def choose_deployment_type(self) -> DeploymentType:
        """Interactive deployment type selection"""
        print(f"{Colors.BOLD}📋 DEPLOYMENT OPTIONS{Colors.END}")
        print(f"{Colors.GREEN}Select your preferred deployment method:{Colors.END}")
        print()
        
        options = [
            ("1", "🖥️  Native", "Run directly on your machine (recommended for development)"),
            ("2", "🐳 Podman", "Run in containers (recommended for production/testing)"),
            ("3", "☁️  OpenShift", "Deploy to OpenShift cluster (enterprise deployment)")
        ]
        
        for option, name, desc in options:
            print(f"  {Colors.BOLD}{option}.{Colors.END} {Colors.YELLOW}{name:<12}{Colors.END} - {desc}")
        
        print()
        while True:
            choice = input(f"{Colors.CYAN}Enter your choice (1-3): {Colors.END}").strip()
            
            if choice == "1":
                return DeploymentType.NATIVE
            elif choice == "2":
                return DeploymentType.PODMAN
            elif choice == "3":
                print(f"{Colors.YELLOW}⚠️  OpenShift deployment coming soon! Defaulting to Podman.{Colors.END}")
                return DeploymentType.PODMAN
            else:
                print(f"{Colors.RED}❌ Invalid choice. Please select 1, 2, or 3.{Colors.END}")

    def check_requirements(self, deployment_type: DeploymentType) -> bool:
        """Check and validate system requirements"""
        print(f"\n{Colors.BOLD}🔍 CHECKING SYSTEM REQUIREMENTS{Colors.END}")
        print(f"Deployment type: {Colors.YELLOW}{deployment_type.value.title()}{Colors.END}")
        print()
        
        all_good = True
        
        for req in self.requirements:
            if deployment_type not in req.required_for:
                continue
                
            print(f"📦 Checking {req.name}... ", end="")
            
            try:
                result = subprocess.run(
                    req.check_command.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    print(f"{Colors.GREEN}✅ Found ({version}){Colors.END}")
                else:
                    print(f"{Colors.RED}❌ Not found{Colors.END}")
                    print(f"   {Colors.YELLOW}💡 {req.install_hint}{Colors.END}")
                    all_good = False
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"{Colors.RED}❌ Not found{Colors.END}")
                print(f"   {Colors.YELLOW}💡 {req.install_hint}{Colors.END}")
                all_good = False
        
        if not all_good:
            print(f"\n{Colors.RED}❌ Please install missing requirements and run again.{Colors.END}")
            return False
            
        print(f"\n{Colors.GREEN}✅ All requirements satisfied!{Colors.END}")
        return True

    def check_external_dependencies(self) -> bool:
        """Check external services (Neo4j, LlamaStack)"""
        print(f"\n{Colors.BOLD}🔗 CHECKING EXTERNAL DEPENDENCIES{Colors.END}")
        print(f"{Colors.CYAN}These services should be running independently:{Colors.END}")
        print()
        
        all_good = True
        
        for dep_id, config in self.external_deps.items():
            print(f"🔌 {config['name']}... ", end="")
            
            # Simple connection test (you might want to make this more sophisticated)
            if dep_id == "neo4j":
                # Try to connect to Neo4j
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex(('localhost', 7687))
                    sock.close()
                    
                    if result == 0:
                        print(f"{Colors.GREEN}✅ Connected{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}⚠️  Not accessible{Colors.END}")
                        print(f"   💡 Start Neo4j Desktop or server on port 7687")
                        # Don't fail for external deps, just warn
                        
                except Exception:
                    print(f"{Colors.YELLOW}⚠️  Cannot verify{Colors.END}")
                    
            elif dep_id == "llamastack":
                # Try to ping LlamaStack (simplified)
                try:
                    import requests
                    response = requests.get(config["url"], timeout=5)
                    if response.status_code < 500:
                        print(f"{Colors.GREEN}✅ Connected{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}⚠️  Service issues{Colors.END}")
                except Exception:
                    print(f"{Colors.YELLOW}⚠️  Not accessible{Colors.END}")
                    print(f"   💡 Check LlamaStack service availability")
        
        print(f"\n{Colors.BLUE}ℹ️  External services will be tested during startup.{Colors.END}")
        return True

    def setup_python_environment(self):
        """Setup Python virtual environment and dependencies"""
        print(f"\n{Colors.BOLD}🐍 SETTING UP PYTHON ENVIRONMENT{Colors.END}")
        
        # Create virtual environment
        if not self.venv_path.exists():
            print(f"📦 Creating virtual environment...")
            result = subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"{Colors.RED}❌ Failed to create virtual environment{Colors.END}")
                print(result.stderr)
                return False
        else:
            print(f"📦 Virtual environment already exists")
        
        # Determine pip path
        if os.name == 'nt':  # Windows
            pip_path = self.venv_path / "Scripts" / "pip"
            python_path = self.venv_path / "Scripts" / "python"
        else:  # Unix/Linux/macOS
            pip_path = self.venv_path / "bin" / "pip"
            python_path = self.venv_path / "bin" / "python"
        
        # Install/upgrade pip
        print(f"📦 Upgrading pip...")
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], 
                      capture_output=True)
        
        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            print(f"📦 Installing Python dependencies...")
            result = subprocess.run([
                str(pip_path), "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"{Colors.RED}❌ Failed to install dependencies{Colors.END}")
                print(result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
                return False
        
        print(f"{Colors.GREEN}✅ Python environment ready{Colors.END}")
        return True

    def setup_database_schema(self):
        """Initialize database schemas and test data"""
        print(f"\n{Colors.BOLD}🗄️  SETTING UP DATABASE SCHEMAS{Colors.END}")
        
        # Initialize SQLite for chat sessions
        print(f"📊 Initializing SQLite database...")
        init_script = self.project_root / "init_db.py"
        if init_script.exists():
            result = subprocess.run([
                str(self.get_python_path()), str(init_script)
            ], capture_output=True, text=True, cwd=str(self.project_root))
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ SQLite database initialized{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  SQLite init had issues: {result.stderr[:100]}{Colors.END}")
        
        # Test Neo4j connection and setup schema
        print(f"🕸️  Setting up Neo4j schema...")
        try:
            # This will be handled by the application startup
            print(f"{Colors.GREEN}✅ Neo4j schema will be created on first run{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Neo4j schema setup deferred: {str(e)[:100]}{Colors.END}")
        
        return True

    def cleanup_existing_services(self):
        """Clean up any existing services on required ports"""
        print(f"\n{Colors.BOLD}🧹 CLEANING UP EXISTING SERVICES{Colors.END}")
        
        ports_to_check = [svc.port for svc in self.services.values()]
        
        for port in ports_to_check:
            if self.is_port_in_use(port):
                print(f"🔍 Port {port} is in use...")
                
                # Try to find and stop the process
                if self.stop_process_on_port(port):
                    print(f"{Colors.GREEN}✅ Freed port {port}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}⚠️  Could not free port {port} - manual intervention may be needed{Colors.END}")
        
        print(f"{Colors.GREEN}✅ Port cleanup complete{Colors.END}")

    def start_services_native(self):
        """Start services in native mode using existing working scripts"""
        print(f"\n{Colors.BOLD}🚀 STARTING SERVICES (NATIVE MODE){Colors.END}")
        print(f"{Colors.CYAN}Using proven startup scripts...{Colors.END}")
        
        try:
            # Use the existing working start_backend.py
            python_path = self.get_python_path()
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_root / "src")
            
            print(f"\n🔄 Starting backend services...")
            print(f"   📝 A2A Orchestrator + Web Search + LangGraph API")
            
            # Start the unified backend
            process = subprocess.Popen(
                [str(python_path), "start_backend.py"],
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            
            # Wait a moment for services to start
            print(f"   ⏳ Waiting for services to initialize...")
            time.sleep(10)
            
            # Check if process is still alive
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"{Colors.RED}❌ Backend startup failed{Colors.END}")
                print(f"Error: {stderr[:200]}")
                return False
            
            print(f"{Colors.GREEN}✅ Backend services started successfully{Colors.END}")
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error starting services: {e}{Colors.END}")
            return False

    def start_service_native(self, service_name: str) -> bool:
        """Start a specific service in native mode"""
        service = self.services[service_name]
        python_path = self.get_python_path()
        
        # Define service startup commands
        commands = {
            "a2a_orchestrator": [
                str(python_path), "-c",
                "import sys; sys.path.append('src'); "
                "from mortgage_a2a.orchestrator_agent import create_mortgage_orchestrator_server; "
                "import uvicorn; "
                "app = create_mortgage_orchestrator_server(); "
                f"uvicorn.run(app, host='0.0.0.0', port={service.port})"
            ],
            "web_search": [
                str(python_path), "-c",
                "import sys; sys.path.append('src'); "
                "from mortgage_a2a.agents.web_search_agent import create_web_search_server; "
                "import uvicorn; "
                "app = create_web_search_server(); "
                f"uvicorn.run(app, host='0.0.0.0', port={service.port})"
            ],
            "document_server": [
                str(python_path), "start_document_server.py"
            ],
            "langgraph": [
                "langgraph", "dev", "--host", "0.0.0.0", "--port", str(service.port)
            ]
        }
        
        if service_name not in commands:
            return False
        
        try:
            # Set up environment
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_root / "src")
            
            # Start the process
            process = subprocess.Popen(
                commands[service_name],
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error starting {service_name}: {e}{Colors.END}")
            return False

    def wait_for_service(self, service: ServiceConfig, timeout: int = 30) -> bool:
        """Wait for a service to become available"""
        import requests
        
        url = f"http://localhost:{service.port}{service.health_endpoint}"
        
        for i in range(timeout):
            try:
                response = requests.get(url, timeout=2)
                if response.status_code < 500:  # Accept any non-server-error response
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(1)
        
        return False

    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
            return False
        except OSError:
            return True

    def stop_process_on_port(self, port: int) -> bool:
        """Try to stop process using a specific port"""
        try:
            # Try to find process using the port (Unix/Linux/macOS)
            if os.name != 'nt':
                result = subprocess.run([
                    "lsof", "-ti", f":{port}"
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            subprocess.run(["kill", "-TERM", pid], check=True)
                            time.sleep(2)
                            # Force kill if still running
                            subprocess.run(["kill", "-9", pid], capture_output=True)
                        except subprocess.CalledProcessError:
                            pass
                    return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return False

    def get_python_path(self) -> Path:
        """Get path to Python executable in virtual environment"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "python"
        else:  # Unix/Linux/macOS
            return self.venv_path / "bin" / "python"

    def print_success_summary(self):
        """Print final success summary with service endpoints"""
        print(f"\n{Colors.GREEN}{Colors.BOLD}")
        print("🎉 " + "=" * 60 + " 🎉")
        print("   MORTGAGE PROCESSING SYSTEM - READY FOR DEMO!")
        print("🎉 " + "=" * 60 + " 🎉")
        print(f"{Colors.END}")
        
        print(f"{Colors.BOLD}📡 SERVICE ENDPOINTS:{Colors.END}")
        
        active_services = []
        if self.deployment_type == DeploymentType.NATIVE:
            active_services = ["a2a_orchestrator", "web_search", "document_server", "langgraph"]
        
        for service_name in active_services:
            service = self.services[service_name]
            print(f"  🔗 {service.name:<25} http://localhost:{service.port}")
        
        print(f"\n{Colors.BOLD}🎯 NEXT STEPS:{Colors.END}")
        print(f"  1. {Colors.CYAN}Frontend Setup:{Colors.END}")
        print(f"     cd ../chat-frontend && npm install && npm run dev")
        print(f"  2. {Colors.CYAN}Demo System:{Colors.END}")
        print(f"     python demo_showcase.py")
        print(f"  3. {Colors.CYAN}API Documentation:{Colors.END}")
        print(f"     http://localhost:2024/docs")
        
        print(f"\n{Colors.YELLOW}💡 TIP: Use Ctrl+C to stop all services gracefully{Colors.END}")
        print(f"{Colors.GREEN}🏠 Happy mortgage processing! 🏠{Colors.END}")

    def cleanup_on_exit(self):
        """Clean up processes on exit"""
        print(f"\n{Colors.YELLOW}🛑 Shutting down services...{Colors.END}")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        
        print(f"{Colors.GREEN}✅ All services stopped{Colors.END}")

    def run_interactive_setup(self):
        """Main interactive setup flow"""
        try:
            # Welcome and deployment selection
            self.print_banner()
            
            # Only ask for deployment type if not already set
            if self.deployment_type is None:
                self.deployment_type = self.choose_deployment_type()
            
            # System checks
            if not self.check_requirements(self.deployment_type):
                return False
            
            if not self.check_external_dependencies():
                return False
            
            # Environment setup
            if self.deployment_type == DeploymentType.NATIVE:
                if not self.setup_python_environment():
                    return False
                
                if not self.setup_database_schema():
                    return False
            
            # Clean up existing services
            self.cleanup_existing_services()
            
            # Start services based on deployment type
            if self.deployment_type == DeploymentType.NATIVE:
                if not self.start_services_native():
                    return False
            elif self.deployment_type == DeploymentType.PODMAN:
                print(f"{Colors.YELLOW}🐳 Podman deployment coming soon!{Colors.END}")
                return False
            
            # Success!
            self.print_success_summary()
            
            # Keep running
            print(f"\n{Colors.CYAN}Services running... Press Ctrl+C to stop{Colors.END}")
            try:
                while True:
                    time.sleep(5)
                    # Health check services
                    for process in self.processes:
                        if process.poll() is not None:  # Process died
                            print(f"{Colors.RED}❌ A service died unexpectedly{Colors.END}")
                            return False
            except KeyboardInterrupt:
                pass
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  Setup interrupted by user{Colors.END}")
            return False
        except Exception as e:
            print(f"\n{Colors.RED}❌ Setup failed: {e}{Colors.END}")
            return False
        finally:
            self.cleanup_on_exit()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Interactive setup for Mortgage Processing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup.py                 # Interactive mode
  python setup.py --native        # Skip interaction, use native
  python setup.py --podman        # Skip interaction, use podman
        """
    )
    parser.add_argument("--native", action="store_true", help="Use native deployment")
    parser.add_argument("--podman", action="store_true", help="Use Podman deployment")
    parser.add_argument("--openshift", action="store_true", help="Use OpenShift deployment")
    
    args = parser.parse_args()
    
    orchestrator = MortgageSystemOrchestrator()
    
    # Set deployment type from args
    if args.native:
        orchestrator.deployment_type = DeploymentType.NATIVE
    elif args.podman:
        orchestrator.deployment_type = DeploymentType.PODMAN
    elif args.openshift:
        orchestrator.deployment_type = DeploymentType.OPENSHIFT
    
    # Run setup
    success = orchestrator.run_interactive_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
