#!/usr/bin/env python3
"""
Test Direct Agent - Bypass Supervisor

Test individual agents directly to see if the issue is with:
1. The supervisor handoff mechanism, OR
2. The agents themselves not using tools
"""

import sys
sys.path.append('src')

from rich.console import Console
from rich.panel import Panel

console = Console()

# Test without full imports that cause supervisor issues
def test_database_tools_directly():
    """Test the database tools directly"""
    console.print(Panel("🧪 Testing Database Tools Directly", border_style="green"))
    
    try:
        # Test the loan recommendation tool directly
        from mortgage_processor.agents.mortgage_advisor_agent.tools.recommend_loan_program import recommend_loan_program
        
        console.print("🔄 [yellow]Testing recommend_loan_program tool directly...[/yellow]")
        
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
        console.print(f"[cyan]📊 Result Type:[/cyan] {type(result)}")
        
        if isinstance(result, dict):
            # Check if it contains actual business rule analysis
            if "recommendations" in result:
                console.print(f"[green]🎯 Found {len(result['recommendations'])} loan recommendations[/green]")
                for i, rec in enumerate(result['recommendations'][:2]):  # Show first 2
                    console.print(f"  {i+1}. {rec.get('program_name', 'Unknown')} - Score: {rec.get('recommendation_score', 'N/A')}")
            
            if "borrower_analysis" in result:
                analysis = result["borrower_analysis"]
                console.print(f"[cyan]📈 Borrower Strengths:[/cyan] {len(analysis.get('strengths', []))}")
                console.print(f"[cyan]⚠️ Considerations:[/cyan] {len(analysis.get('considerations', []))}")
            
            console.print(f"[blue]📋 Full result keys:[/blue] {list(result.keys())}")
        else:
            console.print(f"[yellow]📄 Result:[/yellow] {str(result)[:300]}...")
            
    except ImportError as e:
        console.print(f"[red]❌ Import Error:[/red] {e}")
        console.print("[yellow]This means supervisor import issues are blocking direct tool testing[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Tool Error:[/red] {e}")
        console.print("[yellow]This means the Neo4j tools themselves have issues[/yellow]")

def test_database_connection():
    """Test if the database connection works"""
    console.print(Panel("🔗 Testing Database Connection", border_style="blue"))
    
    try:
        from database.setup.connection import get_connection
        
        connection = get_connection()
        if connection:
            console.print("[green]✅ Database connection successful[/green]")
            
            # Test basic query
            with connection.driver.session(database=connection.database) as session:
                result = session.run("MATCH (lp:LoanProgram) RETURN count(lp) as count")
                count = result.single()["count"]
                console.print(f"[cyan]📊 Loan Programs in DB:[/cyan] {count}")
                
                result = session.run("MATCH (br:BusinessRule) RETURN count(br) as count")
                count = result.single()["count"]  
                console.print(f"[cyan]⚖️ Business Rules in DB:[/cyan] {count}")
                
        else:
            console.print("[red]❌ Database connection failed[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Database Error:[/red] {e}")

def main():
    console.print(Panel(
        "[bold green]🔧 Direct Agent Testing[/bold green]\nBypassing supervisor to test individual components",
        border_style="green"
    ))
    
    # Test database first
    test_database_connection()
    
    # Test tools directly
    test_database_tools_directly()
    
    console.print(Panel(
        "[bold blue]📊 Diagnosis Summary[/bold blue]\n" +
        "• If database works but tools fail → Tool configuration issue\n" +
        "• If tools work directly → Supervisor handoff issue\n" +
        "• If both fail → Core system problem",
        border_style="blue"
    ))

if __name__ == "__main__":
    main()
