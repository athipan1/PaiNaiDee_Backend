import os
import json
from typing import Dict, Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings for FastAPI Phase 1"""
    
    # Database
    database_url: str = Field(default="postgresql://postgres:password@localhost:5432/painaidee_db", env="DATABASE_URL")
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: str = Field(default="5432", env="DB_PORT")
    db_name: str = Field(default="painaidee_db", env="DB_NAME")
    db_user: str = Field(default="postgres", env="DB_USER")
    db_password: str = Field(default="", env="DB_PASSWORD")
    
    # Security
    jwt_secret_key: str = Field(
        default="a-secure-default-secret-for-development",
        env="JWT_SECRET_KEY"
    )
    api_keys: str = Field(
        default="demo-api-key,test-api-key", 
        env="API_KEYS"
    )
    
    # OpenAI/LLM configuration
    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    openai_api_base: str = Field(default="https://api.openai.com/v1", env="OPENAI_API_BASE")
    talk_model: str = Field(default="gpt-3.5-turbo", env="TALK_MODEL")
    talk_max_tokens: int = Field(default=500, env="TALK_MAX_TOKENS")
    talk_temperature: float = Field(default=0.7, env="TALK_TEMPERATURE")
    talk_max_context_length: int = Field(default=10, env="TALK_MAX_CONTEXT_LENGTH")
    
    # Search configuration
    search_rank_weights: str = Field(
        default='{"w_pop": 0.7, "w_recency": 0.3}',
        env="SEARCH_RANK_WEIGHTS"
    )
    max_nearby_radius_km: float = Field(default=50.0, env="MAX_NEARBY_RADIUS_KM")
    trigram_sim_threshold: float = Field(default=0.35, env="TRIGRAM_SIM_THRESHOLD")
    alpha_comment: float = Field(default=2.0, env="ALPHA_COMMENT")
    tau_minutes: float = Field(default=4320.0, env="TAU_MINUTES")  # 3 days
    
    # App configuration
    app_name: str = "PaiNaiDee Backend API - Phase 1"
    version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    attractions_json_path: str = Field(default="attractions_cleaned_ready.json", env="ATTRACTIONS_JSON_PATH")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )

    @field_validator("cors_origins", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """
        Prepares the list of CORS origins, ensuring required domains for the frontend are always included.
        Handles both a comma-separated string from environment variables and a list from default values.
        """
        if isinstance(v, str):
            # Origins from environment variable as a comma-separated string
            origins = {origin.strip() for origin in v.split(",") if origin.strip()}
        else:
            # Origins from the default list
            origins = set(v)

        # Ensure required origins for Vercel frontend and local development are always present
        required_origins = {
            "https://pai-naidee-ui-spark.vercel.app",
            "http://localhost:3000",
        }

        origins.update(required_origins)

        return sorted(list(origins))
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )
    
    @property
    def search_weights(self) -> Dict[str, float]:
        """Parse search rank weights from JSON string"""
        try:
            return json.loads(self.search_rank_weights)
        except (json.JSONDecodeError, TypeError):
            return {"w_pop": 0.7, "w_recency": 0.3}
    
    @property
    def database_uri(self) -> str:
        """Construct database URI if not provided directly"""
        if self.database_url and self.database_url != "postgresql://postgres:password@localhost:5432/painaidee_db":
            return self.database_url
        
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()