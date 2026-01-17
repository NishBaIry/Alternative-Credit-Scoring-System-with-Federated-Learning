# customer_service.py
# Business logic for customer management operations.
# Functions:
# - get_customer_list(bank_id, filters): returns paginated customer list
# - get_customer_detail(bank_id, customer_id): returns full customer profile + score
# - update_customer(bank_id, customer_id, data): updates editable fields
# - create_customer(bank_id, data): adds new customer to dataset
# Abstracts DB operations from API routes, making code cleaner and testable.

from typing import List, Dict, Optional
import pandas as pd
from app.core.db import db_manager

class CustomerService:
    """Service for customer-related operations."""
    
    def __init__(self, bank_id: str):
        self.bank_id = bank_id
    
    def get_customer_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        risk_band: Optional[str] = None
    ) -> Dict:
        """
        Get paginated list of customers.
        """
        df = db_manager.load_customers(self.bank_id)
        
        if risk_band:
            df = df[df['risk_band'] == risk_band]
        
        total = len(df)
        customers = df.iloc[skip:skip + limit].to_dict('records')
        
        return {
            "total": total,
            "customers": customers,
            "page": skip // limit + 1,
            "page_size": limit
        }
    
    def get_customer_detail(self, customer_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific customer.
        """
        customer = db_manager.get_customer(self.bank_id, customer_id)
        
        if customer:
            # TODO: Add score history, factors, etc.
            return {
                **customer,
                "score_history": [],
                "score_factors": []
            }
        
        return None
    
    def update_customer(self, customer_id: str, update_data: Dict) -> Dict:
        """
        Update customer information.
        Only allows editing non-sensitive fields.
        """
        df = db_manager.load_customers(self.bank_id)
        
        # Find customer
        mask = df['customer_id'] == customer_id
        if not mask.any():
            raise ValueError(f"Customer {customer_id} not found")
        
        # Update allowed fields
        allowed_fields = ['email', 'phone', 'marital_status', 'dependents']
        for field in allowed_fields:
            if field in update_data:
                df.loc[mask, field] = update_data[field]
        
        # Save back
        db_manager.save_customers(self.bank_id, df)
        
        return {"message": "Customer updated successfully"}
    
    def create_customer(self, customer_data: Dict) -> Dict:
        """
        Create a new customer record.
        """
        df = db_manager.load_customers(self.bank_id)
        
        # Add new customer
        new_customer = pd.DataFrame([customer_data])
        df = pd.concat([df, new_customer], ignore_index=True)
        
        # Save
        db_manager.save_customers(self.bank_id, df)
        
        return {
            "message": "Customer created successfully",
            "customer_id": customer_data['customer_id']
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
