#!/usr/bin/env python3
"""
Initialize SQLite database for chat persistence.
Run this once to set up the database schema.
"""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mortgage_processor.database import get_database_manager

def init_database():
    """Initialize the SQLite database with proper schema"""
    try:
        # Get database manager (this will create tables automatically)
        db_manager = get_database_manager()
        
        print(" SQLite database initialized successfully!")
        print(f"📁 Database location: {db_manager.database_path}")
        print("🏗️  Tables created:")
        print("   - chat_sessions")
        print("   - chat_messages")
        print()
        print("💬 Chat persistence is now ready!")
        
    except Exception as e:
        print(f" Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
