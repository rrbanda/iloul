#!/usr/bin/env python3
"""
LangGraph App Graph for Mortgage Processing System V1
Provides the compiled supervisor agent for LangGraph dev command

This creates a production-ready supervisor that coordinates all 5 mortgage processing
agents using LangGraph's official supervisor implementation.
"""
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mortgage_processor.agents import create_supervisor_agent

# Create the supervisor agent (already compiled by create_supervisor_agent)
# LangGraph dev handles persistence automatically
app = create_supervisor_agent()
