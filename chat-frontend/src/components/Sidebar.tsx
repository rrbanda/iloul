import React from 'react'
import { 
  MessageSquare, 
  Trash2, 
  FileText,
  Calendar,
  ChevronLeft,
  RotateCcw,
  Menu
} from 'lucide-react'
import { useChat } from '../context/ChatContext'
import { ChatSessionSummary } from '../types/chat'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const { state, selectSession, deleteSession, clearMessages } = useChat()

  const handleSelectSession = async (sessionId: string) => {
    await selectSession(sessionId)
  }

  const handleDeleteSession = async (sessionId: string, event: React.MouseEvent) => {
    event.stopPropagation()
    if (window.confirm('Are you sure you want to delete this chat session?')) {
      await deleteSession(sessionId)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) return 'Today'
    if (days === 1) return 'Yesterday'
    if (days < 7) return `${days} days ago`
    return date.toLocaleDateString()
  }

  const getSessionIcon = (session: ChatSessionSummary) => {
    if (session.has_documents) return <FileText className="w-4 h-4" />
    return <MessageSquare className="w-4 h-4" />
  }

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className={`fixed top-4 z-50 p-3 bg-white border border-gray-200 rounded-lg shadow-md hover:shadow-lg hover:bg-gray-50 transition-all duration-300 ${
          isOpen ? 'left-[276px]' : 'left-4'
        }`}
        title={isOpen ? 'Hide conversations' : 'Show conversations'}
      >
        {isOpen ? (
          <ChevronLeft className="w-5 h-5 text-gray-600" />
        ) : (
          <div className="flex items-center gap-1">
            <Menu className="w-5 h-5 text-gray-600" />
          </div>
        )}
      </button>

      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-full w-80 bg-white border-r border-gray-200 flex flex-col transition-transform duration-300 z-40 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold text-gray-900">
              Conversations
            </h1>
            <div className={`w-3 h-3 rounded-full ${state.isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          </div>
          
          <div className="text-sm text-gray-600 mb-4">
            {state.sessions.length > 0 ? (
              <p>
                You have {state.sessions.length} saved conversation{state.sessions.length !== 1 ? 's' : ''}. 
                Click any conversation below to continue where you left off.
              </p>
            ) : (
              <p>Welcome! Your saved conversations will appear here. Use the Home button above to start a new conversation.</p>
            )}
          </div>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto p-4">
          {state.isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : state.sessions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No saved conversations yet</p>
              <p className="text-sm">Start your first conversation above!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {state.sessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => handleSelectSession(session.session_id)}
                  className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
                    state.currentSession?.session_id === session.session_id
                      ? 'bg-blue-50 border-blue-200 border'
                      : 'hover:bg-gray-50 border border-transparent'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-1">
                      {getSessionIcon(session)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">
                        {session.session_name}
                      </h3>
                      
                      <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                        <Calendar className="w-3 h-3" />
                        <span>{formatDate(session.last_activity)}</span>
                      </div>
                      
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                        <span>{session.message_count} messages</span>
                        {session.has_documents && (
                          <span className="flex items-center gap-1">
                            <FileText className="w-3 h-3" />
                            Documents
                          </span>
                        )}
                        {session.current_application_id && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full">
                            Active App
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => handleDeleteSession(session.session_id, e)}
                        className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                        title="Delete session"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          {/* Clear Messages Button - only show if in active session */}
          {state.currentSession && (
            <div className="mb-4">
              <button
                onClick={async () => {
                  if (state.messages.length === 0) {
                    await clearMessages() // Just clear without confirmation if no messages
                  } else {
                    if (window.confirm('Clear all messages in this conversation? This cannot be undone.')) {
                      await clearMessages()
                    }
                  }
                }}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-gray-200 hover:border-red-200"
              >
                <RotateCcw className="w-4 h-4" />
                {state.messages.length > 0 ? 'Clear Messages' : 'Reset Chat'}
              </button>
            </div>
          )}
          
          <div className="text-xs text-gray-500 text-center">
            <p>Powered by AI-driven mortgage processing</p>
            <p className="mt-1">
              Status: {state.isConnected ? (
                <span className="text-green-600">Connected</span>
              ) : (
                <span className="text-red-600">Disconnected</span>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-25 z-30 lg:hidden"
          onClick={onToggle}
        />
      )}
    </>
  )
}

export default Sidebar
