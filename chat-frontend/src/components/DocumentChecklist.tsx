// NOTE: This component is kept for reference but should be REPLACED
// by agent-generated dynamic content in chat responses.
// The agent should use tools to create personalized document checklists
// based on loan type, borrower situation, etc.

import React, { useState } from 'react'
import { 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Download,
  ArrowRight,
  DollarSign,
  CreditCard,
  Home,
  User
} from 'lucide-react'

interface DocumentItem {
  id: string
  name: string
  description: string
  category: 'income' | 'assets' | 'credit' | 'property' | 'identity'
  required: boolean
  examples: string[]
  tips?: string
}

interface DocumentChecklistProps {
  loanType: 'purchase' | 'refinance' | 'first-time'
  onComplete: (checkedItems: string[]) => void
  onStartWithoutChecklist: () => void
}

function DocumentChecklist({ loanType, onComplete, onStartWithoutChecklist }: DocumentChecklistProps) {
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set())
  const [expandedCategory, setExpandedCategory] = useState<string | null>('income')

  const getDocuments = (type: string): DocumentItem[] => {
    const baseDocuments: DocumentItem[] = [
      {
        id: 'photo-id',
        name: 'Government-Issued Photo ID',
        description: 'Valid driver\'s license, passport, or state ID',
        category: 'identity',
        required: true,
        examples: ['Driver\'s License', 'Passport', 'State ID Card'],
        tips: 'Make sure it\'s not expired'
      },
      {
        id: 'pay-stubs',
        name: 'Recent Pay Stubs',
        description: 'Last 2-3 pay stubs showing year-to-date earnings',
        category: 'income',
        required: true,
        examples: ['Monthly salary stubs', 'Bi-weekly pay stubs', 'Commission statements'],
        tips: 'Include all income sources if you have multiple jobs'
      },
      {
        id: 'w2-forms',
        name: 'W-2 Forms',
        description: 'Last 2 years of W-2 tax forms',
        category: 'income',
        required: true,
        examples: ['2023 W-2', '2022 W-2', 'Multiple W-2s if multiple employers'],
        tips: 'Get copies from HR if you don\'t have them'
      },
      {
        id: 'tax-returns',
        name: 'Tax Returns',
        description: 'Complete tax returns for the past 2 years',
        category: 'income',
        required: true,
        examples: ['Form 1040', 'All schedules and attachments', 'State tax returns'],
        tips: 'Include all pages, even if blank'
      },
      {
        id: 'bank-statements',
        name: 'Bank Statements',
        description: 'Last 2-3 months for all accounts',
        category: 'assets',
        required: true,
        examples: ['Checking account statements', 'Savings account statements', 'Money market accounts'],
        tips: 'Include all pages showing transactions'
      },
      {
        id: 'employment-letter',
        name: 'Employment Verification Letter',
        description: 'Letter from HR confirming employment and salary',
        category: 'income',
        required: false,
        examples: ['HR verification letter', 'Salary confirmation', 'Employment contract'],
        tips: 'Ask HR for this in advance - it can take time'
      }
    ]

    if (type === 'first-time') {
      baseDocuments.push({
        id: 'first-time-cert',
        name: 'First-Time Buyer Certificate',
        description: 'Documentation for first-time buyer programs',
        category: 'property',
        required: false,
        examples: ['HUD counseling certificate', 'First-time buyer education completion'],
        tips: 'Check if you qualify for special programs'
      })
    }

    if (type === 'refinance') {
      baseDocuments.push({
        id: 'current-mortgage',
        name: 'Current Mortgage Statement',
        description: 'Most recent mortgage statement',
        category: 'property',
        required: true,
        examples: ['Monthly mortgage statement', 'Payoff quote', 'Property tax bill'],
        tips: 'Get a current payoff quote from your lender'
      })
    }

    return baseDocuments
  }

  const documents = getDocuments(loanType)
  const categories = [
    { id: 'identity', name: 'Identity', icon: <User className="w-5 h-5" />, color: 'blue' },
    { id: 'income', name: 'Income', icon: <DollarSign className="w-5 h-5" />, color: 'green' },
    { id: 'assets', name: 'Assets', icon: <CreditCard className="w-5 h-5" />, color: 'purple' },
    { id: 'property', name: 'Property', icon: <Home className="w-5 h-5" />, color: 'orange' }
  ]

  const toggleCheck = (itemId: string) => {
    const newChecked = new Set(checkedItems)
    if (newChecked.has(itemId)) {
      newChecked.delete(itemId)
    } else {
      newChecked.add(itemId)
    }
    setCheckedItems(newChecked)
  }

  const getCompletionStats = () => {
    const required = documents.filter(d => d.required)
    const optional = documents.filter(d => !d.required)
    const requiredChecked = required.filter(d => checkedItems.has(d.id)).length
    const optionalChecked = optional.filter(d => checkedItems.has(d.id)).length
    
    return {
      required: requiredChecked,
      requiredTotal: required.length,
      optional: optionalChecked,
      optionalTotal: optional.length,
      isComplete: requiredChecked === required.length
    }
  }

  const stats = getCompletionStats()

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText className="w-8 h-8 text-blue-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Document Checklist
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Gather these documents before you start to speed up your application. 
          Don't worry if you don't have everything - you can always add documents later.
        </p>
      </div>

      {/* Progress Bar */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold text-gray-900">Your Progress</h3>
            <p className="text-sm text-gray-600">
              {stats.required}/{stats.requiredTotal} required documents • {stats.optional}/{stats.optionalTotal} optional documents
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-600">
              {Math.round((stats.required / stats.requiredTotal) * 100)}%
            </div>
            <div className="text-sm text-gray-500">Complete</div>
          </div>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(stats.required / stats.requiredTotal) * 100}%` }}
          />
        </div>
      </div>

      {/* Categories */}
      <div className="space-y-4 mb-8">
        {categories.map(category => {
          const categoryDocs = documents.filter(d => d.category === category.id)
          if (categoryDocs.length === 0) return null
          
          const categoryChecked = categoryDocs.filter(d => checkedItems.has(d.id)).length
          const isExpanded = expandedCategory === category.id
          
          return (
            <div key={category.id} className="bg-white rounded-lg border border-gray-200">
              <button
                onClick={() => setExpandedCategory(isExpanded ? null : category.id)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-${category.color}-100 text-${category.color}-600`}>
                    {category.icon}
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{category.name}</h3>
                    <p className="text-sm text-gray-500">
                      {categoryChecked} of {categoryDocs.length} prepared
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {categoryChecked === categoryDocs.length && (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  )}
                  <ArrowRight className={`w-5 h-5 text-gray-400 transition-transform ${
                    isExpanded ? 'rotate-90' : ''
                  }`} />
                </div>
              </button>
              
              {isExpanded && (
                <div className="border-t border-gray-200 p-4 space-y-4">
                  {categoryDocs.map(doc => (
                    <div key={doc.id} className="flex items-start gap-3">
                      <button
                        onClick={() => toggleCheck(doc.id)}
                        className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                          checkedItems.has(doc.id)
                            ? 'bg-blue-600 border-blue-600 text-white'
                            : 'border-gray-300 hover:border-blue-400'
                        }`}
                      >
                        {checkedItems.has(doc.id) && (
                          <CheckCircle className="w-3 h-3" />
                        )}
                      </button>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-gray-900">{doc.name}</h4>
                          {doc.required && (
                            <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">
                              Required
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{doc.description}</p>
                        
                        <div className="text-xs text-gray-500">
                          <p className="font-medium mb-1">Examples:</p>
                          <ul className="list-disc list-inside space-y-1">
                            {doc.examples.map((example, idx) => (
                              <li key={idx}>{example}</li>
                            ))}
                          </ul>
                          {doc.tips && (
                            <div className="mt-2 flex items-start gap-1">
                              <AlertCircle className="w-3 h-3 text-amber-500 mt-0.5 flex-shrink-0" />
                              <p className="text-amber-700">{doc.tips}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={() => onComplete(Array.from(checkedItems))}
          disabled={!stats.isComplete}
          className={`px-6 py-3 rounded-lg font-medium transition-colors ${
            stats.isComplete
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          Start Application with Documents
        </button>
        
        <button
          onClick={onStartWithoutChecklist}
          className="px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Start Now, Add Documents Later
        </button>
      </div>

      {/* Help Section */}
      <div className="mt-8 p-6 bg-gray-50 rounded-lg">
        <div className="flex items-start gap-4">
          <Download className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Helpful Tips</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Scan documents in high quality (at least 300 DPI) for best results</li>
              <li>• Save files with clear names like "John_Smith_W2_2023.pdf"</li>
              <li>• If you're missing a document, don't worry - our system will guide you</li>
              <li>• All documents are securely encrypted and FDIC-compliant</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DocumentChecklist
