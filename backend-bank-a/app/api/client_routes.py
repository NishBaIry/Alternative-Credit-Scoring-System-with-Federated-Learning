# client_routes.py
# API routes for client-facing features (borrower UI).
# GET /me/score: returns current alternative credit score + risk band for logged-in client.
# GET /me/score-details: returns top factors, feature contributions, history.
# GET /me/profile: returns customer profile (age, region, income, etc.).
# PATCH /me/profile: allows editing non-sensitive fields (email, phone).
# POST /me/refresh-score: re-runs scoring model on latest data.
# All endpoints require valid client JWT (dependency injection from security.py).

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.get("/me/score")
async def get_my_score():
    """
    Get current credit score for logged-in client.
    Returns score, risk band, and timestamp.
    """
    # TODO: Implement score retrieval
    return {
        "score": 742,
        "risk_band": "Low",
        "max_score": 900,
        "last_updated": "2026-01-17T10:30:00Z"
    }

@router.get("/me/score-details")
async def get_score_details():
    """
    Get detailed score breakdown with factors and explanations.
    """
    # TODO: Implement detailed score analysis
    return {
        "score": 742,
        "factors": [
            {"name": "High bill on-time rate", "impact": "positive", "contribution": 45},
            {"name": "High DTI ratio", "impact": "negative", "contribution": -15},
            {"name": "Strong UPI essentials share", "impact": "positive", "contribution": 30}
        ],
        "recommendations": [
            "Try to keep DTI below 40%",
            "Maintain on-time utility payments"
        ]
    }

@router.get("/me/profile")
async def get_my_profile():
    """
    Get customer profile information.
    """
    # TODO: Implement profile retrieval
    return {
        "customer_id": "C12345",
        "name": "John Doe",
        "age": 28,
        "region": "Mumbai",
        "employment_type": "Salaried",
        "monthly_income": 50000
    }

@router.patch("/me/profile")
async def update_my_profile(profile_data: dict):
    """
    Update non-sensitive profile fields.
    """
    # TODO: Implement profile update
    return {"message": "Profile updated successfully"}

@router.post("/me/refresh-score")
async def refresh_my_score():
    """
    Re-calculate credit score with latest data.
    """
    # TODO: Implement score refresh
    return {
        "score": 742,
        "message": "Score refreshed successfully"
    }
