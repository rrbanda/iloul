"""
Remote LlamaStack embedding implementation.
Provides LangChain-compatible embeddings that use LlamaStack API endpoints.
"""

import requests
import logging
from typing import List
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)


class LlamaStackEmbeddings(Embeddings):
    """
    LangChain-compatible embeddings that use LlamaStack embedding endpoints.
    
    This class provides the same interface as HuggingFaceEmbeddings but operates
    via HTTP calls to a remote LlamaStack server for embedding generation.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        llamastack_base_url: str = "http://localhost:5001",
        llamastack_api_key: str = "dummy_key"
    ):
        """
        Initialize the remote embeddings.
        
        Args:
            model_name: Name of the embedding model on LlamaStack
            llamastack_base_url: Base URL of LlamaStack server
            llamastack_api_key: API key for LlamaStack
        """
        self.model_name = model_name
        self.base_url = llamastack_base_url.rstrip("/")
        self.api_key = llamastack_api_key
        self._fallback_embeddings = None
    
    def _get_headers(self) -> dict:
        """Get HTTP headers for LlamaStack API calls."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _get_fallback_embeddings(self):
        """Get fallback local embeddings if remote fails."""
        if self._fallback_embeddings is None:
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
                self._fallback_embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
                logger.info("Initialized fallback local embeddings")
            except Exception as e:
                logger.error(f"Failed to initialize fallback embeddings: {e}")
                raise Exception("Both remote and local embeddings failed")
        return self._fallback_embeddings
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Use LlamaStack embedding endpoint
            data = {
                "model_id": self.model_name,
                "contents": texts
            }
            
            response = requests.post(
                f"{self.base_url}/v1/inference/embeddings",
                headers=self._get_headers(),
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract embeddings from response
                embeddings = []
                for item in result.get("data", []):
                    if "embedding" in item:
                        embeddings.append(item["embedding"])
                    elif "values" in item:
                        embeddings.append(item["values"])
                    else:
                        # Try to find embedding in the item
                        for key, value in item.items():
                            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], (int, float)):
                                embeddings.append(value)
                                break
                
                if len(embeddings) == len(texts):
                    logger.debug(f"Generated {len(embeddings)} embeddings via LlamaStack")
                    return embeddings
                else:
                    logger.warning(f"Embedding count mismatch: expected {len(texts)}, got {len(embeddings)}")
            else:
                logger.warning(f"LlamaStack embedding request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.warning(f"Error calling LlamaStack embeddings: {e}")
        
        # Fall back to local embeddings
        logger.info("Falling back to local HuggingFace embeddings")
        fallback = self._get_fallback_embeddings()
        return fallback.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Use OpenAI-compatible endpoint for single query
            data = {
                "model": self.model_name,
                "input": text
            }
            
            response = requests.post(
                f"{self.base_url}/v1/openai/v1/embeddings",
                headers=self._get_headers(),
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract embedding from OpenAI-style response
                if "data" in result and len(result["data"]) > 0:
                    embedding_data = result["data"][0]
                    if "embedding" in embedding_data:
                        logger.debug("Generated query embedding via LlamaStack (OpenAI endpoint)")
                        return embedding_data["embedding"]
                    elif "values" in embedding_data:
                        return embedding_data["values"]
            else:
                logger.warning(f"LlamaStack query embedding request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.warning(f"Error calling LlamaStack query embeddings: {e}")
        
        # Fall back to local embeddings
        logger.info("Falling back to local HuggingFace embeddings for query")
        fallback = self._get_fallback_embeddings()
        return fallback.embed_query(text)


def create_embeddings(
    model_name: str = "all-MiniLM-L6-v2",
    llamastack_base_url: str = "http://localhost:5001", 
    llamastack_api_key: str = "dummy_key",
    prefer_remote: bool = True
) -> Embeddings:
    """
    Create embeddings instance, preferring remote LlamaStack over local.
    
    Args:
        model_name: Name of the embedding model
        llamastack_base_url: LlamaStack server URL
        llamastack_api_key: LlamaStack API key  
        prefer_remote: Whether to prefer remote over local embeddings
        
    Returns:
        Embeddings instance
    """
    if prefer_remote:
        try:
            return LlamaStackEmbeddings(
                model_name=model_name,
                llamastack_base_url=llamastack_base_url,
                llamastack_api_key=llamastack_api_key
            )
        except Exception as e:
            logger.warning(f"Failed to create remote embeddings: {e}")
    
    # Fall back to local embeddings
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        logger.info("Using local HuggingFace embeddings")
        return HuggingFaceEmbeddings(model_name=model_name)
    except Exception as e:
        logger.error(f"Failed to create local embeddings: {e}")
        raise Exception("Both remote and local embeddings failed")
