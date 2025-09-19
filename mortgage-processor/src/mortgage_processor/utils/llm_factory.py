"""
Centralized LLM Factory for Mortgage Processing Application

This module provides a single source of truth for all LLM configurations,
reading from config.yaml to eliminate hardcoded endpoints.
"""

from langchain_openai import ChatOpenAI
from ..config import AppConfig


def get_llm(temperature=0.1, max_tokens=1200):
    """Get properly configured LLM using Llama Stack Chat Completions API.
    
    Args:
        temperature: Temperature for LLM generation (default: 0.1 for tool calling)
        max_tokens: Maximum tokens for response (default: 1200)
    
    Returns:
        ChatOpenAI: Configured LLM instance using config.yaml settings
    """
    config = AppConfig.load()
    return ChatOpenAI(
        base_url=f"{config.llamastack.base_url}/openai/v1",  # Use Llama Stack OpenAI endpoint
        api_key=config.llamastack.api_key,
        model=config.llamastack.default_model,
        temperature=temperature,
        max_tokens=max_tokens
    )

def get_supervisor_llm():
    """Get LLM configured for supervisor agent (higher temperature, shorter responses)."""
    return get_llm(temperature=0.2, max_tokens=800)

def get_agent_llm():
    """Get LLM configured for regular agents (balanced settings)."""
    return get_llm(temperature=0.4, max_tokens=1500)

def get_grader_llm():
    """Get LLM configured for grading/evaluation tasks (low temperature for consistency)."""
    return get_llm(temperature=0.0, max_tokens=500)
