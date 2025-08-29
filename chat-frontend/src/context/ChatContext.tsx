import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import { ChatSession, ChatMessage, ChatSessionSummary } from '../types/chat'
import { WizardState, WizardType, WIZARD_DEFINITIONS, WizardStepData } from '../types/wizard'
import ChatAPI from '../services/api'
import toast from 'react-hot-toast'

// State interface
interface ChatState {
  sessions: ChatSessionSummary[]
  currentSession: ChatSession | null
  messages: ChatMessage[]
  isLoading: boolean
  isConnected: boolean
  error: string | null
  wizardState: WizardState | null
}

// Action types
type ChatAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_CONNECTED'; payload: boolean }
  | { type: 'SET_SESSIONS'; payload: ChatSessionSummary[] }
  | { type: 'SET_CURRENT_SESSION'; payload: ChatSession | null }
  | { type: 'SET_MESSAGES'; payload: ChatMessage[] }
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'UPDATE_MESSAGE'; payload: { messageId: string; updates: Partial<ChatMessage> } }
  | { type: 'DELETE_SESSION'; payload: string }
  | { type: 'START_WIZARD'; payload: { wizardType: WizardType; sessionName?: string } }
  | { type: 'UPDATE_WIZARD_STEP'; payload: { stepId: string; data?: WizardStepData } }
  | { type: 'COMPLETE_WIZARD_STEP'; payload: { stepId: string } }
  | { type: 'GO_TO_WIZARD_STEP'; payload: { stepId: string } }
  | { type: 'SET_WIZARD_STATE'; payload: WizardState | null }
  | { type: 'CLEAR_WIZARD'; payload: null }

// Initial state
const initialState: ChatState = {
  sessions: [],
  currentSession: null,
  messages: [],
  isLoading: false,
  isConnected: false,
  error: null,
  wizardState: null,
}

// Reducer
function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    
    case 'SET_CONNECTED':
      return { ...state, isConnected: action.payload }
    
    case 'SET_SESSIONS':
      return { ...state, sessions: action.payload }
    
    case 'SET_CURRENT_SESSION':
      return { 
        ...state, 
        currentSession: action.payload,
        messages: action.payload?.messages || []
      }
    
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload }
    
    case 'ADD_MESSAGE':
      return { 
        ...state, 
        messages: [...state.messages, action.payload]
      }
    
    case 'UPDATE_MESSAGE':
      return {
        ...state,
        messages: state.messages.map(msg =>
          msg.message_id === action.payload.messageId
            ? { ...msg, ...action.payload.updates }
            : msg
        )
      }
    
    case 'DELETE_SESSION':
      return {
        ...state,
        sessions: state.sessions.filter(s => s.session_id !== action.payload),
        currentSession: state.currentSession?.session_id === action.payload 
          ? null 
          : state.currentSession
      }
    
    case 'START_WIZARD':
      const wizardDef = WIZARD_DEFINITIONS[action.payload.wizardType as string]
      if (!wizardDef) return state
      
      return {
        ...state,
        wizardState: {
          wizardType: action.payload.wizardType,
          currentStepId: wizardDef.steps[0].id,
          steps: wizardDef.steps.map((step, index) => ({
            ...step,
            isCompleted: false,
            isActive: index === 0
          })),
          collectedData: {},
          completionPercentage: 0,
          isCompleted: false
        }
      }
    
    case 'UPDATE_WIZARD_STEP':
      if (!state.wizardState) return state
      
      return {
        ...state,
        wizardState: {
          ...state.wizardState,
          collectedData: {
            ...state.wizardState.collectedData,
            [action.payload.stepId]: {
              ...state.wizardState.collectedData[action.payload.stepId],
              ...action.payload.data
            }
          }
        }
      }
    
    case 'COMPLETE_WIZARD_STEP':
      if (!state.wizardState) return state
      
      const stepIndex = state.wizardState.steps.findIndex(s => s.id === action.payload.stepId)
      const nextStepIndex = stepIndex + 1
      const hasNextStep = nextStepIndex < state.wizardState.steps.length
      
      return {
        ...state,
        wizardState: {
          ...state.wizardState,
          currentStepId: hasNextStep ? state.wizardState.steps[nextStepIndex].id : action.payload.stepId,
          steps: state.wizardState.steps.map((step, index) => ({
            ...step,
            isCompleted: index <= stepIndex,
            isActive: index === nextStepIndex || (!hasNextStep && index === stepIndex)
          })),
          completionPercentage: Math.round(((stepIndex + 1) / state.wizardState.steps.length) * 100),
          isCompleted: !hasNextStep
        }
      }
    
    case 'GO_TO_WIZARD_STEP':
      if (!state.wizardState) return state
      
      const targetStepIndex = state.wizardState.steps.findIndex(s => s.id === action.payload.stepId)
      if (targetStepIndex === -1) return state
      
      const targetStep = state.wizardState.steps[targetStepIndex]
      
      // Create a system message indicating step change
      const stepChangeMessage: ChatMessage = {
        message_id: `step_change_${Date.now()}`,
        role: 'assistant' as const,
        content: `You've navigated to: **${targetStep.title}**\n\n${targetStep.description}\n\nI'm here to help you with this step. Feel free to ask questions or use the quick prompts above!`,
        timestamp: new Date().toISOString(),
        session_id: state.currentSession?.session_id || ''
      }
      
      return {
        ...state,
        messages: [stepChangeMessage], // Clear old messages and add step info
        wizardState: {
          ...state.wizardState,
          currentStepId: action.payload.stepId,
          steps: state.wizardState.steps.map((step, index) => ({
            ...step,
            isActive: index === targetStepIndex
          }))
        }
      }
    
    case 'SET_WIZARD_STATE':
      return {
        ...state,
        wizardState: action.payload
      }
    
    case 'CLEAR_WIZARD':
      return {
        ...state,
        wizardState: null
      }
    
    default:
      return state
  }
}

// Context
interface ChatContextType {
  state: ChatState
  startNewSession: (sessionName?: string, sessionContext?: string) => Promise<void>
  loadSessions: () => Promise<void>
  selectSession: (sessionId: string) => Promise<void>
  sendMessage: (message: string) => Promise<void>
  uploadFiles: (message: string, files: File[]) => Promise<void>
  deleteSession: (sessionId: string) => Promise<void>
  clearMessages: () => Promise<void>
  goHome: () => void
  clearError: () => void
  // Wizard functions
  startWizard: (wizardType: WizardType, sessionName?: string) => Promise<void>
  updateWizardStep: (stepId: string, data?: WizardStepData) => void
  completeWizardStep: (stepId: string) => void
  goToWizardStep: (stepId: string) => void
  clearWizard: () => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

// Provider component
export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, initialState)

  // Check connection on mount
  useEffect(() => {
    let mounted = true
    
    const initialize = async () => {
      if (mounted) {
        await checkConnection()
        await loadSessions()
      }
    }
    
    initialize()
    
    return () => {
      mounted = false
    }
  }, [])

  const checkConnection = async () => {
    try {
      const healthResponse = await ChatAPI.healthCheck()
      dispatch({ type: 'SET_CONNECTED', payload: true })
    } catch (error) {
      console.error('Health check failed:', error)
      dispatch({ type: 'SET_CONNECTED', payload: false })
      dispatch({ type: 'SET_ERROR', payload: 'Unable to connect to server' })
    }
  }

  const startNewSession = async (sessionName?: string, sessionContext?: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      dispatch({ type: 'SET_ERROR', payload: null })

      const session = await ChatAPI.startSession(undefined, sessionName, sessionContext)
      dispatch({ type: 'SET_CURRENT_SESSION', payload: session })
      
      // Reload sessions to include the new one
      await loadSessions()
      
      toast.success('New chat session started!')
    } catch (error) {
      console.error('Failed to start session:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to start session'
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      toast.error(errorMessage)
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const loadSessions = async () => {
    try {
      const sessions = await ChatAPI.getSessions()
      dispatch({ type: 'SET_SESSIONS', payload: sessions })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load sessions'
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
    }
  }

  const selectSession = async (sessionId: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      dispatch({ type: 'SET_ERROR', payload: null })

      const session = await ChatAPI.getSession(sessionId)
      dispatch({ type: 'SET_CURRENT_SESSION', payload: session })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load session'
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      toast.error(errorMessage)
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const sendMessage = async (message: string) => {
    if (!state.currentSession) {
      toast.error('No active session')
      return
    }

    const sessionId = state.currentSession.session_id

    try {
      dispatch({ type: 'SET_ERROR', payload: null })
      dispatch({ type: 'SET_LOADING', payload: true })

      // Add user message immediately
      const userMessage: ChatMessage = {
        message_id: `temp_${Date.now()}`,
        session_id: sessionId,
        role: 'user',
        content: message,
        message_type: 'text',
        timestamp: new Date().toISOString(),
      }
      dispatch({ type: 'ADD_MESSAGE', payload: userMessage })

      // Send to API
      const response = await ChatAPI.sendMessage(sessionId, message)

      // Add assistant response
      const assistantMessage: ChatMessage = {
        message_id: response.message_id,
        session_id: response.session_id,
        role: 'assistant',
        content: response.response,
        message_type: response.message_type as any,
        timestamp: typeof response.timestamp === 'string' ? response.timestamp : response.timestamp.toString(),
        processing_result: response.processing_result,
        confidence_score: response.confidence_score,
      }
      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage })

    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message'
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      toast.error(errorMessage)
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const uploadFiles = async (message: string, files: File[]) => {
    if (!state.currentSession) {
      toast.error('No active session')
      return
    }

    try {
      dispatch({ type: 'SET_ERROR', payload: null })
      dispatch({ type: 'SET_LOADING', payload: true })

      // Add user message with file indication
      const userMessage: ChatMessage = {
        message_id: `temp_${Date.now()}`,
        session_id: state.currentSession.session_id,
        role: 'user',
        content: `${message} [Uploading ${files.length} file(s)...]`,
        message_type: 'file_upload',
        timestamp: new Date().toISOString(),
      }
      dispatch({ type: 'ADD_MESSAGE', payload: userMessage })

      // Upload files
      console.log('Uploading files to agent:', files.map(f => f.name))
      const response = await ChatAPI.uploadFiles(
        state.currentSession.session_id,
        message,
        files
      )
      console.log('Received file processing response from agent:', response)

      // Add assistant response
      const assistantMessage: ChatMessage = {
        message_id: response.message_id,
        session_id: response.session_id,
        role: 'assistant',
        content: response.response,
        message_type: response.message_type as any,
        timestamp: response.timestamp,
        processing_result: response.processing_result,
        confidence_score: response.confidence_score,
      }
      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage })

      toast.success(`Successfully processed ${files.length} file(s)`)

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload files'
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      toast.error(errorMessage)
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const deleteSession = async (sessionId: string) => {
    try {
      await ChatAPI.deleteSession(sessionId)
      dispatch({ type: 'DELETE_SESSION', payload: sessionId })
      toast.success('Session deleted')
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete session'
      toast.error(errorMessage)
    }
  }

  const clearMessages = async () => {
    if (!state.currentSession) {
      toast.error('No active session to clear')
      return
    }

    try {
      // Clear messages from database
      await ChatAPI.clearSessionMessages(state.currentSession.session_id)
      
      // Clear messages from local state
      dispatch({ type: 'SET_MESSAGES', payload: [] })
      
      toast.success('Chat history cleared')
    } catch (error) {
      console.error('Failed to clear messages:', error)
      toast.error('Failed to clear chat history')
    }
  }

  const goHome = () => {
    dispatch({ type: 'SET_CURRENT_SESSION', payload: null })
    dispatch({ type: 'SET_MESSAGES', payload: [] })
  }

  const clearError = () => {
    dispatch({ type: 'SET_ERROR', payload: null })
  }

  // Wizard functions
  const startWizard = async (wizardType: WizardType, sessionName?: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      dispatch({ type: 'SET_ERROR', payload: null })

      // Start wizard state first
      dispatch({ type: 'START_WIZARD', payload: { wizardType, sessionName } })

      // Create session with wizard context
      const wizardDef = WIZARD_DEFINITIONS[wizardType as string]
      const session = await ChatAPI.startSession(
        undefined, 
        sessionName || wizardDef.title,
        wizardType as string
      )
      
      dispatch({ type: 'SET_CURRENT_SESSION', payload: session })
      
      // Reload sessions to include the new one
      await loadSessions()
      
      toast.success(`Started ${wizardDef.title}`)
    } catch (error) {
      console.error('Failed to start wizard:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to start wizard'
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      toast.error(errorMessage)
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const updateWizardStep = (stepId: string, data?: WizardStepData) => {
    dispatch({ type: 'UPDATE_WIZARD_STEP', payload: { stepId, data } })
  }

  const completeWizardStep = (stepId: string) => {
    dispatch({ type: 'COMPLETE_WIZARD_STEP', payload: { stepId } })
  }

  const goToWizardStep = (stepId: string) => {
    dispatch({ type: 'GO_TO_WIZARD_STEP', payload: { stepId } })
  }

  const clearWizard = () => {
    dispatch({ type: 'CLEAR_WIZARD', payload: null })
  }

  const contextValue: ChatContextType = {
    state,
    startNewSession,
    loadSessions,
    selectSession,
    sendMessage,
    uploadFiles,
    deleteSession,
    clearMessages,
    goHome,
    clearError,
    startWizard,
    updateWizardStep,
    completeWizardStep,
    goToWizardStep,
    clearWizard,
  }

  return (
    <ChatContext.Provider value={contextValue}>
      {children}
    </ChatContext.Provider>
  )
}

// Hook to use chat context
export function useChat() {
  const context = useContext(ChatContext)
  if (context === undefined) {
    console.error('useChat called outside ChatProvider - this may be due to hot module reloading')
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}

// Safe hook that doesn't throw errors
export function useChatSafe() {
  const context = useContext(ChatContext)
  if (context === undefined) {
    console.warn('useChatSafe: Context is undefined, component may be outside ChatProvider')
    return null
  }
  return context
}

export default ChatContext
