"""
Agentic Message Parser for LangGraph Studio
Exposes file content to agents so they can reason about it intelligently
"""

import logging
from typing import Dict, Optional, Any
from .file_processor import parse_multimodal_content

logger = logging.getLogger(__name__)

def extract_message_content_and_files(message: Any) -> Dict[str, Any]:
    """
    Extract content and files from LangGraph message - AGENTIC APPROACH
    Exposes file content to agents so they can reason about it
    
    Args:
        message: LangGraph message object
        
    Returns:
        Dict with all content visible to agents for intelligent processing
    """
    
    # Extract raw content from message
    raw_content = None
    if hasattr(message, 'content'):
        raw_content = message.content
    elif isinstance(message, dict):
        raw_content = message.get('content', '')
    else:
        raw_content = str(message)
    
    # DEBUG: Minimal logging for file uploads
    if isinstance(raw_content, list) and any(item.get('type') == 'image' for item in raw_content if isinstance(item, dict)):
        print(f"🔍 File upload detected: {len([item for item in raw_content if isinstance(item, dict) and item.get('type') == 'image'])} files")
    
    # Parse multimodal content
    parsed = parse_multimodal_content(raw_content)
    
    # AGENTIC: Combine all content so agents can see everything and reason
    full_context = parsed['text']
    
    if parsed['has_uploads']:
        full_context += "\n\n📋 **UPLOADED DOCUMENTS:**\n"
        for i, file_info in enumerate(parsed['files'], 1):
            full_context += f"\n**Document {i}: {file_info['filename']}**\n"
            full_context += f"Type: {file_info['type']}\n"
            full_context += f"Content:\n{file_info['extracted_text']}\n"
            full_context += "---\n"
    
    return {
        'full_content': full_context,  # Everything for agent reasoning
        'text_only': parsed['text'],
        'has_files': parsed['has_uploads'],
        'files': parsed['files'],
        'file_count': len(parsed['files']),
        'routing_hint': 'documents' if parsed['has_uploads'] else 'general'
    }


# Note: Removed rigid routing helper functions
# Now using truly agentic approach where LLM reasons about content
