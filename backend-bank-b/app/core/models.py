# models.py
# ORM models if using SQLAlchemy (optional for hackathon).
# Defines database tables: User, Customer, Score, AuditLog, ModelVersion.
# For CSV-based approach, this file can be minimal or just contain helper dataclasses.
# If switching to real DB, add SQLAlchemy Base and table definitions here.

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """User model for authentication."""
    id: str
    username: str
    password_hash: str
    user_type: str  # client or staff
    bank_id: str
    role: Optional[str] = None  # For staff: admin, risk_analyst

@dataclass
class Customer:
    """Customer/Borrower model."""
    customer_id: str
    bank_id: str
    name: str
    age: int
    region: str
    employment_type: str
    monthly_income: float
    current_score: Optional[int] = None
    risk_band: Optional[str] = None

@dataclass
class ScoreRecord:
    """Score history record."""
    customer_id: str
    bank_id: str
    score: int
    risk_band: str
    timestamp: datetime
    model_version: str

@dataclass
class AuditLog:
    """Audit log for compliance."""
    timestamp: datetime
    user_id: str
    action: str
    bank_id: str
    details: Optional[dict] = None

@dataclass
class ModelVersion:
    """Model version tracking."""
    version: str
    bank_id: str
    trained_at: datetime
    auc: float
    f1_score: float
    records_used: int
