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

// Use LangGraph API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:2024'

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
  // Start a new agentic mortgage application conversation using LangGraph
  static async startApplication(userId?: string): Promise<AgenticStartResponse> {
    try {
      // Create a new LangGraph thread specifically for application processing
      const threadMetadata = {
        user_id: userId || 'anonymous',
        session_name: 'Mortgage Application Process',
        session_context: 'mortgage_application_agent',
        workflow_type: 'application_data_collection',
        created_at: new Date().toISOString()
      }

      const response = await api.post('/threads', {
        metadata: threadMetadata
      })

      const thread = response.data

      // Send initial message to trigger application agent
      const runInput = {
        messages: [
          {
            role: 'user',
            content: 'I want to start a mortgage application',
            timestamp: new Date().toISOString()
          }
        ]
      }

      const runResponse = await api.post(`/threads/${thread.thread_id}/runs`, {
        assistant_id: "mortgage_processing", // Use our graph name as assistant_id
        input: runInput,
        stream: false
      })

      return {
        session_id: thread.thread_id,
        message: 'Welcome to our mortgage application process! I\'ll guide you through collecting all necessary information.',
        status: 'started'
      }
    } catch (error) {
      console.error('Error starting application:', error)
      throw new Error(`Failed to start application: ${error}`)
    }
  }

  // Chat with agentic workflow using LangGraph (specialized agents handle everything)
  static async chatWithAgents(
    sessionId: string, 
    message: string
  ): Promise<AgenticChatResponse> {
    try {
      console.log(`Sending application message to LangGraph thread ${sessionId}:`, message)
      
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
      const runResponse = await api.post(`/threads/${sessionId}/runs`, {
        assistant_id: "mortgage_processing", // Use our graph name as assistant_id
        input: runInput,
        stream: false
      })

      const run = runResponse.data

      // Poll for completion
      let completed = false
      let attempts = 0
      const maxAttempts = 30
      
      while (!completed && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        const statusResponse = await api.get(`/threads/${sessionId}/runs/${run.run_id}`)
        const runStatus = statusResponse.data
        
        if (runStatus.status === 'success') {
          completed = true
          
          // Get the final state to extract the response and application data
          const stateResponse = await api.get(`/threads/${sessionId}/state`)
          const state = stateResponse.data
          
          const messages = state.values?.messages || []
          const lastMessage = messages[messages.length - 1]
          
          // Extract application data from the state
          const applicationData = state.values?.collected_data || {}
          const completionPercentage = state.values?.completion_percentage || 0
          const isComplete = state.values?.application_complete || false
          const currentStep = state.values?.current_step || 'unknown'
          
          return {
            session_id: sessionId,
            response: lastMessage?.content || 'No response generated',
            completion_percentage: completionPercentage,
            is_complete: isComplete,
            phase: currentStep,
            status: 'success',
            timestamp: new Date().toISOString(),
            application_data: applicationData
          }
          
        } else if (runStatus.status === 'error') {
          throw new Error(`LangGraph run failed: ${runStatus.output?.error || 'Unknown error'}`)
        }
        
        attempts++
      }
      
      if (!completed) {
        throw new Error('Request timeout - the application processing is taking longer than expected')
      }
      
    } catch (error) {
      console.error('Error chatting with application agents:', error)
      throw new Error(`Failed to process application message: ${error}`)
    }
    
    // This should never be reached, but TypeScript requires it
    throw new Error('Unexpected error in chatWithAgents')
  }

  // Submit completed application for processing using LangGraph
  static async submitApplication(
    sessionId: string,
    collectedData: Record<string, any>
  ): Promise<ApplicationSubmissionResponse> {
    try {
      // Send submission message to LangGraph
      const submissionMessage = `Please submit my mortgage application with the following data: ${JSON.stringify(collectedData)}`
      
      const runInput = {
        messages: [
          {
            role: 'user',
            content: submissionMessage,
            timestamp: new Date().toISOString()
          }
        ]
      }

      const runResponse = await api.post(`/threads/${sessionId}/runs`, {
        assistant_id: "mortgage_processing", // Use our graph name as assistant_id
        input: runInput,
        stream: false
      })

      const run = runResponse.data

      // Poll for completion
      let completed = false
      let attempts = 0
      const maxAttempts = 30
      
      while (!completed && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        const statusResponse = await api.get(`/threads/${sessionId}/runs/${run.run_id}`)
        const runStatus = statusResponse.data
        
        if (runStatus.status === 'success') {
          completed = true
          
          // Get the final state
          const stateResponse = await api.get(`/threads/${sessionId}/state`)
          const state = stateResponse.data
          
          const applicationId = state.values?.application_id || `app_${Date.now()}`
          
          return {
            application_id: applicationId,
            session_id: sessionId,
            status: 'submitted',
            submitted_at: new Date().toISOString(),
            collected_data: collectedData,
            validation_errors: state.values?.validation_errors || [],
            next_steps: [
              'Application submitted successfully',
              'Our underwriting team will review your application',
              'You will receive updates via email and SMS'
            ],
            urla_form_generated: true
          }
        } else if (runStatus.status === 'error') {
          throw new Error(`Application submission failed: ${runStatus.output?.error || 'Unknown error'}`)
        }
        
        attempts++
      }
      
      if (!completed) {
        throw new Error('Submission timeout - please try again')
      }
      
    } catch (error) {
      console.error('Error submitting application:', error)
      throw new Error(`Failed to submit application: ${error}`)
    }
    
    // This should never be reached, but TypeScript requires it
    throw new Error('Unexpected error in submitApplication')
  }

  // Check application status using LangGraph thread state
  static async checkApplicationStatus(applicationId: string): Promise<ApplicationStatusResponse> {
    try {
      // For now, we'll use the session ID as the thread ID
      // In a real implementation, you might store the mapping between application ID and thread ID
      const sessionId = applicationId.replace('app_', 'thread_')
      
      const stateResponse = await api.get(`/threads/${sessionId}/state`)
      const state = stateResponse.data
      
      const applicationData = state.values?.collected_data || {}
      
      return {
        application_id: applicationId,
        session_id: sessionId,
        status: state.values?.application_complete ? 'completed' : 'in_progress',
        completion_percentage: state.values?.completion_percentage || 0,
        submitted_at: state.values?.submitted_at || new Date().toISOString(),
        updated_at: new Date().toISOString(),
        personal_info: applicationData.personal_info || {},
        employment_info: applicationData.employment_info || {},
        property_info: applicationData.property_info || {},
        financial_info: applicationData.financial_info || {},
        next_steps: state.values?.next_required_fields || ['Complete remaining information'],
        processing_notes: 'Application being processed by LangGraph agents'
      }
    } catch (error) {
      console.error('Error checking application status:', error)
      throw new Error(`Failed to check application status: ${error}`)
    }
  }

  // Health check for LangGraph service
  static async healthCheck(): Promise<any> {
    try {
      // Test if we can create a thread (LangGraph health check)
      const response = await api.post('/threads', {
        metadata: { health_check: true }
      })
      return { 
        status: 'healthy', 
        service: 'LangGraph Agentic Application Service',
        timestamp: new Date().toISOString(),
        thread_id: response.data.thread_id
      }
    } catch (error) {
      throw new Error(`LangGraph application service health check failed: ${error}`)
    }
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
