"""
Flask extensions initialization.

This module contains all Flask extensions that need to be initialized
with the app instance. Extensions are created here and then initialized
in the app factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Optional: Redis for caching (when REDIS_URL is configured)
redis_client = None

def init_redis(app):
    """Initialize Redis client if configured."""
    global redis_client
    redis_url = app.config.get('REDIS_URL')
    
    if redis_url:
        try:
            import redis
            redis_client = redis.from_url(redis_url)
            # Test connection
            redis_client.ping()
            app.logger.info("Redis connection established")
        except ImportError:
            app.logger.warning("Redis URL configured but redis package not installed")
        except Exception as e:
            app.logger.warning(f"Failed to connect to Redis: {e}")
            redis_client = None
    
    return redis_client