export interface ChatMessage {
  message_id: string
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  message_type: 'text' | 'file_upload' | 'document_analysis' | 'processing_result' | 'error'
  timestamp: string
  attachments?: ChatFileAttachment[]
  metadata?: Record<string, any>
  processing_result?: Record<string, any>
  confidence_score?: number
  tool_calls?: Array<Record<string, any>>
}

export interface ChatFileAttachment {
  file_id: string
  file_name: string
  file_size: number
  mime_type: string
  upload_timestamp: string
  processing_status: 'pending' | 'processing' | 'completed' | 'error'
}

export interface ChatSession {
  session_id: string
  user_id?: string
  session_name: string
  status: 'active' | 'paused' | 'completed' | 'error'
  created_at: string
  updated_at: string
  last_activity: string
  current_application_id?: string
  customer_context: Record<string, any>
  session_metadata: Record<string, any>
  session_context?: string // Added for contextual prompts
  messages: ChatMessage[]
}

export interface QuickPrompt {
  id: string
  text: string
  icon: string
  category: string
}

export interface ChatSessionSummary {
  session_id: string
  session_name: string
  status: 'active' | 'paused' | 'completed' | 'error'
  created_at: string
  last_activity: string
  message_count: number
  has_documents: boolean
  current_application_id?: string
}

export interface ChatRequest {
  session_id?: string
  message: string
  include_history?: boolean
}

export interface ChatResponse {
  session_id: string
  message_id: string
  response: string
  message_type: string
  timestamp: string
  processing_time_ms?: number
  tool_calls_made?: string[]
  confidence_score?: number
  attachments?: ChatFileAttachment[]
  processing_result?: Record<string, any>
}

export interface ApiError {
  detail: string
  status_code?: number
}
