#!/usr/bin/env python3
"""
LangGraph App Graph for Mortgage Processing System
Provides the compiled graph for LangGraph dev command
"""
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.mortgage_processor.graph import create_mortgage_graph

# Create the graph (already compiled by create_mortgage_graph)
# LangGraph dev handles persistence automatically
app = create_mortgage_graph()
