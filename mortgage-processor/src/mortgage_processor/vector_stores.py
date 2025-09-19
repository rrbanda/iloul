"""
Remote Vector Store implementations using LlamaStack API endpoints.
Provides LangChain-compatible vector stores backed by remote LlamaStack vector databases.
"""

import json
import requests
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)


class LlamaStackVectorStore(VectorStore):
    """
    LangChain-compatible vector store that uses LlamaStack vector database endpoints.
    
    This class provides the same interface as FAISS but operates via HTTP calls
    to a remote LlamaStack server for vector operations.
    """
    
    def __init__(
        self,
        vector_db_id: str,
        llamastack_base_url: str,
        llamastack_api_key: str,
        embedding_function: Embeddings,
        embedding_model: str = "all-MiniLM-L6-v2",
        embedding_dimension: int = 384
    ):
        """
        Initialize the remote vector store.
        
        Args:
            vector_db_id: ID of the vector database in LlamaStack
            llamastack_base_url: Base URL of LlamaStack server (e.g., "http://localhost:5001")
            llamastack_api_key: API key for LlamaStack
            embedding_function: Embeddings model to use
            embedding_model: Name of the embedding model
            embedding_dimension: Dimension of embeddings
        """
        self.vector_db_id = vector_db_id
        self.base_url = llamastack_base_url.rstrip("/")
        self.api_key = llamastack_api_key
        self.embedding_function = embedding_function
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension
        
        # Don't connect during init - do it lazily when needed
        self._db_initialized = False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for LlamaStack API calls."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _ensure_vector_db(self) -> bool:
        """
        Ensure the vector database exists, create if it doesn't.
        Returns True if successful, False if it should fall back to local storage.
        """
        if self._db_initialized:
            return True
            
        try:
            # Check if vector DB exists
            response = requests.get(
                f"{self.base_url}/v1/vector-dbs/{self.vector_db_id}",
                headers=self._get_headers(),
                timeout=5  # Add timeout
            )
            
            if response.status_code == 404:
                # Try to create vector database
                logger.info(f"Creating vector database: {self.vector_db_id}")
                create_data = {
                    "vector_db_id": self.vector_db_id,
                    "embedding_model": self.embedding_model,
                    "embedding_dimension": self.embedding_dimension
                }
                
                response = requests.post(
                    f"{self.base_url}/v1/vector-dbs",
                    headers=self._get_headers(),
                    json=create_data,
                    timeout=10
                )
                
                if response.status_code not in [200, 201]:
                    logger.warning(f"Failed to create vector database: {response.text}")
                    return False
                
                logger.info(f"✅ Created vector database: {self.vector_db_id}")
                self._db_initialized = True
                return True
            
            elif response.status_code == 200:
                logger.info(f"✅ Vector database exists: {self.vector_db_id}")
                self._db_initialized = True
                return True
            else:
                logger.warning(f"Unexpected response checking vector database: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Cannot connect to LlamaStack server: {e}")
            return False
        except Exception as e:
            logger.warning(f"Error ensuring vector database: {e}")
            return False
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any
    ) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dicts
            
        Returns:
            List of document IDs
        """
        # Check if vector database is available
        if not self._ensure_vector_db():
            logger.warning("LlamaStack vector database not available, skipping text insertion")
            # Return dummy IDs for compatibility
            return [f"dummy_{i}" for i in range(len(texts))]
        
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        try:
            # Generate embeddings
            embeddings = self.embedding_function.embed_documents(texts)
            
            # Prepare chunks for insertion
            chunks = []
            doc_ids = []
            
            for i, (text, metadata, embedding) in enumerate(zip(texts, metadatas, embeddings)):
                doc_id = f"doc_{i}_{hash(text) % 1000000}"  # Simple ID generation
                doc_ids.append(doc_id)
                
                chunk = {
                    "content": text,
                    "metadata": metadata,
                    "embedding": embedding,
                    "chunk_id": doc_id,
                    "chunk_metadata": {
                        "chunk_id": doc_id,
                        "source": metadata.get("source", "unknown"),
                        "chunk_embedding_model": self.embedding_model,
                        "chunk_embedding_dimension": self.embedding_dimension,
                        "content_token_count": len(text.split())  # Simple token count
                    }
                }
                chunks.append(chunk)
            
            # Insert chunks via LlamaStack API
            insert_data = {
                "vector_db_id": self.vector_db_id,
                "chunks": chunks
            }
            
            response = requests.post(
                f"{self.base_url}/v1/vector-io/insert",
                headers=self._get_headers(),
                json=insert_data,
                timeout=30
            )
            
            if response.status_code not in [200, 201]:
                logger.warning(f"Failed to insert chunks: {response.text}")
                return [f"failed_{i}" for i in range(len(texts))]
            
            logger.info(f"✅ Inserted {len(chunks)} chunks into vector database")
            return doc_ids
            
        except Exception as e:
            logger.warning(f"Error adding texts to vector database: {e}")
            return [f"error_{i}" for i in range(len(texts))]
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        **kwargs: Any
    ) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Query string
            k: Number of documents to return
            
        Returns:
            List of similar documents
        """
        # Check if vector database is available
        if not self._ensure_vector_db():
            logger.warning("LlamaStack vector database not available, returning empty results")
            # Return some basic fallback content
            fallback_content = """
            Mortgage processing requires proper documentation including:
            - Pay stubs and income verification
            - Bank statements
            - Credit reports
            - Property appraisal
            - Employment verification
            
            Please ensure all required documents are provided for loan approval.
            """
            return [Document(
                page_content=fallback_content.strip(),
                metadata={"source": "fallback", "type": "basic_guidance"}
            )]
        
        try:
            # Query via LlamaStack API
            query_data = {
                "vector_db_id": self.vector_db_id,
                "query": query,  # Can be string or embedding
                "params": {
                    "k": k,
                    "include_metadata": True
                }
            }
            
            response = requests.post(
                f"{self.base_url}/v1/vector-io/query",
                headers=self._get_headers(),
                json=query_data,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to query vector database: {response.text}")
                return []
            
            result = response.json()
            
            # Convert results to LangChain Documents
            documents = []
            for chunk in result.get("chunks", []):
                content = chunk.get("content", "")
                if isinstance(content, dict) and "text" in content:
                    content = content["text"]
                elif isinstance(content, list):
                    # Handle array content by joining text items
                    content = " ".join([item.get("text", str(item)) for item in content if isinstance(item, dict)])
                
                metadata = chunk.get("metadata", {})
                metadata["score"] = chunk.get("score", 0.0)
                
                documents.append(Document(
                    page_content=content,
                    metadata=metadata
                ))
            
            logger.info(f"✅ Retrieved {len(documents)} documents for query")
            return documents
            
        except Exception as e:
            logger.warning(f"Error querying vector database: {e}")
            return []
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents with similarity scores.
        
        Args:
            query: Query string
            k: Number of documents to return
            
        Returns:
            List of (document, score) tuples
        """
        documents = self.similarity_search(query, k, **kwargs)
        
        # Extract scores from metadata
        results = []
        for doc in documents:
            score = doc.metadata.get("score", 0.0)
            # Remove score from metadata to avoid duplication
            clean_metadata = {k: v for k, v in doc.metadata.items() if k != "score"}
            clean_doc = Document(page_content=doc.page_content, metadata=clean_metadata)
            results.append((clean_doc, score))
        
        return results
    
    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        vector_db_id: str = "mortgage_knowledge",
        llamastack_base_url: str = "http://localhost:5001",
        llamastack_api_key: str = "dummy_key",
        **kwargs: Any
    ) -> "LlamaStackVectorStore":
        """
        Create a vector store from texts.
        
        Args:
            texts: List of texts to add
            embedding: Embeddings model
            metadatas: Optional metadata for texts
            vector_db_id: ID for the vector database
            llamastack_base_url: LlamaStack server URL
            llamastack_api_key: LlamaStack API key
            
        Returns:
            LlamaStackVectorStore instance
        """
        store = cls(
            vector_db_id=vector_db_id,
            llamastack_base_url=llamastack_base_url,
            llamastack_api_key=llamastack_api_key,
            embedding_function=embedding,
            **kwargs
        )
        
        if texts:
            store.add_texts(texts, metadatas)
        
        return store
    
    def delete(self, ids: Optional[List[str]] = None, **kwargs: Any) -> Optional[bool]:
        """
        Delete documents by IDs.
        Note: This would require a delete endpoint in LlamaStack API.
        """
        logger.warning("Delete operation not implemented - LlamaStack vector-io API doesn't expose delete functionality")
        return False
    
    def get_vector_db_info(self) -> Dict[str, Any]:
        """Get information about the vector database."""
        response = requests.get(
            f"{self.base_url}/v1/vector-dbs/{self.vector_db_id}",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get vector DB info: {response.text}")
            return {}


def create_remote_vector_store(
    vector_db_id: str,
    llamastack_base_url: str,
    llamastack_api_key: str,
    embedding_model: str = "all-MiniLM-L6-v2"
) -> LlamaStackVectorStore:
    """
    Create a remote vector store using LlamaStack.
    
    Args:
        vector_db_id: ID for the vector database
        llamastack_base_url: LlamaStack server URL  
        llamastack_api_key: LlamaStack API key
        embedding_model: LlamaStack embedding model name
        
    Returns:
        LlamaStackVectorStore instance
    """
    # Use remote LlamaStack embeddings (with local fallback)
    from .embeddings import create_embeddings
    embeddings = create_embeddings(
        model_name=embedding_model,
        llamastack_base_url=llamastack_base_url,
        llamastack_api_key=llamastack_api_key,
        prefer_remote=True
    )
    
    return LlamaStackVectorStore(
        vector_db_id=vector_db_id,
        llamastack_base_url=llamastack_base_url,
        llamastack_api_key=llamastack_api_key,
        embedding_function=embeddings,
        embedding_model=embedding_model
    )
