"""
Agent Analysis Utilities

Reusable utilities for extracting and analyzing LangGraph agent execution details,
including tool calls, message flows, and execution patterns.

This module provides clean abstractions for understanding what happens
when agents execute, without any hardcoding or custom logging.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json


class MessageRole(Enum):
    """Standard message roles in agent conversations."""
    USER = "user"
    ASSISTANT = "assistant" 
    TOOL = "tool"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class MessageType(Enum):
    """Types of agent execution steps."""
    USER_INPUT = "user_input"
    AGENT_THINKING = "agent_thinking"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    AGENT_RESPONSE = "agent_response"
    UNKNOWN = "unknown"


@dataclass
class ToolCall:
    """Represents a single tool call made by an agent."""
    name: str
    args: Dict[str, Any]
    id: str
    
    def __str__(self) -> str:
        return f"{self.name}({self.args})"


@dataclass
class MessageAnalysis:
    """Analysis of a single message in an agent conversation."""
    index: int
    role: MessageRole
    message_type: MessageType
    content: str
    tool_calls: List[ToolCall]
    raw_message: Any
    
    @property
    def has_tool_calls(self) -> bool:
        """Check if this message contains tool calls."""
        return len(self.tool_calls) > 0
    
    @property
    def short_content(self) -> str:
        """Get truncated content for display."""
        if len(self.content) > 100:
            return self.content[:100] + "..."
        return self.content


@dataclass
class AgentExecutionAnalysis:
    """Complete analysis of an agent execution flow."""
    total_messages: int
    message_analyses: List[MessageAnalysis]
    total_tool_calls: int
    unique_tools_used: List[str]
    execution_pattern: List[MessageType]
    
    def get_tool_call_summary(self) -> Dict[str, int]:
        """Get summary of tool usage."""
        tool_counts = {}
        for analysis in self.message_analyses:
            for tool_call in analysis.tool_calls:
                tool_counts[tool_call.name] = tool_counts.get(tool_call.name, 0) + 1
        return tool_counts
    
    def get_messages_by_type(self, message_type: MessageType) -> List[MessageAnalysis]:
        """Get all messages of a specific type."""
        return [msg for msg in self.message_analyses if msg.message_type == message_type]


def extract_tool_calls_from_message(message: Any) -> List[ToolCall]:
    """
    Extract tool calls from a LangGraph message using the patterns found in the codebase.
    
    Handles multiple formats:
    - Direct tool_calls attribute (LangGraph native) 
    - OpenAI-style in additional_kwargs
    - Dictionary format
    """
    tool_calls = []
    
    # Method 1: Direct tool_calls attribute (LangGraph native)
    if hasattr(message, 'tool_calls') and message.tool_calls:
        for tool_call in message.tool_calls:
            # Handle both object and dictionary formats
            if isinstance(tool_call, dict):
                # Dictionary format (what we found in debug)
                tool_calls.append(ToolCall(
                    name=tool_call.get('name', 'unknown'),
                    args=tool_call.get('args', {}),
                    id=tool_call.get('id', 'unknown')
                ))
            elif hasattr(tool_call, 'name'):
                # Object format
                tool_calls.append(ToolCall(
                    name=tool_call.name,
                    args=getattr(tool_call, 'args', {}),
                    id=getattr(tool_call, 'id', 'unknown')
                ))
    
    # Method 2: OpenAI-style in additional_kwargs
    elif hasattr(message, 'additional_kwargs') and message.additional_kwargs.get('tool_calls'):
        for tool_call in message.additional_kwargs['tool_calls']:
            tool_calls.append(ToolCall(
                name=tool_call.get('function', {}).get('name', 'unknown'),
                args=tool_call.get('function', {}).get('arguments', {}),
                id=tool_call.get('id', 'unknown')
            ))
    
    # Method 3: Message is a dictionary itself
    elif isinstance(message, dict) and message.get('tool_calls'):
        for tool_call in message['tool_calls']:
            tool_calls.append(ToolCall(
                name=tool_call.get('name', 'unknown'),
                args=tool_call.get('args', {}),
                id=tool_call.get('id', 'unknown')
            ))
    
    return tool_calls


def get_message_role(message: Any) -> MessageRole:
    """Extract role from LangGraph message."""
    if hasattr(message, 'type'):
        # LangGraph message object
        msg_type = getattr(message, 'type', '')
        if msg_type == 'ai':
            return MessageRole.ASSISTANT
        elif msg_type == 'human':
            return MessageRole.USER
        elif msg_type == 'tool':
            return MessageRole.TOOL
        elif msg_type == 'system':
            return MessageRole.SYSTEM
        else:
            return MessageRole.UNKNOWN
    elif isinstance(message, dict):
        # Dictionary format
        role = message.get('role', '')
        try:
            return MessageRole(role)
        except ValueError:
            return MessageRole.UNKNOWN
    else:
        return MessageRole.UNKNOWN


def get_message_content(message: Any) -> str:
    """Extract content from LangGraph message."""
    if hasattr(message, 'content'):
        content = getattr(message, 'content', '')
        return str(content) if content is not None else ""
    elif isinstance(message, dict):
        content = message.get('content', '')
        return str(content) if content is not None else ""
    else:
        return str(message)


def determine_message_type(message: Any, role: MessageRole, has_tool_calls: bool) -> MessageType:
    """Determine the type of message in the agent execution flow."""
    if role == MessageRole.USER:
        return MessageType.USER_INPUT
    elif role == MessageRole.TOOL:
        return MessageType.TOOL_RESULT
    elif role == MessageRole.ASSISTANT:
        if has_tool_calls:
            return MessageType.TOOL_CALL
        else:
            # Check if this is thinking (empty content) or final response
            content = get_message_content(message)
            if not content.strip():
                return MessageType.AGENT_THINKING
            else:
                return MessageType.AGENT_RESPONSE
    else:
        return MessageType.UNKNOWN


def analyze_message(message: Any, index: int) -> MessageAnalysis:
    """Analyze a single message and extract all relevant information."""
    role = get_message_role(message)
    content = get_message_content(message)
    tool_calls = extract_tool_calls_from_message(message)
    message_type = determine_message_type(message, role, len(tool_calls) > 0)
    
    return MessageAnalysis(
        index=index,
        role=role,
        message_type=message_type,
        content=content,
        tool_calls=tool_calls,
        raw_message=message
    )


def analyze_agent_execution(agent_result: Dict[str, Any]) -> AgentExecutionAnalysis:
    """
    Analyze complete agent execution and extract all insights.
    
    Args:
        agent_result: Result from agent.invoke() call
        
    Returns:
        Complete analysis of the agent execution flow
    """
    messages = agent_result.get("messages", [])
    message_analyses = []
    
    # Analyze each message
    for i, message in enumerate(messages):
        analysis = analyze_message(message, i)
        message_analyses.append(analysis)
    
    # Extract execution insights
    total_tool_calls = sum(len(analysis.tool_calls) for analysis in message_analyses)
    unique_tools = set()
    execution_pattern = []
    
    for analysis in message_analyses:
        execution_pattern.append(analysis.message_type)
        for tool_call in analysis.tool_calls:
            unique_tools.add(tool_call.name)
    
    return AgentExecutionAnalysis(
        total_messages=len(messages),
        message_analyses=message_analyses,
        total_tool_calls=total_tool_calls,
        unique_tools_used=list(unique_tools),
        execution_pattern=execution_pattern
    )


def format_tool_call_for_display(tool_call: ToolCall, indent: int = 0) -> str:
    """Format a tool call for clean display."""
    spaces = "  " * indent
    args_str = json.dumps(tool_call.args, indent=2) if tool_call.args else "{}"
    
    return f"{spaces}🛠️ {tool_call.name}\n{spaces}   Args: {args_str}\n{spaces}   ID: {tool_call.id}"


def get_execution_summary(analysis: AgentExecutionAnalysis) -> str:
    """Get a human-readable execution summary."""
    tool_summary = analysis.get_tool_call_summary()
    tool_list = ", ".join([f"{tool}({count})" for tool, count in tool_summary.items()])
    
    pattern_str = " → ".join([msg_type.value for msg_type in analysis.execution_pattern])
    
    return f"""
Execution Summary:
- Total Messages: {analysis.total_messages}
- Tool Calls: {analysis.total_tool_calls}
- Tools Used: {tool_list or 'None'}
- Pattern: {pattern_str}
    """.strip()
