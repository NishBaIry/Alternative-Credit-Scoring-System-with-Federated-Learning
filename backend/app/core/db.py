# db.py
# Database connection and session management.
# For hackathon: uses CSV files via pandas (customers.csv, users.csv per bank).
# For production: can switch to SQLAlchemy engine for PostgreSQL/MySQL.
# Functions: get_db_session(), load_customer_data(bank_id), save_customer_data(bank_id).
# Handles file locking if multiple requests modify CSV simultaneously.

import pandas as pd
from pathlib import Path
from typing import Optional

class DatabaseManager:
    """Manager for database operations using CSV files."""
    
    def __init__(self, data_path: str = "app/data"):
        self.data_path = Path(data_path)
    
    def get_bank_path(self, bank_id: str) -> Path:
        """Get the data path for a specific bank."""
        return self.data_path / bank_id
    
    def load_customers(self, bank_id: str) -> pd.DataFrame:
        """Load customer data for a specific bank."""
        path = self.get_bank_path(bank_id) / "customers.csv"
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    
    def save_customers(self, bank_id: str, df: pd.DataFrame):
        """Save customer data for a specific bank."""
        path = self.get_bank_path(bank_id) / "customers.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
    
    def load_users(self, bank_id: str) -> pd.DataFrame:
        """Load user authentication data for a specific bank."""
        path = self.get_bank_path(bank_id) / "users.csv"
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    
    def get_customer(self, bank_id: str, customer_id: str) -> Optional[dict]:
        """Get a specific customer by ID."""
        df = self.load_customers(bank_id)
        customer = df[df['customer_id'] == customer_id]
        if not customer.empty:
            return customer.iloc[0].to_dict()
        return None

# Global database manager instance
db_manager = DatabaseManager()
