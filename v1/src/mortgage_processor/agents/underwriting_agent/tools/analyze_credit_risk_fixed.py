"""
Simple Credit Risk Analysis Tool - Fixed for Structured Tool Calls

This tool provides credit risk analysis using the exact same pattern
as transfer tools that work with structured tool calls.
"""

from langchain_core.tools import tool

try:
    from ....utils.db import get_neo4j_connection, initialize_connection
except ImportError:
    from mortgage_processor.utils.db import get_neo4j_connection, initialize_connection


@tool
def analyze_credit_risk_fixed(borrower_info: str) -> str:
    """Analyze credit risk based on borrower information from Neo4j underwriting rules.
    
    Args:
        borrower_info: Borrower credit information like "720 credit score, conventional loan, stable employment, no bankruptcy"
    """
    
    # Initialize Neo4j connection
    if not initialize_connection():
        return "Error: Failed to connect to Neo4j database"
    
    connection = get_neo4j_connection()
    
    try:
        # Parse borrower info
        info = borrower_info.lower()
        
        # Extract credit score
        import re
        score_match = re.search(r'(\d{3})\s*credit\s*score', info)
        credit_score = int(score_match.group(1)) if score_match else 700
        
        # Extract loan program  
        loan_program = "conventional"
        if "fha" in info:
            loan_program = "fha"
        elif "va" in info:
            loan_program = "va"
        elif "usda" in info:
            loan_program = "usda"
        elif "jumbo" in info:
            loan_program = "jumbo"
        
        # Query Neo4j for credit analysis rules
        with connection.driver.session(database=connection.database) as session:
            credit_rules_query = """
            MATCH (r:UnderwritingRule)
            WHERE r.category = 'CreditAnalysis'
            RETURN r
            ORDER BY r.rule_id
            """
            result = session.run(credit_rules_query)
            credit_rules = [dict(record['r']) for record in result]
        
        if not credit_rules:
            return "No credit analysis rules found in Neo4j"
        
        # Analyze credit risk
        analysis_report = []
        analysis_report.append("=== CREDIT RISK ANALYSIS ===")
        analysis_report.append(f"Credit Score: {credit_score}")
        analysis_report.append(f"Loan Program: {loan_program.upper()}")
        analysis_report.append("")
        
        # Check minimum score requirements
        meets_requirements = True
        for rule in credit_rules:
            if rule.get('sub_category') == 'MinimumScore':
                rule_program = rule.get('loan_program', '').lower()
                if rule_program == loan_program or rule_program == 'all':
                    min_score = rule.get('min_score', 620)
                    if credit_score >= min_score:
                        analysis_report.append(f"✓ {rule.get('description', 'Credit requirement met')}")
                    else:
                        analysis_report.append(f"✗ {rule.get('description', 'Credit requirement not met')}")
                        meets_requirements = False
        
        # Overall assessment
        analysis_report.append("")
        if meets_requirements:
            if credit_score >= 740:
                analysis_report.append("RISK ASSESSMENT: EXCELLENT - Prime borrower with superior credit")
            elif credit_score >= 680:
                analysis_report.append("RISK ASSESSMENT: GOOD - Strong credit profile, favorable terms")
            else:
                analysis_report.append("RISK ASSESSMENT: ACCEPTABLE - Meets minimum requirements")
        else:
            analysis_report.append("RISK ASSESSMENT: HIGH RISK - Credit score below program requirements")
        
        # Recommendations
        analysis_report.append("")
        analysis_report.append("RECOMMENDATIONS:")
        if credit_score >= 740:
            analysis_report.append("- Qualify for best available rates")
            analysis_report.append("- No additional credit documentation required")
        elif credit_score >= 680:
            analysis_report.append("- Good rate qualification")
            analysis_report.append("- Standard documentation acceptable")
        elif credit_score >= 620:
            analysis_report.append("- May require additional documentation")
            analysis_report.append("- Consider compensating factors")
        else:
            analysis_report.append("- Credit improvement recommended")
            analysis_report.append("- Consider alternative loan programs")
        
        return "\n".join(analysis_report)
        
    except Exception as e:
        return f"Credit risk analysis error: {str(e)}"
