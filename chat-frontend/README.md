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
# API Base URL (FastAPI backend)
VITE_API_BASE_URL=http://localhost:8000

# App Configuration  
VITE_APP_NAME=Mortgage Chat Assistant
VITE_ENVIRONMENT=development
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

The frontend connects to the FastAPI backend running on `http://localhost:8000`. 

### Key API Endpoints:

- `POST /chat/sessions/start` - Start new chat session
- `GET /chat/sessions` - List chat sessions  
- `POST /chat/sessions/{id}/messages` - Send message
- `POST /chat/sessions/{id}/upload` - Upload files
- `GET /health` - Health check

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

## 🔄 Connecting to Backend

1. **Start the FastAPI backend** first:
   ```bash
   cd ../mortgage-processor
   python run.py
   ```

2. **Then start the frontend**:
   ```bash
   npm run dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

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

This frontend follows the same separation pattern as your tech-explorer project:

- **Separate codebase** from backend
- **API-first communication** via HTTP/REST
- **Modern React patterns** with hooks and context
- **TypeScript throughout** for type safety
- **Component-based architecture** for reusability

The chat interface provides a familiar ChatGPT-like experience while integrating seamlessly with your existing mortgage processing agent.
