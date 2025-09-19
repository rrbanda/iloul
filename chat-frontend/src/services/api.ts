import axios, { AxiosResponse } from 'axios'
import { 
  ChatSession, 
  ChatSessionSummary, 
  ChatRequest, 
  ChatResponse,
  ApiError 
} from '../types/chat'

// Configure axios base URL for LangGraph API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:2024'

console.log('LangGraph API Base URL:', API_BASE_URL) // Debug log

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for debugging (reduced logging)
api.interceptors.request.use(
  (config) => {
    // Only log important requests to avoid spam
    if (config.url?.includes('messages') || config.url?.includes('sessions/start')) {
      console.log('API:', config.method?.toUpperCase(), config.url)
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail)
    }
    throw new Error(error.message || 'An unexpected error occurred')
  }
)

// LangGraph API types
interface LangGraphThread {
  thread_id: string
  created_at: string
  metadata?: Record<string, any>
}

interface LangGraphRun {
  run_id: string
  thread_id: string
  status: 'pending' | 'running' | 'success' | 'error' | 'interrupted'
  input: any
  output?: any
  created_at: string
  updated_at: string
}

interface LangGraphMessage {
  id: string
  type: 'human' | 'ai' | 'system'
  content: string
  timestamp: string
  metadata?: Record<string, any>
}

export class ChatAPI {
  // Create a new LangGraph thread (equivalent to starting a session)
  static async startSession(userId?: string, sessionName?: string, sessionContext?: string): Promise<ChatSession> {
    const threadMetadata = {
      user_id: userId || 'anonymous',
      session_name: sessionName || 'Mortgage Application Chat',
      session_context: sessionContext || 'mortgage_application',
      created_at: new Date().toISOString()
    }

    const response: AxiosResponse<LangGraphThread> = await api.post('/threads', {
      metadata: threadMetadata
    })

    const thread = response.data
    
    // Convert LangGraph thread to ChatSession format
    return {
      session_id: thread.thread_id,
      user_id: userId || 'anonymous',
      session_name: sessionName || 'Mortgage Application Chat',
      status: 'active',
      created_at: thread.created_at,
      updated_at: thread.created_at,
      message_count: 0,
      last_message: null,
      session_context: sessionContext || 'mortgage_application'
    } as ChatSession
  }

  // Get list of threads (sessions) - Note: LangGraph may not support listing all threads
  static async getSessions(userId?: string, activeOnly: boolean = true): Promise<ChatSessionSummary[]> {
    // LangGraph doesn't have a built-in endpoint to list all threads
    // For now, we'll return an empty array or implement local storage
    console.warn('LangGraph does not support listing all threads. Consider implementing local storage.')
    return []
  }

  // Get a specific thread (session)
  static async getSession(sessionId: string): Promise<ChatSession> {
    try {
      const response: AxiosResponse<LangGraphThread> = await api.get(`/threads/${sessionId}`)
      const thread = response.data
      
      // Get thread state to extract messages
      const stateResponse = await api.get(`/threads/${sessionId}/state`)
      const state = stateResponse.data
      
      const messages = state.values?.messages || []
      
      return {
        session_id: thread.thread_id,
        user_id: thread.metadata?.user_id || 'anonymous',
        session_name: thread.metadata?.session_name || 'Mortgage Chat',
        status: 'active',
        created_at: thread.created_at,
        updated_at: new Date().toISOString(),
        message_count: messages.length,
        last_message: messages.length > 0 ? messages[messages.length - 1] : null,
        session_context: thread.metadata?.session_context || 'mortgage_application'
      } as ChatSession
    } catch (error) {
      throw new Error(`Failed to get session: ${error}`)
    }
  }

  // Send a message to LangGraph
  static async sendMessage(sessionId: string, message: string, includeHistory: boolean = true): Promise<ChatResponse> {
    try {
      console.log(`Sending message to LangGraph thread ${sessionId}:`, message)
      
      // Create the input for the LangGraph run
      const runInput = {
        messages: [
          {
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
          }
        ]
      }

      // Start a run on the thread
      const runResponse: AxiosResponse<LangGraphRun> = await api.post(
        `/threads/${sessionId}/runs`, 
        {
          assistant_id: "mortgage_processing", // Use our graph name as assistant_id
          input: runInput,
          stream: false // Set to false for now, can enable streaming later
        }
      )

      const run = runResponse.data
      console.log('LangGraph run started:', run.run_id)

      // Poll for completion (in a real app, you might want to use streaming)
      let completed = false
      let attempts = 0
      const maxAttempts = 30 // 30 seconds timeout
      
      while (!completed && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1000)) // Wait 1 second
        
        const statusResponse = await api.get(`/threads/${sessionId}/runs/${run.run_id}`)
        const runStatus = statusResponse.data
        
        if (runStatus.status === 'success') {
          completed = true
          
          // Get the final state to extract the response
          const stateResponse = await api.get(`/threads/${sessionId}/state`)
          const state = stateResponse.data
          
          const messages = state.values?.messages || []
          const lastMessage = messages[messages.length - 1]
          
          return {
            message_id: `msg_${Date.now()}`,
            session_id: sessionId,
            user_message: message,
            assistant_response: lastMessage?.content || 'No response generated',
            timestamp: new Date().toISOString(),
            status: 'success',
            metadata: {
              run_id: run.run_id,
              agent_used: lastMessage?.metadata?.agent || 'supervisor',
              processing_time: Date.now() - new Date(run.created_at).getTime()
            }
          } as ChatResponse
          
        } else if (runStatus.status === 'error') {
          throw new Error(`LangGraph run failed: ${runStatus.output?.error || 'Unknown error'}`)
        }
        
        attempts++
      }
      
      if (!completed) {
        throw new Error('Request timeout - the mortgage processing system is taking longer than expected')
      }
      
    } catch (error) {
      console.error('Error sending message to LangGraph:', error)
      throw new Error(`Failed to send message: ${error}`)
    }
    
    // This should never be reached, but TypeScript requires it
    throw new Error('Unexpected error in sendMessage')
  }

  // Upload files (LangGraph doesn't have built-in file upload, so we'll handle it differently)
  static async uploadFiles(sessionId: string, message: string, files: File[]): Promise<ChatResponse> {
    // For now, we'll convert files to text and include in the message
    // In a production system, you might want to upload files to a separate service
    
    let fileContents = ''
    for (const file of files) {
      const text = await file.text()
      fileContents += `\n\n--- File: ${file.name} ---\n${text}\n--- End of ${file.name} ---`
    }
    
    const enhancedMessage = `${message}\n\nAttached files:${fileContents}`
    
    return this.sendMessage(sessionId, enhancedMessage, true)
  }

  // Get conversation history from LangGraph thread state
  static async getHistory(sessionId: string, limit?: number) {
    try {
      const stateResponse = await api.get(`/threads/${sessionId}/state`)
      const state = stateResponse.data
      
      let messages = state.values?.messages || []
      
      if (limit) {
        messages = messages.slice(-limit)
      }
      
      return {
        session_id: sessionId,
        messages: messages.map((msg: any, index: number) => ({
          id: `msg_${index}`,
          type: msg.role === 'user' ? 'human' : 'ai',
          content: msg.content,
          timestamp: msg.timestamp || new Date().toISOString(),
          metadata: msg.metadata || {}
        })),
        total_count: messages.length
      }
    } catch (error) {
      console.error('Error getting history from LangGraph:', error)
      return {
        session_id: sessionId,
        messages: [],
        total_count: 0
      }
    }
  }

  // Delete a thread (LangGraph doesn't have delete, so we'll clear state)
  static async deleteSession(sessionId: string): Promise<void> {
    try {
      // LangGraph doesn't have a delete endpoint, so we'll just clear the state
      await api.patch(`/threads/${sessionId}/state`, {
        values: { messages: [] }
      })
    } catch (error) {
      console.warn('Could not delete LangGraph thread:', error)
    }
  }

  // Clear messages from a thread
  static async clearSessionMessages(sessionId: string): Promise<void> {
    try {
      await api.patch(`/threads/${sessionId}/state`, {
        values: { messages: [] }
      })
    } catch (error) {
      console.error('Error clearing messages:', error)
      throw new Error(`Failed to clear messages: ${error}`)
    }
  }

  // Health check for LangGraph
  static async healthCheck() {
    try {
      // LangGraph doesn't have a standard health endpoint, so we'll check if we can create a thread
      const response = await api.post('/threads', {
        metadata: { health_check: true }
      })
      return { 
        status: 'healthy', 
        service: 'LangGraph Mortgage Processing',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(`LangGraph health check failed: ${error}`)
    }
  }

  // Get system info (replace mortgage config)
  static async getMortgageConfig() {
    // Since we're using LangGraph, we can return static config or try to get it from the graph
    return {
      system: 'LangGraph Mortgage Processing System',
      agents: [
        'AssistantAgent - Customer guidance and education',
        'DataAgent - Data collection and processing', 
        'PropertyAgent - Property valuation and analysis',
        'UnderwritingAgent - Risk analysis and loan decisions',
        'ComplianceAgent - Regulatory compliance',
        'ClosingAgent - Closing coordination',
        'CustomerServiceAgent - Post-submission support',
        'ApplicationAgent - Interactive application processing'
      ],
      version: '2.0.0',
      capabilities: [
        'Multi-agent mortgage processing',
        'Real-time RAG knowledge retrieval',
        'Neo4j graph database integration',
        'Automated workflow orchestration'
      ]
    }
  }
}

export default ChatAPI
