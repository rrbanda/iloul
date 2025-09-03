export interface MortgageApplicationData {
  personal_info?: {
    full_name?: string
    ssn?: string
    date_of_birth?: string
    phone?: string
    email?: string
  }
  current_address?: {
    street_address?: string
    city?: string
    state?: string
    zip_code?: string
    years_at_address?: number
  }
  employment?: {
    employer_name?: string
    job_title?: string
    years_employed?: number
    employment_type?: string
  }
  financial?: {
    gross_annual_income?: number
    additional_income?: number
    monthly_debts?: number
    down_payment?: number
    assets_savings?: number
  }
  property?: {
    property_address?: string
    property_city?: string
    property_state?: string
    property_zip?: string
    purchase_price?: number
    property_type?: string
  }
  loan_details?: {
    loan_amount?: number
    loan_type?: string
    loan_purpose?: string
  }
}

export interface ApplicationSession {
  session_id: string
  completion_percentage: number
  is_complete: boolean
  collected_data: MortgageApplicationData
  missing_fields: MissingField[]
  status: string
}

export interface MissingField {
  field: string
  section: string
  display: string
}

export interface ApplicationChatResponse {
  session_id: string
  response: string
  completion_percentage: number
  is_complete: boolean
  collected_data: MortgageApplicationData
  status: string
  timestamp: string
}

export interface ApplicationFormData {
  session_id: string
  form_data: MortgageApplicationData
  is_complete: boolean
  validation_errors: string[]
  urla_form_fields: URLAFormFields
  status: string
}

export interface URLAFormFields {
  // Personal Information
  borrower_first_name?: string
  borrower_last_name?: string
  borrower_ssn?: string
  borrower_date_of_birth?: string
  borrower_phone?: string
  borrower_email?: string
  
  // Current Address
  present_address_street?: string
  present_address_city?: string
  present_address_state?: string
  present_address_zip?: string
  years_at_present_address?: number
  
  // Employment
  employer_name?: string
  position_title?: string
  years_employed?: number
  employment_type?: string
  
  // Financial
  gross_monthly_income?: number
  other_monthly_income?: number
  total_monthly_obligations?: number
  down_payment?: number
  liquid_assets?: number
  
  // Property
  subject_property_address?: string
  subject_property_city?: string
  subject_property_state?: string
  subject_property_zip?: string
  purchase_price?: number
  property_type?: string
  
  // Loan Details
  loan_amount?: number
  loan_type?: string
  loan_purpose?: string
}

export interface ApplicationSubmissionResult {
  application_id: string
  session_id: string
  status: string
  submitted_at: string
  collected_data: MortgageApplicationData
  next_steps: string[]
}

// Enums for dropdown values
export const EMPLOYMENT_TYPES = [
  "Full-time W-2",
  "Part-time W-2", 
  "Self-employed",
  "Contract/1099",
  "Retired",
  "Other"
] as const

export const PROPERTY_TYPES = [
  "Single Family Home",
  "Condominium",
  "Townhouse",
  "Multi-family (2-4 units)",
  "Manufactured Home"
] as const

export const LOAN_TYPES = [
  "Conventional",
  "FHA",
  "VA", 
  "USDA",
  "Jumbo"
] as const

export const LOAN_PURPOSES = [
  "Purchase",
  "Refinance",
  "Cash-out Refinance"
] as const

export type EmploymentType = typeof EMPLOYMENT_TYPES[number]
export type PropertyType = typeof PROPERTY_TYPES[number]
export type LoanType = typeof LOAN_TYPES[number]
export type LoanPurpose = typeof LOAN_PURPOSES[number]
