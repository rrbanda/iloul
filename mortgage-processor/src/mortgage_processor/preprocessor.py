"""
Document preprocessing module for mortgage application processing.

This module handles all preprocessing logic including document formatting,
context building, and prompt assembly before agent execution.
"""

import logging
from typing import Dict, List, Any, Tuple
from .config import AppConfig

logger = logging.getLogger(__name__)


class DocumentPreprocessor:
    """
    Handles preprocessing of mortgage application data and documents
    before agent processing.
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize the preprocessor with configuration.
        
        Args:
            config: Application configuration containing templates and rules
        """
        self.config = config
        logger.debug("DocumentPreprocessor initialized")
    
    def extract_customer_info(self, application_data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """
        Extract and validate customer information from application data.
        
        Args:
            application_data: Raw application data
            
        Returns:
            Tuple of (customer_dict, loan_type)
        """
        customer = application_data.get("customer", {})
        loan_type = customer.get('loan_type', 'Unknown')
        
        logger.debug(f"Extracted customer info: {customer.get('name', 'Unknown')}, loan_type: {loan_type}")
        return customer, loan_type
    
    def format_document_list(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format documents into a structured list using configuration templates.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Formatted document list string
        """
        document_list = ""
        
        for i, doc in enumerate(documents, 1):
            # Extract document information with safe defaults
            file_name = doc.get('file_name', 'Unknown')
            content = doc.get('content', '')
            file_size = len(str(content))
            mime_type = doc.get('mime_type', 'unknown')
            content_preview = doc.get('content_preview', content)[:300]
            
            # Format using configuration template
            doc_info = self.config.format_document_info(
                index=i,
                file_name=file_name,
                file_size=file_size,
                mime_type=mime_type,
                content_preview=content_preview
            )
            document_list += doc_info + "\n"
        
        logger.debug(f"Formatted {len(documents)} documents")
        return document_list.strip()
    
    def build_required_documents_context(self, loan_type: str) -> str:
        """
        Build required documents context for the given loan type.
        
        Args:
            loan_type: Type of loan being processed
            
        Returns:
            Formatted required documents string
        """
        required_docs = self.config.get_required_documents(loan_type)
        required_documents = "\n".join([
            f"- {req.document_type}: {req.description}" 
            for req in required_docs
        ])
        
        logger.debug(f"Built required documents context for {loan_type}: {len(required_docs)} documents")
        return required_documents
    
    def build_validation_rules_context(self) -> str:
        """
        Build validation rules context from configuration.
        
        Returns:
            Formatted validation rules string
        """
        validation_rules = ""
        for doc_type, rules in self.config.mortgage.validation_rules.items():
            validation_rules += f"- {doc_type}: {rules}\n"
        
        logger.debug(f"Built validation rules context for {len(self.config.mortgage.validation_rules)} document types")
        return validation_rules.strip()
    
    def assemble_processing_prompt(
        self, 
        application_data: Dict[str, Any], 
        documents: List[Dict[str, Any]]
    ) -> str:
        """
        Assemble the complete processing prompt using all preprocessing steps.
        
        Args:
            application_data: Raw application data
            documents: List of documents to process
            
        Returns:
            Complete formatted prompt for agent processing
        """
        # Step 1: Extract customer information
        customer, loan_type = self.extract_customer_info(application_data)
        
        # Step 2: Format document list
        document_list = self.format_document_list(documents)
        
        # Step 3: Build required documents context
        required_documents = self.build_required_documents_context(loan_type)
        
        # Step 4: Build validation rules context
        validation_rules = self.build_validation_rules_context()
        
        # Step 5: Assemble final prompt using template
        prompt = self.config.format_processing_prompt(
            customer_name=customer.get('name', 'Unknown'),
            customer_age=customer.get('age', 'Unknown'),
            loan_type=loan_type,
            credit_authorized=customer.get('credit_authorized', False),
            application_id=application_data.get("application_id", "NEW"),
            document_count=len(documents),
            document_list=document_list,
            required_documents=required_documents,
            validation_rules=validation_rules
        )
        
        logger.info(f"Assembled processing prompt for {customer.get('name', 'Unknown')} with {len(documents)} documents")
        return prompt
    
    def validate_input_data(self, application_data: Dict[str, Any], documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate input data before processing.
        
        Args:
            application_data: Raw application data
            documents: List of documents to process
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check application data
        if not application_data:
            validation_result["valid"] = False
            validation_result["errors"].append("Application data is empty")
        
        # Check documents
        if not documents:
            validation_result["valid"] = False
            validation_result["errors"].append("No documents provided")
        
        # Check customer information
        customer = application_data.get("customer", {})
        if not customer.get("name"):
            validation_result["warnings"].append("Customer name is missing")
        
        if not customer.get("loan_type"):
            validation_result["warnings"].append("Loan type is missing")
        
        # Validate document structure
        for i, doc in enumerate(documents):
            if not doc.get("file_name"):
                validation_result["warnings"].append(f"Document {i+1} missing file_name")
            if not doc.get("content") and not doc.get("content_preview"):
                validation_result["warnings"].append(f"Document {i+1} missing content")
        
        logger.debug(f"Input validation completed: valid={validation_result['valid']}, "
                    f"errors={len(validation_result['errors'])}, warnings={len(validation_result['warnings'])}")
        
        return validation_result
