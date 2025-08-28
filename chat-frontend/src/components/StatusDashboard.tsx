// NOTE: This component is kept for reference but should be REPLACED
// by agent-generated dynamic status updates in chat responses.
// The agent should use tools to generate real-time application status,
// progress updates, and contextual next steps based on actual data.

import React from 'react'
import { 
  User, 
  Home, 
  DollarSign, 
  FileText, 
  Calendar,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp,
  Download,
  MessageSquare,
  Phone
} from 'lucide-react'
import ApplicationProgress from './ApplicationProgress'

interface ApplicationSummary {
  applicationId: string
  applicantName: string
  loanType: 'purchase' | 'refinance' | 'heloc'
  loanAmount: number
  propertyValue?: number
  applicationDate: string
  expectedCloseDate?: string
  currentStage: string
  status: 'in-progress' | 'approved' | 'conditional' | 'declined' | 'needs-attention'
}

interface DocumentStatus {
  total: number
  uploaded: number
  verified: number
  needsAttention: number
}

interface LoanDetails {
  requestedAmount: number
  estimatedRate?: number
  estimatedPayment?: number
  downPayment?: number
  loanToValue?: number
  debtToIncome?: number
}

interface StatusDashboardProps {
  application: ApplicationSummary
  documents: DocumentStatus
  loanDetails: LoanDetails
  completionPercentage: number
  onContinueChat: () => void
  onViewDocuments: () => void
  onContactLender: () => void
}

function StatusDashboard({
  application,
  documents,
  loanDetails,
  completionPercentage,
  onContinueChat,
  onViewDocuments,
  onContactLender
}: StatusDashboardProps) {

  const getStatusBadge = (status: ApplicationSummary['status']) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'conditional':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'declined':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'needs-attention':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200'
    }
  }

  const getStatusIcon = (status: ApplicationSummary['status']) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'conditional':
        return <Clock className="w-5 h-5 text-yellow-600" />
      case 'declined':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'needs-attention':
        return <AlertCircle className="w-5 h-5 text-orange-600" />
      default:
        return <Clock className="w-5 h-5 text-blue-600" />
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const formatPercent = (value: number) => {
    return `${value.toFixed(2)}%`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Mortgage Application Dashboard</h1>
            <p className="text-gray-600">Application ID: {application.applicationId}</p>
          </div>
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${getStatusBadge(application.status)}`}>
            {getStatusIcon(application.status)}
            <span className="font-medium capitalize">{application.status.replace('-', ' ')}</span>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <User className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Applicant</p>
              <p className="font-medium text-gray-900">{application.applicantName}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Loan Amount</p>
              <p className="font-medium text-gray-900">{formatCurrency(application.loanAmount)}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Applied</p>
              <p className="font-medium text-gray-900">{formatDate(application.applicationDate)}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Home className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Loan Type</p>
              <p className="font-medium text-gray-900 capitalize">{application.loanType}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Progress Section */}
        <ApplicationProgress
          currentStage={application.currentStage}
          stages={[]}
          completionPercentage={completionPercentage}
          applicationId={application.applicationId}
        />

        {/* Quick Stats */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Application Summary</h3>
          
          <div className="space-y-4">
            {/* Document Status */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900">Documents</span>
                <span className="text-sm text-gray-600">
                  {documents.verified}/{documents.total} verified
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${(documents.verified / documents.total) * 100}%` }}
                />
              </div>
              {documents.needsAttention > 0 && (
                <p className="text-sm text-orange-600 mt-2">
                  {documents.needsAttention} document(s) need attention
                </p>
              )}
            </div>

            {/* Loan Details */}
            <div className="grid grid-cols-2 gap-4">
              {loanDetails.estimatedRate && (
                <div>
                  <p className="text-sm text-gray-600">Est. Interest Rate</p>
                  <p className="font-semibold text-gray-900">{formatPercent(loanDetails.estimatedRate)}</p>
                </div>
              )}
              
              {loanDetails.estimatedPayment && (
                <div>
                  <p className="text-sm text-gray-600">Est. Monthly Payment</p>
                  <p className="font-semibold text-gray-900">{formatCurrency(loanDetails.estimatedPayment)}</p>
                </div>
              )}
              
              {loanDetails.loanToValue && (
                <div>
                  <p className="text-sm text-gray-600">Loan-to-Value</p>
                  <p className="font-semibold text-gray-900">{formatPercent(loanDetails.loanToValue)}</p>
                </div>
              )}
              
              {loanDetails.debtToIncome && (
                <div>
                  <p className="text-sm text-gray-600">Debt-to-Income</p>
                  <p className="font-semibold text-gray-900">{formatPercent(loanDetails.debtToIncome)}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Action Items */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Next Steps</h3>
        
        <div className="grid md:grid-cols-3 gap-4">
          <button
            onClick={onContinueChat}
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition-all group"
          >
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
              <MessageSquare className="w-5 h-5 text-blue-600" />
            </div>
            <div className="text-left">
              <h4 className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                Continue Chat
              </h4>
              <p className="text-sm text-gray-600">Ask questions or upload more documents</p>
            </div>
          </button>

          <button
            onClick={onViewDocuments}
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:shadow-sm transition-all group"
          >
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
              <FileText className="w-5 h-5 text-green-600" />
            </div>
            <div className="text-left">
              <h4 className="font-medium text-gray-900 group-hover:text-green-600 transition-colors">
                Review Documents
              </h4>
              <p className="text-sm text-gray-600">View uploaded documents and status</p>
            </div>
          </button>

          <button
            onClick={onContactLender}
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:shadow-sm transition-all group"
          >
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center group-hover:bg-purple-200 transition-colors">
              <Phone className="w-5 h-5 text-purple-600" />
            </div>
            <div className="text-left">
              <h4 className="font-medium text-gray-900 group-hover:text-purple-600 transition-colors">
                Contact Lender
              </h4>
              <p className="text-sm text-gray-600">Speak with a loan officer</p>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-green-900">Bank statements verified</p>
              <p className="text-xs text-green-600">2 hours ago</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
            <FileText className="w-5 h-5 text-blue-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900">W-2 forms uploaded</p>
              <p className="text-xs text-blue-600">4 hours ago</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <User className="w-5 h-5 text-gray-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Application started</p>
              <p className="text-xs text-gray-600">{formatDate(application.applicationDate)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Help & Support */}
      <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200 p-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
            <Phone className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-blue-900 mb-1">Need Help?</h3>
            <p className="text-sm text-blue-700 mb-3">
              Our loan specialists are available to answer questions and guide you through the process.
            </p>
            <div className="flex gap-3">
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                Call (555) 123-LOAN
              </button>
              <button className="px-4 py-2 border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 transition-colors text-sm font-medium">
                Schedule Callback
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatusDashboard
