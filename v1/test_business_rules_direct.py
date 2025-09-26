#!/usr/bin/env python3
"""
Direct Business Rules Test - Bypass Broken Imports

Test Neo4j business rule tools directly without going through 
the mortgage_processor package that has supervisor import issues.
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel
import json

console = Console()

def test_neo4j_tools():
    """Test Neo4j business rule tools directly"""
    console.print(Panel("🧪 Testing Neo4j Business Rules Directly", border_style="green"))
    
    # Setup database connection first
    from database.setup.connection import initialize_connection, get_connection
    initialize_connection()
    connection = get_connection()
    
    console.print(f"✅ [green]Database connected: {connection.database}[/green]")
    
    # Test what's in the database
    with connection.driver.session(database=connection.database) as session:
        result = session.run("MATCH (lp:LoanProgram) RETURN lp.name as name, lp.min_credit_score as min_credit")
        programs = [(record["name"], record["min_credit"]) for record in result]
        console.print(f"[cyan]📊 Loan Programs:[/cyan] {programs}")
        
        result = session.run("MATCH (qm:QM_Rule) RETURN qm.rule_id as rule_id LIMIT 3")
        qm_rules = [record["rule_id"] for record in result]
        console.print(f"[cyan]⚖️ QM Rules:[/cyan] {qm_rules}")
    
    # Now test tool directly by importing just the tool file
    console.print("\n🔄 [yellow]Testing recommend_loan_program tool directly...[/yellow]")
    
    try:
        # Import tool file directly - add its directory to path
        tool_dir = "/Users/raghurambanda/iloul/v1/src/mortgage_processor/agents/mortgage_advisor_agent/tools"
        sys.path.insert(0, tool_dir)
        
        # Also add utils directory
        utils_dir = "/Users/raghurambanda/iloul/v1/src/mortgage_processor/utils"
        sys.path.insert(0, utils_dir)
        
        # Set up environment to find db utils
        os.environ['PYTHONPATH'] = '/Users/raghurambanda/iloul/v1/src'
        
        # Import the specific function we need
        from recommend_loan_program import recommend_loan_program
        
        # Test with Sarah's profile
        result = recommend_loan_program(
            credit_score=720,
            down_payment_percent=0.133,  # 13.3%
            annual_income=95000,
            monthly_debts=850,
            property_type="single_family",
            property_location="suburban",
            military_status="none",
            first_time_buyer=True
        )
        
        console.print("[green]✅ Tool executed successfully![/green]")
        
        if isinstance(result, dict):
            if "recommendations" in result:
                recs = result["recommendations"]
                console.print(f"[green]🎯 Found {len(recs)} loan program recommendations![/green]")
                
                for i, rec in enumerate(recs):
                    program = rec.get("program_name", "Unknown")
                    score = rec.get("recommendation_score", 0)
                    reason = rec.get("recommendation_reason", "No reason")
                    
                    console.print(f"  [bold]{i+1}. {program}[/bold] (Score: {score})")
                    console.print(f"     💡 {reason[:100]}...")
                    
                    if "qualification_details" in rec:
                        details = rec["qualification_details"][:2]  # First 2 details
                        for detail in details:
                            console.print(f"     ✓ {detail}")
                    
                    console.print()
            
            if "borrower_analysis" in result:
                analysis = result["borrower_analysis"]
                strengths = analysis.get("strengths", [])
                considerations = analysis.get("considerations", [])
                
                console.print(f"[cyan]📈 Borrower Profile Analysis:[/cyan]")
                console.print(f"  [green]Strengths ({len(strengths)}):[/green]")
                for strength in strengths[:3]:  # First 3
                    console.print(f"    ✓ {strength}")
                
                console.print(f"  [yellow]Considerations ({len(considerations)}):[/yellow]")
                for consideration in considerations[:3]:  # First 3
                    console.print(f"    ⚠️ {consideration}")
            
            if "success" in result:
                console.print(f"[green]✅ Success:[/green] {result['success']}")
        else:
            console.print(f"[yellow]📄 Result:[/yellow] {str(result)[:500]}...")
            
    except ImportError as e:
        console.print(f"[red]❌ Import Error:[/red] {e}")
        console.print("[yellow]Tool import still blocked by dependencies[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Execution Error:[/red] {e}")
        import traceback
        traceback.print_exc()

def main():
    console.print(Panel(
        "[bold green]🔧 Direct Neo4j Business Rules Test[/bold green]\n" +
        "Testing business rule tools directly to bypass supervisor import issues",
        border_style="green"
    ))
    
    test_neo4j_tools()
    
    console.print(Panel(
        "[bold blue]📊 Summary[/bold blue]\n" +
        "• If tools work: Supervisor handoff is the issue\n" +
        "• If tools fail: Core tool configuration needs fixing\n" +
        "• If database works but tools don't: Import/dependency issues",
        border_style="blue"
    ))

if __name__ == "__main__":
    main()
