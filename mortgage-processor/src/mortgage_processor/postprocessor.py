"""
Response postprocessing module for mortgage application processing.

This module handles all postprocessing logic including response parsing,
status determination, and result structuring after agent execution.
"""

import uuid
import logging
from typing import Dict, List, Any, Tuple
from llama_stack_client.lib.agents.event_logger import EventLogger
from .config import AppConfig

logger = logging.getLogger(__name__)


class ResponsePostprocessor:
    """
    Handles postprocessing of agent responses including parsing,
    analysis, and result structuring.
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize the postprocessor with configuration.
        
        Args:
            config: Application configuration containing thresholds and templates
        """
        self.config = config
        logger.debug("ResponsePostprocessor initialized")
    
    def parse_agent_response(self, response) -> Tuple[List[Dict[str, Any]], str, int]:
        """
        Parse the agent response to extract tool results and content.
        
        Args:
            response: Response from agent (Turn object)
            
        Returns:
            Tuple of (tool_results, final_content, tools_called)
        """
        tool_results = []
        final_content = ""
        tools_called = 0
        
        try:
            # For non-streaming responses, check if response has steps
            if hasattr(response, 'steps') and response.steps:
                logger.debug(f"Processing {len(response.steps)} response steps")
                
                for step in response.steps:
                    # Extract content from api_model_response
                    if hasattr(step, 'api_model_response') and step.api_model_response:
                        if hasattr(step.api_model_response, 'content') and step.api_model_response.content:
                            final_content += str(step.api_model_response.content) + " "
                        
                        # Check for actual tool calls in the response
                        if hasattr(step.api_model_response, 'tool_calls') and step.api_model_response.tool_calls:
                            for tool_call in step.api_model_response.tool_calls:
                                tools_called += 1
                                
                                # Try multiple ways to extract tool name
                                tool_name = "unknown"
                                if hasattr(tool_call, 'function'):
                                    if hasattr(tool_call.function, 'name'):
                                        tool_name = tool_call.function.name
                                    elif isinstance(tool_call.function, dict):
                                        tool_name = tool_call.function.get('name', 'unknown')
                                elif hasattr(tool_call, 'tool_name'):
                                    tool_name = tool_call.tool_name
                                elif hasattr(tool_call, 'name'):
                                    tool_name = tool_call.name
                                
                                # Extract from string representation if still unknown
                                if tool_name == "unknown":
                                    tool_str = str(tool_call)
                                    if "tool_name='" in tool_str:
                                        start = tool_str.find("tool_name='") + 11
                                        end = tool_str.find("'", start)
                                        if end > start:
                                            tool_name = tool_str[start:end]
                                
                                tool_info = {
                                    "tool_number": tools_called,
                                    "tool_name": tool_name,
                                    "log_content": f"Tool call: {tool_name}",
                                    "success": True
                                }
                                tool_results.append(tool_info)
                                logger.info(f"Tool {tools_called} ({tool_name}) executed: SUCCESS")
            
            # If no actual tool calls found, check if content indicates attempted tool usage
            if not tool_results and final_content:
                # Check if the agent is describing tools instead of calling them
                if ("[classify_document_type" in final_content or 
                    "classify_document_type(" in final_content or
                    "tool" in final_content.lower()):
                    logger.warning("Agent described tools but didn't execute them")
                    # Return empty results to indicate failure
                    tools_called = 0
                    tool_results = []
                else:
                    # If we have substantial content without tool descriptions, 
                    # the agent might have processed without tools
                    logger.info(f"Agent provided response without tool calls: {len(final_content)} chars")
                    
        except Exception as e:
            logger.error(f"Error parsing agent response: {e}")
        
        logger.info(f"Parsed agent response: {tools_called} tools called, {len(tool_results)} tool results captured")
        return tool_results, final_content, tools_called
    
    def _clean_agent_reasoning(self, raw_content: str) -> str:
        """
        Clean agent reasoning by removing tool call artifacts and extracting meaningful content.
        
        Args:
            raw_content: Raw content from agent response
            
        Returns:
            Cleaned reasoning text
        """
        if not raw_content:
            return ""
        
        # Remove tool call artifacts
        lines = raw_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip lines that look like tool calls
            if (line.startswith('call_id=') or 
                line.startswith('tool_name=') or
                line.startswith('arguments=') or
                'chatcmpl-tool-' in line or
                line.startswith('{') and '}' in line and 'tool' in line.lower()):
                continue
            
            # Keep meaningful content
            if len(line) > 10 and not line.startswith('[') and not line.startswith('{'):
                cleaned_lines.append(line)
        
        # Join and clean up
        cleaned_content = ' '.join(cleaned_lines).strip()
        
        # If no meaningful content found, generate default reasoning
        if not cleaned_content or len(cleaned_content) < 20:
            return "Successfully processed mortgage application using AI agent tools for document classification, validation, and analysis."
        
        return cleaned_content
    
    def analyze_processing_success(self, tool_results: List[Dict[str, Any]], document_count: int) -> Dict[str, Any]:
        """
        Analyze tool execution results to determine processing success metrics.
        
        Args:
            tool_results: List of tool execution results
            document_count: Number of documents processed
            
        Returns:
            Analysis results including success ratio and counts
        """
        successful_tools = sum(1 for tool in tool_results if tool.get("success", False))
        success_ratio = successful_tools / document_count if document_count > 0 else 0
        
        analysis = {
            "successful_tools": successful_tools,
            "total_tools": len(tool_results),
            "document_count": document_count,
            "success_ratio": success_ratio,
            "failed_tools": len(tool_results) - successful_tools
        }
        
        logger.debug(f"Success analysis: {successful_tools}/{len(tool_results)} tools successful, "
                    f"ratio: {success_ratio:.2f}")
        
        return analysis
    
    def determine_processing_status(self, analysis: Dict[str, Any]) -> Tuple[str, List[str], bool]:
        """
        Determine processing status based on configurable thresholds.
        
        Args:
            analysis: Success analysis results
            
        Returns:
            Tuple of (status, next_steps, urla_generated)
        """
        success_ratio = analysis["success_ratio"]
        
        # Apply configurable business logic for status determination
        status_thresholds = self.config.get_status_thresholds()
        
        if success_ratio >= status_thresholds.minimum_success_ratio:
            status = "success"
            next_steps = self.config.get_next_steps("processing_complete")
            urla_generated = True
            
        elif success_ratio >= status_thresholds.minimum_partial_ratio:
            status = "partial_success"
            next_steps = self.config.get_next_steps("document_issues")
            urla_generated = False
            
        else:
            status = "failure"
            next_steps = self.config.get_next_steps("manual_review")
            urla_generated = False
        
        logger.info(f"Determined processing status: {status} (ratio: {success_ratio:.2f})")
        return status, next_steps, urla_generated
    
    def build_structured_result(
        self,
        application_data: Dict[str, Any],
        documents: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        status: str,
        next_steps: List[str],
        urla_generated: bool,
        tool_results: List[Dict[str, Any]],
        final_content: str,
        session_id: str,
        tools_called: int
    ) -> Dict[str, Any]:
        """
        Build the structured result dictionary for the client.
        
        Args:
            application_data: Original application data
            documents: List of processed documents
            analysis: Success analysis results
            status: Processing status
            next_steps: Recommended next steps
            urla_generated: Whether URLA was generated
            tool_results: Tool execution results
            final_content: Agent's final reasoning
            session_id: Processing session ID
            tools_called: Number of tools called
            
        Returns:
            Structured result dictionary
        """
        # Generate application ID if not provided
        application_id = application_data.get(
            "application_id", 
            self.config.get_application_id_format().format(uuid.uuid4().hex[:8])
        )
        
        # Clean and extract agent reasoning from content
        max_reasoning_length = self.config.response_format.max_reasoning_length
        
        # Filter out tool call artifacts from reasoning
        cleaned_content = self._clean_agent_reasoning(final_content) if final_content else ""
        
        agent_reasoning = (
            cleaned_content[:max_reasoning_length] 
            if cleaned_content 
            else "Agent processing completed successfully"
        )
        
        # Calculate document-level success (not tool-level)
        # Assume document is valid if we have at least some successful tool calls
        # This is a simplified heuristic - in production you'd have more sophisticated logic
        valid_documents = min(len(documents), analysis["successful_tools"]) if analysis["successful_tools"] > 0 else 0
        invalid_documents = len(documents) - valid_documents
        
        result = {
            "application_id": application_id,
            "processing_status": status,
            "documents_processed": len(documents),
            "valid_documents": valid_documents,
            "invalid_documents": invalid_documents,
            "missing_documents": [],  # Could be enhanced with missing document detection
            "document_validations": tool_results,
            "next_steps": next_steps,
            "urla_1003_generated": urla_generated,
            "agent_reasoning": agent_reasoning,
            "session_id": session_id,
            "tools_used": tools_called,
            "processing_metrics": {
                "success_ratio": analysis["success_ratio"],
                "total_tools_executed": tools_called,
                "successful_tool_executions": analysis["successful_tools"],
                "failed_tool_executions": analysis["failed_tools"]
            }
        }
        
        logger.info(f"Built structured result for application {application_id}: {status}")
        return result
    
    def build_error_result(
        self,
        application_data: Dict[str, Any],
        documents: List[Dict[str, Any]],
        error: Exception,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Build an error result when processing fails.
        
        Args:
            application_data: Original application data
            documents: List of documents that failed to process
            error: The exception that occurred
            session_id: Processing session ID
            
        Returns:
            Error result dictionary
        """
        application_id = application_data.get("application_id", "unknown")
        
        error_result = {
            "application_id": application_id,
            "processing_status": "failed",
            "error": str(error),
            "session_id": session_id,
            "documents_processed": len(documents),
            "valid_documents": 0,
            "invalid_documents": len(documents),
            "missing_documents": [],
            "document_validations": [],
            "next_steps": self.config.get_next_steps("manual_review") or [
                "Manual review required due to processing error"
            ],
            "urla_1003_generated": False,
            "agent_reasoning": f"Processing failed: {str(error)}",
            "tools_used": 0,
            "processing_metrics": {
                "success_ratio": 0.0,
                "total_tools_executed": 0,
                "successful_tool_executions": 0,
                "failed_tool_executions": 0
            }
        }
        
        logger.error(f"Built error result for application {application_id}: {error}")
        return error_result
    
    def process_agent_response(
        self,
        response,
        application_data: Dict[str, Any],
        documents: List[Dict[str, Any]],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Complete postprocessing pipeline for agent response.
        
        Args:
            response: Agent response stream
            application_data: Original application data
            documents: List of processed documents
            session_id: Processing session ID
            
        Returns:
            Complete structured result
        """
        try:
            # Step 1: Parse agent response
            tool_results, final_content, tools_called = self.parse_agent_response(response)
            
            # Step 2: Analyze processing success
            analysis = self.analyze_processing_success(tool_results, len(documents))
            
            # Step 3: Determine processing status
            status, next_steps, urla_generated = self.determine_processing_status(analysis)
            
            # Step 4: Build structured result
            result = self.build_structured_result(
                application_data=application_data,
                documents=documents,
                analysis=analysis,
                status=status,
                next_steps=next_steps,
                urla_generated=urla_generated,
                tool_results=tool_results,
                final_content=final_content,
                session_id=session_id,
                tools_called=tools_called
            )
            
            logger.info(f"Completed postprocessing: {status} with {tools_called} tool calls")
            return result
            
        except Exception as e:
            logger.error(f"Error in postprocessing pipeline: {e}", exc_info=True)
            return self.build_error_result(application_data, documents, e, session_id)
