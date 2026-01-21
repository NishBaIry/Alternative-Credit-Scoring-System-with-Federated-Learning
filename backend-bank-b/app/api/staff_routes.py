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
from app.services.new_applications_service import get_new_applications_service
from app.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Get default bank_id from config
DEFAULT_BANK_ID = settings.BANK_ID

@router.get("/customers")
async def list_customers(bank_id: str = None, skip: int = 0, limit: int = 100, min_score: Optional[int] = None):
    bank_id = bank_id or DEFAULT_BANK_ID
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
async def get_customer_detail(customer_id: str, bank_id: str = None):
    """
    Get detailed information for a specific customer from SQLite.
    """
    bank_id = bank_id or DEFAULT_BANK_ID
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
async def update_customer(customer_id: str, update_data: dict, bank_id: str = None):
    """
    Update non-sensitive customer information in SQLite.
    """
    bank_id = bank_id or DEFAULT_BANK_ID
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
async def score_application(application_data: dict, bank_id: str = None):
    bank_id = bank_id or DEFAULT_BANK_ID
    """
    Score a loan application using the local model.
    For existing customers: update their record in bank database.
    For new customers: save to new_applications.db.
    """
    try:
        customer_id = application_data.get('customer_id')
        
        # Score the application
        scoring_service = get_scoring_service()
        alt_score, risk_band, p_default = scoring_service.predict_score(application_data)

        # Add score to application data
        application_data['alt_score'] = alt_score
        application_data['credit_score'] = alt_score

        # Check if customer exists in bank database
        from app.core.db import db_manager
        try:
            existing_customer = db_manager.get_customer(bank_id, customer_id)
            if existing_customer is not None:
                # Update existing customer in bank database
                update_data = {
                    'credit_score': alt_score,
                    'loan_amount': application_data.get('loan_amount'),
                    'loan_duration_months': application_data.get('loan_duration_months'),
                }
                db_manager.update_customer(bank_id, customer_id, update_data)
                saved = True
                is_new = False
            else:
                # Save as new application
                new_apps_service = get_new_applications_service()
                saved = new_apps_service.save_application(application_data)
                is_new = True
        except Exception:
            # If customer doesn't exist, save as new application
            new_apps_service = get_new_applications_service()
            saved = new_apps_service.save_application(application_data)
            is_new = True

        return {
            "status": "success",
            "alt_score": alt_score,
            "credit_score": alt_score,
            "risk_band": risk_band,
            "default_probability": round(p_default, 4),
            "recommendation": "Approve" if alt_score >= 650 else "Review" if alt_score >= 500 else "Decline",
            "saved": saved,
            "is_new_customer": is_new,
            "customer_id": customer_id
        }
    except Exception as e:
        logger.error(f"Failed to score application: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/applications/approve/{customer_id}")
async def approve_application(customer_id: str):
    """
    Approve a pending loan application.
    """
    try:
        new_apps_service = get_new_applications_service()
        success = new_apps_service.approve_application(customer_id)

        if success:
            return {
                "status": "success",
                "message": f"Application {customer_id} approved",
                "customer_id": customer_id
            }
        else:
            raise HTTPException(status_code=404, detail=f"Application {customer_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve application: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/applications/reject/{customer_id}")
async def reject_application(customer_id: str):
    """
    Reject a pending loan application.
    """
    try:
        new_apps_service = get_new_applications_service()
        success = new_apps_service.reject_application(customer_id)

        if success:
            return {
                "status": "success",
                "message": f"Application {customer_id} rejected",
                "customer_id": customer_id
            }
        else:
            raise HTTPException(status_code=404, detail=f"Application {customer_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject application: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/applications/count")
async def get_new_applications_count():
    """
    Get count of pending new applications in new_applications.db.
    """
    try:
        new_apps_service = get_new_applications_service()
        count = new_apps_service.get_application_count()
        return {
            "count": count,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to get application count: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/applications/next-customer-id")
async def get_next_customer_id(bank_id: str = None):
    """
    Get the next customer ID by counting total customers in bank database + new_applications.db.
    """
    bank_id = bank_id or "bank_b"  # Default to bank_b for this backend
    try:
        from app.core.db import db_manager

        # Get count from bank database
        bank_df = db_manager.load_customers(bank_id)
        bank_count = len(bank_df)

        # Get count from new applications
        new_apps_service = get_new_applications_service()
        new_apps_count = new_apps_service.get_application_count()

        # Next ID is total + 1
        next_id = bank_count + new_apps_count + 1
        customer_id = f"{next_id:08d}"  # Format: 00000001, 00000002, etc. (8 digits)

        return {
            "customer_id": customer_id,
            "total_existing": bank_count + new_apps_count,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to get next customer ID: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/status")
async def get_model_status():
    """
    Get current model training status and metrics.
    """
    try:
        # Get new applications count
        new_apps_service = get_new_applications_service()
        new_app_count = new_apps_service.get_application_count()

        # TODO: Get actual model metrics
        return {
            "local_records": 1234,
            "new_applications": new_app_count,
            "good_bad_ratio": "70:30",
            "last_training": "2 days ago",
            "local_auc": 0.94,
            "global_round": 12,
            "global_auc": 0.95,
            "privacy_budget": 0.7
        }
    except Exception as e:
        logger.error(f"Failed to get model status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
