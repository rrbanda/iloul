# Process Flowcharts

This section contains visual representations of both the comprehensive and simplified loan underwriting processes.

## Comprehensive 5-Phase Process

The following diagram shows the complete traditional mortgage lending workflow with all regulatory requirements and verification steps.

```mermaid
graph TD
    A[Borrower Submits Application] --> B[Collect Required Documents]
    B --> C[Extract Financial Data]
    C --> D[Validate Information]
    D --> E{Complete Documentation?}
    E -->|No| F[Request Missing Documents]
    F --> B
    E -->|Yes| G[Authorize Credit Pull]
    
    G --> H[Pull Credit Report]
    H --> I[Submit to AUS System]
    I --> J[Generate Loan Estimate]
    J --> K[Deliver Disclosures]
    K --> L{Proceed with Loan?}
    L -->|No| M[Application Withdrawn]
    L -->|Yes| N[Order Appraisal]
    
    N --> O[Title Search]
    O --> P[Verify Employment]
    P --> Q[Verify Assets]
    Q --> R[Request Tax Transcripts]
    R --> S[Collect Insurance]
    
    S --> T[Calculate Income]
    T --> U[Analyze Debt Ratios]
    U --> V[Review Appraisal]
    V --> W[Evaluate Credit Risk]
    W --> X[Apply Guidelines]
    X --> Y{Underwriting Decision}
    
    Y -->|Approved| Z[Clear Approval]
    Y -->|Conditional| AA[List Conditions]
    Y -->|Declined| BB[Decline Notice]
    
    AA --> CC[Collect Responses]
    CC --> DD{Conditions Met?}
    DD -->|No| EE[Request More Info]
    EE --> CC
    DD -->|Yes| FF[Final Verification]
    
    Z --> FF
    FF --> GG[Closing Disclosure]
    GG --> HH[Three Day Wait]
    HH --> II[Final Review]
    II --> JJ[Clear to Close]
    JJ --> KK[Fund Loan]
    
    BB --> LL[End Process]
    M --> LL
    KK --> MM[Loan Complete]


