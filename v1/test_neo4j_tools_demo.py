#!/usr/bin/env python3
"""
Test Neo4j Tools Demo - Force Agent Tool Usage

This demo tests agents with specific queries that MUST trigger Neo4j tool usage
to prove the business rules are working.
"""

import json
import requests
from rich.console import Console
from rich.panel import Panel

console = Console()

# Agent system API configuration
AGENT_URL = "http://127.0.0.1:2024"

def create_thread():
    """Create a new thread"""
    response = requests.post(f"{AGENT_URL}/threads", json={})
    return response.json()["thread_id"]

def get_assistant():
    """Get the mortgage assistant"""
    response = requests.post(f"{AGENT_URL}/assistants/search", json={})
    assistants = response.json()
    for assistant in assistants:
        if assistant.get("graph_id") == "mortgage_processing":
            return assistant["assistant_id"]
    return None

def invoke_assistant(assistant_id, thread_id, message):
    """Invoke assistant"""
    payload = {
        "input": {"messages": [{"role": "user", "content": message}]},
        "assistant_id": assistant_id
    }
    response = requests.post(f"{AGENT_URL}/threads/{thread_id}/runs/wait", json=payload)
    return response.json()

def show_tool_calls(result, query_description):
    """Extract and display tool calls"""
    console.print(f"\n[bold blue]🔍 {query_description}[/bold blue]")
    
    messages = result.get("messages", [])
    tool_calls_found = False
    
    for msg in messages:
        if msg.get("type") == "ai":
            tool_calls = msg.get("tool_calls", [])
            if tool_calls:
                for tool_call in tool_calls:
                    tool_name = tool_call.get("name", "Unknown")
                    if not tool_name.startswith("transfer"):
                        tool_calls_found = True
                        console.print(f"[green]🛠️ Neo4j Tool Used:[/green] {tool_name}")
                        
                        # Show arguments
                        args = tool_call.get("args", {})
                        if args:
                            console.print(f"[yellow]📊 Arguments:[/yellow] {args}")
                            
        elif msg.get("type") == "tool":
            tool_name = msg.get("name", "Unknown")
            content = msg.get("content", "")
            if not tool_name.startswith("transfer") and content:
                console.print(f"[cyan]📤 Neo4j Result:[/cyan] {content[:200]}...")
    
    if not tool_calls_found:
        console.print("[red]❌ No Neo4j tools used - only transfers![/red]")

def main():
    console.print(Panel(
        "[bold green]🧪 Neo4j Business Rules Test[/bold green]\nTesting specific queries that MUST use Neo4j tools",
        border_style="green"
    ))
    
    # Setup
    assistant_id = get_assistant()
    thread_id = create_thread()
    
    if not assistant_id or not thread_id:
        console.print("[red]Failed to setup test environment[/red]")
        return
    
    console.print(f"✅ [green]Setup complete: {assistant_id[:8]}.../{thread_id[:8]}...[/green]")
    
    # Test 1: Specific loan program recommendation (should use recommend_loan_program tool)
    test_1 = """Based on my profile, recommend specific loan programs:
- Credit Score: 720
- Annual Income: $95,000  
- Down Payment: $60,000 (13.3%)
- Monthly Debts: $850
- Property: Single family, suburban
- First-time buyer: Yes"""
    
    result_1 = invoke_assistant(assistant_id, thread_id, test_1)
    show_tool_calls(result_1, "TEST 1: Loan Program Recommendation (should use recommend_loan_program)")
    
    # Test 2: Specific qualification analysis (should use check_qualification_requirements)  
    test_2 = """Analyze my qualification for FHA and Conventional loans:
- Credit Score: 680
- Down Payment Available: 5%
- Current DTI: 35%
- Property Location: Urban
- Military Status: None"""
    
    result_2 = invoke_assistant(assistant_id, thread_id, test_2)
    show_tool_calls(result_2, "TEST 2: Qualification Analysis (should use check_qualification_requirements)")
    
    # Test 3: Credit risk analysis (should use underwriting tools)
    test_3 = """Perform underwriting credit analysis:
- Credit Score: 640
- Loan Program: FHA
- Bankruptcy: 3 years ago
- Late Payments: 2 in last 12 months
- Collections: 1 open account
- Credit History: 8 years"""
    
    result_3 = invoke_assistant(assistant_id, thread_id, test_3)
    show_tool_calls(result_3, "TEST 3: Credit Risk Analysis (should use analyze_credit_risk)")
    
    console.print(Panel(
        "[bold blue]🎯 Test Complete![/bold blue]\nIf agents are working correctly, you should see Neo4j tool calls above.",
        border_style="blue"
    ))

if __name__ == "__main__":
    main()
