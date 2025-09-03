
import { Bot, User } from 'lucide-react'
import { ChatMessage } from '../types/chat'
import DynamicPromptsRenderer from './DynamicPromptsRenderer'

interface MessageListProps {
  messages: ChatMessage[]
  isLoading: boolean
}

function MessageList({ messages, isLoading }: MessageListProps) {

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="p-4">
        <div className="text-center text-gray-500">
          <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">Chat conversation will appear here</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 space-y-4">
      {messages.map((message, index) => (
        <div
          key={message.message_id || `message-${index}`}
          className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          {message.role === 'assistant' && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
          )}

          <div className={`max-w-2xl ${message.role === 'user' ? 'order-first' : ''}`}>
            <div className={`rounded-lg px-4 py-3 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200 text-gray-900'
            }`}>
              {/* Check for dynamic prompts in assistant messages */}
              {message.role === 'assistant' && message.content.startsWith('DYNAMIC_PROMPTS:') ? (
                <DynamicPromptsRenderer content={message.content} />
              ) : (
                <div className="whitespace-pre-wrap">{message.content}</div>
              )}
            </div>
            
            <div className={`text-xs text-gray-500 mt-1 ${
              message.role === 'user' ? 'text-right' : 'text-left'
            }`}>
              {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>

          {message.role === 'user' && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center">
              <User className="w-4 h-4" />
            </div>
          )}
        </div>
      ))}

      {/* Loading indicator */}
      {isLoading && (
        <div className="flex gap-3">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
            <Bot className="w-4 h-4 animate-pulse" />
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <span className="text-blue-700 font-medium">Thinking...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MessageList