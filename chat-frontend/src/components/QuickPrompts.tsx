import React from 'react'
import { 
  DollarSign, 
  FileText, 
  CreditCard, 
  Home, 
  Calculator,
  TrendingUp,
  HelpCircle,
  Upload,
  CheckCircle,
  Clock
} from 'lucide-react'
import { QuickPrompt } from '../types/chat'
import { useChat } from '../context/ChatContext'

interface QuickPromptsProps {
  sessionContext?: string
  onPromptClick?: (prompt: string) => void
}

function QuickPrompts({ sessionContext, onPromptClick }: QuickPromptsProps) {
  const { sendMessage } = useChat()

  // Define contextual prompts based on session context
  const getContextualPrompts = (context?: string): QuickPrompt[] => {
    switch (context) {
      case 'First-Time Buyer Consultation':
        return [
          {
            id: 'budget-calc',
            text: 'What can I afford with my salary?',
            icon: '💰',
            category: 'budget'
          },
          {
            id: 'loan-types',
            text: 'Explain FHA vs Conventional loans',
            icon: '🏠',
            category: 'education'
          },
          {
            id: 'down-payment',
            text: 'What\'s the minimum down payment?',
            icon: '💳',
            category: 'requirements'
          },
          {
            id: 'first-time-programs',
            text: 'What first-time buyer programs exist?',
            icon: '🎯',
            category: 'programs'
          },
          {
            id: 'credit-requirements',
            text: 'What credit score do I need?',
            icon: '📊',
            category: 'qualification'
          },
          {
            id: 'docs-needed',
            text: 'What documents will I need?',
            icon: '📄',
            category: 'preparation'
          }
        ]

      case 'Pre-Approval Check':
        return [
          {
            id: 'upload-docs',
            text: 'Upload my financial documents',
            icon: '📤',
            category: 'action'
          },
          {
            id: 'income-analysis',
            text: 'Analyze my income and employment',
            icon: '💼',
            category: 'analysis'
          },
          {
            id: 'debt-ratio',
            text: 'Calculate my debt-to-income ratio',
            icon: '📊',
            category: 'calculation'
          },
          {
            id: 'max-loan',
            text: 'What\'s my maximum loan amount?',
            icon: '🎯',
            category: 'calculation'
          },
          {
            id: 'credit-pull',
            text: 'Run my credit analysis',
            icon: '📈',
            category: 'verification'
          },
          {
            id: 'rates-terms',
            text: 'Show me current rates and terms',
            icon: '📋',
            category: 'information'
          }
        ]

      case 'Refinance Consultation':
        return [
          {
            id: 'current-loan',
            text: 'Analyze my current mortgage',
            icon: '🏡',
            category: 'analysis'
          },
          {
            id: 'rate-comparison',
            text: 'Compare with current market rates',
            icon: '📊',
            category: 'comparison'
          },
          {
            id: 'cash-out',
            text: 'Calculate cash-out refinance options',
            icon: '💰',
            category: 'calculation'
          },
          {
            id: 'break-even',
            text: 'When will I break even on costs?',
            icon: '⚖️',
            category: 'analysis'
          },
          {
            id: 'closing-costs',
            text: 'Estimate my closing costs',
            icon: '💳',
            category: 'costs'
          },
          {
            id: 'refinance-docs',
            text: 'What documents do I need?',
            icon: '📄',
            category: 'preparation'
          }
        ]

      case 'Document Analysis':
        return [
          {
            id: 'upload-docs',
            text: 'Upload my mortgage documents',
            icon: '📎',
            category: 'upload'
          },
          {
            id: 'analyze-income',
            text: 'Analyze my income documents',
            icon: '💼',
            category: 'analysis'
          },
          {
            id: 'bank-statements',
            text: 'Review my bank statements',
            icon: '🏦',
            category: 'verification'
          },
          {
            id: 'tax-returns',
            text: 'Process my tax returns',
            icon: '📊',
            category: 'income'
          },
          {
            id: 'employment-verification',
            text: 'Verify my employment letter',
            icon: '',
            category: 'verification'
          },
          {
            id: 'document-status',
            text: 'Check document processing status',
            icon: '⏱️',
            category: 'status'
          }
        ]

      case 'Qualification Assessment':
        return [
          {
            id: 'debt-to-income',
            text: 'Calculate my debt-to-income ratio',
            icon: '🧮',
            category: 'calculation'
          },
          {
            id: 'loan-amount',
            text: 'How much can I borrow?',
            icon: '💰',
            category: 'qualification'
          },
          {
            id: 'credit-impact',
            text: 'How does my credit score affect options?',
            icon: '📈',
            category: 'credit'
          },
          {
            id: 'income-qualification',
            text: 'Do I qualify with my current income?',
            icon: '💼',
            category: 'income'
          },
          {
            id: 'loan-programs',
            text: 'What loan programs am I eligible for?',
            icon: '🎯',
            category: 'programs'
          },
          {
            id: 'pre-approval',
            text: 'Get my pre-approval estimate',
            icon: '',
            category: 'approval'
          }
        ]

      case 'Compliance Checking':
        return [
          {
            id: 'regulatory-requirements',
            text: 'What regulations apply to my loan?',
            icon: '⚖️',
            category: 'regulations'
          },
          {
            id: 'disclosure-requirements',
            text: 'Review required disclosures',
            icon: '📋',
            category: 'disclosures'
          },
          {
            id: 'qm-compliance',
            text: 'Check Qualified Mortgage compliance',
            icon: '',
            category: 'compliance'
          },
          {
            id: 'ability-to-repay',
            text: 'Verify ability to repay standards',
            icon: '🔍',
            category: 'verification'
          },
          {
            id: 'fair-lending',
            text: 'Ensure fair lending compliance',
            icon: '⚖️',
            category: 'fairness'
          },
          {
            id: 'audit-trail',
            text: 'Review compliance audit trail',
            icon: '📄',
            category: 'documentation'
          }
        ]

      case 'Real-time Processing':
        return [
          {
            id: 'processing-status',
            text: 'Check my application status',
            icon: '⏳',
            category: 'status'
          },
          {
            id: 'instant-feedback',
            text: 'Get instant document feedback',
            icon: '⚡',
            category: 'feedback'
          },
          {
            id: 'missing-items',
            text: 'What documents am I missing?',
            icon: '❓',
            category: 'requirements'
          },
          {
            id: 'next-steps',
            text: 'What are my next steps?',
            icon: '👣',
            category: 'guidance'
          },
          {
            id: 'real-time-updates',
            text: 'Enable real-time notifications',
            icon: '🔔',
            category: 'notifications'
          },
          {
            id: 'live-assistance',
            text: 'Get live processing assistance',
            icon: '💬',
            category: 'support'
          }
        ]

      default:
        // General mortgage prompts
        return [
          {
            id: 'get-started',
            text: 'I want to apply for a mortgage',
            icon: '🏠',
            category: 'start'
          },
          {
            id: 'check-rates',
            text: 'What are current mortgage rates?',
            icon: '📈',
            category: 'information'
          },
          {
            id: 'affordability',
            text: 'How much house can I afford?',
            icon: '💰',
            category: 'calculation'
          },
          {
            id: 'requirements',
            text: 'What are the loan requirements?',
            icon: '📋',
            category: 'requirements'
          },
          {
            id: 'process-help',
            text: 'Explain the mortgage process',
            icon: '❓',
            category: 'education'
          },
          {
            id: 'upload-start',
            text: 'Upload documents to get started',
            icon: '📤',
            category: 'action'
          }
        ]
    }
  }

  const prompts = getContextualPrompts(sessionContext)

  const handlePromptClick = async (prompt: QuickPrompt) => {
    const message = prompt.text
    
    if (onPromptClick) {
      onPromptClick(message)
    } else {
      await sendMessage(message)
    }
  }

  const getIconComponent = (emoji: string) => {
    // Map emojis to Lucide icons for consistency
    const iconMap: Record<string, React.ReactNode> = {
      '💰': <DollarSign className="w-4 h-4" />,
      '🏠': <Home className="w-4 h-4" />,
      '💳': <CreditCard className="w-4 h-4" />,
      '📄': <FileText className="w-4 h-4" />,
      '📊': <TrendingUp className="w-4 h-4" />,
      '📤': <Upload className="w-4 h-4" />,
      '📈': <TrendingUp className="w-4 h-4" />,
      '💼': <Calculator className="w-4 h-4" />,
      '🎯': <CheckCircle className="w-4 h-4" />,
      '❓': <HelpCircle className="w-4 h-4" />,
      '📋': <FileText className="w-4 h-4" />,
      '🏡': <Home className="w-4 h-4" />,
      '⚖️': <Calculator className="w-4 h-4" />
    }
    
    return iconMap[emoji] || <span className="text-sm">{emoji}</span>
  }

  if (prompts.length === 0) return null

  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 mb-3">
        <Clock className="w-4 h-4 text-gray-500" />
        <span className="text-sm font-medium text-gray-700">Quick Actions</span>
      </div>
      
      <div className="grid grid-cols-2 gap-2">
        {prompts.map((prompt) => (
          <button
            key={prompt.id}
            onClick={() => handlePromptClick(prompt)}
            className="flex items-center gap-2 p-3 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all group text-sm"
          >
            <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center group-hover:bg-blue-100 transition-colors">
              {getIconComponent(prompt.icon)}
            </div>
            <span className="text-gray-700 group-hover:text-blue-700 transition-colors">
              {prompt.text}
            </span>
          </button>
        ))}
      </div>
      
      <div className="mt-3 text-xs text-gray-500 text-center">
        Click any suggestion above or type your own question
      </div>
    </div>
  )
}

export default QuickPrompts
