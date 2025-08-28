import React from 'react'
import { Bot, User, FileText, AlertTriangle, CheckCircle, Clock, Copy, Check } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { ChatMessage } from '../types/chat'

interface MessageListProps {
  messages: ChatMessage[]
  isLoading: boolean
}

interface CodeBlockProps {
  children: string
  className?: string
  isDarkBackground?: boolean
}

function CodeBlock({ children, className, isDarkBackground = false }: CodeBlockProps) {
  const [copied, setCopied] = React.useState(false)
  
  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(children)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Extract language from className (format: language-xxx)
  const language = className?.replace('language-', '') || 'text'

  return (
    <div className="relative group my-4">
      <div className="flex items-center justify-between bg-gray-800 text-gray-300 px-4 py-2 text-sm rounded-t-lg">
        <span className="font-mono text-xs uppercase tracking-wide">
          {language === 'text' ? 'Code' : language}
        </span>
        <button
          onClick={copyToClipboard}
          className="flex items-center gap-1 px-2 py-1 rounded text-xs hover:bg-gray-700 transition-colors"
          title="Copy code"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              Copy
            </>
          )}
        </button>
      </div>
      <SyntaxHighlighter
        language={language}
        style={isDarkBackground ? vscDarkPlus : vs}
        customStyle={{
          margin: 0,
          borderRadius: '0 0 0.5rem 0.5rem',
          fontSize: '0.875rem',
        }}
        showLineNumbers={children.split('\n').length > 3}
      >
        {children}
      </SyntaxHighlighter>
    </div>
  )
}

function MessageList({ messages, isLoading }: MessageListProps) {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  // Enhanced text formatter for much better UX
  const formatAgentText = (text: string): string => {
    if (!text) return text

    // If it's a document checklist or requirements, format it properly
    if (text.includes('typically required') || text.includes('documents are') || text.includes('checklist')) {
      return formatDocumentChecklist(text)
    }

    // For other responses, apply general formatting
    let formatted = text
    
    // Convert ** bold ** to markdown bold
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '**$1**')
    
    // Add proper line breaks and sections
    formatted = formatted.replace(/\s*\*\*\s*([A-Z][^*]*)\s*\*\*\s*:/g, '\n\n### $1\n')
    
    // Format bullet points
    formatted = formatted.replace(/([a-z])\s+\*\s+([A-Z])/g, '$1\n\n• $2')
    
    // Clean up
    formatted = formatted.replace(/\n{3,}/g, '\n\n')
    
    return formatted.trim()
  }

  // Specialized formatter for document checklists
  const formatDocumentChecklist = (text: string): string => {
    const sections = [
      'Personal Documents', 'Identification Documents', 'Income Documents', 
      'Financial Documents', 'Employment Documents', 'Property Documents',
      'Asset Documents', 'Credit Documents', 'Additional Requirements'
    ]

    let result = '## Required Documents Checklist\n\n'
    
    // Split into logical sections
    sections.forEach(section => {
      const sectionRegex = new RegExp(`(${section}[^•]*?)(?=\\*\\*\\s*[A-Z]|$)`, 'i')
      const match = text.match(sectionRegex)
      
      if (match) {
        result += `### ${section}\n`
        
        // Extract individual items
        const items = match[1].match(/\*\*([^*]+)\*\*[^•]*?(?=\*\*|$)/g)
        if (items) {
          items.forEach(item => {
            const cleanItem = item.replace(/\*\*/g, '').trim()
            if (cleanItem.length > 0) {
              result += `• **${cleanItem}**\n`
            }
          })
        }
        result += '\n'
      }
    })

    // Add any processing notes at the end
    if (text.includes('Please note')) {
      const noteMatch = text.match(/(Please note.*$)/i)
      if (noteMatch) {
        result += `### Important Notes\n${noteMatch[1]}\n`
      }
    }

    return result
  }

  const getMessageIcon = (message: ChatMessage) => {
    switch (message.role) {
      case 'user':
        return <User className="w-5 h-5" />
      case 'assistant':
        return <Bot className="w-5 h-5" />
      case 'system':
        return <AlertTriangle className="w-5 h-5" />
      default:
        return <User className="w-5 h-5" />
    }
  }

  const getMessageTypeIndicator = (message: ChatMessage) => {
    switch (message.message_type) {
      case 'file_upload':
        return (
          <div className="flex items-center gap-1 text-xs text-blue-600 mb-2">
            <FileText className="w-3 h-3" />
            File Upload
          </div>
        )
      case 'document_analysis':
        return (
          <div className="flex items-center gap-1 text-xs text-green-600 mb-2">
            <CheckCircle className="w-3 h-3" />
            Document Analysis
          </div>
        )
      case 'processing_result':
        return (
          <div className="flex items-center gap-1 text-xs text-purple-600 mb-2">
            <Clock className="w-3 h-3" />
            Processing Result
          </div>
        )
      case 'error':
        return (
          <div className="flex items-center gap-1 text-xs text-red-600 mb-2">
            <AlertTriangle className="w-3 h-3" />
            Error
          </div>
        )
      default:
        return null
    }
  }

  const ProcessingResultDisplay = ({ result }: { result: any }) => {
    if (!result) return null

    // Only show processing details if there's meaningful information
    const hasDocumentInfo = result.valid_documents !== undefined || 
                           result.invalid_documents !== undefined || 
                           result.missing_documents?.length > 0
    const hasFormGeneration = result.urla_1003_generated
    const hasImportantStatus = result.processing_status && 
                              result.processing_status !== 'success' && 
                              result.processing_status !== 'completed'

    // Don't show for basic chat responses
    if (!hasDocumentInfo && !hasFormGeneration && !hasImportantStatus) {
      return null
    }

    return (
      <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600">
        {result.processing_status && hasImportantStatus && (
          <div className="mb-1">
            <span className={`px-2 py-1 rounded-full text-xs ${
              result.processing_status === 'success' 
                ? 'bg-green-100 text-green-700'
                : result.processing_status === 'partial'
                ? 'bg-yellow-100 text-yellow-700'
                : 'bg-red-100 text-red-700'
            }`}>
              {result.processing_status}
            </span>
          </div>
        )}

        {result.valid_documents !== undefined && (
          <div className="text-xs text-gray-600 mb-1">
            Valid Documents: {result.valid_documents}
          </div>
        )}

        {result.invalid_documents !== undefined && result.invalid_documents > 0 && (
          <div className="text-xs text-red-600 mb-1">
            Issues Found: {result.invalid_documents}
          </div>
        )}

        {result.missing_documents && result.missing_documents.length > 0 && (
          <div className="text-xs text-gray-600">
            Missing: {result.missing_documents.join(', ')}
          </div>
        )}

        {result.urla_1003_generated && (
          <div className="text-xs text-green-600 mt-1">
             URLA 1003 Form Generated
          </div>
        )}
      </div>
    )
  }

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center text-gray-500">
          <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p className="text-lg mb-2">Start a conversation!</p>
          <p className="text-sm">Ask me anything about mortgage processing or upload documents to analyze.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 space-y-6">
      {messages.map((message) => (
        <div
          key={message.message_id}
          className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          {message.role !== 'user' && (
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
              message.role === 'assistant' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
            }`}>
              {getMessageIcon(message)}
            </div>
          )}

          <div className={`max-w-4xl ${message.role === 'user' ? 'order-first' : ''}`}>
            <div className={`rounded-lg px-6 py-4 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : message.message_type === 'error'
                ? 'bg-red-50 border border-red-200 text-red-800'
                : 'bg-white border border-gray-200 text-gray-900 shadow-sm'
            }`}>
              {getMessageTypeIndicator(message)}
              
              <div className={`message-content ${message.role === 'user' ? 'text-white' : ''}`}>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Custom components for better styling
                    p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
                    h1: ({ children }) => <h1 className="text-xl font-bold mb-4 text-gray-900 border-b border-gray-200 pb-2">{children}</h1>,
                    h2: ({ children }) => <h2 className="text-lg font-bold mb-3 text-blue-900 mt-6 first:mt-0">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-base font-semibold mb-2 text-gray-800 mt-4 first:mt-0">{children}</h3>,
                    ul: ({ children }) => <ul className="list-none mb-4 space-y-2 ml-0">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside mb-4 space-y-2">{children}</ol>,
                    li: ({ children }) => (
                      <li className="flex items-start gap-2 py-1">
                        <span className="text-blue-500 mt-1 flex-shrink-0">•</span>
                        <span className="flex-1">{children}</span>
                      </li>
                    ),
                    strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                    
                    // Enhanced code block support with syntax highlighting
                    pre: ({ children, ...props }) => {
                      return <div {...props}>{children}</div>
                    },
                    code: ({ node, inline, className, children, ...props }) => {
                      const codeContent = String(children).replace(/\n$/, '')
                      
                      if (inline) {
                        // Inline code
                        return (
                          <code 
                            className={`px-1.5 py-0.5 rounded font-mono text-sm ${
                              message.role === 'user' 
                                ? 'bg-blue-500 text-blue-100' 
                                : 'bg-gray-200 text-gray-800'
                            }`}
                            {...props}
                          >
                            {codeContent}
                          </code>
                        )
                      }
                      
                      // Code block
                      return (
                        <CodeBlock 
                          className={className}
                          isDarkBackground={message.role === 'user'}
                        >
                          {codeContent}
                        </CodeBlock>
                      )
                    },
                    
                    // Enhanced table support
                    table: ({ children }) => (
                      <div className="overflow-x-auto my-4">
                        <table className="min-w-full border border-gray-300 rounded-lg">{children}</table>
                      </div>
                    ),
                    thead: ({ children }) => <thead className="bg-gray-50">{children}</thead>,
                    th: ({ children }) => (
                      <th className="px-4 py-2 text-left border-b border-gray-300 font-semibold text-gray-900">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="px-4 py-2 border-b border-gray-200 text-gray-700">
                        {children}
                      </td>
                    ),
                    
                    // Enhanced blockquote
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-blue-500 pl-4 my-4 italic text-gray-600">
                        {children}
                      </blockquote>
                    ),
                  }}
                >
                  {message.role === 'assistant' ? formatAgentText(message.content) : message.content}
                </ReactMarkdown>
              </div>

              {/* Show processing results for assistant messages */}
              {message.role === 'assistant' && message.processing_result && (
                <ProcessingResultDisplay result={message.processing_result} />
              )}

              {/* Show confidence score if available */}
              {message.confidence_score && (
                <div className="mt-2 text-xs text-gray-500">
                  Confidence: {Math.round(message.confidence_score * 100)}%
                </div>
              )}
            </div>

            <div className={`text-xs text-gray-500 mt-1 ${
              message.role === 'user' ? 'text-right' : 'text-left'
            }`}>
              {formatTimestamp(message.timestamp)}
            </div>
          </div>

          {message.role === 'user' && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center">
              {getMessageIcon(message)}
            </div>
          )}
        </div>
      ))}

      {/* Loading indicator */}
      {isLoading && (
        <div className="flex gap-3">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
            <Bot className="w-5 h-5 animate-pulse" />
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="flex space-x-1">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <span className="text-blue-700 font-medium">Agent is thinking...</span>
            </div>
            <div className="text-xs text-blue-600 mt-1">Processing your request with AI tools</div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MessageList
