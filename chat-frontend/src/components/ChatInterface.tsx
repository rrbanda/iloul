import React, { useRef, useEffect } from 'react'
import { AlertCircle, FileText, HelpCircle, Home, ArrowLeft } from 'lucide-react'
import { useChat } from '../context/ChatContext'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import WelcomeScreen from './WelcomeScreen'
import QuickPrompts from './QuickPrompts'

function ChatInterface() {
  const { state, goHome } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [state.messages])

  // Show error banner if there's an error
  const ErrorBanner = () => {
    if (!state.error) return null

    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 m-4">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-800 font-medium">Error</span>
        </div>
        <p className="text-red-700 mt-1">{state.error}</p>
      </div>
    )
  }

  // Show connection status
  const ConnectionStatus = () => {
    if (state.isConnected) return null

    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 m-4">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-yellow-600" />
          <span className="text-yellow-800 font-medium">Connection Issue</span>
        </div>
        <p className="text-yellow-700 mt-1">
          Unable to connect to the server. Please check your connection and try again.
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 p-4">
        {state.currentSession ? (
          /* Session Active Layout */
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Navigation Buttons */}
              <button
                onClick={goHome}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Back to Home"
              >
                <Home className="w-4 h-4" />
                <span className="hidden sm:inline">Home</span>
              </button>
              
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-semibold text-gray-900">
                    {state.currentSession.session_name}
                  </h2>
                </div>
                <p className="text-sm text-gray-500">
                  {state.messages.length} messages
                  {state.currentSession.session_context && (
                    <span className="ml-2 inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                      <FileText className="w-3 h-3" />
                      {state.currentSession.session_context}
                    </span>
                  )}
                  {state.currentSession.current_application_id && (
                    <span className="ml-2 inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                      <FileText className="w-3 h-3" />
                      Application: {state.currentSession.current_application_id}
                    </span>
                  )}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                title="Help"
              >
                <HelpCircle className="w-5 h-5" />
              </button>
            </div>
          </div>
        ) : (
          /* No Session - Centered Layout */
          <div className="flex items-center justify-between">
            {/* Empty left spacer for balance */}
            <div className="w-24"></div>
            
            {/* Centered Title */}
            <div className="text-center">
              <h2 className="text-lg font-semibold text-gray-900">
                Mortgage Processing Assistant
              </h2>
              <p className="text-sm text-gray-500">
                AI-powered help for your mortgage application
              </p>
            </div>

            {/* Right side actions */}
            <div className="flex items-center gap-2 w-24 justify-end">
              <button
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                title="Help"
              >
                <HelpCircle className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Error and Connection Status */}
      <ErrorBanner />
      <ConnectionStatus />

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {state.currentSession ? (
          <>
            {/* Quick Actions at Top for Better UX */}
            {state.messages.length <= 1 && state.currentSession && (
              <div className="flex-shrink-0 border-b border-gray-200 p-4 bg-gray-50">
                <QuickPrompts 
                  sessionContext={
                    state.currentSession.session_context || 
                    (state.currentSession.session_name?.includes('First-Time Buyer') ? 'First-Time Buyer Consultation' :
                     state.currentSession.session_name?.includes('Pre-Approval') ? 'Pre-Approval Check' :
                     state.currentSession.session_name?.includes('Refinance') ? 'Refinance Consultation' :
                     state.currentSession.session_name?.includes('Document Analysis') ? 'Document Analysis' :
                     state.currentSession.session_name?.includes('Qualification') ? 'Qualification Assessment' :
                     state.currentSession.session_name?.includes('Compliance') ? 'Compliance Checking' :
                     state.currentSession.session_name?.includes('Real-time') ? 'Real-time Processing' :
                     'General')
                  } 
                />
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto">
              <MessageList messages={state.messages} isLoading={state.isLoading} />
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex-shrink-0 border-t border-gray-200 p-4">
              <ChatInput disabled={!state.isConnected || state.isLoading} />
            </div>
          </>
        ) : (
          // Welcome Screen when no session is active
          <WelcomeScreen />
        )}
      </div>
    </div>
  )
}

export default ChatInterface
