## Simplified 3-Step Process - This streamlined version consolidates activities for platform demonstration while maintaining lending authenticity.


    graph TD
    A[Application Submitted] --> B[Process Documents]
    B --> C[Extract Data]
    C --> D[Validate Info]
    D --> E{Complete?}
    E -->|No| F[Request More]
    F --> B
    E -->|Yes| G[Risk Screen]
    G --> H[Provide Feedback]
    
    H --> I[Risk Analysis]
    I --> J[Credit Evaluation]
    J --> K[Income Analysis]
    K --> L[Collateral Review]
    L --> M[Compliance Check]
    M --> N[Confidence Score]
    N --> O{Assessment Done?}
    O -->|Review Needed| P[Manual Review]
    O -->|Complete| Q[Decision Logic]
    
    Q --> R[Final Decision]
    R --> S{Loan Decision}
    S -->|Approved| T[Approval Letter]
    S -->|Conditional| U[Condition List]
    S -->|Declined| V[Decline Notice]
    
    T --> W[Generate Disclosures]
    U --> W
    V --> W
    
    W --> X[Explain Decision]
    X --> Y[Digital Workflow]
    Y --> Z[Send to Borrower]
    
    P --> AA[Human Review]
    AA --> R
    
    Z --> BB{Response}
    BB -->|Accept| CC[Proceed to Close]
    BB -->|Change| DD[Modify Terms]
    BB -->|Decline| EE[Close File]
    
    DD --> Q
    CC --> FF[Complete]
    EE --> FF