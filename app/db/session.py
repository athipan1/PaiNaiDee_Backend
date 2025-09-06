from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.core.config import settings
from app.core.logging import logger

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


from app.db.seeding import seed_data

async def init_db():
    """Initialize database, create tables, and seed initial data."""
    logger.log_event("db.init.start", {"message": "Starting database initialization..."})
    from app.db.models import Base

    try:
        # Use a connection with autocommit for creating extensions
        async with async_engine.connect() as conn:
            if "postgresql" in settings.database_uri:
                await conn.execute(text("COMMIT")) # Ensure no transaction is active
                logger.log_event("db.init.extensions.start", {"db_type": "postgresql"})
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                    logger.log_event("db.init.extensions.success", {"extensions": ["pg_trgm", "postgis"]})
                except Exception as e:
                    logger.log_event("db.init.extensions.warning", {"message": f"PostGIS not available: {e}"})

        # Now create tables in a new transaction
        async with async_engine.begin() as conn:
            logger.log_event("db.init.create_all.start", {})
            await conn.run_sync(Base.metadata.create_all)
            logger.log_event("db.init.create_all.success", {})

        # Seed data
        logger.log_event("db.seeding.start", {})
        async with AsyncSessionLocal() as db_session:
            await seed_data(db_session)

        logger.log_event("db.init.finish", {"message": "Database initialization and seeding completed successfully."})

    except Exception as e:
        logger.log_event("db.init.failed", {"error": str(e)})
        raise