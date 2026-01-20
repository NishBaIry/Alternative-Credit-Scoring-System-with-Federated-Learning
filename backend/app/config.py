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
    
    # Database Paths (SQLite)
    BANK_A_DB: str = "data/bank_a.db"
    BANK_B_DB: str = "data/bank_b.db"
    
    # Model Paths
    MODEL_PATH: str = "models/model.h5"
    WEIGHTS_PATH: str = "models/model.weights.h5"
    SCALER_PATH: str = "models/scaler.pkl"
    ENCODERS_PATH: str = "models/encoders.pkl"
    
    # Model Settings
    MODEL_VERSION: str = "2.0"
    SCORE_MIN: int = 300
    SCORE_MAX: int = 900
    
    # Federated Learning
    FL_SERVER_URL: Optional[str] = None
    FL_ROUNDS: int = 10
    FL_EPOCHS: int = 5
    FL_BATCH_SIZE: int = 256
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
