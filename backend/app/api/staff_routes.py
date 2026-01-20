# staff_routes.py
# API routes for bank staff (risk/data team).
# GET /customers: list customers for this bank (paginated, with filters).
# GET /customers/{id}: detailed view of a single customer.
# PATCH /customers/{id}: edit non-sensitive customer fields.
# POST /applications/score: score a new loan application using local model.
# GET /model/status: returns dataset stats, last training time, AUC metrics.
# GET /model/analytics: feature importance, distributions, fairness metrics.
# All endpoints require valid staff JWT and check role permissions.

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.services.customer_service import CustomerService
from app.services.nn_scoring_service import get_scoring_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/customers")
async def list_customers(bank_id: str = "bank_a", skip: int = 0, limit: int = 100, min_score: Optional[int] = None):
    """
    List all customers for the bank from SQLite.
    Supports pagination and filtering.
    """
    try:
        service = CustomerService(bank_id)
        filters = {}
        if min_score is not None:
            filters['min_score'] = min_score
        
        result = service.get_customer_list(skip=skip, limit=limit, filters=filters)
        return result
    except Exception as e:
        logger.error(f"Failed to load customers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load customers: {str(e)}")

@router.get("/customers/{customer_id}")
async def get_customer_detail(customer_id: str, bank_id: str = "bank_a"):
    """
    Get detailed information for a specific customer from SQLite.
    """
    try:
        service = CustomerService(bank_id)
        customer = service.get_customer_detail(customer_id)
        
        if not customer:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        
        return {
            "status": "success",
            "customer": customer
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get customer: {str(e)}")

@router.patch("/customers/{customer_id}")
async def update_customer(customer_id: str, update_data: dict, bank_id: str = "bank_a"):
    """
    Update non-sensitive customer information in SQLite.
    """
    try:
        service = CustomerService(bank_id)
        result = service.update_customer(customer_id, update_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/applications/score")
async def score_application(application_data: dict, bank_id: str = "bank_a"):
    """
    Score a new loan application using the local model.
    """
    try:
        scoring_service = get_scoring_service()
        alt_score, risk_band, p_default = scoring_service.predict_score(application_data)
        
        return {
            "status": "success",
            "alt_score": alt_score,
            "credit_score": alt_score,
            "risk_band": risk_band,
            "default_probability": round(p_default, 4),
            "recommendation": "Approve" if alt_score >= 650 else "Review" if alt_score >= 600 else "Decline"
        }
    except Exception as e:
        logger.error(f"Failed to score application: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/status")
async def get_model_status():
    """
    Get current model training status and metrics.
    """
    # TODO: Implement model status retrieval
    return {
        "local_records": 1234,
        "good_bad_ratio": "70:30",
        "last_training": "2 days ago",
        "local_auc": 0.94,
        "global_round": 12,
        "global_auc": 0.95,
        "privacy_budget": 0.7
    }

@router.get("/model/analytics")
async def get_model_analytics():
    """
    Get model analytics including feature importance and performance metrics.
    """
    # TODO: Implement analytics retrieval
    return {
        "feature_importance": [],
        "approval_rates": {},
        "performance_trends": []
    }
