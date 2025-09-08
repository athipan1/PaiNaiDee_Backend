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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Set environment variables for Codespaces/Docker development
    os.environ["DEBUG"] = "true"
    
    # Use PostgreSQL when in Docker/Codespaces environment, fallback to SQLite
    if os.getenv("DB_HOST") or os.getenv("DATABASE_URL"):
        # PostgreSQL is available (Codespaces/Docker environment)
        if not os.getenv("DATABASE_URL"):
            db_host = os.getenv("DB_HOST", "db")
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "Got0896177698")
            db_name = os.getenv("DB_NAME", "painaidee_db")
            db_port = os.getenv("DB_PORT", "5432")
            os.environ["DATABASE_URL"] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        print("🗄️  Using PostgreSQL database")
    else:
        # Fallback to SQLite for standalone demo
        os.environ["DATABASE_URL"] = "sqlite:///./demo.db"
        print("🗄️  Using SQLite database (demo mode)")
    
    print("🇹🇭 Starting PaiNaiDee Backend API - Phase 1")
    print("📍 Contextual Travel Content Search API")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("DEBUG", "false").lower() == "true"

    print(f"🔗 Documentation: http://localhost:{port}/docs")
    print(f"🔗 Health Check: http://localhost:{port}/health")
    print(f"🔍 Search Example: http://localhost:{port}/api/search?q=เชียงใหม่")
    print("")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_level="info"
    )