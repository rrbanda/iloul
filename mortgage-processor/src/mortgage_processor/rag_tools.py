"""
RAG tools for mortgage knowledge retrieval and document processing
Contains tools for agentic RAG including retriever, grading, and rewriting
"""

from typing import Literal
from pathlib import Path
from pydantic import BaseModel, Field
from langchain.tools.retriever import create_retriever_tool
try:
    from langchain_openai import OpenAIEmbeddings
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from .prompt_loader import (
    load_document_grading_prompt,
    load_query_rewrite_prompt,
    load_answer_generation_prompt
)

# Initialize the grader model for document relevance (configured lazily)
grader_model = None

def get_grader_model():
    """Get grader model from config"""
    global grader_model
    if grader_model is None:
        from .config import AppConfig
        config = AppConfig.load()
        
        from mortgage_processor.utils.llm_factory import get_llm, get_supervisor_llm, get_agent_llm, get_grader_llm
        grader_model = get_grader_llm()  # Centralized LLM from config.yaml
    return grader_model

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

# Prompts are now loaded from external files




def create_mortgage_knowledge_retriever():
    """
    Create a comprehensive retriever tool for mortgage knowledge base.
    Uses remote LlamaStack vector database exclusively (no local fallback).
    """
    from .config import AppConfig
    from .embeddings import create_embeddings
    
    # Load configuration
    config = AppConfig.load()
    
    # Use remote LlamaStack embeddings (with local fallback)
    embeddings = create_embeddings(
        model_name=config.vector_db.embedding,
        llamastack_base_url=config.llamastack.base_url,
        llamastack_api_key=config.llamastack.api_key,
        prefer_remote=True
    )
    
    # Try remote LlamaStack vector database first
    try:
        print("🔗 Attempting to connect to remote LlamaStack vector database...")
        from .vector_stores import LlamaStackVectorStore
        
        vectorstore = LlamaStackVectorStore(
            vector_db_id=config.vector_db.default_db_id,
            llamastack_base_url=config.llamastack.base_url,
            llamastack_api_key=config.llamastack.api_key,
            embedding_function=embeddings,
            embedding_model=config.vector_db.embedding,
            embedding_dimension=config.vector_db.embedding_dimension
        )
        
        # Test if remote vector database is working
        test_results = vectorstore.similarity_search("mortgage requirements", k=1)
        
        # If we get here, remote database is working
        if not test_results:
            print("🔄 Remote vector database is empty, populating with mortgage knowledge...")
            _populate_vector_database(vectorstore)
        else:
            print(f"✅ Using remote LlamaStack vector database with {len(test_results)} sample results")
        
        # Create retriever tool
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        retriever_tool = create_retriever_tool(
            retriever,
            "retrieve_mortgage_knowledge",
            """Search comprehensive mortgage knowledge base including:
            - Loan types (FHA, VA, Conventional, USDA)
            - Qualification requirements and credit scores
            - Documentation requirements and forms (URLA 1003)
            - Regulatory compliance (TRID, QM Rule, Fair Lending)
            - Real-world scenarios and case studies
            - Down payment options and income verification
            - Self-employed borrower requirements
            Use this for detailed mortgage information and specific guidance."""
        )
        
        print("🎯 Mortgage knowledge retriever tool created with remote LlamaStack vector database")
        return retriever_tool
        
    except Exception as e:
        print(f" LlamaStack vector database connection failed: {e}")
        print("💥 No fallback configured - RAG system requires LlamaStack connectivity")
        raise Exception(f"LlamaStack vector database unavailable: {e}. "
                       f"Check LlamaStack service at {config.llamastack.base_url}")


def _load_mortgage_knowledge_documents():
    """
    Load mortgage knowledge documents from files and return as LangChain Document objects.
    
    Returns:
        List of Document objects containing mortgage knowledge
    """
    # Load comprehensive mortgage knowledge from local files
    knowledge_base_path = Path(__file__).parent.parent.parent / "mortgage_knowledge"
    comprehensive_docs = []
    
    # Load mortgage forms documentation
    forms_file = knowledge_base_path / "mortgage_forms.md"
    if forms_file.exists():
        with open(forms_file, 'r') as f:
            content = f.read()
            comprehensive_docs.append({
                "page_content": content,
                "metadata": {"source": "mortgage_forms", "type": "forms_documentation", "category": "requirements"}
            })
    
    # Load regulations documentation  
    regulations_file = knowledge_base_path / "mortgage_regulations.md"
    if regulations_file.exists():
        with open(regulations_file, 'r') as f:
            content = f.read()
            comprehensive_docs.append({
                "page_content": content,
                "metadata": {"source": "mortgage_regulations", "type": "regulatory_guidance", "category": "compliance"}
            })
    
    # Load scenario documentation
    scenarios_file = knowledge_base_path / "mortgage_scenarios.md"
    if scenarios_file.exists():
        with open(scenarios_file, 'r') as f:
            content = f.read()
            comprehensive_docs.append({
                "page_content": content,
                "metadata": {"source": "mortgage_scenarios", "type": "case_studies", "category": "examples"}
            })
    
    # Add enhanced basic mortgage knowledge
    enhanced_docs = [
        {
            "page_content": """
            FHA Loans: Federal Housing Administration loans require a minimum down payment of 3.5% 
            and are available to borrowers with credit scores as low as 580. These loans are backed 
            by the government and offer more flexible qualification requirements. FHA loans also 
            require mortgage insurance premiums (MIP) both upfront (1.75% of loan amount) and 
            annually (0.45% to 1.05% depending on loan terms). Properties must be primary residences 
            and meet FHA property standards.
            """,
            "metadata": {"source": "fha_comprehensive", "type": "loan_type", "category": "government_loans"}
        },
        {
            "page_content": """
            Conventional Loans: These are not backed by the government and typically require higher 
            credit scores (620+) and down payments (usually 3-20%). They offer competitive interest 
            rates for qualified borrowers and have flexible terms. Conventional loans require private 
            mortgage insurance (PMI) if down payment is less than 20%, but PMI can be removed once 
            20% equity is reached. These loans have higher conforming loan limits and can be used for 
            primary residences, second homes, or investment properties.
            """,
            "metadata": {"source": "conventional_comprehensive", "type": "loan_type", "category": "conventional_loans"}
        },
        {
            "page_content": """
            VA Loans: Available to eligible veterans, active duty service members, National Guard, 
            Reserve members, and surviving spouses. These loans offer 0% down payment options, no 
            private mortgage insurance requirement, competitive interest rates, and no prepayment 
            penalties. Borrowers must obtain a Certificate of Eligibility (COE) and the property 
            must be a primary residence. VA funding fees apply but can be financed into the loan 
            and are waived for veterans with service-connected disabilities.
            """,
            "metadata": {"source": "va_comprehensive", "type": "loan_type", "category": "government_loans"}
        },
        {
            "page_content": """
            USDA Rural Development Loans: Available for properties in eligible rural and suburban areas. 
            These loans offer 100% financing (no down payment), below-market interest rates, and 
            reduced mortgage insurance. Borrowers must meet income limits (typically 115% of median 
            area income) and the property must be in an eligible rural area as defined by USDA. 
            Properties must be primary residences and meet USDA property requirements.
            """,
            "metadata": {"source": "usda_info", "type": "loan_type", "category": "government_loans"}
        },
        {
            "page_content": """
            Credit Score Impact on Mortgage Rates: Credit scores significantly affect mortgage interest 
            rates and loan approval. Scores of 740+ typically receive the best rates. Scores 720-739 
            get good rates with minimal pricing adjustments. Scores 680-719 may have small rate increases. 
            Scores 620-679 often face higher rates and stricter requirements. Scores below 620 may 
            require specialized programs like FHA loans. Each 20-point score decrease can increase 
            rates by 0.125% to 0.375%.
            """,
            "metadata": {"source": "credit_score_impact", "type": "qualification", "category": "credit_requirements"}
        },
        {
            "page_content": """
            Debt-to-Income Ratio Requirements: Most lenders prefer DTI ratios of 43% or less for conventional 
            loans, though some allow up to 50% with compensating factors. FHA loans allow DTI up to 57% 
            in some cases. DTI includes all monthly debt payments divided by gross monthly income. 
            Housing DTI (front-end ratio) should typically be 28% or less. Student loans, car payments, 
            credit cards, and other recurring debts are included in calculations. Lower DTI ratios 
            improve approval chances and may qualify for better rates.
            """,
            "metadata": {"source": "dti_requirements", "type": "qualification", "category": "income_requirements"}
        },
        {
            "page_content": """
            Down Payment Sources and Requirements: Acceptable down payment sources include savings, 
            checking accounts, investment accounts (stocks, bonds, mutual funds), retirement accounts 
            (with restrictions), gifts from family members (with gift letters), grants from down 
            payment assistance programs, and employer assistance programs. Large deposits must be 
            sourced and documented. Cash advances, borrowed funds, and unsecured loans cannot be 
            used for down payments. Seasoning requirements may apply to some fund sources.
            """,
            "metadata": {"source": "down_payment_sources", "type": "qualification", "category": "down_payment"}
        },
        {
            "page_content": """
            Self-Employed Income Documentation: Self-employed borrowers typically need 2 years of 
            personal tax returns, business tax returns (if applicable), profit & loss statements, 
            and CPA letters. Income is usually calculated as a 2-year average after business 
            deductions. Bank statement loans are alternative options that use deposits to qualify 
            income. Self-employed borrowers may need larger down payments and higher credit scores. 
            Some programs allow 1-year documentation with strong compensating factors.
            """,
            "metadata": {"source": "self_employed_income", "type": "documentation", "category": "income_verification"}
        }
    ]
    
    # Combine all documents
    all_docs = comprehensive_docs + enhanced_docs
    
    # Convert to Document objects
    from langchain_core.documents import Document
    docs = [Document(**doc) for doc in all_docs]
    
    print(f"📚 Loaded {len(docs)} mortgage knowledge documents")
    
    # Split documents for better retrieval
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=100  # Larger chunks for mortgage content
    )
    doc_splits = text_splitter.split_documents(docs)
    
    print(f"📄 Split into {len(doc_splits)} chunks for retrieval")
    return doc_splits


def _populate_vector_database(vectorstore):
    """
    Populate the vector database with mortgage knowledge.
    
    Args:
        vectorstore: Any vector store that supports add_texts method
    """
    doc_splits = _load_mortgage_knowledge_documents()
    
    # Add chunks to vector store
    texts = [chunk.page_content for chunk in doc_splits]
    metadatas = [chunk.metadata for chunk in doc_splits]
    
    vectorstore.add_texts(texts, metadatas)
    print(f"💾 Saved {len(doc_splits)} chunks to vector database")


def populate_customer_knowledge():
    """
    Populate additional customer-specific documents and scenarios into the knowledge base.
    This adds customer documents and real examples to enhance RAG responses.
    """
    import os
    
    # Load customer documents for RAG context
    customer_docs_path = Path(__file__).parent.parent.parent / "customer_docs"
    customer_documents = []
    
    if customer_docs_path.exists():
        for doc_file in customer_docs_path.glob("*.md"):
            with open(doc_file, 'r') as f:
                content = f.read()
                customer_documents.append({
                    "page_content": content,
                    "metadata": {
                        "source": f"customer_docs/{doc_file.name}",
                        "type": "customer_example",
                        "category": "sample_data"
                    }
                })
    
    print(f"📋 Loaded {len(customer_documents)} customer example documents")
    return customer_documents


def initialize_mortgage_rag_system():
    """
    Initialize the complete mortgage RAG system with comprehensive knowledge base.
    This function sets up both the knowledge retriever and populates sample data.
    """
    print("🚀 Initializing comprehensive mortgage RAG system...")
    
    # Create main knowledge retriever
    retriever_tool = create_mortgage_knowledge_retriever()
    
    # Load customer examples
    customer_docs = populate_customer_knowledge()
    
    print("✅ Mortgage RAG system initialized with:")
    print("   📚 Comprehensive mortgage knowledge base")
    print("   🏦 Regulatory and compliance documentation")
    print("   📋 Real-world scenarios and case studies")
    print("   👥 Customer example documents")
    print("   🔗 Neo4j vector integration (when available)")
    
    return retriever_tool


@tool
def grade_mortgage_documents(question: str, context: str) -> Literal["relevant", "not_relevant"]:
    """
    Grade retrieved mortgage documents for relevance to the user question.
    
    Args:
        question: The user's mortgage-related question
        context: The retrieved document content
        
    Returns:
        "relevant" if the document is relevant, "not_relevant" otherwise
    """
    # Load grading prompt from external file
    grade_prompt_template = load_document_grading_prompt()
    prompt = grade_prompt_template.format(question=question, document=context)
    
    grader = get_grader_model()
    response = (
        grader
        .with_structured_output(GradeDocuments)
        .invoke([{"role": "user", "content": prompt}])
    )
    
    return "relevant" if response.binary_score == "yes" else "not_relevant"


@tool  
def rewrite_mortgage_question(question: str) -> str:
    """
    Rewrite a mortgage question to improve retrieval results.
    
    Args:
        question: The original mortgage-related question
        
    Returns:
        An improved version of the question for better retrieval
    """
    # Load rewrite prompt from external file
    rewrite_prompt_template = load_query_rewrite_prompt()
    prompt = rewrite_prompt_template.format(question=question)
    
    grader = get_grader_model()
    response = grader.invoke([{"role": "user", "content": prompt}])
    return response.content


# Lazy initialization of mortgage retriever tool
_mortgage_retriever_tool = None

def get_mortgage_retriever_tool():
    """Get the mortgage retriever tool with lazy initialization."""
    global _mortgage_retriever_tool
    if _mortgage_retriever_tool is None:
        _mortgage_retriever_tool = create_mortgage_knowledge_retriever()
    return _mortgage_retriever_tool

# Export the lazy-loaded tool
mortgage_retriever_tool = get_mortgage_retriever_tool

# Export the tools
__all__ = [
    "mortgage_retriever_tool",
    "grade_mortgage_documents", 
    "rewrite_mortgage_question"
]
