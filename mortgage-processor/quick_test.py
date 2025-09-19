#!/usr/bin/env python3
"""
Quick Test Script for Mortgage Processing System
Tests basic functionality before full demo
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import MortgageApplicationAgent for testing
from src.mortgage_processor.workflow_manager import MortgageApplicationAgent

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from src.mortgage_processor.workflow_manager import MortgageApplicationAgent
        print("✅ MortgageApplicationAgent imported successfully")
        
        from src.mortgage_processor.neo4j_mortgage import (
            update_application_status,
            get_application_status,
            store_loan_decision,
            initiate_processing_workflow
        )
        print("✅ Neo4j tools imported successfully")
        
        from src.mortgage_processor.graph import create_mortgage_graph
        print("✅ Graph creation imported successfully")
        
        return True
    except Exception as e:
        print(f" Import error: {e}")
        return False

def test_agent_creation():
    """Test that the mortgage agent can be created."""
    print("\n🤖 Testing agent creation...")
    
    try:
        agent = MortgageApplicationAgent()
        print("✅ MortgageApplicationAgent created successfully")
        return agent
    except Exception as e:
        print(f" Agent creation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_simple_chat(agent):
    """Test a simple chat interaction."""
    print("\n💬 Testing simple chat...")
    
    try:
        response = agent.chat(
            message="Hello, I have questions about mortgages. What documents do I need?",
            thread_id="test_thread_001"
        )
        print(f"✅ Chat successful. Response length: {len(response)} characters")
        print(f"📝 Response preview: {response[:150]}...")
        return True
    except Exception as e:
        print(f" Chat error: {e}")
        return False

def main():
    """Run basic tests."""
    print("🏠 **Quick Test - Mortgage Processing System**\n")
    
    # Test 1: Imports
    if not test_imports():
        print("\n **Import test failed. Please check dependencies.**")
        return False
    
    # Test 2: Agent Creation
    agent = test_agent_creation()
    if not agent:
        print("\n **Agent creation failed. Please check configuration.**")
        return False
    
    # Test 3: Simple Chat
    if not test_simple_chat(agent):
        print("\n **Chat test failed. Please check LLM connectivity.**")
        return False
    
    print("\n✅ **All basic tests passed!**")
    print("\n🎉 **System is ready for full demo and UI integration!**")
    print("\n📋 **Next steps:**")
    print("1. Run full demo: `python demo_end_to_end.py`")
    print("2. Check Neo4j is running for application storage")
    print("3. Integrate with chat frontend")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
