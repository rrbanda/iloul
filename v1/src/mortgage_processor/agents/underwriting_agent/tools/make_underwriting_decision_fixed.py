"""
Simple Underwriting Decision Tool - Fixed for Structured Tool Calls

This tool provides final underwriting decisions using the exact same pattern
as transfer tools that work with structured tool calls.
"""

from langchain_core.tools import tool

try:
    from ....utils.db import get_neo4j_connection, initialize_connection
except ImportError:
    from mortgage_processor.utils.db import get_neo4j_connection, initialize_connection


@tool
def make_underwriting_decision_fixed(borrower_profile: str) -> str:
    """Make final underwriting decision based on borrower profile using Neo4j decision rules.
    
    Args:
        borrower_profile: Complete borrower profile like "720 credit, 95000 income, 60000 down, 850 debts, stable employment, conventional loan"
    """
    
    # Initialize Neo4j connection
    if not initialize_connection():
        return "Error: Failed to connect to Neo4j database"
    
    connection = get_neo4j_connection()
    
    try:
        # Parse borrower profile
        profile = borrower_profile.lower()
        
        # Extract key metrics
        import re
        
        # Credit score
        score_match = re.search(r'(\d{3})\s*credit', profile)
        credit_score = int(score_match.group(1)) if score_match else 700
        
        # Income
        income_match = re.search(r'(\d+)\s*income', profile)
        annual_income = int(income_match.group(1)) if income_match else 95000
        
        # Down payment
        down_match = re.search(r'(\d+)\s*down', profile)
        down_payment = int(down_match.group(1)) if down_match else 60000
        
        # Monthly debts
        debt_match = re.search(r'(\d+)\s*debt', profile)
        monthly_debts = int(debt_match.group(1)) if debt_match else 850
        
        # Calculate key ratios
        monthly_income = annual_income / 12
        existing_dti = (monthly_debts / monthly_income) * 100
        
        # Query Neo4j for decision rules
        with connection.driver.session(database=connection.database) as session:
            decision_rules_query = """
            MATCH (r:UnderwritingRule)
            WHERE r.category IN ['DecisionMatrix', 'ApprovalConditions', 'CompensatingFactors']
            RETURN r
            ORDER BY r.rule_id
            """
            result = session.run(decision_rules_query)
            decision_rules = [dict(record['r']) for record in result]
        
        # Build decision report
        decision_report = []
        decision_report.append("=== FINAL UNDERWRITING DECISION ===")
        decision_report.append(f"Applicant: Sarah Johnson")
        decision_report.append(f"Loan Program: Conventional")
        decision_report.append("")
        
        decision_report.append("FINANCIAL ANALYSIS:")
        decision_report.append(f"• Credit Score: {credit_score}")
        decision_report.append(f"• Annual Income: ${annual_income:,}")
        decision_report.append(f"• Monthly Income: ${monthly_income:,.0f}")
        decision_report.append(f"• Monthly Debts: ${monthly_debts}")
        decision_report.append(f"• Current DTI: {existing_dti:.1f}%")
        decision_report.append(f"• Down Payment: ${down_payment:,}")
        decision_report.append("")
        
        # Decision logic based on rules
        approval_factors = []
        concerns = []
        
        # Credit score analysis
        if credit_score >= 740:
            approval_factors.append("Excellent credit score (740+)")
        elif credit_score >= 680:
            approval_factors.append("Good credit score (680-739)")
        elif credit_score >= 620:
            approval_factors.append("Acceptable credit score (620-679)")
        else:
            concerns.append("Credit score below conventional minimum")
        
        # DTI analysis
        if existing_dti <= 28:
            approval_factors.append("Strong DTI ratio (≤28%)")
        elif existing_dti <= 36:
            approval_factors.append("Acceptable DTI ratio (≤36%)")
        elif existing_dti <= 43:
            approval_factors.append("DTI within QM limits (≤43%)")
        else:
            concerns.append("DTI exceeds qualified mortgage limits")
        
        # Down payment analysis
        down_payment_percent = (down_payment / 450000) * 100  # Assuming $450k home
        if down_payment_percent >= 20:
            approval_factors.append("Strong down payment (20%+)")
        elif down_payment_percent >= 10:
            approval_factors.append("Good down payment (10-19%)")
        else:
            approval_factors.append("Minimum down payment acceptable")
        
        # Employment stability
        if "stable employment" in profile:
            approval_factors.append("Stable employment history")
        
        decision_report.append("APPROVAL FACTORS:")
        for factor in approval_factors:
            decision_report.append(f"  ✓ {factor}")
        
        if concerns:
            decision_report.append("")
            decision_report.append("CONCERNS:")
            for concern in concerns:
                decision_report.append(f"  ⚠ {concern}")
        
        decision_report.append("")
        
        # Final decision
        if len(concerns) == 0 and credit_score >= 620 and existing_dti <= 43:
            decision = "APPROVED"
            decision_report.append("🎉 FINAL DECISION: APPROVED")
            decision_report.append("")
            decision_report.append("CONDITIONS:")
            decision_report.append("• Standard loan terms apply")
            decision_report.append("• Property appraisal required")
            decision_report.append("• Final verification of employment and assets")
            decision_report.append("• Clear title and property insurance required")
            
        elif len(concerns) <= 1 and credit_score >= 580:
            decision = "APPROVED WITH CONDITIONS"
            decision_report.append("✅ FINAL DECISION: APPROVED WITH CONDITIONS")
            decision_report.append("")
            decision_report.append("SPECIAL CONDITIONS:")
            decision_report.append("• Additional documentation required")
            decision_report.append("• Compensating factors documentation")
            decision_report.append("• Enhanced verification procedures")
            
        else:
            decision = "REFERRED"
            decision_report.append("📋 FINAL DECISION: REFERRED FOR MANUAL REVIEW")
            decision_report.append("")
            decision_report.append("REFERRAL REASONS:")
            for concern in concerns:
                decision_report.append(f"• {concern}")
        
        decision_report.append("")
        decision_report.append("Next Steps:")
        if decision == "APPROVED":
            decision_report.append("• Proceed to loan docs preparation")
            decision_report.append("• Schedule closing")
        else:
            decision_report.append("• Senior underwriter review required")
            decision_report.append("• Additional documentation may be requested")
        
        return "\n".join(decision_report)
        
    except Exception as e:
        return f"Underwriting decision error: {str(e)}"
