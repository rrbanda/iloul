import axios, { AxiosResponse } from 'axios'

// Simple types for agentic workflow
interface AgenticStartResponse {
  session_id: string
  message: string
  status: string
}

interface AgenticChatResponse {
  session_id: string
  response: string
  completion_percentage: number
  is_complete: boolean
  phase: string
  status: string
  timestamp: string
  application_data?: {
    personal_info?: {
      full_name?: string
      phone?: string
      email?: string
    }
    employment_info?: {
      annual_income?: number
      employer?: string
      employment_type?: string
    }
    property_info?: {
      purchase_price?: number
      property_type?: string
      property_location?: string
    }
    financial_info?: {
      down_payment?: number
      credit_score?: number
    }
  }
}

interface ApplicationSubmissionRequest {
  session_id: string
  collected_data: Record<string, any>
}

interface ApplicationSubmissionResponse {
  application_id: string
  session_id: string
  status: string
  submitted_at: string
  collected_data: Record<string, any>
  validation_errors: string[]
  next_steps: string[]
  urla_form_generated: boolean
}

interface ApplicationStatusResponse {
  application_id: string
  session_id: string
  status: string
  completion_percentage: number
  submitted_at: string
  updated_at: string
  personal_info: {
    full_name?: string
    phone?: string
    email?: string
  }
  employment_info: {
    annual_income?: number
    employer?: string
    employment_type?: string
  }
  property_info: {
    purchase_price?: number
    property_type?: string
    property_location?: string
  }
  financial_info: {
    down_payment?: number
    credit_score?: number
  }
  next_steps: string[]
  processing_notes?: string
}

// Use same base URL as existing API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('Agentic API:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('Agentic API Request error:', error)
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

export class AgenticApplicationAPI {
  // Start a new agentic mortgage application conversation
  static async startApplication(userId?: string): Promise<AgenticStartResponse> {
    const response: AxiosResponse<AgenticStartResponse> = await api.post(
      '/mortgage/application/start',
      {
        user_id: userId
      }
    )
    return response.data
  }

  // Chat with agentic workflow (specialized agents handle everything)
  static async chatWithAgents(
    sessionId: string, 
    message: string
  ): Promise<AgenticChatResponse> {
    const response: AxiosResponse<AgenticChatResponse> = await api.post(
      `/mortgage/application/${sessionId}/chat`,
      {
        message
      }
    )
    return response.data
  }

  // Submit completed application for processing
  static async submitApplication(
    sessionId: string,
    collectedData: Record<string, any>
  ): Promise<ApplicationSubmissionResponse> {
    const response: AxiosResponse<ApplicationSubmissionResponse> = await api.post(
      `/mortgage/application/${sessionId}/submit`,
      {
        session_id: sessionId,
        collected_data: collectedData
      }
    )
    return response.data
  }

  // Check application status by application ID
  static async checkApplicationStatus(applicationId: string): Promise<ApplicationStatusResponse> {
    const response: AxiosResponse<ApplicationStatusResponse> = await api.get(
      `/applications/${applicationId}`
    )
    return response.data
  }

  // Health check for agentic service
  static async healthCheck(): Promise<any> {
    const response = await api.get('/health')
    return response.data
  }
}

export default AgenticApplicationAPI
export type { 
  AgenticStartResponse, 
  AgenticChatResponse, 
  ApplicationSubmissionResponse,
  ApplicationSubmissionRequest,
  ApplicationStatusResponse
}
