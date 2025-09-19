# Mortgage Chat Frontend

A modern React-based chat interface for the mortgage processing assistant, built with TypeScript, Tailwind CSS, and Vite.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

## 🏗️ Project Structure

```
chat-frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ChatInterface.tsx
│   │   ├── Sidebar.tsx
│   │   ├── MessageList.tsx
│   │   ├── ChatInput.tsx
│   │   └── WelcomeScreen.tsx
│   ├── context/            # React context providers
│   │   └── ChatContext.tsx
│   ├── services/           # API services
│   │   └── api.ts
│   ├── types/              # TypeScript types
│   │   └── chat.ts
│   ├── App.tsx            # Main app component
│   └── main.tsx           # App entry point
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

## 🔧 Environment Variables

Create a `.env` file in the root directory:

```env
# LangGraph API Base URL (LangGraph Dev Server)
VITE_API_BASE_URL=http://localhost:2024

# App Configuration  
VITE_APP_NAME=Mortgage Processing System
VITE_ENVIRONMENT=development
VITE_DEBUG_MODE=true
```

## 🛠️ Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Styling framework
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering
- **React Dropzone** - File upload
- **React Hot Toast** - Notifications
- **Lucide React** - Icon library

## 🔌 Backend Integration

The frontend connects to the **LangGraph Development Server** running on `http://localhost:2024`. 

### Key LangGraph API Endpoints:

- `POST /threads` - Create new LangGraph thread (session)
- `GET /threads/{thread_id}` - Get thread information
- `POST /threads/{thread_id}/runs` - Execute LangGraph workflow
- `GET /threads/{thread_id}/runs/{run_id}` - Check run status
- `GET /threads/{thread_id}/state` - Get thread state and messages
- `PATCH /threads/{thread_id}/state` - Update thread state

### Multi-Agent System:
The LangGraph backend orchestrates **8 specialized agents**:
- **SupervisorAgent** - Routes to appropriate agents
- **AssistantAgent** - Customer guidance and education
- **DataAgent** - Data collection and processing
- **PropertyAgent** - Property valuation and analysis
- **UnderwritingAgent** - Risk analysis and loan decisions
- **ComplianceAgent** - Regulatory compliance
- **ClosingAgent** - Closing coordination
- **CustomerServiceAgent** - Post-submission support
- **ApplicationAgent** - Interactive application processing

## 🎨 Features

### Chat Interface
- **Real-time messaging** with the mortgage processing agent
- **File upload support** with drag & drop
- **Conversation history** with session management
- **Markdown support** for rich text responses
- **Document analysis** results display

### Session Management
- **Multiple chat sessions** with persistent history
- **Session sidebar** with quick access
- **Auto-save** conversations
- **Delete sessions** functionality

### File Handling
- **Drag & drop upload** for documents
- **Multiple file support** (PDF, images, text)
- **File preview** with size information
- **Processing status** indicators

### UI/UX
- **ChatGPT-like interface** for familiar experience
- **Responsive design** for mobile and desktop
- **Loading states** and error handling
- **Toast notifications** for user feedback

## 🚧 Development

```bash
# Development server with hot reload
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔄 Connecting to LangGraph Backend

1. **Start the LangGraph Development Server** first:
   ```bash
   cd ../mortgage-processor
   source venv/bin/activate
   langgraph dev
   ```

2. **Then start the frontend**:
   ```bash
   npm run dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - LangGraph API: http://localhost:2024
   - LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://localhost:2024
   - API Docs: http://localhost:2024/docs

### 🎯 How It Works:
- Frontend sends messages via LangGraph API threads
- LangGraph **Supervisor** routes to appropriate agents
- Agents process requests using **RAG** and **Neo4j** integration
- Responses stream back through the thread state

## 📱 Usage

1. **Start a new chat session** from the sidebar
2. **Ask questions** about mortgage requirements
3. **Upload documents** for analysis via drag & drop
4. **View processing results** with detailed feedback
5. **Manage multiple sessions** for different applications

## 🎯 Production Deployment

For production deployment:

1. **Build the frontend**:
   ```bash
   npm run build
   ```

2. **Deploy the `dist/` folder** to your hosting platform
3. **Update environment variables** for production API URL
4. **Configure CORS** in the FastAPI backend for your domain

## 🤝 Architecture

This frontend integrates with the **LangGraph Multi-Agent System**:

- **Separate codebase** from LangGraph backend
- **LangGraph API communication** via threads and runs
- **Modern React patterns** with hooks and context
- **TypeScript throughout** for type safety
- **Component-based architecture** for reusability

### 🏗️ System Architecture:
```
Frontend (React) → LangGraph API → Supervisor → 8 Specialized Agents
                                              ↓
                                    RAG + Neo4j + FAISS Vector DB
```

### 🔄 Message Flow:
1. **User** sends message via React frontend
2. **LangGraph Thread** receives message and starts run
3. **Supervisor Agent** analyzes intent and routes to appropriate agent
4. **Specialized Agent** processes request with tools and knowledge
5. **Response** flows back through thread state to frontend

The chat interface provides a familiar ChatGPT-like experience while leveraging the full power of the multi-agent mortgage processing system.
