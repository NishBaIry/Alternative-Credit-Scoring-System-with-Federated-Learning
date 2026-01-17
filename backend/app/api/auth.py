# auth.py
# Authentication endpoints for both clients and bank staff.
# POST /login/client: customer_id + password, returns JWT token.
# POST /login/staff: username + password, returns JWT with role (Admin/Analyst).
# Validates credentials against users.csv per bank.
# Uses security.py helpers to hash passwords and generate tokens.
# Keep bank_id in token payload for multi-tenant FL simulation.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/login/client")
async def client_login(bank_id: str, customer_id: str, password: str):
    """
    Client login endpoint.
    Validates customer credentials and returns JWT token.
    """
    # TODO: Implement authentication logic
    return {
        "access_token": "mock-token",
        "token_type": "bearer",
        "user_type": "client",
        "bank_id": bank_id
    }

@router.post("/login/staff")
async def staff_login(bank_id: str, username: str, password: str):
    """
    Staff login endpoint.
    Validates staff credentials and returns JWT token with role.
    """
    # TODO: Implement authentication logic
    return {
        "access_token": "mock-token",
        "token_type": "bearer",
        "user_type": "staff",
        "role": "risk_analyst",
        "bank_id": bank_id
    }

@router.post("/logout")
async def logout():
    """
    Logout endpoint (client or staff).
    Invalidates the current token.
    """
    return {"message": "Logged out successfully"}
