#!/bin/bash
# Installation script for Mortgage Processing Agent

echo "🏠 Installing Mortgage Processing Agent..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Installation completed!"
echo "Run with: ./scripts/start.sh"
