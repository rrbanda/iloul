import { useRef, useEffect, useState } from 'react'
import { AlertCircle, HelpCircle, Home, ArrowLeft, CheckCircle } from 'lucide-react'
import { useChat } from '../context/ChatContext'
import MessageList from './MessageList'
import ChatInput, { ChatInputRef } from './ChatInput'
import WelcomeScreen from './WelcomeScreen'
import QuickPrompts from './QuickPrompts'
import WizardStep from './WizardStep'

function ChatInterface() {
  const { 
    state, 
    goHome, 
    clearWizard, 
    completeWizardStep, 
    goToWizardStep,
    startMortgageApplication,
    submitMortgageApplication,
    clearMortgageApplication,
    updateMortgageApplication
  } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatInputRef = useRef<ChatInputRef>(null)
  const [hasStartedMortgage, setHasStartedMortgage] = useState(false)

  // Get current wizard step
  const currentStep = state.wizardState?.steps.find(s => s.isActive)
  const currentStepIndex = state.wizardState?.steps.findIndex(s => s.isActive) ?? -1

  // Check if we're in mortgage application mode (LangGraph)
  const isMortgageApplication = state.mortgageApplication.isActive || 
                                state.wizardState?.wizardType === 'mortgage_application'

  // Auto-start mortgage application if needed
  useEffect(() => {
    if (isMortgageApplication && !hasStartedMortgage && !state.mortgageApplication.isActive) {
      startMortgageApplication()
      setHasStartedMortgage(true)
    }
  }, [isMortgageApplication, hasStartedMortgage, state.mortgageApplication.isActive, startMortgageApplication])

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

  // Mortgage application handlers
  const handleMortgageBack = () => {
    clearMortgageApplication()
    setHasStartedMortgage(false)
    goHome()
  }

  // Check if application is complete and ready for summary
  const showMortgageApplicationSummary = state.mortgageApplication.isComplete

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

  // Application Summary Component (moved from MortgageApplicationWizard)
  const ApplicationSummary = ({ collectedData, onSubmit, onEdit }: {
    collectedData: Record<string, any>
    onSubmit: () => void
    onEdit: () => void
  }) => {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-2xl mx-auto">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <h2 className="text-lg font-semibold text-green-800">
                Application Data Collection Complete!
              </h2>
            </div>
            <p className="text-green-700 text-sm">
              Review your information below and submit your mortgage application.
            </p>
          </div>

          {/* Collected Data Display */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Your Application Information
            </h3>
            
            {Object.keys(collectedData).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(collectedData).map(([key, value]) => (
                  <div key={key} className="flex justify-between py-2 border-b border-gray-100 last:border-b-0">
                    <span className="font-medium text-gray-700 capitalize">
                      {key.replace(/_/g, ' ')}:
                    </span>
                    <span className="text-gray-900">
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">No data collected yet.</p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onEdit}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Edit Information
            </button>
            <button
              onClick={onSubmit}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Submit Application
            </button>
          </div>

          {/* Next Steps Info */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">Next Steps:</h4>
            <ul className="text-blue-700 text-sm space-y-1">
              <li>• Submit this application for processing</li>
              <li>• Upload required documents</li>
              <li>• Wait for initial review and approval</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Compact Header with Integrated Progress */}
      <div className="flex-shrink-0 border-b border-gray-200 bg-white">
        {state.currentSession ? (
          <div className="p-2">
            {/* Mortgage Application Mode - Special Header */}
            {isMortgageApplication ? (
              <div className="bg-white border-b border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={handleMortgageBack}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                      title="Back to home"
                    >
                      <ArrowLeft size={20} className="text-gray-600" />
                    </button>
                    <div>
                      <h1 className="text-xl font-semibold text-gray-900">
                        Mortgage Application
                      </h1>
                      <p className="text-sm text-gray-600">
                        {state.mortgageApplication.phase === 'data_collection' 
                          ? 'Collecting your information...' 
                          : 'Complete'}
                      </p>
                    </div>
                  </div>
                  
                  {/* Progress indicator */}
                  <div className="flex items-center gap-3">
                    <div className="text-sm text-gray-600">
                      {Math.round((state.mortgageApplication.completionPercentage || 0) * 100)}% Complete
                    </div>
                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 transition-all duration-500"
                        style={{ 
                          width: `${(state.mortgageApplication.completionPercentage || 0) * 100}%` 
                        }}
                      />
                    </div>
                    {state.mortgageApplication.isComplete && (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    )}
                  </div>
                </div>
              </div>
            ) : state.wizardState ? (
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
        ) : isMortgageApplication ? (
          // Mortgage Application (LangGraph) - Inline handling
          <div className="flex-1 flex flex-col min-h-0">
            {!showMortgageApplicationSummary ? (
              <>
                {/* Chat Messages */}
                <div className="flex-1 overflow-y-auto bg-gray-50 min-h-0">
                  <div className="max-w-4xl mx-auto">
                    <MessageList 
                      messages={state.messages}
                      isLoading={state.isLoading}
                    />
                  </div>
                </div>

                {/* Chat Input */}
                <div className="flex-shrink-0 border-t border-gray-200 bg-white p-4">
                  <div className="max-w-4xl mx-auto">
                    <ChatInput 
                      disabled={state.isLoading || state.mortgageApplication.isComplete}
                      placeholder={
                        state.mortgageApplication.isComplete 
                          ? "Application data collection complete!"
                          : "Type your answer..."
                      }
                    />
                  </div>
                </div>
              </>
            ) : (
              /* Application Summary & Submission */
              <ApplicationSummary 
                collectedData={state.mortgageApplication.collectedData || {}}
                onSubmit={async () => {
                  // Extract collected data from the application state
                  const collectedData = {
                    // Get data from messages or state
                    ...state.mortgageApplication.collectedData
                  }
                  
                  // Submit the application
                  const result = await submitMortgageApplication(collectedData)
                  
                  if (result) {
                    console.log('Application submitted successfully:', result.application_id)
                    // Optionally redirect to success page or show next steps
                  }
                }}
                onEdit={() => {
                  // Allow editing by clearing completion status
                  // Update the context to allow continued conversation
                  updateMortgageApplication({ isComplete: false, completionPercentage: 90 })
                }}
              />
            )}

            {/* Status Messages */}
            {state.error && (
              <div className="bg-red-50 border border-red-200 p-3 m-4 rounded-lg">
                <p className="text-red-800 text-sm">{state.error}</p>
              </div>
            )}
          </div>
        ) : (
          // Welcome Screen when no session is active
          <WelcomeScreen />
        )}
      </div>
    </div>
  )
}

export default ChatInterface
