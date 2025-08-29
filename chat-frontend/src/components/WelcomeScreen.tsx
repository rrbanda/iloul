import React from 'react'
import { 
  MessageSquare, 
  FileText, 
  HelpCircle, 
  Calculator, 
  CheckCircle, 
  Clock,
  ArrowRight,
  Home,
  CreditCard,
  TrendingUp 
} from 'lucide-react'
import { useChat } from '../context/ChatContext'
import { WizardType } from '../types/wizard'

function WelcomeScreen() {
  const { startWizard, startNewSession } = useChat()

  const wizardOptions = [
    {
      wizardType: 'first_time_buyer' as WizardType,
      icon: <Home className="w-8 h-8" />,
      title: "First-Time Home Buyer Guide",
      description: "Get personalized guidance and preparation for your home buying journey",
      features: ["Affordability analysis", "Loan option education", "Document preparation", "Process roadmap"],
      badge: "Most Popular",
      badgeColor: "bg-green-100 text-green-700"
    },
    {
      wizardType: 'pre_approval' as WizardType,
      icon: <Calculator className="w-8 h-8" />,
      title: "Pre-Approval Preparation",
      description: "Prepare for pre-approval with financial analysis and document guidance",
      features: ["Financial readiness check", "Credit score guidance", "Document preparation", "Lender recommendations"],
      badge: "Fast Track",
      badgeColor: "bg-blue-100 text-blue-700"
    },
    {
      wizardType: 'mortgage_application' as WizardType,
      icon: <CheckCircle className="w-8 h-8" />,
      title: "Apply for Mortgage",
      description: "Complete your mortgage application with step-by-step guidance",
      features: ["Application assistance", "Document upload", "Progress tracking", "Lender matching"],
      badge: "Apply Now",
      badgeColor: "bg-orange-100 text-orange-700"
    },
    {
      wizardType: 'refinance' as WizardType,
      icon: <TrendingUp className="w-8 h-8" />,
      title: "Refinance Analysis",
      description: "Analyze if refinancing makes sense for your situation",
      features: ["Rate comparison", "Break-even analysis", "Cash-out options", "Savings calculator"],
      badge: null,
      badgeColor: ""
    }
  ]

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-7xl mx-auto p-6 min-h-full flex flex-col justify-center">
        {/* Hero Section - Larger but Efficient */}
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <MessageSquare className="w-10 h-10 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            What brings you here today?
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Choose your path below. I'll guide you step-by-step with personalized help and AI analysis.
          </p>
        </div>

        {/* Wizard Options - Responsive Grid for 4 Cards */}
        <div className="grid xl:grid-cols-4 lg:grid-cols-2 md:grid-cols-2 grid-cols-1 gap-4 mb-8">
          {wizardOptions.map((option, index) => (
            <button
              key={index}
              onClick={() => startWizard(option.wizardType)}
              className="relative p-4 text-left border-2 border-gray-200 rounded-xl hover:border-blue-300 hover:shadow-xl transition-all group bg-white h-full"
            >
              {option.badge && (
                <div className="absolute top-2 right-2">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${option.badgeColor}`}>
                    {option.badge}
                  </span>
                </div>
              )}
              
              <div className="flex flex-col h-full">
                <div className="flex items-start gap-3 mb-3">
                  <div className="flex-shrink-0 w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600 group-hover:bg-blue-100 transition-colors">
                    {React.cloneElement(option.icon, { className: "w-6 h-6" })}
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors leading-tight pr-20">
                    {option.title}
                  </h3>
                </div>
                
                <p className="text-gray-600 mb-4 leading-snug flex-grow text-sm">
                  {option.description}
                </p>
                
                <div className="space-y-1.5 mb-4">
                  {option.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-center gap-2 text-xs text-gray-600">
                      <CheckCircle className="w-3 h-3 text-green-500 flex-shrink-0" />
                      <span className="leading-tight">{feature}</span>
                    </div>
                  ))}
                </div>
                
                <div className="flex items-center text-blue-600 font-semibold group-hover:translate-x-2 transition-transform mt-auto text-sm">
                  Start This Journey
                  <ArrowRight className="w-4 h-4 ml-2" />
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Alternative Options - Spacious */}
        <div className="border-t border-gray-200 pt-8">
          <div className="text-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Prefer to explore first?
            </h2>
            <p className="text-gray-600">
              Start with general questions or browse information before committing to a specific path.
            </p>
          </div>
          
          <div className="flex items-center justify-center">
            <button
              onClick={() => startNewSession("General Mortgage Consultation", "General")}
              className="inline-flex items-center gap-3 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <MessageSquare className="w-5 h-5" />
              Just Ask Questions
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            Powered by AI • Secure & Compliant • Real-time Analysis
          </p>
        </div>
      </div>
    </div>
  )
}

export default WelcomeScreen
