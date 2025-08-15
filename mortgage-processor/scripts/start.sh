#!/bin/bash
# Start script for Mortgage Processing Agent

echo "🚀 Starting Mortgage Processing Agent API..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Start the application
python run.py
