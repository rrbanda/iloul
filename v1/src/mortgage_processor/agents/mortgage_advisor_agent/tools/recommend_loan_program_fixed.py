"""
Simple Loan Program Recommendation Tool - Fixed for Structured Tool Calls

This tool provides loan program recommendations using the exact same pattern
as transfer tools that work with structured tool calls.
"""

from langchain_core.tools import tool

try:
    from ....utils.db import get_neo4j_connection, initialize_connection
except ImportError:
    from mortgage_processor.utils.db import get_neo4j_connection, initialize_connection


@tool
def recommend_loan_program_fixed(borrower_info: str) -> str:
    """Recommend loan programs based on borrower information from Neo4j business rules.
    
    Args:
        borrower_info: Borrower information like "720 credit score, 95000 income, 60000 down payment, 850 monthly debts"
    """
    
    # Initialize Neo4j connection
    if not initialize_connection():
        return "Error: Failed to connect to Neo4j database"
    
    connection = get_neo4j_connection()
    
    try:
        # Parse basic info from the borrower_info string
        info = borrower_info.lower()
        
        # Extract credit score
        if 'credit score' in info:
            import re
            credit_match = re.search(r'(\d{3})\s*credit\s*score', info)
            credit_score = int(credit_match.group(1)) if credit_match else 650
        else:
            credit_score = 650
        
        # Extract income
        if 'income' in info:
            income_match = re.search(r'(\d+)\s*income', info)
            annual_income = int(income_match.group(1)) if income_match else 75000
        else:
            annual_income = 75000
        
        # Query loan programs from Neo4j
        with connection.driver.session(database=connection.database) as session:
            query = """
            MATCH (lp:LoanProgram)
            RETURN lp.name as name, lp.full_name as full_name, 
                   lp.min_credit_score as min_credit, lp.min_down_payment as min_down
            ORDER BY lp.name
            """
            
            result = session.run(query)
            programs = []
            for record in result:
                programs.append({
                    'name': record['name'],
                    'full_name': record['full_name'],
                    'min_credit': record.get('min_credit', 580),
                    'min_down': record.get('min_down', 0.0)
                })
        
        # Analyze qualification for each program
        recommendations = []
        for program in programs[:4]:  # Top 4 programs
            min_credit = program['min_credit'] or 580
            qualification = "Qualified" if credit_score >= min_credit else "Not Qualified"
            
            recommendations.append(f"• {program['name']} ({program['full_name']}): {qualification}")
        
        # Format result
        result_text = f"""LOAN PROGRAM ANALYSIS FOR YOUR PROFILE:

📊 Your Profile:
• Credit Score: {credit_score}
• Annual Income: ${annual_income:,}

🏠 Loan Program Recommendations:
{chr(10).join(recommendations)}

💡 Analysis: Based on your {credit_score} credit score, you qualify for {'most' if credit_score >= 650 else 'limited'} loan programs.

This analysis uses real Neo4j business rules to evaluate your qualification status."""
        
        return result_text
        
    except Exception as e:
        return f"Error analyzing loan programs: {str(e)}"
    finally:
        connection.disconnect()
