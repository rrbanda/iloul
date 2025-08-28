#!/usr/bin/env python3
"""
Ingest customer documents into vector database
"""
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llama_stack_client import LlamaStackClient, RAGDocument
from mortgage_processor.config import AppConfig

def ingest_customer_documents():
    """Ingest all customer markdown documents."""
    
    # Load config and client
    config = AppConfig.load()
    client = LlamaStackClient(base_url=config.llama.base_url)
    
    # Ensure vector DB exists
    try:
        client.vector_dbs.register(
            vector_db_id=config.vector_db.id,
            embedding_model=config.vector_db.embedding,
            embedding_dimension=int(config.vector_db.embedding_dimension),
            provider_id=config.vector_db.provider,
        )
        print(f" Vector DB '{config.vector_db.id}' ready")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f" Vector DB '{config.vector_db.id}' already exists")
        else:
            print(f" Vector DB error: {e}")
            return
    
    # Find all customer documents
    docs_dir = Path("customer_docs")
    if not docs_dir.exists():
        print(" customer_docs directory not found")
        return
    
    rag_documents = []
    
    for md_file in docs_dir.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            
            # Extract customer_id and doc_type from content
            customer_id = None
            doc_type = None
            customer_name = None
            
            for line in content.split('\n'):
                if line.startswith('**Customer ID:**'):
                    customer_id = line.split('**Customer ID:**')[1].strip()
                elif line.startswith('**Document Type:**'):
                    doc_type = line.split('**Document Type:**')[1].strip()
                elif line.startswith('**Customer Name:**'):
                    customer_name = line.split('**Customer Name:**')[1].strip()
            
            if not customer_id or not doc_type:
                print(f"⚠️  Skipping {md_file.name} - missing customer_id or doc_type")
                continue
            
            # Create RAG document with rich metadata
            rag_doc = RAGDocument(
                document_id=f"customer_{customer_id}_{doc_type}_{uuid.uuid4().hex[:8]}",
                content=content,
                mime_type="text/markdown",
                metadata={
                    "customer_id": customer_id,
                    "document_type": doc_type,
                    "customer_name": customer_name,
                    "file_name": md_file.name,
                    "source": "customer_documents",
                    "ingestion_date": "2025-08-14"
                }
            )
            
            rag_documents.append(rag_doc)
            print(f"📄 Prepared: {customer_name} - {doc_type}")
            
        except Exception as e:
            print(f" Error processing {md_file.name}: {e}")
    
    if not rag_documents:
        print(" No documents to ingest")
        return
    
    # Ingest into RAG
    try:
        client.tool_runtime.rag_tool.insert(
            documents=rag_documents,
            vector_db_id=config.vector_db.id,
            chunk_size_in_tokens=int(config.vector_db.chunk_size)
        )
        
        print(f"\n🎉 Successfully ingested {len(rag_documents)} customer documents!")
        print("📊 Summary:")
        
        # Group by customer
        customers = {}
        for doc in rag_documents:
            cust_id = doc.metadata["customer_id"]
            cust_name = doc.metadata["customer_name"]
            doc_type = doc.metadata["document_type"]
            
            if cust_id not in customers:
                customers[cust_id] = {"name": cust_name, "docs": []}
            customers[cust_id]["docs"].append(doc_type)
        
        for cust_id, info in customers.items():
            print(f"   👤 {info['name']} ({cust_id}): {len(info['docs'])} documents")
            for doc_type in info['docs']:
                print(f"      📋 {doc_type}")
        
    except Exception as e:
        print(f" Ingestion failed: {e}")

if __name__ == "__main__":
    ingest_customer_documents()
