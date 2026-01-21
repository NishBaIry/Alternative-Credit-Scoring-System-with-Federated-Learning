# config.py
# Central configuration file for environment variables and settings.
# Loads from .env file: database URLs, secret keys, bank data paths.
# Provides get_settings() function for dependency injection in FastAPI.
# Single source of truth for all configuration across the backend.

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CashFlow"

    # Bank Configuration
    BANK_ID: str = os.getenv("BANK_ID", "bank_b")
    BANK_NAME: str = os.getenv("BANK_NAME", "Bank B")

    # Directory Paths
    DATA_DIR: str = "data"
    MODEL_DIR: str = "models"

    # Database Paths (SQLite)
    BANK_A_DB: str = "data/bank_a.db"
    BANK_B_DB: str = "data/bank_b.db"
    NEW_APPLICATIONS_DB: str = "data/new_applications.db"

    # Model Paths
    GLOBAL_MODEL_PATH: str = "models/global_model.h5"
    ACTIVE_MODEL_PATH: str = "models/active_model.h5"
    SCALER_PATH: str = "models/scaler.pkl"
    ENCODERS_PATH: str = "models/encoders.pkl"

    # Scoring Configuration
    SCORE_MIN: int = 300
    SCORE_MAX: int = 900
    SCORE_CENTER: int = 600
    LOG_ODDS_FACTOR: int = 50

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Federated Learning
    FL_SERVER_URL: str = "http://localhost:5000"
    FL_ROUNDS: int = 10
    FL_EPOCHS: int = 5
    FL_BATCH_SIZE: int = 256
    FL_VALIDATION_SPLIT: float = 0.2

    # Helper methods to get paths
    def get_bank_db_path(self, bank_id: str = None) -> str:
        """Get database path for a specific bank."""
        bank = bank_id or self.BANK_ID
        if bank == "bank_a":
            return self.BANK_A_DB
        elif bank == "bank_b":
            return self.BANK_B_DB
        return f"{self.DATA_DIR}/{bank}.db"

    def get_client_model_path(self, bank_id: str = None) -> str:
        """Get client model path for a specific bank."""
        bank = bank_id or self.BANK_ID
        return f"{self.MODEL_DIR}/{bank}_model.h5"

    def get_weights_upload_path(self, bank_id: str = None) -> str:
        """Get weights upload path for a specific bank."""
        bank = bank_id or self.BANK_ID
        return f"{self.MODEL_DIR}/{bank}_weights.npz"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars like TF_* settings


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency injection helper for FastAPI."""
    return settings
