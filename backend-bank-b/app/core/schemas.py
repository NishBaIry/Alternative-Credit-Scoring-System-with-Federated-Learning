# schemas.py
# Pydantic models for request/response validation.
# Defines: ClientLoginRequest, StaffLoginRequest, TokenResponse, CustomerProfile,
# ScoreResponse, ApplicationScoreRequest, TrainRequest, FLStatusResponse, etc.
# Used by FastAPI to auto-validate JSON payloads and generate OpenAPI docs.
# Keep these aligned with frontend API expectations.

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Authentication Schemas
class ClientLoginRequest(BaseModel):
    bank_id: str
    customer_id: str
    password: str

class StaffLoginRequest(BaseModel):
    bank_id: str
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: str
    bank_id: str
    role: Optional[str] = None

# Score Schemas
class ScoreResponse(BaseModel):
    score: int = Field(..., ge=300, le=900)
    risk_band: str
    max_score: int = 900
    last_updated: datetime

class ScoreFactor(BaseModel):
    name: str
    impact: str  # positive, negative, neutral
    contribution: float

class ScoreDetailsResponse(BaseModel):
    score: int
    factors: List[ScoreFactor]
    recommendations: List[str]

# Customer Schemas
class CustomerProfile(BaseModel):
    customer_id: str
    name: str
    age: int
    region: str
    employment_type: str
    monthly_income: float

class CustomerListItem(BaseModel):
    id: str
    name: str
    score: int
    risk_band: str
    age: int
    region: str

# Application Scoring
class ApplicationScoreRequest(BaseModel):
    customer_id: Optional[str] = None
    age: int
    monthly_income: float
    loan_amount: float
    dti: float
    # Add more fields as needed

class ApplicationScoreResponse(BaseModel):
    score: int
    risk_band: str
    top_drivers: List[str]

# Model Training
class TrainRequest(BaseModel):
    bank_id: str

class TrainResponse(BaseModel):
    status: str
    message: str
    metrics: dict
    training_time: str
    records_used: int

# Federated Learning
class FLStatusResponse(BaseModel):
    current_round: int
    total_rounds: int
    participating_banks: int
    global_auc: float
    last_update: str
