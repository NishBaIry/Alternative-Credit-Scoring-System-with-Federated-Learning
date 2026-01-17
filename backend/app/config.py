# config.py
# Central configuration file for environment variables and settings.
# Loads from .env file: database URLs, secret keys, bank data paths.
# Provides get_settings() function for dependency injection in FastAPI.
# Single source of truth for all configuration across the backend.

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CashFlow"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database (if using real DB later)
    DATABASE_URL: Optional[str] = None
    
    # Bank Data Paths
    BANK_A_DATA_PATH: str = "app/data/bank_a"
    BANK_B_DATA_PATH: str = "app/data/bank_b"
    
    # Model Settings
    MODEL_VERSION: str = "1.0"
    SCORE_MIN: int = 300
    SCORE_MAX: int = 900
    
    # Federated Learning
    FL_SERVER_URL: Optional[str] = None
    FL_ROUNDS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
