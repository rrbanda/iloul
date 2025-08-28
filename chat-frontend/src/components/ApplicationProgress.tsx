import React from 'react'
import { 
  CheckCircle, 
  Circle, 
  Clock, 
  AlertCircle,
  FileText,
  CreditCard,
  Home,
  DollarSign,
  Award
} from 'lucide-react'

export interface ApplicationStage {
  id: string
  name: string
  description: string
  status: 'completed' | 'current' | 'pending' | 'blocked'
  icon: React.ReactNode
  estimatedTime?: string
  nextSteps?: string[]
}

interface ApplicationProgressProps {
  currentStage: string
  stages: ApplicationStage[]
  completionPercentage: number
  applicationId?: string
}

function ApplicationProgress({ 
  currentStage, 
  stages, 
  completionPercentage, 
  applicationId 
}: ApplicationProgressProps) {
  
  const defaultStages: ApplicationStage[] = [
    {
      id: 'document-collection',
      name: 'Document Collection',
      description: 'Gather and upload required financial documents',
      status: 'completed',
      icon: <FileText className="w-5 h-5" />,
      estimatedTime: '5-10 minutes',
      nextSteps: ['Upload W-2 forms', 'Upload bank statements', 'Upload pay stubs']
    },
    {
      id: 'verification',
      name: 'Document Verification',
      description: 'AI analysis and validation of submitted documents',
      status: 'current',
      icon: <CheckCircle className="w-5 h-5" />,
      estimatedTime: '2-3 minutes',
      nextSteps: ['Verify income information', 'Check document quality', 'Cross-reference data']
    },
    {
      id: 'credit-check',
      name: 'Credit Assessment',
      description: 'Credit score evaluation and history analysis',
      status: 'pending',
      icon: <CreditCard className="w-5 h-5" />,
      estimatedTime: '1-2 minutes',
      nextSteps: ['Pull credit report', 'Analyze credit history', 'Calculate debt-to-income ratio']
    },
    {
      id: 'underwriting',
      name: 'AI Underwriting',
      description: 'Automated loan qualification and risk assessment',
      status: 'pending',
      icon: <DollarSign className="w-5 h-5" />,
      estimatedTime: '3-5 minutes',
      nextSteps: ['Apply lending guidelines', 'Calculate approval amount', 'Generate decision']
    },
    {
      id: 'approval',
      name: 'Loan Decision',
      description: 'Final approval status and loan terms',
      status: 'pending',
      icon: <Award className="w-5 h-5" />,
      estimatedTime: '1 minute',
      nextSteps: ['Generate approval letter', 'Prepare loan terms', 'Set up next steps']
    }
  ]

  const displayStages = stages.length > 0 ? stages : defaultStages
  const currentStageIndex = displayStages.findIndex(stage => stage.id === currentStage)
  const currentStageData = displayStages[currentStageIndex]

  const getStatusIcon = (status: ApplicationStage['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />
      case 'current':
        return <Clock className="w-6 h-6 text-blue-500 animate-pulse" />
      case 'blocked':
        return <AlertCircle className="w-6 h-6 text-red-500" />
      default:
        return <Circle className="w-6 h-6 text-gray-300" />
    }
  }

  const getStatusColor = (status: ApplicationStage['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'current':
        return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'blocked':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-gray-500 bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Application Progress</h3>
          {applicationId && (
            <p className="text-sm text-gray-500">Application ID: {applicationId}</p>
          )}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">{completionPercentage}%</div>
          <div className="text-sm text-gray-500">Complete</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>

      {/* Current Stage Highlight */}
      {currentStageData && (
        <div className={`p-4 rounded-lg border mb-6 ${getStatusColor(currentStageData.status)}`}>
          <div className="flex items-center gap-3 mb-2">
            <div className="flex-shrink-0">
              {currentStageData.icon}
            </div>
            <div>
              <h4 className="font-medium">{currentStageData.name}</h4>
              <p className="text-sm opacity-75">{currentStageData.description}</p>
            </div>
            <div className="ml-auto">
              {getStatusIcon(currentStageData.status)}
            </div>
          </div>
          
          {currentStageData.estimatedTime && (
            <div className="text-sm opacity-75 mb-2">
              ⏱️ Estimated time: {currentStageData.estimatedTime}
            </div>
          )}
          
          {currentStageData.nextSteps && currentStageData.nextSteps.length > 0 && (
            <div className="text-sm">
              <p className="font-medium mb-1">Next steps:</p>
              <ul className="list-disc list-inside opacity-75 space-y-1">
                {currentStageData.nextSteps.map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* All Stages List */}
      <div className="space-y-4">
        {displayStages.map((stage, index) => (
          <div key={stage.id} className="flex items-center gap-4">
            {/* Stage Number & Icon */}
            <div className="flex-shrink-0 relative">
              <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center ${
                stage.status === 'completed' 
                  ? 'bg-green-50 border-green-200 text-green-600'
                  : stage.status === 'current'
                  ? 'bg-blue-50 border-blue-200 text-blue-600'
                  : stage.status === 'blocked'
                  ? 'bg-red-50 border-red-200 text-red-600'
                  : 'bg-gray-50 border-gray-200 text-gray-400'
              }`}>
                {stage.status === 'completed' ? (
                  <CheckCircle className="w-5 h-5" />
                ) : stage.status === 'current' ? (
                  <Clock className="w-5 h-5" />
                ) : stage.status === 'blocked' ? (
                  <AlertCircle className="w-5 h-5" />
                ) : (
                  <span className="text-sm font-medium">{index + 1}</span>
                )}
              </div>
              
              {/* Connector Line */}
              {index < displayStages.length - 1 && (
                <div className={`absolute top-10 left-1/2 transform -translate-x-1/2 w-0.5 h-6 ${
                  stage.status === 'completed' ? 'bg-green-200' : 'bg-gray-200'
                }`} />
              )}
            </div>

            {/* Stage Content */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h4 className={`font-medium ${
                  stage.status === 'current' ? 'text-blue-900' : 
                  stage.status === 'completed' ? 'text-green-900' :
                  stage.status === 'blocked' ? 'text-red-900' :
                  'text-gray-600'
                }`}>
                  {stage.name}
                </h4>
                
                {stage.status === 'current' && (
                  <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                    In Progress
                  </span>
                )}
                
                {stage.status === 'blocked' && (
                  <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">
                    Needs Attention
                  </span>
                )}
              </div>
              
              <p className="text-sm text-gray-600">{stage.description}</p>
              
              {stage.estimatedTime && stage.status === 'pending' && (
                <p className="text-xs text-gray-500 mt-1">
                  Est. {stage.estimatedTime}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Circle className="w-4 h-4" />
          <span>
            {displayStages.filter(s => s.status === 'completed').length} of {displayStages.length} stages completed
          </span>
        </div>
      </div>
    </div>
  )
}

export default ApplicationProgress
