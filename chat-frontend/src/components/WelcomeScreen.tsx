import React from 'react'
import { 
  MessageSquare, 
  FileText, 
  HelpCircle, 
  Calculator, 
  CheckCircle, 
  Clock,
  ArrowRight 
} from 'lucide-react'
import { useChat } from '../context/ChatContext'

function WelcomeScreen() {
  const { startNewSession } = useChat()

  const features = [
    {
      icon: <FileText className="w-6 h-6" />,
      title: "Document Analysis",
      description: "Upload and analyze mortgage documents instantly with AI-powered processing",
      action: () => startNewSession("Document Analysis Session", "Document Analysis")
    },
    {
      icon: <Calculator className="w-6 h-6" />,
      title: "Qualification Assessment", 
      description: "Get insights on loan qualification based on your financial documents",
      action: () => startNewSession("Qualification Assessment", "Qualification Assessment")
    },
    {
      icon: <CheckCircle className="w-6 h-6" />,
      title: "Compliance Checking",
      description: "Ensure all requirements are met with automated compliance validation",
      action: () => startNewSession("Compliance Checking", "Compliance Checking")
    },
    {
      icon: <Clock className="w-6 h-6" />,
      title: "Real-time Processing",
      description: "Get instant feedback and recommendations as you submit information",
      action: () => startNewSession("Real-time Processing Session", "Real-time Processing")
    }
  ]

  const quickActions = [
    {
      title: "First-Time Home Buyer",
      description: "New to buying a home? Get personalized guidance on loan options, down payments, and the application process.",
      action: () => startNewSession("First-Time Buyer Consultation", "First-Time Buyer Consultation"),
      badge: "Popular"
    },
    {
      title: "Check Pre-Approval Eligibility", 
      description: "Upload your financial documents and get an instant pre-approval estimate based on your income and credit.",
      action: () => startNewSession("Pre-Approval Check", "Pre-Approval Check"),
      badge: "Fast"
    },
    {
      title: "Refinance Existing Loan",
      description: "See if you qualify for better rates or cash-out refinancing on your current home.",
      action: () => startNewSession("Refinance Consultation", "Refinance Consultation"),
      badge: null
    }
  ]

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-4xl mx-auto p-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <MessageSquare className="w-8 h-8 text-blue-600" />
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Apply for Your Home Loan
          </h1>
          
          <p className="text-lg text-gray-600 mb-4 max-w-2xl mx-auto">
            Get pre-approved in minutes, not weeks. Our AI-powered system analyzes your documents instantly 
            and guides you through every step of your mortgage application.
          </p>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 max-w-xl mx-auto">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="font-medium text-blue-900">Ready to get started?</span>
            </div>
            <p className="text-blue-800 text-sm">
              Most applications take 10-15 minutes. Have your financial documents ready for the best experience.
            </p>
          </div>
          
          <div className="flex items-center justify-center gap-6 text-sm text-gray-500 mb-8">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Secure & Compliant</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Instant Analysis</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>24/7 Available</span>
            </div>
          </div>

          <button
            onClick={() => startNewSession("General Mortgage Consultation", "General")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-lg font-medium"
          >
            Start Chatting
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {features.map((feature, index) => (
            <button
              key={index}
              onClick={feature.action}
              className="p-6 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all group bg-white cursor-pointer"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600 group-hover:bg-blue-100 transition-colors">
                  {feature.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">{feature.title}</h3>
                  <p className="text-gray-600 text-sm">{feature.description}</p>
                  <div className="flex items-center text-blue-600 text-sm font-medium mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    Start Session
                    <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="border-t border-gray-200 pt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
            What would you like to do?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={action.action}
                className="relative p-6 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all group bg-white"
              >
                {action.badge && (
                  <div className="absolute top-3 right-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      action.badge === 'Popular' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-blue-100 text-blue-700'
                    }`}>
                      {action.badge}
                    </span>
                  </div>
                )}
                <h3 className="font-semibold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors pr-16">
                  {action.title}
                </h3>
                <p className="text-sm text-gray-600 mb-4 leading-relaxed">{action.description}</p>
                <div className="flex items-center text-blue-600 text-sm font-medium">
                  Get Started
                  <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Help Section */}
        <div className="mt-12 p-6 bg-gray-50 rounded-lg">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <HelpCircle className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Common Questions from Borrowers</h3>
              <p className="text-gray-600 text-sm mb-3">
                Get instant answers to questions like these:
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• "How much house can I afford with my $75,000 salary?"</li>
                <li>• "What's the minimum down payment for a first-time buyer?"</li>
                <li>• "My credit score is 650 - what loan options do I have?"</li>
                <li>• "Can I qualify with 1099 income from freelance work?"</li>
                <li>• "What's the difference between conventional and FHA loans?"</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            Powered by AI-driven mortgage processing • 
            Secure document handling • 
            Real-time analysis
          </p>
        </div>
      </div>
    </div>
  )
}

export default WelcomeScreen
