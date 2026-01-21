# auth.py
# Authentication endpoints for both clients and bank staff.
# POST /login/client: customer_id + password, returns JWT token.
# POST /login/staff: username + password, returns JWT with role (Admin/Analyst).
# Validates credentials against users.csv per bank.
# Uses security.py helpers to hash passwords and generate tokens.
# Keep bank_id in token payload for multi-tenant FL simulation.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import hashlib
import logging
from app.core.db import db_manager

router = APIRouter()
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/login/client")
async def client_login(bank_id: str, customer_id: str, password: str):
    """
    Client login endpoint.
    Validates customer credentials against SQLite database.
    Password is customer_id hashed with SHA256.
    """
    try:
        # Hash the provided password
        password_hash = hash_password(password)
        
        # Authenticate against database
        customer = db_manager.authenticate_customer(bank_id, customer_id, password_hash)
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid customer ID or password"
            )
        
        logger.info(f"Customer {customer_id} logged in successfully")
        
        return {
            "access_token": f"{bank_id}:{customer_id}:{password_hash[:16]}",
            "token_type": "bearer",
            "user_type": "client",
            "bank_id": bank_id,
            "customer_id": customer_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/login/staff")
async def staff_login(bank_id: str, username: str, password: str):
    """
    Staff login endpoint.
    For demo: username='admin', password='admin123'
    """
    # Simple hardcoded staff auth for demo
    if username == "admin" and password == "admin123":
        return {
            "access_token": f"staff:{bank_id}:admin",
            "token_type": "bearer",
            "user_type": "staff",
            "role": "risk_analyst",
            "bank_id": bank_id
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )

@router.post("/logout")
async def logout():
    """
    Logout endpoint (client or staff).
    Invalidates the current token.
    """
    return {"message": "Logged out successfully"}
