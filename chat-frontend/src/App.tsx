import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'
import { ChatProvider } from './context/ChatContext'
import './App.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <ChatProvider>
      <div className="flex h-screen bg-gray-50">
        <Toaster position="top-right" />
        
        {/* Sidebar */}
        <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
        
        {/* Main Chat Area */}
        <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? '' : 'pl-16'}`}>{/* Add left padding when sidebar is closed to account for toggle button */}
          <ChatInterface />
        </div>
      </div>
    </ChatProvider>
  )
}

export default App
