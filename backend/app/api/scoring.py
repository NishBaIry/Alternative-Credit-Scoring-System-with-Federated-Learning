# scoring.py
# Scoring-related API endpoints shared across client and staff.
# POST /score: general endpoint to score arbitrary feature vectors using NN model.
# GET /score/explain: SHAP or model-based explanation for a given score.
# POST /score/reload-model: Force reload the scoring model after FL update.
# GET /score/model-info: Get information about the currently loaded model.
# Uses nn_scoring_service.py which loads FL-trained neural network models.

from fastapi import APIRouter, Depends, HTTPException
from app.services.nn_scoring_service import get_scoring_service, predict_credit_score
from app.services.fl_data_collector import append_to_fl_dataset
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/score")
async def score_features(features: dict):
    """
    Score a set of features using the neural network model.
    Computes alt_score = 300 + 600 * (1 - p_default).
    """
    try:
        result = predict_credit_score(features)
        return result
    except Exception as e:
        logger.error(f"Scoring error: {e}")
        raise HTTPException(status_code=500, detail=f"Scoring error: {str(e)}")

@router.post("/score/customer/{customer_id}")
async def score_customer(customer_id: str, bank_id: str = "bank_a"):
    """
    Score a specific customer from the database.
    Retrieves customer data from SQLite, scores it, and updates alt_score in DB.
    """
    try:
        from app.services.customer_service import CustomerService
        
        service = CustomerService(bank_id)
        result = service.score_customer(customer_id)
        
        return {
            "status": "success",
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error scoring customer: {e}")
        raise HTTPException(status_code=500, detail=f"Scoring error: {str(e)}")

@router.get("/score/explain")
async def explain_score(customer_id: str):
    """
    Get detailed explanation for a customer's score.
    Uses SHAP or similar explainability methods.
    """
    # TODO: Implement SHAP-based score explanation
    return {
        "customer_id": customer_id,
        "score": 742,
        "explanation": {
            "top_features": [],
            "shap_values": [],
            "feature_contributions": {}
        }
    }

@router.post("/score/reload-model")
async def reload_scoring_model():
    """
    Force reload the scoring model.
    Useful after FL model download to ensure latest model is being used.
    """
    try:
        service = get_scoring_service()
        success = service.reload_model()
        
        if success:
            return {
                "status": "success",
                "message": "Model reloaded successfully",
                "model_info": service.get_model_info()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reload model")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reload error: {str(e)}")

@router.get("/score/model-info")
async def get_model_info():
    """
    Get information about the currently loaded scoring model.
    """
    try:
        service = get_scoring_service()
        return {
            "status": "success",
            "model_info": service.get_model_info()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

