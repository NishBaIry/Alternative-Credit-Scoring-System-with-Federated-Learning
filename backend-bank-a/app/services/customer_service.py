# customer_service.py
# Business logic for customer management operations using SQLite.
# Functions:
# - get_customer_list(bank_id, filters): returns paginated customer list
# - get_customer_detail(bank_id, customer_id): returns full customer profile + score
# - update_customer(bank_id, customer_id, data): updates editable fields
# - score_customer(bank_id, customer_id): computes and updates alt_score
# Abstracts DB operations from API routes, making code cleaner and testable.

from typing import List, Dict, Optional
import logging
from app.core.db import db_manager
from app.services.nn_scoring_service import get_scoring_service

logger = logging.getLogger(__name__)

class CustomerService:
    """Service for customer-related operations using SQLite."""
    
    def __init__(self, bank_id: str):
        self.bank_id = bank_id
    
    def get_customer_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Get paginated list of customers from SQLite.
        """
        customers, total = db_manager.get_customers_paginated(
            self.bank_id, skip, limit, filters
        )
        
        # Remove password field from results
        for customer in customers:
            if 'password' in customer:
                del customer['password']
        
        return {
            "total": total,
            "customers": customers,
            "page": skip // limit + 1 if limit > 0 else 1,
            "page_size": limit
        }
    
    def get_customer_detail(self, customer_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific customer from SQLite.
        Computes alt_score if not present.
        """
        customer = db_manager.get_customer(self.bank_id, customer_id)

        if customer:
            # Remove password for security
            if 'password' in customer:
                del customer['password']

            # Compute alt_score if not present or is 0
            if not customer.get('alt_score') or customer.get('alt_score') == 0:
                try:
                    scoring_service = get_scoring_service()
                    alt_score, risk_band, p_default = scoring_service.predict_score(customer)
                    customer['alt_score'] = alt_score

                    # Update in database for future use
                    db_manager.update_customer(
                        self.bank_id,
                        customer_id,
                        {'alt_score': alt_score}
                    )
                except Exception as e:
                    logger.error(f"Failed to compute alt_score for {customer_id}: {e}")
                    # Fallback to credit_score if available
                    customer['alt_score'] = customer.get('credit_score', None)

            return {
                **customer,
                "score_history": [],
                "score_factors": []
            }

        return None
    
    def update_customer(self, customer_id: str, update_data: Dict) -> Dict:
        """
        Update customer information in SQLite.
        Only allows editing non-sensitive fields.
        """
        # Filter to allowed fields only
        allowed_fields = ['monthly_income', 'dti', 'loan_amount', 'loan_duration_months']
        filtered_updates = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not filtered_updates:
            raise ValueError("No valid fields to update")
        
        success = db_manager.update_customer(self.bank_id, customer_id, filtered_updates)
        
        if not success:
            raise ValueError(f"Customer {customer_id} not found or update failed")
        
        return {"message": "Customer updated successfully"}
    
    def score_customer(self, customer_id: str) -> Dict:
        """
        Score a customer and update their alt_score in the database.
        Returns the scoring result.
        """
        # Get customer data from database
        customer = db_manager.get_customer(self.bank_id, customer_id)
        
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Get scoring service
        service = get_scoring_service()
        
        # Predict score
        alt_score, risk_band, p_default = service.predict_score(customer)
        
        # Update alt_score in database
        db_manager.update_customer(
            self.bank_id, 
            customer_id, 
            {'credit_score': alt_score}
        )
        
        logger.info(f"Scored customer {customer_id}: alt_score={alt_score}, risk={risk_band}")
        
        return {
            "customer_id": customer_id,
            "alt_score": alt_score,
            "credit_score": alt_score,
            "risk_band": risk_band,
            "default_probability": round(p_default, 4)
        }
    
    def search_customers(self, query: str) -> List[Dict]:
        """
        Search customers by ID, name, or other fields.
        """
        df = db_manager.load_customers(self.bank_id)
        
        # Simple search across multiple columns
        mask = (
            df['customer_id'].str.contains(query, case=False, na=False) |
            df['name'].str.contains(query, case=False, na=False)
        )
        
        return df[mask].to_dict('records')

def get_customer_service(bank_id: str) -> CustomerService:
    """Factory function to get customer service for a bank."""
    return CustomerService(bank_id)
