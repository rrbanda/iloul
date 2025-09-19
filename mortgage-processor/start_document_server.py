#!/usr/bin/env python3
"""
Start the Document Management Server with Knowledge Graph Extraction
"""

import sys
import subprocess
from pathlib import Path

# Add source path
sys.path.append('src')

def main():
    """Start the document management server"""
    
    print("🏠 Mortgage Document Management Server")
    print("=" * 50)
    print("🚀 Starting FastAPI server with knowledge graph extraction...")
    print()
    print("📡 Server will be available at:")
    print("   • API Documentation: http://localhost:8001/docs")
    print("   • Alternative Docs: http://localhost:8001/redoc") 
    print("   • Health Check: http://localhost:8001/health")
    print("   • Root Endpoint: http://localhost:8001/")
    print()
    print("📄 Available Endpoints:")
    print("   • POST /api/documents/upload - Upload documents with KG extraction")
    print("   • GET /api/documents/status/{document_id} - Document status")
    print("   • GET /api/documents/knowledge-graph/{application_id} - Query KG")
    print("   • GET /api/documents/applications/{application_id}/documents - List docs")
    print()
    print("🧠 Knowledge Graph Features:")
    print("   • Automatic entity extraction (Person, Income, Asset, etc.)")
    print("   • Relationship mapping (EMPLOYED_BY, EARNS, OWNS, etc.)")
    print("   • Triple storage: Vector DB + Neo4j Knowledge Graph + Metadata")
    print("   • Support for PDF, Word, Images, Text files")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the server
        from src.mortgage_processor.document_server import run_server
        run_server(host="0.0.0.0", port=8001, reload=True)
        
    except ImportError as e:
        print(f" Import Error: {e}")
        print("💡 Installing required dependencies...")
        
        # Install dependencies
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "fastapi", "uvicorn", "python-multipart", 
            "langchain-experimental", "PyPDF2", "python-docx", 
            "Pillow", "pytesseract"
        ])
        
        print("✅ Dependencies installed. Restarting server...")
        from src.mortgage_processor.document_server import run_server
        run_server(host="0.0.0.0", port=8001, reload=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        print("👋 Thanks for using the Document Management API!")
        
    except Exception as e:
        print(f" Server Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
