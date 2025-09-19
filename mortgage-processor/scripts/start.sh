#!/bin/bash
# Start script for Complete Mortgage Processing Backend

echo "🚀 Starting Complete Mortgage Processing Backend..."
echo "   - LangGraph API Server"
echo "   - A2A Orchestrator" 
echo "   - Web Search Agent"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Navigate to the project root (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Start the unified backend
python start_backend.py
