export interface WizardStep {
  id: string
  title: string
  description: string
  progress: number // 0-100
  isCompleted: boolean
  isActive: boolean
  data?: Record<string, any>
}

export interface WizardState {
  wizardType: WizardType
  currentStepId: string
  steps: WizardStep[]
  collectedData: Record<string, any>
  completionPercentage: number
  isCompleted: boolean
}

export type WizardType = 
  | 'first_time_buyer'
  | 'pre_approval'
  | 'mortgage_application'
  | 'refinance'
  | 'general'
  | null

export interface WizardDefinition {
  type: WizardType
  title: string
  description: string
  steps: Omit<WizardStep, 'isCompleted' | 'isActive'>[]
}

// Wizard step definitions
export const WIZARD_DEFINITIONS: Record<string, WizardDefinition> = {
  first_time_buyer: {
    type: 'first_time_buyer',
    title: 'First-Time Home Buyer',
    description: 'Get guided help for your first home purchase',
    steps: [
      {
        id: 'situation',
        title: 'Your Situation',
        description: 'Tell us about your income and home buying goals',
        progress: 20,
        data: {}
      },
      {
        id: 'finances',
        title: 'Financial Picture',
        description: 'Review your income, debts, and savings',
        progress: 40,
        data: {}
      },
      {
        id: 'documents',
        title: 'Document Upload',
        description: 'Upload your financial documents for verification',
        progress: 60,
        data: {}
      },
      {
        id: 'loan_options',
        title: 'Loan Options',
        description: 'Explore loan programs that fit your situation',
        progress: 80,
        data: {}
      },
      {
        id: 'application',
        title: 'Application',
        description: 'Complete your mortgage application',
        progress: 100,
        data: {}
      }
    ]
  },
  pre_approval: {
    type: 'pre_approval',
    title: 'Pre-Approval Check',
    description: 'Get pre-approved quickly with instant analysis',
    steps: [
      {
        id: 'quick_info',
        title: 'Quick Info',
        description: 'Basic income and debt information',
        progress: 25,
        data: {}
      },
      {
        id: 'credit_check',
        title: 'Credit Analysis',
        description: 'Estimate your credit qualifications',
        progress: 50,
        data: {}
      },
      {
        id: 'documentation',
        title: 'Documentation',
        description: 'Upload documents for verification',
        progress: 75,
        data: {}
      },
      {
        id: 'pre_approval_letter',
        title: 'Pre-Approval Letter',
        description: 'Get your pre-approval letter',
        progress: 100,
        data: {}
      }
    ]
  },
  mortgage_application: {
    type: 'mortgage_application',
    title: 'Mortgage Application',
    description: 'Complete your full mortgage application',
    steps: [
      {
        id: 'applicant_info',
        title: 'Applicant Information',
        description: 'Personal and employment details',
        progress: 20,
        data: {}
      },
      {
        id: 'financial_details',
        title: 'Financial Details',
        description: 'Income, assets, and debt information',
        progress: 40,
        data: {}
      },
      {
        id: 'property_info',
        title: 'Property Information',
        description: 'Details about the property you\'re purchasing',
        progress: 60,
        data: {}
      },
      {
        id: 'loan_details',
        title: 'Loan Details',
        description: 'Loan amount, term, and program selection',
        progress: 80,
        data: {}
      },
      {
        id: 'submit_application',
        title: 'Submit Application',
        description: 'Review and submit your completed application',
        progress: 100,
        data: {}
      }
    ]
  },
  refinance: {
    type: 'refinance',
    title: 'Refinance Consultation',
    description: 'See if refinancing makes sense for you',
    steps: [
      {
        id: 'current_loan',
        title: 'Current Loan',
        description: 'Tell us about your existing mortgage',
        progress: 33,
        data: {}
      },
      {
        id: 'goals',
        title: 'Refinance Goals',
        description: 'What do you want to accomplish?',
        progress: 66,
        data: {}
      },
      {
        id: 'analysis',
        title: 'Analysis & Options',
        description: 'Review your refinancing options',
        progress: 100,
        data: {}
      }
    ]
  }
}

export interface WizardAction {
  type: string
  label: string
  data?: Record<string, any>
  isQuick?: boolean
}

export interface WizardStepData {
  situation?: {
    income?: string
    location?: string
    timeframe?: string
    creditScore?: string
    monthlyDebts?: string
  }
  finances?: {
    annualIncome?: number
    monthlyIncome?: number
    downPayment?: number
    debtToIncomeRatio?: number
    assets?: number
  }
  documents?: {
    uploadedFiles?: string[]
    documentsAnalyzed?: boolean
    validationResults?: Record<string, any>
  }
  loan_options?: {
    selectedLoanType?: string
    estimatedRate?: number
    monthlyPayment?: number
  }
  application?: {
    applicationId?: string
    urlaGenerated?: boolean
    submitted?: boolean
  }
}
