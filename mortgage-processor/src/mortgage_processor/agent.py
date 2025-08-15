import os
import uuid
import logging
from typing import Dict, List, Any, Optional
from llama_stack_client import LlamaStackClient, Agent
from llama_stack_client.lib.agents.event_logger import EventLogger

from .config import AppConfig
from .tools import (
    classify_document_type,
    validate_document_expiration,
    extract_personal_information,
    extract_income_information,
    check_document_quality,
    authorize_credit_check,
    generate_urla_1003_form,
    cross_validate_documents
)

logger = logging.getLogger(__name__)


class MortgageProcessingAgent:
    """
    Mortgage processing agent using regular Agent with tool calling.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = LlamaStackClient(
            base_url=config.llama.base_url,
            provider_data={}
        )
        
        # Create regular Agent with tools
        self.agent = Agent(
            client=self.client,
            model=config.llama.model_id,
            instructions=f"""{config.llama.instructions}

When processing mortgage documents, use these tools systematically:
- classify_document_type: Identify the type of document
- check_document_quality: Assess document readability and quality
- extract_personal_information: Extract personal details from documents
- extract_income_information: Extract financial information from documents
- validate_document_expiration: Check if documents are expired
- authorize_credit_check: Process credit check authorizations
- cross_validate_documents: Compare information across documents
- generate_urla_1003_form: Create URLA 1003 forms

Always use appropriate tools when analyzing documents.""",
            tools=[
                classify_document_type,
                validate_document_expiration,
                extract_personal_information,
                extract_income_information,
                check_document_quality,
                authorize_credit_check,
                generate_urla_1003_form,
                cross_validate_documents
            ],
            sampling_params={
                "strategy": {"type": "greedy"},
                "max_tokens": 2048,
            }
        )
        
        logger.info(f"Initialized MortgageProcessingAgent with regular Agent")
    
    def create_session(self) -> str:
        """Create a new processing session."""
        session_id = f"mortgage-session-{uuid.uuid4().hex}"
        return self.agent.create_session(session_id)
    
    def process_mortgage_application(
        self, 
        application_data: Dict[str, Any], 
        documents: List[Dict[str, Any]], 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process mortgage application using regular Agent with tools.
        """
        if not session_id:
            session_id = self.create_session()
        
        customer = application_data.get("customer", {})
        
        # Build processing prompt
        prompt = f"""Please process this mortgage application:

Customer: {customer.get('name', 'Unknown')}
Loan Type: {customer.get('loan_type', 'Unknown')}

Documents to analyze ({len(documents)} total):"""
        
        for i, doc in enumerate(documents, 1):
            content = doc.get('content_preview', doc.get('content', ''))[:300]
            prompt += f"""

Document {i}: {doc.get('file_name', 'Unknown')}
Content: {content}"""
        
        prompt += """

Please use your tools to:
1. Classify each document type
2. Check document quality
3. Extract personal information
4. Validate expiration dates
5. Provide a summary of findings

Start by using classify_document_type for the first document."""
        
        try:
            logger.info(f"Processing mortgage application for {customer.get('name', 'Unknown')}")
            
            response = self.agent.create_turn(
                messages=[{"role": "user", "content": prompt}],
                session_id=session_id,
                stream=True,
            )
            
            # Collect tool results properly
            tool_results = []
            final_content = ""
            tools_called = 0
            
            for log in EventLogger().log(response):
                try:
                    log_str = str(log)
                    
                    # Look for tool execution logs
                    if "tool_execution>" in log_str and "Tool:" in log_str:
                        tools_called += 1
                        # Extract tool name and result
                        tool_info = {
                            "tool_number": tools_called,
                            "log_content": log_str[:200] + "..." if len(log_str) > 200 else log_str,
                            "success": "error" not in log_str.lower()
                        }
                        tool_results.append(tool_info)
                        logger.info(f"Tool {tools_called} executed: {log_str[:100]}...")
                    
                    # Capture final response content
                    if hasattr(log, 'content') and log.content and len(str(log.content)) > 10:
                        final_content += str(log.content) + " "
                        
                except Exception as e:
                    logger.warning(f"Error processing log: {e}")
            
            # Count successful tools
            successful_tools = sum(1 for tool in tool_results if tool.get("success", False))
            
            # Determine status based on tool execution
            if successful_tools >= len(documents):
                status = "success"
                next_steps = ["All documents processed successfully", "Generate URLA 1003", "Proceed to underwriting"]
                urla_generated = True
            elif successful_tools > 0:
                status = "partial"
                next_steps = ["Some documents processed", "Review flagged items", "Manual review may be needed"]
                urla_generated = False
            else:
                status = "failed"
                next_steps = ["Tool execution failed", "Manual review required"]
                urla_generated = False
            
            # Build structured result
            result = {
                "application_id": application_data.get("application_id", f"APP_{uuid.uuid4().hex[:8]}"),
                "processing_status": status,
                "documents_processed": len(documents),
                "valid_documents": successful_tools,
                "invalid_documents": max(0, len(documents) - successful_tools),
                "missing_documents": [],
                "document_validations": tool_results,  # Now properly formatted as list of dicts
                "next_steps": next_steps,
                "urla_1003_generated": urla_generated,
                "agent_reasoning": final_content[:500] if final_content else "Agent processing completed successfully",
                "session_id": session_id,
                "tools_used": tools_called
            }
            
            logger.info(f"Processing completed: {status} with {tools_called} tool calls")
            return result
            
        except Exception as e:
            logger.error(f"Error processing with Agent: {e}", exc_info=True)
            return {
                "application_id": application_data.get("application_id", "unknown"),
                "processing_status": "failed",
                "error": str(e),
                "session_id": session_id,
                "documents_processed": len(documents),
                "valid_documents": 0,
                "invalid_documents": len(documents),
                "missing_documents": [],
                "document_validations": [],
                "next_steps": ["Manual review required due to processing error"],
                "urla_1003_generated": False,
                "agent_reasoning": f"Processing failed: {str(e)}",
                "tools_used": 0
            }


def create_mortgage_agent(config: AppConfig) -> MortgageProcessingAgent:
    """Factory function to create a mortgage processing agent."""
    return MortgageProcessingAgent(config)
