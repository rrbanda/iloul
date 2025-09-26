#!/usr/bin/env python3
"""
Mortgage Terminal Demo

Uses the same tool call extraction patterns as the repo's test files
to show real agent execution on the terminal. No custom logging - 
only real LangGraph data with terminal formatting.

Based on patterns from:
- test_end_to_end.py 
- test_langsmith_evaluations.py
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich import print as rprint
import json
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Use the same extraction functions as the repo's test files
def _extract_message_content(message):
    """Extract content from either dict or LangChain message object."""
    if hasattr(message, 'content'):
        return getattr(message, 'content', '')
    elif isinstance(message, dict):
        return message.get('content', '')
    else:
        return str(message)

def _get_message_role(message):
    """Get role from either dict or LangChain message object."""
    if hasattr(message, 'type'):
        msg_type = getattr(message, 'type', '')
        if msg_type == 'ai':
            return 'assistant'
        elif msg_type == 'human':
            return 'user'
        elif msg_type == 'tool':
            return 'tool'
        else:
            return msg_type
    elif isinstance(message, dict):
        return message.get('role', '')
    else:
        return 'unknown'

def _has_tool_calls(message):
    """Check if message has tool calls - same as test files."""
    if hasattr(message, 'tool_calls'):
        tool_calls = getattr(message, 'tool_calls', [])
        return len(tool_calls) > 0
    elif isinstance(message, dict):
        tool_calls = message.get('tool_calls', [])
        return len(tool_calls) > 0
    else:
        return False

def _get_tool_calls(message):
    """Get tool calls from message - same as test files."""
    if hasattr(message, 'tool_calls'):
        return getattr(message, 'tool_calls', [])
    elif isinstance(message, dict):
        return message.get('tool_calls', [])
    else:
        return []

def _extract_tool_calls(messages):
    """Extract tool calls from messages - same as LangSmith evaluation code."""
    tool_calls = []
    for msg in messages:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                # Handle dictionary format (what we actually get)
                if isinstance(tool_call, dict):
                    tool_calls.append({
                        "name": tool_call.get('name', 'unknown'),
                        "args": tool_call.get('args', {}),
                        "id": tool_call.get('id', 'unknown')
                    })
                elif hasattr(tool_call, 'name'):
                    tool_calls.append({
                        "name": tool_call.name,
                        "args": getattr(tool_call, 'args', {}),
                        "id": getattr(tool_call, 'id', 'unknown')
                    })
        elif hasattr(msg, 'additional_kwargs') and msg.additional_kwargs.get('tool_calls'):
            for tool_call in msg.additional_kwargs['tool_calls']:
                tool_calls.append({
                    "name": tool_call.get('function', {}).get('name'),
                    "args": tool_call.get('function', {}).get('arguments', {}),
                    "id": tool_call.get('id', 'unknown')
                })
    return tool_calls

def display_message_analysis(messages, console):
    """Display message analysis using repo patterns."""
    rprint("\n[bold cyan]🔍 MESSAGE FLOW ANALYSIS[/bold cyan]")
    rprint("Following the same pattern as repo test files:")
    
    for i, message in enumerate(messages):
        role = _get_message_role(message)
        content = _extract_message_content(message)
        has_tools = _has_tool_calls(message)
        
        # Choose display style based on role and tools
        if role == 'user':
            icon = "👤"
            color = "blue"
        elif role == 'assistant' and has_tools:
            icon = "🔧"  
            color = "green"
        elif role == 'tool':
            icon = "🗄️"
            color = "yellow"
        elif role == 'assistant':
            icon = "🤖"
            color = "green"
        else:
            icon = "❓"
            color = "white"
        
        # Show content (truncated)
        display_content = content[:100] + "..." if len(content) > 100 else content
        
        panel_content = f"Role: {role}\nContent: {display_content}"
        
        # Add tool calls if present (using repo extraction)
        if has_tools:
            tool_calls = _get_tool_calls(message)
            panel_content += f"\nTool Calls: {len(tool_calls)}"
            for tool_call in tool_calls:
                if isinstance(tool_call, dict):
                    name = tool_call.get('name', 'unknown')
                    args = tool_call.get('args', {})
                    panel_content += f"\n  • {name}({args})"
        
        console.print(Panel(
            panel_content,
            title=f"{icon} Message {i}",
            border_style=color
        ))

def display_tool_calls_summary(messages, console):
    """Display tool calls summary using repo extraction methods."""
    tool_calls = _extract_tool_calls(messages)
    
    if tool_calls:
        rprint(f"\n[bold green]🛠️ TOOL CALLS DETECTED: {len(tool_calls)}[/bold green]")
        rprint("Extracted using the same method as LangSmith evaluations:")
        
        for i, tool_call in enumerate(tool_calls):
            console.print(Panel(
                f"Name: {tool_call['name']}\n"
                f"Args: {json.dumps(tool_call['args'], indent=2)}\n"
                f"ID: {tool_call['id']}",
                title=f"🔧 Tool Call {i+1}",
                border_style="green"
            ))
    else:
        rprint("[yellow]⚠️ No tool calls found[/yellow]")

def run_mortgage_advisor_demo():
    """Run mortgage advisor demo using repo patterns."""
    console = Console()
    
    console.print(Panel(
        "Mortgage Knowledge Graph Demo\n\n"
        "Using the same tool call extraction patterns as the repo's\n"
        "test files and LangSmith evaluation code.\n\n"
        "Shows REAL agent execution - no custom logging!",
        title="🏦 Mortgage Terminal Demo",
        border_style="cyan"
    ))
    
    try:
        # Import and create agent
        from mortgage_processor.agents.mortgage_advisor_agent import create_mortgage_advisor_agent
        
        rprint("\n[yellow]📋 Creating MortgageAdvisorAgent...[/yellow]")
        agent = create_mortgage_advisor_agent()
        rprint("[green]✅ Agent created[/green]")
        
        # Demo scenarios
        scenarios = [
            "Can you explain the differences between FHA and VA loans?",
            "What loan program would you recommend for a first-time buyer with 620 credit score?",
            "I'm a veteran with no down payment. What are my options?"
        ]
        
        for i, user_input in enumerate(scenarios, 1):
            console.print(f"\n[bold cyan]🎬 SCENARIO {i}[/bold cyan]")
            console.print("=" * 60)
            
            rprint(f"[blue]👤 User:[/blue] {user_input}")
            
            # Create test input
            test_input = {
                "messages": [{"role": "user", "content": user_input}]
            }
            
            rprint("[yellow]🔄 Invoking agent (real LangGraph execution)...[/yellow]")
            
            # Real agent invoke - no custom logging
            result = agent.invoke(test_input)
            messages = result.get("messages", [])
            
            rprint(f"[green]✅ Agent completed with {len(messages)} messages[/green]")
            
            # Display using repo patterns
            display_message_analysis(messages, console)
            display_tool_calls_summary(messages, console)
            
            # Show final response
            if messages:
                final_message = messages[-1]
                final_content = _extract_message_content(final_message)
                final_role = _get_message_role(final_message)
                
                if final_role == 'assistant' and final_content.strip():
                    console.print(Panel(
                        final_content,
                        title="🤖 Final Agent Response",
                        border_style="green"
                    ))
            
            if i < len(scenarios):
                rprint("\n[dim]Press Enter for next scenario...[/dim]")
                input()
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return False

def run_application_agent_demo():
    """Run application agent demo."""
    console = Console()
    
    console.print(f"\n[bold cyan]🏦 APPLICATION AGENT DEMO[/bold cyan]")
    console.print("=" * 50)
    
    try:
        from mortgage_processor.agents.application_agent import create_application_agent
        
        rprint("[yellow]📋 Creating ApplicationAgent...[/yellow]")
        agent = create_application_agent()
        rprint("[green]✅ Agent created[/green]")
        
        user_input = "I want to apply for a mortgage. My income is $85,000 and I'm looking at a $400,000 house."
        rprint(f"[blue]👤 User:[/blue] {user_input}")
        
        test_input = {
            "messages": [{"role": "user", "content": user_input}]
        }
        
        rprint("[yellow]🔄 Invoking agent...[/yellow]")
        result = agent.invoke(test_input)
        messages = result.get("messages", [])
        
        # Display using same patterns
        display_message_analysis(messages, console)
        display_tool_calls_summary(messages, console)
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ ApplicationAgent demo failed: {e}[/red]")
        return False

def main():
    """Run the mortgage terminal demo."""
    console = Console()
    
    # Run mortgage advisor demo
    success1 = run_mortgage_advisor_demo()
    
    # Run application agent demo
    success2 = run_application_agent_demo()
    
    if success1 and success2:
        console.print("\n[bold green]🎉 DEMO COMPLETED SUCCESSFULLY![/bold green]")
        console.print("[green]All tool call extraction used real repo patterns[/green]")
    else:
        console.print("\n[bold red]❌ DEMO HAD ISSUES[/bold red]")

if __name__ == "__main__":
    main()
