import axios, { AxiosResponse } from 'axios'
import { 
  ChatSession, 
  ChatSessionSummary, 
  ChatRequest, 
  ChatResponse,
  ApiError 
} from '../types/chat'

// Configure axios base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

console.log('API Base URL:', API_BASE_URL) // Debug log

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

export class ChatAPI {
  // Start a new chat session
  static async startSession(userId?: string, sessionName?: string, sessionContext?: string): Promise<ChatSession> {
    const response: AxiosResponse<ChatSession> = await api.post('/chat/sessions/start', {
      user_id: userId,
      session_name: sessionName,
      session_context: sessionContext,
    })
    return response.data
  }

  // Get list of chat sessions
  static async getSessions(userId?: string, activeOnly: boolean = true): Promise<ChatSessionSummary[]> {
    const params = new URLSearchParams()
    if (userId) params.append('user_id', userId)
    if (activeOnly) params.append('active_only', 'true')

    const response: AxiosResponse<ChatSessionSummary[]> = await api.get(
      `/chat/sessions?${params.toString()}`
    )
    return response.data
  }

  // Get a specific session
  static async getSession(sessionId: string): Promise<ChatSession> {
    const response: AxiosResponse<ChatSession> = await api.get(`/chat/sessions/${sessionId}`)
    return response.data
  }

  // Send a chat message
  static async sendMessage(sessionId: string, message: string, includeHistory: boolean = true): Promise<ChatResponse> {
    const response: AxiosResponse<ChatResponse> = await api.post(
      `/chat/sessions/${sessionId}/messages`,
      {
        message,
        include_history: includeHistory,
      }
    )
    return response.data
  }

  // Upload files and send message
  static async uploadFiles(sessionId: string, message: string, files: File[]): Promise<ChatResponse> {
    const formData = new FormData()
    formData.append('message', message)
    
    files.forEach((file) => {
      formData.append('files', file)
    })

    const response: AxiosResponse<ChatResponse> = await api.post(
      `/chat/sessions/${sessionId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  }

  // Get conversation history
  static async getHistory(sessionId: string, limit?: number) {
    const params = new URLSearchParams()
    if (limit) params.append('limit', limit.toString())

    const response = await api.get(`/chat/sessions/${sessionId}/history?${params.toString()}`)
    return response.data
  }

  // Delete a session
  static async deleteSession(sessionId: string): Promise<void> {
    await api.delete(`/chat/sessions/${sessionId}`)
  }

  // Clear all messages from a session (but keep session active)
  static async clearSessionMessages(sessionId: string): Promise<void> {
    await api.delete(`/chat/sessions/${sessionId}/messages`)
  }

  // Health check
  static async healthCheck() {
    const response = await api.get('/health')
    return response.data
  }

  // Get mortgage config (from existing API)
  static async getMortgageConfig() {
    const response = await api.get('/mortgage/config')
    return response.data
  }
}

export default ChatAPI
