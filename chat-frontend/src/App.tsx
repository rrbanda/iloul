import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'
import { ChatProvider, useChat } from './context/ChatContext'
import './App.css'

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { state } = useChat()
  
  // Only show sidebar when there's an active session (not on welcome screen)
  const showSidebar = !!state.currentSession

  return (
    <div className="flex h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Sidebar - Only show when in chat/wizard mode */}
      {showSidebar && (
        <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      )}
      
      {/* Main Chat Area */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${
        showSidebar && !sidebarOpen ? 'pl-16' : ''
      }`}>
        <ChatInterface />
      </div>
    </div>
  )
}

function App() {
  return (
    <ChatProvider>
      <AppContent />
    </ChatProvider>
  )
}

export default App
