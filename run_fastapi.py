#!/usr/bin/env python3
"""
FastAPI Phase 1 startup script

This script demonstrates the FastAPI application with stub data
when no database is available. It showcases the API structure
and response formats defined in Phase 1.
"""

import uvicorn
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Set environment variables for demo
    os.environ["DEBUG"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///./demo.db"  # Use SQLite for demo
    
    print("🇹🇭 Starting PaiNaiDee Backend API - Phase 1")
    print("📍 Contextual Travel Content Search API")
    print("🔗 Documentation: http://localhost:8000/docs")
    print("🔗 Health Check: http://localhost:8000/health")
    print("🔍 Search Example: http://localhost:8000/api/search?q=เชียงใหม่")
    print("")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )