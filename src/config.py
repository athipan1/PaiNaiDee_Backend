import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size


class DevelopmentConfig(Config):
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "painaidee_db")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


class DockerConfig(Config):
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "painaidee_db")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"


class ProductionConfig(Config):
    # Production uses DATABASE_URL env var for Railway/Heroku compatibility
    # Fallback to the Supabase URL provided by the user.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql://postgres.quptneebcplnmzkyuxlu:tubci4-miqcAq-qadnuz@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"


class HuggingFaceConfig(Config):
    # For Hugging Face Spaces, DATABASE_URL must be set as a secret.
    # It should be a PostgreSQL connection string, e.g., for Supabase:
    # postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("WARNING: DATABASE_URL not set. Falling back to SQLite. This will not work in a deployed Space.")
        db_url = 'sqlite:///painaidee_dev.db'
    SQLALCHEMY_DATABASE_URI = db_url
    TESTING = False


config = {
    "development": DevelopmentConfig,
    "docker": DockerConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "huggingface": HuggingFaceConfig,
    "default": DevelopmentConfig,
}
