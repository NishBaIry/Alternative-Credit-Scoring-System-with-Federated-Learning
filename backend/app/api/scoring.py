# scoring.py
# Scoring-related API endpoints shared across client and staff.
# POST /score: general endpoint to score arbitrary feature vectors.
# GET /score/explain: SHAP or model-based explanation for a given score.
# Used by both client refresh-score and staff score-application flows.
# Calls credit_model.py service to run LightGBM inference.

from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/score")
async def score_features(features: dict):
    """
    Score a set of features using the local model.
    Generic endpoint that can be used for any scoring request.
    """
    # TODO: Implement feature scoring
    return {
        "score": 742,
        "risk_band": "Low",
        "confidence": 0.89
    }

@router.get("/score/explain")
async def explain_score(customer_id: str):
    """
    Get detailed explanation for a customer's score.
    Uses SHAP or similar explainability methods.
    """
    # TODO: Implement score explanation
    return {
        "customer_id": customer_id,
        "score": 742,
        "explanation": {
            "top_features": [],
            "shap_values": [],
            "feature_contributions": {}
        }
    }
