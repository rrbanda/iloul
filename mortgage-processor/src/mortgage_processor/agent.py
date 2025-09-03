import os
import uuid
import logging
from typing import Dict, List, Any, Optional
from llama_stack_client import LlamaStackClient, Agent

from .config import AppConfig
from .preprocessor import DocumentPreprocessor
from .postprocessor import ResponsePostprocessor
from .tools import (
    classify_document_type,
    validate_document_expiration,
    extract_personal_information,
    extract_income_information,
    check_document_quality,
    authorize_credit_check,
    generate_urla_1003_form,
    cross_validate_documents,
    get_current_date_time
)

logger = logging.getLogger(__name__)


class MortgageProcessingAgent:
    """
    Mortgage processing agent using regular Agent with tool calling.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.preprocessor = DocumentPreprocessor(config)
        self.postprocessor = ResponsePostprocessor(config)
        self.client = LlamaStackClient(
            base_url=config.llamastack.base_url,
            provider_data={}
        )
        
        # Get agent config and resolve instructions template
        agent_config = config.get_mortgage_agent()
        instructions = agent_config.instructions if agent_config else config.get_agent_instructions("mortgage_processing")
        
        # Resolve template if needed
        if instructions.startswith("{") and instructions.endswith("}"):
            # Parse template like {agent_instructions.chat_conversation}
            template_parts = instructions.strip("{}").split(".")
            if len(template_parts) == 2 and template_parts[0] == "agent_instructions":
                instructions = config.get_agent_instructions(template_parts[1])
        
        # Create regular Agent with tools
        self.agent = Agent(
            client=self.client,
            model=config.llamastack.default_model,
            instructions=instructions,
            tools=[
                classify_document_type,
                validate_document_expiration,
                extract_personal_information,
                extract_income_information,
                check_document_quality,
                authorize_credit_check,
                generate_urla_1003_form,
                cross_validate_documents,
                get_current_date_time
            ],
            sampling_params=config.get_sampling_params()
        )
        
        logger.info(f"Initialized MortgageProcessingAgent with regular Agent")
    
    def create_session(self) -> str:
        """Create a new processing session."""
        session_id = self.config.get_session_id_format().format(uuid.uuid4().hex)
        return self.agent.create_session(session_id)
    
    async def query_knowledge_base(self, query: str, customer_id: str = None, max_chunks: int = 5):
        """Query the RAG knowledge base for customer information"""
        try:
            from .rag_endpoints import QueryMortgageKnowledgeRequest, query_mortgage_knowledge
            
            request = QueryMortgageKnowledgeRequest(
                query=query,
                customer_id=customer_id,
                max_chunks=max_chunks
            )
            
            return await query_mortgage_knowledge(request)
            
        except Exception as e:
            logger.error(f"Failed to query knowledge base: {e}")
            return {
                "answer": "Unable to retrieve information from knowledge base.",
                "sources": [],
                "confidence": 0.0
            }
    
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
        
        # Validate input data before processing
        validation_result = self.preprocessor.validate_input_data(application_data, documents)
        if not validation_result["valid"]:
            logger.error(f"Input validation failed: {validation_result['errors']}")
            # Could return early here, but continuing for compatibility
        
        if validation_result["warnings"]:
            logger.warning(f"Input validation warnings: {validation_result['warnings']}")
        
        # Build processing prompt
        customer = application_data.get("customer", {})
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
            customer_name = application_data.get("customer", {}).get('name', 'Unknown')
            logger.info(f"Processing mortgage application for {customer_name}")
            
            response = self.agent.create_turn(
                messages=[{"role": "user", "content": prompt}],
                session_id=session_id,
                stream=True,
            )
            
            # Process the streaming response and extract tool calls
            from llama_stack_client.lib.agents.event_logger import EventLogger
            
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
                "document_validations": tool_results,
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
    
    def handle_chat_query(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle conversational queries about mortgage processing using the agent.
        """
        if not session_id:
            session_id = self.create_session()
        
        try:
            logger.info(f"Processing chat query: {user_message[:100]}...")
            
            # Create a new agent session for this chat query
            # (Chat session IDs are different from agent session IDs)
            agent_session_id = self.create_session()
            
            # Prepare the message for the agent
            messages = [{"role": "user", "content": user_message}]
            
            # Call the agent with the user message (use streaming like document processing)
            response = self.agent.create_turn(
                messages=messages,
                session_id=agent_session_id,
                stream=True,
            )
            
            # Extract response content from the agent
            response_text = ""
            all_content = []
            
            # Process the streaming response like we do for document processing
            from llama_stack_client.lib.agents.event_logger import EventLogger
            
            logger.info(f"Processing agent response for: {user_message[:50]}...")
            
            for log in EventLogger().log(response):
                try:
                    log_str = str(log)
                    
                    # Log everything we're getting to debug
                    if hasattr(log, 'content') and log.content:
                        content = str(log.content).strip()
                        all_content.append(content)
                        logger.info(f"Agent content chunk: {content[:100]}...")
                        
                        # Skip tool execution logs but keep actual content
                        if content and not content.startswith('tool_execution>') and not content.startswith('Tool:'):
                            response_text += content + " "
                        
                except Exception as e:
                    logger.warning(f"Error processing chat log: {e}")
            
            # Log what we collected
            logger.info(f"All content chunks: {all_content}")
            logger.info(f"Final response_text: {response_text}")
            
            # Clean up and provide fallback
            response_text = response_text.strip()
            if not response_text:
                response_text = "I'm here to help with your mortgage needs. Could you please rephrase your question?"
            
            # Return structured response
            return {
                "response": response_text,
                "type": "chat_response",
                "session_id": session_id,
                "tool_calls_made": getattr(response, 'tool_calls', []),
                "processing_successful": True
            }
            
        except Exception as e:
            logger.error(f"Error in chat query processing: {e}", exc_info=True)
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
                "type": "error",
                "session_id": session_id,
                "error": str(e),
                "processing_successful": False
            }


def create_mortgage_agent(config: AppConfig) -> MortgageProcessingAgent:
    """Factory function to create a mortgage processing agent."""
    return MortgageProcessingAgent(config)
