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
    Uses the active FL-trained model (automatically updated by FL downloads).
    Also appends the scored application to fl_dataset.csv for next FL round.
    """
    try:
        result = predict_credit_score(features)
        
        # Append to fl_dataset.csv for next FL training round
        # Add default_flag based on score (simple rule: score < 600 = high risk = default=1)
        application_data = features.copy()
        
        # Determine default_flag based on score (this should be actual repayment outcome in production)
        # For now, use a simple threshold as proxy
        credit_score = result.get('credit_score', 650)
        application_data['default_flag'] = 1 if credit_score < 600 else 0
        
        # Append to FL dataset
        if append_to_fl_dataset(application_data):
            logger.info(f"✅ Application added to FL dataset (score: {credit_score})")
        else:
            logger.warning("⚠️  Failed to append application to FL dataset")
        
        return result
    except Exception as e:
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

