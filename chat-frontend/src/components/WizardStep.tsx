import React, { useEffect } from 'react'
import { ArrowLeft, ArrowRight, CheckCircle, DollarSign, Home, FileText, Calculator, Clock } from 'lucide-react'
import { useChat } from '../context/ChatContext'
import { WizardStep as WizardStepType, WizardStepData } from '../types/wizard'
import QuickPrompts from './QuickPrompts'

interface WizardStepProps {
  step: WizardStepType
  onNext: () => void
  onPrevious: () => void
  isFirst: boolean
  isLast: boolean
  onPreFillMessage?: (text: string) => void
}

function WizardStep({ step, onNext, onPrevious, isFirst, isLast, onPreFillMessage }: WizardStepProps) {
  const { sendMessage, state, updateWizardStep, completeWizardStep } = useChat()

  // Auto-complete step when we have enough data (disabled for now - user-driven progression)
  /*
  useEffect(() => {
    if (step.isActive && hasRequiredData()) {
      const timer = setTimeout(() => {
        completeWizardStep(step.id)
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [step.isActive, state.wizardState?.collectedData[step.id], completeWizardStep, step.id])
  */

  const hasRequiredData = (): boolean => {
    const collectedData = state.wizardState?.collectedData[step.id]
    if (!collectedData) return false

    switch (step.id) {
      case 'situation':
        // Need at least income and location to progress
        return !!(collectedData.income && collectedData.location)
      case 'finances':
        return !!(collectedData.downPayment)
      case 'documents':
        return !!(collectedData.uploadedFiles && collectedData.uploadedFiles.length > 0)
      default:
        return false
    }
  }

  const getStepIcon = () => {
    switch (step.id) {
      case 'situation':
        return <Home className="w-6 h-6" />
      case 'finances':
        return <DollarSign className="w-6 h-6" />
      case 'documents':
        return <FileText className="w-6 h-6" />
      case 'loan_options':
        return <Calculator className="w-6 h-6" />
      case 'application':
        return <CheckCircle className="w-6 h-6" />
      // Mortgage Application specific icons
      case 'applicant_info':
        return <Home className="w-6 h-6" />
      case 'financial_details':
        return <DollarSign className="w-6 h-6" />
      case 'property_info':
        return <Home className="w-6 h-6" />
      case 'loan_details':
        return <Calculator className="w-6 h-6" />
      case 'submit_application':
        return <CheckCircle className="w-6 h-6" />
      default:
        return <FileText className="w-6 h-6" />
    }
  }

  const getQuickActions = () => {
    switch (step.id) {
      case 'situation':
        return [
          {
            text: 'What income do I need to qualify?',
            action: () => onPreFillMessage?.('What annual household income do I need to qualify for a mortgage?')
          },
          {
            text: 'How much house can I afford?',
            action: () => onPreFillMessage?.('Based on my income and expenses, how much house can I afford?')
          },
          {
            text: 'What credit score do I need?',
            action: () => onPreFillMessage?.('What minimum credit score do I need for different loan types?')
          },
          {
            text: 'First-time buyer programs?',
            action: () => onPreFillMessage?.('What special programs are available for first-time home buyers in my area?')
          }
        ]

      case 'finances':
        return [
          {
            text: 'How do I calculate debt-to-income?',
            action: () => onPreFillMessage?.('How do I calculate my debt-to-income ratio? What should I include?')
          },
          {
            text: 'What down payment do I need?',
            action: () => onPreFillMessage?.('What is the minimum down payment I need, and are there low down payment options?')
          },
          {
            text: 'What\'s my maximum loan amount?',
            action: () => onPreFillMessage?.('Based on my income, what\'s the maximum loan amount I could qualify for?')
          },
          {
            text: 'Monthly payment estimates?',
            action: () => onPreFillMessage?.('Can you show me estimated monthly payments for different loan amounts and rates?')
          }
        ]

      case 'documents':
        return [
          {
            text: 'What documents do I need?',
            action: () => onPreFillMessage?.('What specific documents do I need to provide for my mortgage application?')
          },
          {
            text: 'Upload my pay stubs',
            action: () => onPreFillMessage?.('I\'m ready to upload my pay stubs. What should I know before uploading?')
          },
          {
            text: 'Upload bank statements',
            action: () => onPreFillMessage?.('I have my bank statements ready. How many months do I need?')
          },
          {
            text: 'Check document requirements',
            action: () => onPreFillMessage?.('Can you verify if I have all the required documents for my loan type?')
          }
        ]

      // Mortgage Application specific steps
      case 'applicant_info':
        return [
          {
            text: 'Help with personal information',
            action: () => onPreFillMessage?.('What personal information do I need to provide for my mortgage application?')
          },
          {
            text: 'Employment verification help',
            action: () => onPreFillMessage?.('How do I properly document my employment history for the application?')
          },
          {
            text: 'Social Security questions',
            action: () => onPreFillMessage?.('What do I need to know about providing my Social Security number?')
          },
          {
            text: 'Address history help',
            action: () => onPreFillMessage?.('How far back do I need to provide my address history?')
          }
        ]

      case 'financial_details':
        return [
          {
            text: 'Income documentation',
            action: () => onPreFillMessage?.('How should I document all my sources of income for the application?')
          },
          {
            text: 'Asset verification',
            action: () => onPreFillMessage?.('What assets do I need to disclose and how should I document them?')
          },
          {
            text: 'Debt obligations',
            action: () => onPreFillMessage?.('What debts and monthly obligations do I need to list?')
          },
          {
            text: 'Tax return questions',
            action: () => onPreFillMessage?.('How many years of tax returns do I need and what should I know about them?')
          }
        ]

      case 'property_info':
        return [
          {
            text: 'Property details help',
            action: () => onPreFillMessage?.('What property information is required for the mortgage application?')
          },
          {
            text: 'Purchase contract',
            action: () => onPreFillMessage?.('What details from my purchase contract are needed for the application?')
          },
          {
            text: 'Property type questions',
            action: () => onPreFillMessage?.('How does my property type affect my mortgage application?')
          },
          {
            text: 'Down payment source',
            action: () => onPreFillMessage?.('How do I properly document the source of my down payment?')
          }
        ]

      case 'loan_details':
        return [
          {
            text: 'Loan program selection',
            action: () => onPreFillMessage?.('Help me choose the right loan program for my situation.')
          },
          {
            text: 'Interest rate options',
            action: () => onPreFillMessage?.('What are my interest rate options and how do I choose?')
          },
          {
            text: 'Loan term decisions',
            action: () => onPreFillMessage?.('Should I choose a 15-year or 30-year mortgage term?')
          },
          {
            text: 'PMI and insurance',
            action: () => onPreFillMessage?.('What do I need to know about PMI and homeowners insurance?')
          }
        ]

      case 'submit_application':
        return [
          {
            text: 'Review my application',
            action: () => onPreFillMessage?.('Can you help me review my application before submitting?')
          },
          {
            text: 'Missing information check',
            action: () => onPreFillMessage?.('What should I check to make sure nothing is missing from my application?')
          },
          {
            text: 'Submission timeline',
            action: () => onPreFillMessage?.('What happens after I submit my application and what are the next steps?')
          },
          {
            text: 'Application fees',
            action: () => onPreFillMessage?.('What fees should I expect when submitting my mortgage application?')
          }
        ]

      default:
        return []
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Step Header */}
      <div className="flex-shrink-0 border-b border-gray-200 p-6 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              step.isCompleted ? 'bg-green-100 text-green-600' : 
              step.isActive ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
            }`}>
              {step.isCompleted ? <CheckCircle className="w-6 h-6" /> : getStepIcon()}
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">{step.title}</h2>
              <p className="text-gray-600">{step.description}</p>
            </div>
          </div>
          
          {step.isCompleted && (
            <div className="text-green-600 font-medium">
              ✓ Completed
            </div>
          )}
        </div>

        {/* Progress Summary */}
        {state.wizardState?.collectedData[step.id] && (
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-gray-900">Information Collected:</h3>
              {step.isActive && hasRequiredData() && (
                <button
                  onClick={() => completeWizardStep(step.id)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                >
                  Continue to Next Step →
                </button>
              )}
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {Object.entries(state.wizardState.collectedData[step.id] || {}).map(([key, value]) => (
                <div key={key} className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span className="text-gray-600 capitalize">{key}:</span>
                  <span className="font-medium">{String(value)}</span>
                </div>
              ))}
            </div>
            {step.isActive && hasRequiredData() && (
              <div className="mt-3 text-xs text-gray-500 text-center">
                Great! You've provided the key information. The next step will unlock automatically in a moment, or click Continue above.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Step Instructions and Quick Actions - COLLAPSIBLE */}
      {step.isActive && (
        <div className="flex-shrink-0 border-b border-gray-200 bg-gray-50">
          {/* Clean Quick Questions Section */}
          <div className="p-3 bg-blue-50">
            <div className="text-center mb-3">
              <span className="text-sm font-medium text-blue-700">💬 Quick questions to get started:</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {getQuickActions().map((action, index) => (
                <button
                  key={index}
                  onClick={action.action}
                  className="flex items-center gap-2 p-2 text-left border border-blue-200 rounded-lg hover:border-blue-300 hover:bg-blue-100 transition-all group text-sm bg-white"
                >
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                    <ArrowRight className="w-3 h-3" />
                  </div>
                  <span className="text-gray-700 group-hover:text-blue-700 transition-colors text-xs">
                    {action.text}
                  </span>
                </button>
              ))}
            </div>
            <div className="mt-2 text-xs text-center text-blue-600">
              💡 Click any question above, or share your information directly in the chat below
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      {(step.isCompleted || !step.isActive) && (
        <div className="flex-shrink-0 border-b border-gray-200 p-4 bg-white">
          <div className="flex items-center justify-between">
            <button
              onClick={onPrevious}
              disabled={isFirst}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Previous Step
            </button>
            
            <div className="text-sm text-gray-500">
              Step {step.progress}% Complete
            </div>
            
            <button
              onClick={onNext}
              disabled={isLast || !step.isCompleted}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next Step
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default WizardStep
