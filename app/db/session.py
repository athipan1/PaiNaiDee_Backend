from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings

# Synchronous database setup (for migrations)
sync_engine = create_engine(settings.database_uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Asynchronous database setup (for FastAPI)
async_database_url = settings.database_uri
if "postgresql://" in async_database_url:
    async_database_url = async_database_url.replace("postgresql://", "postgresql+asyncpg://")
elif "sqlite://" in async_database_url:
    async_database_url = async_database_url.replace("sqlite://", "sqlite+aiosqlite://")

async_engine = create_async_engine(async_database_url)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize database with extensions"""
    async with async_engine.begin() as conn:
        # Only run PostgreSQL-specific commands if using PostgreSQL
        if "postgresql" in settings.database_uri:
            # Enable pg_trgm extension for fuzzy search
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

            # Enable PostGIS if available (optional)
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            except Exception:
                # PostGIS not available, will use lat/lng columns instead
                pass
        else:
            # For SQLite, we'll use simple text matching instead of pg_trgm
            pass
