"""Extract Document Data Tool - Neo4j Powered"""

import json
import re
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

try:
    from ....utils.db import get_neo4j_connection, initialize_connection
except ImportError:
    from mortgage_processor.utils.db import get_neo4j_connection, initialize_connection


class DocumentExtractionRequest(BaseModel):
    """Schema for document extraction requests"""
    document_content: str = Field(description="Text content of the document")
    document_type: str = Field(description="Type: paystub, w2, bank_statement, employment_verification")
    borrower_name: Optional[str] = Field(description="Expected borrower name", default=None)


@tool
def extract_document_data(document_info: str) -> str:
    """Extract structured data from mortgage documents using Neo4j business rules.
    
    Args:
        document_info: Document details like "Type: paystub, Content: John Smith, TechCorp, Pay Period: 01/01-01/15, Gross: 4500, Net: 3200, YTD Gross: 18000"
    """
    
    try:
        # Parse document info string
        import re
        info = document_info.lower()
        
        # Extract document type
        type_match = re.search(r'type:\s*([a-z_]+)', info)
        document_type = type_match.group(1) if type_match else "paystub"
        
        # Extract borrower name
        name_match = re.search(r'(?:content:|borrower:)\s*([a-z]+\s+[a-z]+)', info)
        borrower_name = name_match.group(1).title() if name_match else "John Smith"
        
        # Extract document content (simplified)
        content_match = re.search(r'content:\s*(.+)', info)
        document_content = content_match.group(1) if content_match else info
        
        # Get rules from Neo4j
        initialize_connection()
        connection = get_neo4j_connection()
        
        with connection.driver.session(database=connection.database) as session:
            query = """
            MATCH (dvr:DocumentVerificationRule)
            WHERE toLower(dvr.document_type) CONTAINS toLower($doc_type)
            RETURN dvr.required_fields as required_fields, dvr.red_flags as red_flags
            LIMIT 5
            """
            result = session.run(query, doc_type=document_type)
            rules = [dict(record) for record in result]
        
        # Extract data based on document type
        if document_type.lower() == "paystub":
            fields = _extract_paystub(document_content)
        elif document_type.lower() == "w2":
            fields = _extract_w2(document_content)
        elif document_type.lower() == "bank_statement":
            fields = _extract_bank_statement(document_content)
        else:
            fields = {"document_type": document_type}
        
        # Validate
        issues = []
        if not fields.get("full_name"):
            issues.append("No name found in document")
        
        if borrower_name and fields.get("full_name"):
            name_match = _name_similarity(fields["full_name"], borrower_name)
            if name_match < 0.7:
                issues.append(f"Name mismatch: expected {borrower_name}")
        
        result = {
            "valid": len(issues) == 0,
            "issues": issues,
            "fields": fields,
            "document_info": {
                "type": document_type,
                "timestamp": datetime.now().isoformat(),
                "rules_checked": len(rules)
            },
            "success": True
        }
        
        return json.dumps(result, ensure_ascii=False, default=str)
        
    except Exception as e:
        return json.dumps({
            "valid": False,
            "issues": [f"Extraction failed: {str(e)}"],
            "fields": {},
            "document_info": {"type": document_type, "error": str(e)},
            "success": False
        })


def _extract_paystub(content: str) -> Dict:
    """Extract paystub data"""
    fields = {"document_type": "paystub"}
    
    # Extract employee name
    name_match = re.search(r"(?:Employee|Name):\s*([A-Za-z\s,]+)", content, re.IGNORECASE)
    if name_match:
        fields["full_name"] = name_match.group(1).strip()
        fields["employee_name"] = fields["full_name"]
    
    # Extract gross pay
    gross_match = re.search(r"(?:Gross Pay|Gross):\s*\$?([0-9,]+\.?[0-9]*)", content, re.IGNORECASE)
    if gross_match:
        try:
            fields["gross_pay"] = float(gross_match.group(1).replace(',', '').replace('$', ''))
        except ValueError:
            fields["gross_pay"] = gross_match.group(1)
    
    # Extract employer
    employer_match = re.search(r"(?:Company|Employer):\s*([A-Za-z\s&.,]+)", content, re.IGNORECASE)
    if employer_match:
        fields["employer_name"] = employer_match.group(1).strip()
    
    return fields


def _extract_w2(content: str) -> Dict:
    """Extract W2 data"""
    fields = {"document_type": "w2"}
    
    name_match = re.search(r"(?:Employee|Name):\s*([A-Za-z\s,]+)", content, re.IGNORECASE)
    if name_match:
        fields["full_name"] = name_match.group(1).strip()
    
    wages_match = re.search(r"(?:Wages|Box 1):\s*\$?([0-9,]+\.?[0-9]*)", content, re.IGNORECASE)
    if wages_match:
        try:
            fields["wages"] = float(wages_match.group(1).replace(',', '').replace('$', ''))
        except ValueError:
            fields["wages"] = wages_match.group(1)
    
    return fields


def _extract_bank_statement(content: str) -> Dict:
    """Extract bank statement data"""
    fields = {"document_type": "bank_statement"}
    
    holder_match = re.search(r"(?:Account Holder|Name):\s*([A-Za-z\s,&]+)", content, re.IGNORECASE)
    if holder_match:
        fields["full_name"] = holder_match.group(1).strip()
        fields["account_holder"] = fields["full_name"]
    
    balance_match = re.search(r"(?:Ending Balance|Balance):\s*\$?([0-9,]+\.?[0-9]*)", content, re.IGNORECASE)
    if balance_match:
        try:
            fields["ending_balance"] = float(balance_match.group(1).replace(',', '').replace('$', ''))
        except ValueError:
            fields["ending_balance"] = balance_match.group(1)
    
    return fields


def _name_similarity(name1: str, name2: str) -> float:
    """Calculate name similarity"""
    if not name1 or not name2:
        return 0.0
    
    words1 = set(name1.lower().split())
    words2 = set(name2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0