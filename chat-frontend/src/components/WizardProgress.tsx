import React from 'react'
import { CheckCircle, Circle } from 'lucide-react'
import { WizardState } from '../types/wizard'

interface WizardProgressProps {
  wizardState: WizardState
  onStepClick?: (stepId: string) => void
}

function WizardProgress({ wizardState, onStepClick }: WizardProgressProps) {
  const { steps, currentStepId, completionPercentage } = wizardState

  return (
    <div className="bg-white border-b border-gray-200 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{completionPercentage}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const canClick = step.isCompleted || step.isActive
            return (
              <div key={step.id} className="flex items-center">
                {/* Step Circle */}
                <button
                  onClick={() => canClick && onStepClick?.(step.id)}
                  disabled={!canClick}
                  className={`flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all ${
                    step.isCompleted 
                      ? 'bg-green-100 border-green-500 text-green-600 hover:bg-green-200 cursor-pointer' 
                      : step.isActive
                        ? 'bg-blue-100 border-blue-500 text-blue-600 hover:bg-blue-200 cursor-pointer'
                        : 'bg-gray-100 border-gray-300 text-gray-400 cursor-not-allowed'
                  }`}
                  title={canClick ? `Go to ${step.title}` : `Complete previous steps to unlock ${step.title}`}
                >
                  {step.isCompleted ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <span className="text-xs font-semibold">{index + 1}</span>
                  )}
                </button>

                {/* Step Label */}
                <div className="ml-2 hidden sm:block">
                  <button
                    onClick={() => canClick && onStepClick?.(step.id)}
                    disabled={!canClick}
                    className={`text-xs font-medium transition-colors ${
                      step.isCompleted 
                        ? 'text-green-600 hover:text-green-700 cursor-pointer' 
                        : step.isActive
                          ? 'text-blue-600 hover:text-blue-700 cursor-pointer'
                          : 'text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    {step.title}
                  </button>
                </div>

                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div className={`hidden md:block ml-4 mr-4 flex-1 h-0.5 ${
                    step.isCompleted ? 'bg-green-300' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            )
          })}
        </div>

        {/* Current Step Description */}
        <div className="mt-4 text-center">
          {steps.find(s => s.isActive) && (
            <div className="text-sm text-gray-600">
              <span className="font-medium">Current:</span> {steps.find(s => s.isActive)?.description}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default WizardProgress
