import os
import json
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024))  # 50MB default
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "super-secret"
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    
    # Search Configuration
    @property
    def SEARCH_RANK_WEIGHTS(self):
        """Parse search ranking weights from JSON string."""
        weights_str = os.environ.get("SEARCH_RANK_WEIGHTS", '{"popularity": 0.4, "freshness": 0.3, "similarity": 0.3}')
        try:
            return json.loads(weights_str)
        except (json.JSONDecodeError, TypeError):
            # Fallback to default weights
            return {"popularity": 0.4, "freshness": 0.3, "similarity": 0.3}
    
    MAX_NEARBY_RADIUS_KM = float(os.environ.get("MAX_NEARBY_RADIUS_KM", 50))
    TRIGRAM_SIM_THRESHOLD = float(os.environ.get("TRIGRAM_SIM_THRESHOLD", 0.3))
    
    # Feature flags
    FEATURE_AUTOCOMPLETE = os.environ.get("FEATURE_AUTOCOMPLETE", "true").lower() == "true"
    FEATURE_NEARBY = os.environ.get("FEATURE_NEARBY", "true").lower() == "true"
    
    # Redis Configuration (optional)
    REDIS_URL = os.environ.get("REDIS_URL")
    
    # Analytics
    ENABLE_ANALYTICS = os.environ.get("ENABLE_ANALYTICS", "true").lower() == "true"
    ANALYTICS_RETENTION_DAYS = int(os.environ.get("ANALYTICS_RETENTION_DAYS", 90))
    
    # Security
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", 60))
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
    TALK_MODEL = os.environ.get("TALK_MODEL", "gpt-3.5-turbo")
    TALK_MAX_TOKENS = int(os.environ.get("TALK_MAX_TOKENS", 500))
    TALK_TEMPERATURE = float(os.environ.get("TALK_TEMPERATURE", 0.7))
    TALK_MAX_CONTEXT_LENGTH = int(os.environ.get("TALK_MAX_CONTEXT_LENGTH", 10))
    
    @classmethod
    def validate_required_config(cls):
        """Validate that required configuration values are present."""
        required_vars = []
        missing_vars = []
        
        # Check for database configuration
        if not hasattr(cls, 'SQLALCHEMY_DATABASE_URI') or not cls.SQLALCHEMY_DATABASE_URI:
            required_vars.append("DATABASE_URL or individual DB_* variables")
        
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate search weights sum to 1.0 (approximately)
        weights = cls().SEARCH_RANK_WEIGHTS
        total_weight = sum(weights.values())
        if not (0.9 <= total_weight <= 1.1):  # Allow small floating point errors
            raise ValueError(f"Search rank weights must sum to approximately 1.0, got {total_weight}")
        
        return True


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    APP_ENV = "development"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
    
    # Database configuration - support both DATABASE_URL and individual components
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "painaidee_db")
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )


class DockerConfig(Config):
    """Docker container configuration."""
    DEBUG = False
    APP_ENV = "docker"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST", "db")  # Docker service name
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "painaidee_db")
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    APP_ENV = "production"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING")
    
    # In production, DATABASE_URL should always be provided
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required for production")
        return database_url
    
    # Production-specific overrides
    RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", 30))  # Stricter in production


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    APP_ENV = "testing"
    LOG_LEVEL = "CRITICAL"  # Suppress logs during testing
    
    # Use SQLite for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    
    # Disable features that might interfere with testing
    ENABLE_ANALYTICS = False
    JWT_SECRET_KEY = "test-secret"
    
    # Override search config for consistent testing
    SEARCH_RANK_WEIGHTS = {"popularity": 0.4, "freshness": 0.3, "similarity": 0.3}
    MAX_NEARBY_RADIUS_KM = 10
    TRIGRAM_SIM_THRESHOLD = 0.3


config = {
    "development": DevelopmentConfig,
    "docker": DockerConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
