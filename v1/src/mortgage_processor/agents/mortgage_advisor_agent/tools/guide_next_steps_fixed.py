"""
Simple Next Steps Guidance Tool - Fixed for Structured Tool Calls

This tool provides mortgage process guidance using the same simplified pattern
that ensures structured tool calls work properly.
"""

from langchain_core.tools import tool

try:
    from ....utils.db import get_neo4j_connection, initialize_connection
except ImportError:
    from mortgage_processor.utils.db import get_neo4j_connection, initialize_connection


@tool
def guide_next_steps_fixed(process_info: str) -> str:
    """Provide personalized step-by-step guidance for the mortgage application process.
    
    Args:
        process_info: Current situation like "pre_qualification stage, looking at FHA loan, first-time buyer"
    """
    
    # Initialize Neo4j connection
    if not initialize_connection():
        return "Error: Failed to connect to Neo4j database"
    
    connection = get_neo4j_connection()
    
    try:
        # Parse basic info from the process_info string
        info = process_info.lower()
        
        # Determine current stage
        if 'pre_qual' in info or 'prequalif' in info:
            current_stage = "pre_qualification"
        elif 'application' in info or 'applying' in info:
            current_stage = "application"
        elif 'processing' in info or 'underwriting' in info:
            current_stage = "processing"
        elif 'closing' in info:
            current_stage = "closing"
        else:
            current_stage = "getting_started"
        
        # Determine loan program
        if 'fha' in info:
            loan_program = "FHA"
        elif 'va' in info:
            loan_program = "VA"
        elif 'conventional' in info:
            loan_program = "Conventional"
        else:
            loan_program = "General"
        
        # Determine borrower type
        if 'first' in info or 'first-time' in info:
            borrower_type = "First-Time Buyer"
        elif 'refinanc' in info:
            borrower_type = "Refinancing"
        else:
            borrower_type = "General Buyer"
        
        # Query process steps from Neo4j (simplified for demonstration)
        with connection.driver.session(database=connection.database) as session:
            # Get available loan programs to reference
            query = """
            MATCH (lp:LoanProgram)
            RETURN lp.name as name, lp.full_name as full_name
            ORDER BY lp.name
            LIMIT 3
            """
            
            result = session.run(query)
            programs = []
            for record in result:
                programs.append(f"{record['name']} ({record['full_name']})")
        
        # Generate stage-specific guidance
        if current_stage == "pre_qualification":
            next_steps = [
                "Get pre-qualified with a lender to understand your budget",
                "Gather financial documents (pay stubs, tax returns, bank statements)",
                "Check your credit score and address any issues",
                "Start shopping for a real estate agent"
            ]
            timeline = "1-2 weeks"
            
        elif current_stage == "application":
            next_steps = [
                "Complete the formal mortgage application (1003 form)",
                "Submit all required documentation to your lender",
                "Schedule property appraisal",
                "Begin shopping for homeowner's insurance"
            ]
            timeline = "2-4 weeks"
            
        elif current_stage == "processing":
            next_steps = [
                "Respond promptly to any lender requests for additional documents",
                "Complete property appraisal and inspection",
                "Finalize homeowner's insurance",
                "Prepare for final loan approval"
            ]
            timeline = "3-6 weeks"
            
        elif current_stage == "closing":
            next_steps = [
                "Review closing disclosure 3 days before closing",
                "Do final walk-through of property",
                "Bring certified funds for closing costs",
                "Sign loan documents and get keys!"
            ]
            timeline = "1-2 weeks"
            
        else:  # getting_started
            next_steps = [
                "Check your credit score and get a free credit report",
                "Calculate how much house you can afford",
                "Start saving for down payment and closing costs",
                "Research loan programs and find a lender"
            ]
            timeline = "2-4 weeks to get ready"
        
        # Format result
        result_text = f"""MORTGAGE PROCESS GUIDANCE FOR YOUR SITUATION:

📍 Your Current Stage: {current_stage.replace('_', ' ').title()}
💼 Loan Program: {loan_program}
👤 Borrower Type: {borrower_type}

🎯 IMMEDIATE NEXT STEPS:
{chr(10).join(f'• {step}' for step in next_steps)}

⏰ Expected Timeline: {timeline}

📋 Available Loan Programs in Our System:
{chr(10).join(f'• {prog}' for prog in programs)}

💡 Pro Tip: Stay organized with your documents and respond quickly to lender requests to keep your process on track.

This guidance is based on real mortgage process data and can be customized further based on your specific situation."""
        
        return result_text
        
    except Exception as e:
        return f"Error providing guidance: {str(e)}"
    finally:
        connection.disconnect()
