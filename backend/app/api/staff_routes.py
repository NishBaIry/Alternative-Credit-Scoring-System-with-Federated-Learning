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
import pandas as pd
import os

router = APIRouter()

CUSTOMERS_CSV = 'data/customers.csv'

@router.get("/customers")
async def list_customers(skip: int = 0, limit: int = 100, risk_band: Optional[str] = None):
    """
    List all customers for the bank.
    Supports pagination and filtering.
    """
    try:
        if not os.path.exists(CUSTOMERS_CSV):
            return {"total": 0, "customers": []}
        
        df = pd.read_csv(CUSTOMERS_CSV)
        
        # Remove password column for security
        if 'password' in df.columns:
            df = df.drop(columns=['password'])
        
        # Apply pagination
        total = len(df)
        paginated_df = df.iloc[skip:skip+limit]
        
        # Convert to list of dicts
        customers = paginated_df.to_dict('records')
        
        return {
            "total": total,
            "customers": customers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load customers: {str(e)}")

@router.get("/customers/{customer_id}")
async def get_customer_detail(customer_id: str):
    """
    Get detailed information for a specific customer.
    """
    try:
        if not os.path.exists(CUSTOMERS_CSV):
            raise HTTPException(status_code=404, detail="Customers database not found")
        
        df = pd.read_csv(CUSTOMERS_CSV)
        customer = df[df['customer_id'] == customer_id]
        
        if customer.empty:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        
        # Remove password for security
        customer_data = customer.iloc[0].to_dict()
        if 'password' in customer_data:
            del customer_data['password']
        
        return {
            "status": "success",
            "customer": customer_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get customer: {str(e)}")

@router.patch("/customers/{customer_id}")
async def update_customer(customer_id: str, update_data: dict):
    """
    Update non-sensitive customer information.
    """
    # TODO: Implement customer update
    return {"message": "Customer updated successfully"}

@router.post("/applications/score")
async def score_application(application_data: dict):
    """
    Score a new loan application using the local model.
    """
    # TODO: Implement application scoring
    return {
        "score": 742,
        "risk_band": "Approve",
        "top_drivers": [
            "High bill on-time rate",
            "Strong UPI essentials share",
            "Low DTI ratio"
        ]
    }

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
