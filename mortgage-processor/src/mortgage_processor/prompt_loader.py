"""Prompt loading utilities for external prompt management."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache


class PromptLoader:
    """Utility class for loading prompts from external YAML files."""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """Initialize the prompt loader.
        
        Args:
            prompts_dir: Directory containing prompt files. If None, uses default.
        """
        if prompts_dir is None:
            # Default to prompts directory relative to project root
            current_dir = Path(__file__).parent.parent.parent
            self.prompts_dir = current_dir / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
            
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompts directory not found: {self.prompts_dir}")
    
    @lru_cache(maxsize=32)
    def _load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """Load and cache a YAML file.
        
        Args:
            filename: Name of the YAML file to load
            
        Returns:
            Dictionary containing the loaded YAML content
        """
        file_path = self.prompts_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {filename}: {e}")
    
    def get_supervisor_prompts(self) -> Dict[str, str]:
        """Load supervisor agent prompts.
        
        Returns:
            Dictionary containing supervisor prompts
        """
        return self._load_yaml_file("supervisor_prompts.yaml")
    
    def get_assistant_prompts(self) -> Dict[str, str]:
        """Load assistant agent prompts.
        
        Returns:
            Dictionary containing assistant agent prompts
        """
        return self._load_yaml_file("assistant_agent_prompts.yaml")
    
    def get_data_agent_prompts(self) -> Dict[str, str]:
        """Load data agent prompts.
        
        Returns:
            Dictionary containing data agent prompts
        """
        return self._load_yaml_file("data_agent_prompts.yaml")
    
    def get_rag_prompts(self) -> Dict[str, str]:
        """Load RAG system prompts.
        
        Returns:
            Dictionary containing RAG prompts
        """
        return self._load_yaml_file("rag_prompts.yaml")
    
    def get_property_agent_prompts(self) -> Dict[str, str]:
        """Load property agent prompts.
        
        Returns:
            Dictionary containing property agent prompts
        """
        return self._load_yaml_file("property_agent_prompts.yaml")
    
    def get_underwriting_agent_prompts(self) -> Dict[str, str]:
        """Load underwriting agent prompts.
        
        Returns:
            Dictionary containing underwriting agent prompts
        """
        return self._load_yaml_file("underwriting_agent_prompts.yaml")
    
    def get_compliance_agent_prompts(self) -> Dict[str, str]:
        """Load compliance agent prompts.
        
        Returns:
            Dictionary containing compliance agent prompts
        """
        return self._load_yaml_file("compliance_agent_prompts.yaml")
    
    def get_closing_agent_prompts(self) -> Dict[str, str]:
        """Load closing agent prompts.
        
        Returns:
            Dictionary containing closing agent prompts
        """
        return self._load_yaml_file("closing_agent_prompts.yaml")
    
    def get_customer_service_agent_prompts(self) -> Dict[str, str]:
        """Load customer service agent prompts.
        
        Returns:
            Dictionary containing customer service agent prompts
        """
        return self._load_yaml_file("customer_service_agent_prompts.yaml")
    
    def get_application_agent_prompts(self) -> Dict[str, str]:
        """Load application agent prompts.
        
        Returns:
            Dictionary containing application agent prompts
        """
        return self._load_yaml_file("application_agent_prompts.yaml")
    
    def get_document_agent_prompts(self) -> Dict[str, str]:
        """Load document agent prompts.
        
        Returns:
            Dictionary containing document agent prompts
        """
        return self._load_yaml_file("document_agent_prompts.yaml")
    
    def get_prompt(self, category: str, prompt_name: str) -> str:
        """Get a specific prompt by category and name.
        
        Args:
            category: Category of prompt (supervisor, assistant, data_agent, rag)
            prompt_name: Name of the specific prompt
            
        Returns:
            The requested prompt string
        """
        loaders = {
            "supervisor": self.get_supervisor_prompts,
            "assistant": self.get_assistant_prompts,
            "data_agent": self.get_data_agent_prompts,
            "rag": self.get_rag_prompts,
            "property_agent": self.get_property_agent_prompts,
            "underwriting_agent": self.get_underwriting_agent_prompts,
            "compliance_agent": self.get_compliance_agent_prompts,
            "closing_agent": self.get_closing_agent_prompts,
            "customer_service_agent": self.get_customer_service_agent_prompts,
            "application_agent": self.get_application_agent_prompts,
            "document_agent": self.get_document_agent_prompts,
        }
        
        if category not in loaders:
            raise ValueError(f"Unknown prompt category: {category}")
        
        prompts = loaders[category]()
        
        if prompt_name not in prompts:
            raise ValueError(f"Prompt '{prompt_name}' not found in category '{category}'")
        
        return prompts[prompt_name]


# Global prompt loader instance
_prompt_loader = None


def get_prompt_loader() -> PromptLoader:
    """Get the global prompt loader instance."""
    global _prompt_loader
    if _prompt_loader is None:
        _prompt_loader = PromptLoader()
    return _prompt_loader


# Convenience functions for common use cases
def load_supervisor_prompt() -> str:
    """Load the main supervisor system prompt."""
    return get_prompt_loader().get_prompt("supervisor", "supervisor_system_prompt")


def load_assistant_prompt() -> str:
    """Load the main assistant agent system prompt."""
    return get_prompt_loader().get_prompt("assistant", "system_prompt")


def load_data_agent_prompt() -> str:
    """Load the main data agent system prompt."""
    return get_prompt_loader().get_prompt("data_agent", "system_prompt")


def load_rag_agent_prompt() -> str:
    """Load the RAG agent system prompt."""
    return get_prompt_loader().get_prompt("rag", "rag_agent_system_prompt")


def load_query_rewrite_prompt() -> str:
    """Load the query rewrite prompt for RAG."""
    return get_prompt_loader().get_prompt("rag", "query_rewrite_prompt")


def load_document_grading_prompt() -> str:
    """Load the document grading prompt for RAG."""
    return get_prompt_loader().get_prompt("rag", "document_grading_prompt")


def load_answer_generation_prompt() -> str:
    """Load the answer generation prompt for RAG."""
    return get_prompt_loader().get_prompt("rag", "answer_generation_prompt")


def load_property_agent_prompt() -> str:
    """Load the main property agent system prompt."""
    return get_prompt_loader().get_prompt("property_agent", "system_prompt")


def load_underwriting_agent_prompt() -> str:
    """Load the main underwriting agent system prompt."""
    return get_prompt_loader().get_prompt("underwriting_agent", "system_prompt")


def load_compliance_agent_prompt() -> str:
    """Load the main compliance agent system prompt."""
    return get_prompt_loader().get_prompt("compliance_agent", "system_prompt")


def load_closing_agent_prompt() -> str:
    """Load the main closing agent system prompt."""
    return get_prompt_loader().get_prompt("closing_agent", "system_prompt")


def load_customer_service_agent_prompt() -> str:
    """Load the main customer service agent system prompt."""
    return get_prompt_loader().get_prompt("customer_service_agent", "system_prompt")


def load_application_agent_prompt() -> str:
    """Load the main application agent system prompt."""
    return get_prompt_loader().get_prompt("application_agent", "system_prompt")

def load_document_agent_prompt() -> str:
    """Load the main document agent system prompt."""
    return get_prompt_loader().get_prompt("document_agent", "document_agent")
