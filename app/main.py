from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger
from app.db.session import init_db
from app.api import routes_search, routes_locations, routes_posts, routes_engagement
from app.api.error_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.log_event("app.startup", {"version": settings.version})
    try:
        await init_db()
        logger.log_event("db.initialized", {"success": True})
    except Exception as e:
        logger.log_event("db.initialization_failed", {"error": str(e)})
        # Continue anyway for demo purposes
    
    yield
    
    # Shutdown
    logger.log_event("app.shutdown", {"version": settings.version})


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="""
# PaiNaiDee Backend API - Phase 1

Contextual Travel Content Search API with fuzzy matching, keyword expansion, and ranking.

## Features

### Search (`/api/search`)
- **Fuzzy matching** on location names using trigram similarity
- **Keyword expansion** via static mapping (province → landmarks)
- **Ranking algorithm** combining popularity and recency
- **Multi-field search** across captions, tags, and locations

### Locations (`/api/locations`)
- **Location details** with post counts and metadata
- **Nearby places** using geographic distance or similarity fallback
- **Autocomplete** with fuzzy matching and popularity ranking

### Posts (`/api/posts`)
- **Multipart upload** supporting images and videos
- **Auto-location matching** based on coordinates
- **Tag processing** and indexing
- **Structured logging** for analytics

## Architecture

Built with FastAPI for async performance and automatic OpenAPI documentation.
Uses PostgreSQL with pg_trgm extension for fuzzy search capabilities.

## Phase 1 Scope

This implementation focuses on:
- Basic fuzzy search and keyword expansion
- Geographic proximity matching
- Simple popularity + recency ranking
- Foundation for future semantic search (Phase 2)

## Open Questions

- PostGIS availability for advanced geographic queries
- Authentication system integration
- Dual Flask/FastAPI framework support
        """,
        lifespan=lifespan,
        debug=settings.debug
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(routes_search.router)
    app.include_router(routes_locations.router)
    app.include_router(routes_posts.router)
    app.include_router(routes_engagement.router)

    # Register exception handlers
    register_exception_handlers(app)
    
    @app.get("/", tags=["health"])
    async def root():
        """Health check and API information"""
        return {
            "message": "🇹🇭 PaiNaiDee Backend API - Phase 1",
            "version": settings.version,
            "description": "Contextual Travel Content Search API",
            "endpoints": {
                "search": "/api/search",
                "locations": "/api/locations",
                "posts": "/api/posts",
                "engagement": "/api/posts/{id}/like, /api/posts/{id}/comments",
                "documentation": "/docs",
                "openapi": "/openapi.json"
            },
            "features": [
                "Fuzzy search with trigram similarity",
                "Keyword expansion via static mapping",
                "Geographic proximity matching",
                "Popularity + recency ranking",
                "Auto-location matching for posts"
            ],
            "phase": "1",
            "next_phase": "Semantic search with embeddings"
        }
    
    @app.get("/health", tags=["health"])
    async def health_check():
        """Enhanced health check endpoint with database status"""
        from sqlalchemy import text
        from app.db.session import get_async_db
        
        health_status = {
            "status": "ok", 
            "message": "Backend is running",
            "app_version": settings.version,
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Check database connection
        try:
            async for db in get_async_db():
                result = await db.execute(text("SELECT 1"))
                result.scalar()
                health_status["components"]["database"] = {
                    "status": "ok",
                    "type": "postgresql" if "postgresql" in settings.database_uri else "sqlite"
                }
                break
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["components"]["database"] = {
                "status": "error",
                "error": str(e)[:100]  # Limit error message length
            }
        
        # Check extensions (for PostgreSQL)
        if "postgresql" in settings.database_uri:
            try:
                async for db in get_async_db():
                    pg_trgm_result = await db.execute(text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm')"))
                    has_pg_trgm = pg_trgm_result.scalar()
                    
                    postgis_result = await db.execute(text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')"))
                    has_postgis = postgis_result.scalar()
                    
                    health_status["components"]["extensions"] = {
                        "pg_trgm": "available" if has_pg_trgm else "missing",
                        "postgis": "available" if has_postgis else "missing"
                    }
                    break
            except Exception:
                pass  # Extensions check is optional
        
        return health_status

    @app.get("/api/health", tags=["health"])
    async def api_health_check():
        """Simple health check endpoint for API gateway"""
        return {"status": "ok", "message": "API is running", "version": settings.version}
    
    return app


# Create app instance
app = create_app()