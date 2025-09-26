#!/usr/bin/env python3
"""
Test Agent Analysis Utility

Test the reusable agent analysis utilities with our mortgage agents
to ensure they work correctly before building the demo.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mortgage_processor.utils.agent_analysis import (
    analyze_agent_execution,
    get_execution_summary,
    format_tool_call_for_display,
    MessageType
)


def test_mortgage_advisor_analysis():
    """Test the agent analysis utility with MortgageAdvisorAgent."""
    console = Console()
    
    try:
        # Import mortgage advisor agent
        from mortgage_processor.agents.mortgage_advisor_agent import create_mortgage_advisor_agent
        
        console.print("\n🤖 Testing Agent Analysis Utility with MortgageAdvisorAgent", style="bold blue")
        console.print("=" * 70)
        
        # Create agent
        rprint("[yellow]📋 Creating MortgageAdvisorAgent...[/yellow]")
        agent = create_mortgage_advisor_agent()
        rprint("[green]✅ Agent created successfully[/green]")
        
        # Test input that should trigger tool calls
        test_input = {
            "messages": [
                {"role": "user", "content": "Can you compare FHA and VA loans for me?"}
            ]
        }
        
        rprint(f"\n[yellow]💬 User Input:[/yellow] {test_input['messages'][0]['content']}")
        rprint("[yellow]🔄 Invoking agent...[/yellow]")
        
        # Invoke agent and analyze
        result = agent.invoke(test_input)
        analysis = analyze_agent_execution(result)
        
        rprint(f"[green]✅ Agent execution analyzed successfully[/green]")
        
        # Display execution summary
        summary = get_execution_summary(analysis)
        console.print(Panel(summary, title="📊 Execution Summary", border_style="cyan"))
        
        # Display each message analysis
        rprint("\n[bold cyan]📋 MESSAGE-BY-MESSAGE ANALYSIS:[/bold cyan]")
        
        for msg_analysis in analysis.message_analyses:
            # Choose color based on message type
            if msg_analysis.message_type == MessageType.USER_INPUT:
                color = "blue"
                icon = "💬"
            elif msg_analysis.message_type == MessageType.TOOL_CALL:
                color = "green"
                icon = "🔧"
            elif msg_analysis.message_type == MessageType.TOOL_RESULT:
                color = "yellow" 
                icon = "📊"
            elif msg_analysis.message_type == MessageType.AGENT_RESPONSE:
                color = "green"
                icon = "🤖"
            else:
                color = "white"
                icon = "❓"
            
            # Build panel content
            content_lines = [
                f"Role: {msg_analysis.role.value}",
                f"Type: {msg_analysis.message_type.value}",
                f"Content: {msg_analysis.short_content}",
            ]
            
            # Add tool calls if present
            if msg_analysis.has_tool_calls:
                content_lines.append(f"Tool Calls: {len(msg_analysis.tool_calls)}")
                for tool_call in msg_analysis.tool_calls:
                    content_lines.append(f"  • {tool_call.name}({tool_call.args})")
            
            console.print(Panel(
                "\n".join(content_lines),
                title=f"{icon} Message {msg_analysis.index}",
                border_style=color
            ))
        
        # Test specific analysis features
        rprint("\n[bold cyan]🔍 DETAILED TOOL CALL ANALYSIS:[/bold cyan]")
        
        tool_call_messages = analysis.get_messages_by_type(MessageType.TOOL_CALL)
        if tool_call_messages:
            for msg in tool_call_messages:
                for tool_call in msg.tool_calls:
                    formatted = format_tool_call_for_display(tool_call)
                    console.print(Panel(formatted, title="🛠️ Tool Call Details", border_style="green"))
        else:
            rprint("[yellow]⚠️ No tool calls found in analysis[/yellow]")
        
        # Test tool usage summary
        tool_summary = analysis.get_tool_call_summary()
        if tool_summary:
            rprint(f"\n[bold green]🔧 TOOL USAGE SUMMARY:[/bold green]")
            for tool_name, count in tool_summary.items():
                rprint(f"  • {tool_name}: {count} calls")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
        return False


def test_application_agent_analysis():
    """Test with ApplicationAgent to verify utility works across different agents."""
    console = Console()
    
    try:
        # Import application agent  
        from mortgage_processor.agents.application_agent import create_application_agent
        
        console.print("\n🏦 Testing with ApplicationAgent", style="bold blue")
        console.print("=" * 50)
        
        # Create agent
        rprint("[yellow]📋 Creating ApplicationAgent...[/yellow]")
        agent = create_application_agent()
        rprint("[green]✅ Agent created successfully[/green]")
        
        # Test input for application processing
        test_input = {
            "messages": [
                {"role": "user", "content": "I want to apply for a mortgage. I make $75,000 per year and looking at a $300,000 house."}
            ]
        }
        
        rprint(f"\n[yellow]💬 User Input:[/yellow] {test_input['messages'][0]['content']}")
        rprint("[yellow]🔄 Invoking agent...[/yellow]")
        
        # Invoke and analyze
        result = agent.invoke(test_input)
        analysis = analyze_agent_execution(result)
        
        # Quick summary
        summary = get_execution_summary(analysis)
        console.print(Panel(summary, title="📊 ApplicationAgent Analysis", border_style="cyan"))
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ ApplicationAgent test failed: {e}[/red]")
        return False


def main():
    """Test the agent analysis utility."""
    console = Console()
    
    console.print(Panel(
        "Agent Analysis Utility Test\n\n"
        "Testing the reusable agent analysis utilities with mortgage agents.\n"
        "This ensures our tool call extraction and execution analysis works\n"
        "before building the full demo.",
        title="🧪 Utility Test",
        border_style="cyan"
    ))
    
    # Test with MortgageAdvisorAgent
    success1 = test_mortgage_advisor_analysis()
    
    # Test with ApplicationAgent
    success2 = test_application_agent_analysis() 
    
    if success1 and success2:
        console.print("\n[bold green]🎉 ALL TESTS PASSED![/bold green]")
        console.print("[green]Agent analysis utility is working correctly.[/green]")
        console.print("[green]Ready to build the colorful terminal demo![/green]")
    else:
        console.print("\n[bold red]❌ SOME TESTS FAILED![/bold red]")
        console.print("[red]Need to fix utility before building demo.[/red]")


if __name__ == "__main__":
    main()
