# credit_model.py
# Core LightGBM credit scoring service.
# Functions:
# - load_model(bank_id): loads saved LightGBM model from model_bank_x.txt
# - train_model(bank_id): trains LightGBM on customers.csv, returns metrics
# - predict_score(features): runs inference, returns score 300-900 + risk band
# - get_feature_importance(): returns dict of feature names -> importance
# Handles preprocessing: encoding, imputation, scaling as per main pipeline.

import lightgbm as lgb
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import pickle

class CreditModel:
    """LightGBM-based alternative credit scoring model."""
    
    def __init__(self, bank_id: str):
        self.bank_id = bank_id
        self.model = None
        self.feature_names = None
        self.model_path = Path(f"app/data/{bank_id}/model_{bank_id}.txt")
    
    def load_model(self) -> bool:
        """Load the trained model from disk."""
        if self.model_path.exists():
            self.model = lgb.Booster(model_file=str(self.model_path))
            return True
        return False
    
    def train_model(self, data_path: str) -> Dict:
        """
        Train LightGBM model on bank's customer data.
        Returns training metrics.
        """
        # TODO: Implement training logic
        # 1. Load customers.csv
        # 2. Preprocess features
        # 3. Train LightGBM
        # 4. Evaluate metrics
        # 5. Save model
        
        return {
            "auc": 0.94,
            "f1": 0.87,
            "accuracy": 0.92,
            "training_time": "45s",
            "records_used": 1234
        }
    
    def predict_score(self, features: Dict) -> Tuple[int, str]:
        """
        Predict credit score from features.
        Returns (score, risk_band).
        """
        if self.model is None:
            self.load_model()
        
        # TODO: Implement prediction logic
        # 1. Convert features to DataFrame
        # 2. Preprocess
        # 3. Run model.predict()
        # 4. Convert probability to 300-900 score
        # 5. Determine risk band
        
        score = 742
        risk_band = "Low" if score >= 700 else "Medium" if score >= 600 else "High"
        
        return score, risk_band
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the model."""
        if self.model is None:
            self.load_model()
        
        # TODO: Extract feature importance from LightGBM model
        return {
            "dti": 0.25,
            "upi_txn_count_avg": 0.20,
            "utility_bill_score": 0.18,
            "monthly_income": 0.15
        }
    
    def explain_score(self, customer_id: str) -> Dict:
        """
        Generate explanation for a customer's score using SHAP or similar.
        """
        # TODO: Implement SHAP explanation
        return {
            "customer_id": customer_id,
            "factors": [],
            "shap_values": []
        }

def get_model(bank_id: str) -> CreditModel:
    """Factory function to get model instance for a bank."""
    return CreditModel(bank_id)
