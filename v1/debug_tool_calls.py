#!/usr/bin/env python3
"""
Debug Tool Call Structure

Let's see exactly what's in the message objects to understand 
how to extract tool call information properly.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_message_structure(msg, index):
    """Debug the actual structure of each message."""
    console = Console()
    
    console.print(f"\n[bold cyan]🔍 DEBUGGING MESSAGE {index}[/bold cyan]")
    console.print("=" * 50)
    
    # Show type
    console.print(f"[yellow]Type:[/yellow] {type(msg)}")
    
    # Show all attributes
    console.print(f"[yellow]Attributes:[/yellow]")
    attrs = dir(msg)
    for attr in attrs:
        if not attr.startswith('_'):
            try:
                value = getattr(msg, attr)
                if callable(value):
                    console.print(f"  {attr}: <method>")
                else:
                    # Truncate long values
                    str_val = str(value)
                    if len(str_val) > 100:
                        str_val = str_val[:100] + "..."
                    console.print(f"  {attr}: {str_val}")
            except:
                console.print(f"  {attr}: <error accessing>")
    
    # Check for tool_calls specifically
    console.print(f"[yellow]Tool Call Checks:[/yellow]")
    
    # Method 1: Direct tool_calls attribute
    if hasattr(msg, 'tool_calls'):
        tool_calls = getattr(msg, 'tool_calls')
        console.print(f"  hasattr(msg, 'tool_calls'): True")
        console.print(f"  msg.tool_calls: {tool_calls}")
        console.print(f"  type(msg.tool_calls): {type(tool_calls)}")
        console.print(f"  len(msg.tool_calls): {len(tool_calls) if tool_calls else 'None'}")
        
        if tool_calls:
            for i, tc in enumerate(tool_calls):
                console.print(f"    Tool Call {i}:")
                console.print(f"      Type: {type(tc)}")
                console.print(f"      Attributes: {dir(tc) if hasattr(tc, '__dict__') else 'N/A'}")
                if hasattr(tc, 'name'):
                    console.print(f"      Name: {tc.name}")
                if hasattr(tc, 'args'):
                    console.print(f"      Args: {tc.args}")
    else:
        console.print(f"  hasattr(msg, 'tool_calls'): False")
    
    # Method 2: additional_kwargs
    if hasattr(msg, 'additional_kwargs'):
        additional_kwargs = getattr(msg, 'additional_kwargs')
        console.print(f"  hasattr(msg, 'additional_kwargs'): True")
        console.print(f"  msg.additional_kwargs: {additional_kwargs}")
        if isinstance(additional_kwargs, dict) and 'tool_calls' in additional_kwargs:
            console.print(f"  Found tool_calls in additional_kwargs!")
    else:
        console.print(f"  hasattr(msg, 'additional_kwargs'): False")
    
    console.print("-" * 50)

def main():
    """Debug tool call structure."""
    console = Console()
    
    console.print(Panel(
        "Tool Call Structure Debug\n\n"
        "This will show the exact structure of messages\n"
        "to understand how to extract tool calls properly.",
        title="🔍 Debug Script",
        border_style="cyan"
    ))
    
    try:
        # Import after path setup
        from mortgage_processor.agents.mortgage_advisor_agent import create_mortgage_advisor_agent
        
        console.print("\n🤖 Creating MortgageAdvisorAgent...")
        agent = create_mortgage_advisor_agent()
        
        # Test input that should trigger tool calls
        test_input = {
            "messages": [
                {"role": "user", "content": "Can you explain FHA loans?"}
            ]
        }
        
        console.print(f"\n💬 User Input: {test_input['messages'][0]['content']}")
        console.print("🔄 Invoking agent...")
        
        # Invoke agent
        result = agent.invoke(test_input)
        
        console.print(f"✅ Agent responded with {len(result.get('messages', []))} messages")
        
        # Debug each message
        messages = result.get("messages", [])
        for i, msg in enumerate(messages):
            debug_message_structure(msg, i)
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")

if __name__ == "__main__":
    main()
