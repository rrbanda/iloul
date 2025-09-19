#!/usr/bin/env python3
"""
Ingest customer documents into vector database
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import List

# Set up the module path
import sys
sys.path.append(str(Path(__file__).parent / "src"))

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mortgage_processor.config import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_customer_documents() -> List[MortgageDocument]:
    """Load sample customer documents from the customer_docs directory"""
    
    docs_dir = Path(__file__).parent / "customer_docs"
    documents = []
    
    # Sample customer documents
    doc_files = [
        ("john_smith_driver_license.md", "john_smith", "driver_license"),
        ("john_smith_bank_statements.md", "john_smith", "bank_statement"), 
        ("john_smith_employment.md", "john_smith", "employment_verification"),
        ("jane_doe_driver_license.md", "jane_doe", "driver_license"),
    ]
    
    for file_name, customer_id, doc_type in doc_files:
        file_path = docs_dir / file_name
        
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                
                doc = MortgageDocument(
                    customer_id=customer_id,
                    application_id=f"app_{customer_id}_001",
                    document_type=doc_type,
                    file_name=file_name,
                    content=content,
                    mime_type="text/markdown",
                    metadata={
                        "source": "customer_upload",
                        "processed_date": "2024-01-01"
                    }
                )
                
                documents.append(doc)
                logger.info(f"Loaded document: {file_name}")
                
            except Exception as e:
                logger.error(f"Failed to load {file_name}: {e}")
        else:
            logger.warning(f"Document file not found: {file_path}")
    
    return documents

async def main():
    """Main ingestion function"""
    
    try:
        # Load configuration
        config = load_config()
        
        # Create agent (which initializes LlamaStack client)
        agent = create_mortgage_agent(config)
        
        # Load customer documents
        logger.info("Loading customer documents...")
        documents = await load_customer_documents()
        
        if not documents:
            logger.error("No documents found to ingest")
            return
        
        logger.info(f"Found {len(documents)} documents to ingest")
        
        # Ingest documents using RAG endpoints
        logger.info("Starting document ingestion...")
        response = await ingest_documents(documents, chunk_size=512)
        
        logger.info(f" Ingestion completed successfully!")
        logger.info(f"📊 Processed: {response.processed_count} documents")
        logger.info(f"🆔 Document IDs: {response.document_ids}")
        
        # Test query
        logger.info("Testing knowledge base query...")
        test_query = "What is John Smith's employment status?"
        query_response = await agent.query_knowledge_base(
            query=test_query,
            customer_id="john_smith"
        )
        
        logger.info(f"📋 Test query: {test_query}")
        logger.info(f"💡 Answer: {query_response.answer}")
        
    except Exception as e:
        logger.error(f" Ingestion failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
