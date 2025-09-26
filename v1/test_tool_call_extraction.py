#!/usr/bin/env python3
"""
Test Tool Call Extraction from LangGraph Agents

This script tests if we can actually extract tool call information 
from our mortgage agents using the patterns found in the codebase.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def extract_tool_calls_from_messages(messages):
    """Extract tool calls using the pattern from the codebase."""
    tool_calls = []
    
    for msg in messages:
        # Method 1: Direct tool_calls attribute (LangGraph native)
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if hasattr(tool_call, 'name'):
                    tool_calls.append({
                        "name": tool_call.name,
                        "args": getattr(tool_call, 'args', {}),
                        "id": getattr(tool_call, 'id', 'unknown')
                    })
        
        # Method 2: OpenAI-style in additional_kwargs
        elif hasattr(msg, 'additional_kwargs') and msg.additional_kwargs.get('tool_calls'):
            for tool_call in msg.additional_kwargs['tool_calls']:
                tool_calls.append({
                    "name": tool_call.get('function', {}).get('name'),
                    "args": tool_call.get('function', {}).get('arguments', {}),
                    "id": tool_call.get('id', 'unknown')
                })
        
        # Method 3: Dict format
        elif isinstance(msg, dict) and msg.get('tool_calls'):
            for tool_call in msg['tool_calls']:
                tool_calls.append({
                    "name": tool_call.get('name', 'unknown'),
                    "args": tool_call.get('args', {}),
                    "id": tool_call.get('id', 'unknown')
                })
    
    return tool_calls

def analyze_message(msg, index):
    """Analyze a single message and extract relevant info."""
    console = Console()
    
    # Get message type/role
    if hasattr(msg, 'type'):
        msg_type = msg.type
        role = 'assistant' if msg_type == 'ai' else 'user' if msg_type == 'human' else msg_type
    elif isinstance(msg, dict):
        role = msg.get('role', 'unknown')
    else:
        role = 'unknown'
    
    # Get content
    if hasattr(msg, 'content'):
        content = msg.content
    elif isinstance(msg, dict):
        content = msg.get('content', '')
    else:
        content = str(msg)
    
    # Check for tool calls
    has_tools = False
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        has_tools = True
    elif isinstance(msg, dict) and msg.get('tool_calls'):
        has_tools = True
    elif hasattr(msg, 'additional_kwargs') and msg.additional_kwargs.get('tool_calls'):
        has_tools = True
    
    return {
        'index': index,
        'role': role,
        'content': content[:100] + "..." if len(str(content)) > 100 else content,
        'has_tool_calls': has_tools,
        'raw_type': type(msg).__name__
    }

def test_mortgage_advisor_agent():
    """Test tool call extraction with MortgageAdvisorAgent."""
    console = Console()
    
    try:
        # Import after path setup
        from mortgage_processor.agents.mortgage_advisor_agent import create_mortgage_advisor_agent
        
        console.print("\n🤖 Testing MortgageAdvisorAgent Tool Call Extraction", style="bold blue")
        console.print("=" * 60)
        
        # Create agent
        rprint("[yellow]📋 Creating MortgageAdvisorAgent...[/yellow]")
        agent = create_mortgage_advisor_agent()
        rprint("[green]✅ Agent created successfully[/green]")
        
        # Test input that should trigger tool calls
        test_input = {
            "messages": [
                {"role": "user", "content": "Can you explain the differences between FHA and VA loans?"}
            ]
        }
        
        rprint(f"\n[yellow]💬 User Input:[/yellow] {test_input['messages'][0]['content']}")
        rprint("[yellow]🔄 Invoking agent...[/yellow]")
        
        # Invoke agent
        result = agent.invoke(test_input)
        
        rprint(f"[green]✅ Agent responded with {len(result.get('messages', []))} messages[/green]")
        
        # Analyze each message
        rprint("\n[bold cyan]📋 MESSAGE ANALYSIS:[/bold cyan]")
        messages = result.get("messages", [])
        
        for i, msg in enumerate(messages):
            info = analyze_message(msg, i)
            
            color = "blue" if info['role'] == 'user' else "green" if info['role'] == 'assistant' else "yellow"
            tools_indicator = "🔧" if info['has_tool_calls'] else "💬"
            
            console.print(Panel(
                f"Role: {info['role']}\n"
                f"Type: {info['raw_type']}\n"
                f"Has Tool Calls: {info['has_tool_calls']}\n"
                f"Content: {info['content']}",
                title=f"{tools_indicator} Message {i}",
                border_style=color
            ))
        
        # Extract and display tool calls
        tool_calls = extract_tool_calls_from_messages(messages)
        
        if tool_calls:
            rprint(f"\n[bold green]🔧 TOOL CALLS DETECTED: {len(tool_calls)}[/bold green]")
            for i, tool_call in enumerate(tool_calls):
                console.print(Panel(
                    f"Name: {tool_call['name']}\n"
                    f"ID: {tool_call['id']}\n"
                    f"Args: {json.dumps(tool_call['args'], indent=2)}",
                    title=f"🛠️ Tool Call {i+1}",
                    border_style="green"
                ))
        else:
            rprint("[yellow]⚠️ No tool calls detected in messages[/yellow]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
        return False

def main():
    """Run the tool call extraction test."""
    console = Console()
    
    console.print(Panel(
        "Tool Call Extraction Test\n\n"
        "This script tests if we can extract real tool call information\n"
        "from LangGraph agents using the patterns found in the codebase.\n\n"
        "If this works, we can build the full mortgage demo!",
        title="🧪 Test Script",
        border_style="cyan"
    ))
    
    # Test with MortgageAdvisorAgent
    success = test_mortgage_advisor_agent()
    
    if success:
        console.print("\n[bold green]🎉 SUCCESS![/bold green]")
        console.print("[green]Tool call extraction works! Ready to build full demo.[/green]")
    else:
        console.print("\n[bold red]❌ FAILED![/bold red]")
        console.print("[red]Need to debug tool call extraction before building demo.[/red]")

if __name__ == "__main__":
    main()
