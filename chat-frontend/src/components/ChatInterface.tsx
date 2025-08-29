import { useRef, useEffect } from 'react'
import { AlertCircle, HelpCircle, Home } from 'lucide-react'
import { useChat } from '../context/ChatContext'
import MessageList from './MessageList'
import ChatInput, { ChatInputRef } from './ChatInput'
import WelcomeScreen from './WelcomeScreen'
import QuickPrompts from './QuickPrompts'
import WizardStep from './WizardStep'

function ChatInterface() {
  const { state, goHome, clearWizard, completeWizardStep, goToWizardStep } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatInputRef = useRef<ChatInputRef>(null)

  // Get current wizard step
  const currentStep = state.wizardState?.steps.find(s => s.isActive)
  const currentStepIndex = state.wizardState?.steps.findIndex(s => s.isActive) ?? -1

  // Wizard navigation
  const handleWizardNext = () => {
    if (currentStepIndex < (state.wizardState?.steps.length ?? 0) - 1) {
      const nextStep = state.wizardState?.steps[currentStepIndex + 1]
      if (nextStep) {
        completeWizardStep(nextStep.id)
      }
    }
  }

  const handleWizardPrevious = () => {
    if (currentStepIndex > 0) {
      const previousStep = state.wizardState?.steps[currentStepIndex - 1]
      if (previousStep) {
        goToWizardStep(previousStep.id)
      }
    }
  }

  const handleExitWizard = () => {
    if (window.confirm('Are you sure you want to exit the guided process? You can always restart it later.')) {
      clearWizard()
      goHome() // Take user back to home/welcome screen
    }
  }

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
      {/* Compact Header with Integrated Progress */}
      <div className="flex-shrink-0 border-b border-gray-200 bg-white">
        {state.currentSession ? (
          <div className="p-2">
            {/* Wizard Mode - Ultra Compact Layout */}
            {state.wizardState ? (
              <div className="space-y-1.5">
                {/* Top Row: Exit + Title + Progress */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleExitWizard}
                      className="flex items-center gap-1 px-2 py-1 text-xs text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    >
                      <Home className="w-3 h-3" />
                      <span>Exit Guide</span>
                    </button>
                    <h2 className="text-sm font-semibold text-gray-900">
                      {state.currentSession.session_name}
                    </h2>
                    <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded text-xs">
                      Guided Mode
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {state.wizardState.completionPercentage}% • {state.messages.length} msgs
                  </div>
                </div>

                {/* Compact Step Indicators in One Line */}
                <div className="flex items-center gap-1">
                  {state.wizardState.steps.map((step, index) => (
                    <div key={step.id} className="flex items-center">
                      <button
                        onClick={() => goToWizardStep(step.id)}
                        className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium transition-colors ${
                          step.isCompleted 
                            ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                            : step.isActive 
                              ? 'bg-blue-100 text-blue-700 hover:bg-blue-200' 
                              : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                        }`}
                        title={step.title}
                      >
                        {step.isCompleted ? '✓' : index + 1}
                      </button>
                      {index < (state.wizardState?.steps.length ?? 0) - 1 && (
                        <div className={`w-3 h-0.5 ${
                          step.isCompleted ? 'bg-green-300' : 'bg-gray-200'
                        }`} />
                      )}
                    </div>
                  ))}
                  <div className="ml-2 text-xs text-gray-600 font-medium">
                    {currentStep?.title}
                  </div>
                </div>
              </div>
            ) : (
              /* Regular Chat Mode */
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    onClick={goHome}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <Home className="w-4 h-4" />
                    <span>Home</span>
                  </button>
                  <h2 className="text-lg font-semibold text-gray-900">
                    {state.currentSession.session_name}
                  </h2>
                </div>
                <div className="text-sm text-gray-500">
                  {state.messages.length} messages
                </div>
              </div>
            )}
          </div>
        ) : (
          /* No Session - Centered Layout */
          <div className="flex items-center justify-between">
            {/* Empty left spacer for balance */}
            <div className="w-24"></div>
            
            {/* Centered Title */}
            <div className="text-center mt-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Mortgage Expert
              </h1>
              <p className="text-lg text-gray-600">
                Get personalized guidance from application to approval
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
            {/* Wizard Step Component - CONSTRAINED HEIGHT */}
            {state.wizardState && currentStep && (
              <div className="flex-shrink-0 max-h-96 overflow-y-auto">
                <WizardStep
                  step={currentStep}
                  onNext={handleWizardNext}
                  onPrevious={handleWizardPrevious}
                  isFirst={currentStepIndex === 0}
                  isLast={currentStepIndex === (state.wizardState.steps.length - 1)}
                  onPreFillMessage={(text) => chatInputRef.current?.preFillMessage(text)}
                />
              </div>
            )}

            {/* Quick Actions at Top for Better UX - Only show if not in wizard mode */}
            {!state.wizardState && state.messages.length <= 1 && state.currentSession && (
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

            {/* Messages - NOW WITH GUARANTEED SPACE */}
            <div className="flex-1 min-h-0 overflow-y-auto bg-gray-50">
              <MessageList messages={state.messages} isLoading={state.isLoading} />
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex-shrink-0 border-t border-gray-200 p-4">
              <ChatInput 
                ref={chatInputRef}
                disabled={!state.isConnected || state.isLoading}
                placeholder={
                  state.wizardState && currentStep
                    ? currentStep.id === 'situation' 
                      ? 'e.g., "My household income is $85,000" or "I\'m looking in Austin, Texas"'
                      : currentStep.id === 'finances'
                      ? 'e.g., "I have $40,000 saved for down payment" or "I pay $600/month in debt"'
                      : currentStep.id === 'documents'
                      ? 'Ask questions about documents or drag & drop files above'
                      : 'Type your message here...'
                    : undefined
                }
              />
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
