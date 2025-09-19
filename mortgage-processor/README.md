# 🏠 Mortgage Processing System - Production Ready Agentic Solution

> **A comprehensive mortgage application processing system using LangGraph multi-agent architecture with AI-powered decision making, document processing, and knowledge graph integration.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-red.svg)](https://neo4j.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal.svg)](https://fastapi.tiangolo.com/)

---

## 🚀 **One-Command Setup (Recommended)**

**New! Interactive Production Setup** - Get everything running with guided assistance:

```bash
python setup.py
```

This intelligent setup script will:
- ✅ **Guide you through deployment options** (Native/Podman/OpenShift)
- ✅ **Check all prerequisites** and suggest fixes
- ✅ **Set up virtual environment** and dependencies
- ✅ **Initialize databases** and schemas
- ✅ **Start services in correct order** with health checks
- ✅ **Provide clear next steps** and endpoints

### Quick Options:
```bash
python setup.py --native    # Skip interaction, use native
python setup.py --podman    # Skip interaction, use containers
python setup.py --help      # Show all options
```

---

## 🏗️ **System Architecture**

### **🤖 Multi-Agent Processing Engine**
```
Frontend (React) → LangGraph API → Supervisor Agent
                                        ↓
    ┌─────────────────────────────────────────────────────────────────┐
    │  🏠 Application  🏦 Underwriting  📊 Data Collection  👥 Customer │
    │     Agent           Agent            Agent          Service Agent │
    │                                                                  │
    │  🏡 Property     📋 Compliance    🤝 Closing      📄 Document     │
    │     Agent           Agent          Agent         Management      │
    │                                                     Agent        │
    └─────────────────────────────────────────────────────────────────┘
                                        ↓
                    Neo4j Graph Database + Vector Store + RAG
```

### **🔗 External Integration (A2A)**
- **🌐 Web Search Agent** - Real-time market data and property information
- **🏠 A2A Orchestrator** - Intelligent routing and external service integration
- **📡 Google A2A Integration** - External agent communication

### **💾 Data Architecture**
- **Neo4j Graph Database** - Application relationships and workflow state
- **Vector Database** - Document embeddings and RAG knowledge base
- **Knowledge Graph** - Extracted entities and relationships from documents
- **SQLite** - Chat session persistence

---

## 🎯 **Core Features**

### **🤖 Intelligent Agent Routing**
- **Supervisor Agent** analyzes user intent and routes to specialized agents
- **Context-aware handoffs** between agents based on conversation flow
- **Memory persistence** across agent interactions

### **📄 Document Processing Pipeline**
- **Automated knowledge extraction** from uploaded documents
- **Multi-format support** (PDF, Word, images, text)
- **Entity recognition** and relationship mapping
- **Triple storage** in vector DB + Neo4j knowledge graph

### **🧠 Agentic Application Management**
- **Intelligent application detection** from chat conversations
- **Unified lifecycle management** across document and chat workflows
- **No conflicts** between different interaction points
- **Automatic phase progression** based on completeness

### **🔍 RAG-Enhanced Processing**
- **Mortgage knowledge base** with semantic search
- **Document-aware responses** using uploaded content
- **Real-time external data integration** via A2A agents

---

## 📋 **Prerequisites**

### **🖥️ For Native Deployment:**
- **Python 3.11+** - Main runtime
- **Node.js 18+** - For React frontend
- **Neo4j Desktop/Server** - Graph database (running on port 7687)
- **LlamaStack** - Remote LLM and vector services

### **🐳 For Container Deployment:**
- **Podman** - Container runtime
- **Neo4j Desktop/Server** - External dependency
- **LlamaStack** - External dependency

### **📝 Configuration:**
Create `.env` file in the project root:
```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# LlamaStack Configuration  
LLAMASTACK_BASE_URL=https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com
LLAMASTACK_API_KEY=your-api-key-here
```

---

## 🎬 **Demo & Testing**

### **🎨 Full System Demo**
```bash
# Automated showcase demo (colorful CLI)
python demo_showcase.py

# Core system functionality test
python test_unified_agentic_system.py

# Knowledge graph extraction test
python test_knowledge_graph.py

# Quick health check
python quick_test.py
```

### **🌐 Frontend Integration**
```bash
# Start React frontend (separate terminal)
cd ../chat-frontend
npm install
npm run dev
# Frontend: http://localhost:3000
```

---

## 📡 **Service Endpoints**

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| **A2A Orchestrator** | 8000 | Agent-to-agent communication hub | `GET /` |
| **Web Search Agent** | 8002 | External web search capabilities | `GET /` |
| **Document API** | 8001 | Document upload & knowledge extraction | `GET /health` |
| **LangGraph API** | 2024 | Multi-agent processing engine | `GET /health` |
| **React Frontend** | 3000 | User interface | `GET /` |

---

## 🔧 **Manual Setup (Alternative)**

### **1. Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### **2. Database Initialization**
```bash
# Initialize SQLite for chat sessions
python init_db.py

# Neo4j schema will be created automatically on first run
```

### **3. Start Services Manually**
```bash
# Terminal 1: A2A System
python src/start_a2a_only.py

# Terminal 2: Document API  
python start_document_server.py

# Terminal 3: LangGraph API
langgraph dev --host 0.0.0.0 --port 2024
```

---

## 🔍 **API Usage Examples**

### **💬 Chat API**
```bash
# Start a conversation
curl -X POST http://localhost:2024/threads/default/runs \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [{"role": "user", "content": "I want to apply for a $500,000 mortgage"}]
    }
  }'
```

### **📄 Document Upload**
```bash
# Upload document with knowledge extraction
curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@paystub.pdf" \
  -F "document_type=pay_stub" \
  -F "application_id=APP_12345"
```

### **🕸️ Knowledge Graph Query**
```bash
# Query extracted relationships
curl -X GET http://localhost:8001/api/documents/knowledge-graph/APP_12345
```

---

## 🐳 **Container Deployment**

### **🚀 Podman (Coming Soon)**
```bash
python setup.py --podman
```

### **☁️ OpenShift (Enterprise)**
```bash
# Deploy to OpenShift cluster
kubectl apply -f deploy/openshift/
```

---

## 🧪 **Development**

### **🔧 Development Mode**
```bash
# Start with auto-reload
python setup.py --native
# Or manually:
langgraph dev --host 0.0.0.0 --port 2024 --reload
```

### **🧪 Testing**
```bash
# Run all tests
python -m pytest tests/

# Test specific components
python test_unified_agentic_system.py
python test_knowledge_graph.py
```

### **📊 Monitoring**
- **LangSmith Tracing** - https://smith.langchain.com/
- **API Documentation** - http://localhost:2024/docs
- **Health Endpoints** - Various `/health` endpoints per service

---

## 📂 **Project Structure**

```
mortgage-processor/
├── setup.py                    # 🚀 Main interactive setup script
├── requirements.txt            # 📦 Python dependencies
├── config.yaml                # ⚙️ Application configuration
├── .env                       # 🔐 Environment variables
│
├── src/mortgage_processor/    # 🏠 Main application
│   ├── agents/               # 🤖 Specialized mortgage agents
│   ├── graph.py             # 🕸️ LangGraph workflow definition
│   ├── workflow_manager.py  # 🎛️ Chat and state management
│   ├── neo4j_mortgage.py    # 📊 Graph database operations
│   ├── knowledge_graph.py   # 🧠 Entity extraction & KG
│   ├── vector_stores.py     # 📄 Vector database integration
│   └── api/                 # 🌐 REST API endpoints
│
├── src/mortgage_a2a/         # 🔗 Agent-to-Agent system
│   ├── orchestrator_agent.py # 🎯 A2A routing and orchestration
│   └── agents/              # 🔍 External service agents
│
├── prompts/                 # 📝 Agent system prompts
├── demo_showcase.py         # 🎬 Full system demonstration
├── test_*.py               # 🧪 Comprehensive test suites
└── deploy/                 # 🚀 Container & cloud deployment
```

---

## 🎯 **Production Features**

### **🔒 Security & Compliance**
- Environment variable configuration for sensitive data
- Input validation and sanitization
- Secure agent communication protocols
- CORS configuration for production frontends

### **📈 Scalability**
- Asynchronous processing with proper concurrency
- Stateless agent design for horizontal scaling
- Database connection pooling and optimization
- Container-ready architecture

### **🔍 Monitoring & Debugging**
- Comprehensive logging throughout the system
- LangSmith integration for agent trace analysis
- Health check endpoints for all services
- Graceful error handling and recovery

### **🎛️ Configuration Management**
- Centralized configuration via `config.yaml`
- Environment-specific settings via `.env`
- Runtime configuration for different deployment modes
- Feature flags for optional components

---

## 🤝 **Contributing**

### **🐛 Found a Bug?**
1. Check existing issues
2. Create detailed bug report with reproduction steps
3. Include system information and logs

### **💡 Feature Request?**
1. Describe the use case and expected behavior
2. Consider how it fits with the existing architecture
3. Provide implementation suggestions if possible

### **🔧 Development Setup**
```bash
# Clone and setup development environment
git clone <repository>
cd mortgage-processor
python setup.py --native
```

---

## 📚 **Architecture Details**

### **🤖 Agent Specialization**
- **ApplicationAgent** - Mortgage application collection and validation
- **UnderwritingAgent** - Credit analysis and risk assessment
- **DataAgent** - External data collection and verification
- **CustomerServiceAgent** - User interaction and support
- **PropertyAgent** - Property valuation and analysis
- **ComplianceAgent** - Regulatory compliance checking
- **ClosingAgent** - Final processing and documentation
- **DocumentAgent** - Document management and verification
- **RAGAgent** - Knowledge retrieval and context enhancement

### **🔄 Workflow Orchestration**
1. **Supervisor Agent** receives user input and analyzes intent
2. **Route to appropriate specialist** based on content and context
3. **Agent processes request** using available tools and knowledge
4. **State persistence** maintains conversation context
5. **Handoff coordination** manages multi-agent workflows

### **💾 Data Flow**
```
User Input → LangGraph → Supervisor → Specialist Agent
                                             ↓
                     Tools (Neo4j, Vector DB, A2A, RAG)
                                             ↓
                     Response → State Update → User
```

---

## 🏆 **What Makes This Special**

### **🎯 True Agentic Behavior**
- **LLM-based decision making** - Agents use language models to decide which tools to invoke
- **Dynamic workflow adaptation** - Conversation flow adapts based on user needs
- **Context-aware routing** - Supervisor intelligently routes based on conversation state

### **🧠 Knowledge Integration**
- **Hybrid storage approach** - Vector DB for content, Neo4j for relationships
- **Automatic knowledge extraction** - Documents become queryable knowledge graphs
- **RAG-enhanced responses** - Agents can reference uploaded documents and knowledge base

### **🔗 External Intelligence**
- **Google A2A integration** - Connects to external agent networks
- **Real-time data enrichment** - Web search for current market information
- **Extensible architecture** - Easy to add new external service integrations

### **📈 Production Ready**
- **Comprehensive error handling** - Graceful degradation and recovery
- **Health monitoring** - All services provide health check endpoints
- **Container deployment** - Production-ready containerization
- **Interactive setup** - Guided installation and configuration

---

## 📞 **Getting Help**

- **📖 Documentation** - This README covers all essential information
- **🧪 Test Scripts** - Use `test_*.py` files to verify functionality
- **🎬 Demo Scripts** - Run `demo_showcase.py` for full system demonstration
- **🔍 Health Checks** - Use `/health` endpoints to verify service status

---

## 🎉 **Ready to Get Started?**

```bash
# One command to rule them all! 🚀
python setup.py
```

**Welcome to the future of mortgage processing!** 🏠✨