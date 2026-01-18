"""
Neural Network Scoring Service - Uses FL-trained models for credit scoring
Loads the active_model.h5 which is updated by FL model downloads
Provides credit score predictions using the latest global model
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler, LabelEncoder
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging
from datetime import datetime

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model paths
ACTIVE_MODEL_PATH = 'models/active_model.h5'
GLOBAL_MODEL_PATH = 'models/global_model.h5'
FALLBACK_MODEL_PATH = 'models/global_aggregated_round1.h5'

# Feature specification (same as FL training)
FEATURE_COLS = [
    'age', 'gender', 'marital_status', 'education', 'dependents', 'home_ownership', 'region',
    'monthly_income', 'annual_income', 'job_type', 'job_tenure_years', 'net_monthly_income',
    'monthly_debt_payments', 'dti', 'total_dti',
    'savings_balance', 'checking_balance', 'total_assets', 'total_liabilities', 'net_worth',
    'loan_amount', 'loan_duration_months', 'loan_purpose',
    'base_interest_rate', 'interest_rate', 'monthly_loan_payment',
    'tot_enq', 'enq_L3m', 'enq_L6m', 'enq_L12m', 'time_since_recent_enq',
    'num_30dpd', 'num_60dpd', 'max_delinquency_level',
    'CC_utilization', 'PL_utilization', 'HL_flag', 'GL_flag',
    'utility_bill_score',
    'upi_txn_count_avg', 'upi_txn_count_std', 'upi_total_spend_month_avg',
    'upi_merchant_diversity', 'upi_spend_volatility', 'upi_failed_txn_rate', 'upi_essentials_share',
]


class NeuralNetworkScoringService:
    """Neural Network-based credit scoring using FL-trained models"""
    
    def __init__(self):
        self.model = None
        self.model_path = None
        self.model_loaded_at = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def _get_model_path(self) -> Optional[str]:
        """Determine which model to use (priority order)"""
        # 1. Active model (updated by FL downloads)
        if os.path.exists(ACTIVE_MODEL_PATH):
            return ACTIVE_MODEL_PATH
        
        # 2. Global model (base model)
        if os.path.exists(GLOBAL_MODEL_PATH):
            return GLOBAL_MODEL_PATH
        
        # 3. Fallback model
        if os.path.exists(FALLBACK_MODEL_PATH):
            return FALLBACK_MODEL_PATH
        
        return None
    
    def load_model(self, force_reload: bool = False) -> bool:
        """Load the active model"""
        try:
            model_path = self._get_model_path()
            
            if model_path is None:
                logger.error("No model file found")
                return False
            
            # Check if we need to reload (model changed)
            if not force_reload and self.model is not None and self.model_path == model_path:
                # Model already loaded and path hasn't changed
                return True
            
            # Load the model
            logger.info(f"Loading model from: {model_path}")
            self.model = tf.keras.models.load_model(model_path, compile=False, safe_mode=False)
            self.model_path = model_path
            self.model_loaded_at = datetime.now().isoformat()
            
            # Compile for inference
            self.model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info(f"✅ Model loaded successfully from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def preprocess_features(self, features: Dict) -> np.ndarray:
        """Preprocess features for model input"""
        try:
            # Create DataFrame with single row
            df = pd.DataFrame([features])
            
            # Select only expected features
            available_features = [col for col in FEATURE_COLS if col in df.columns]
            X = df[available_features].copy()
            
            # Identify categorical and numerical columns
            categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
            numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
            
            # Fill missing values
            for col in numerical_cols:
                if X[col].isnull().any():
                    X[col].fillna(0, inplace=True)
            
            for col in categorical_cols:
                if X[col].isnull().any():
                    X[col].fillna('unknown', inplace=True)
            
            # Encode categorical variables
            for col in categorical_cols:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    # Fit with common values
                    self.label_encoders[col].fit(['unknown', 'male', 'female', 'other'])
                
                try:
                    X[col] = self.label_encoders[col].transform(X[col].astype(str))
                except:
                    # If unseen category, map to 'unknown'
                    X[col] = 0
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)
            
            return X_scaled
            
        except Exception as e:
            logger.error(f"Error preprocessing features: {e}")
            raise
    
    def predict_score(self, features: Dict) -> Tuple[int, str, float]:
        """
        Predict credit score from features.
        Returns (score, risk_band, probability)
        """
        try:
            # Load model if not loaded
            if self.model is None:
                if not self.load_model():
                    raise Exception("Failed to load model")
            
            # Preprocess features
            X = self.preprocess_features(features)
            
            # Make prediction
            default_prob = float(self.model.predict(X, verbose=0)[0][0])
            
            # Convert probability to credit score (300-900 range)
            # Lower default probability = higher credit score
            non_default_prob = 1 - default_prob
            score = int(300 + (non_default_prob * 600))
            
            # Determine risk band
            if score >= 750:
                risk_band = "Very Low"
            elif score >= 700:
                risk_band = "Low"
            elif score >= 650:
                risk_band = "Medium"
            elif score >= 600:
                risk_band = "High"
            else:
                risk_band = "Very High"
            
            return score, risk_band, non_default_prob
            
        except Exception as e:
            logger.error(f"Error predicting score: {e}")
            # Return default safe values
            return 650, "Medium", 0.5
    
    def get_model_info(self) -> Dict:
        """Get information about the currently loaded model"""
        return {
            "model_path": self.model_path,
            "model_loaded_at": self.model_loaded_at,
            "model_exists": self.model is not None,
            "active_model_available": os.path.exists(ACTIVE_MODEL_PATH),
            "global_model_available": os.path.exists(GLOBAL_MODEL_PATH),
        }
    
    def reload_model(self) -> bool:
        """Force reload the model (useful after FL update)"""
        logger.info("Force reloading model...")
        return self.load_model(force_reload=True)


# Global instance
_scoring_service = None


def get_scoring_service() -> NeuralNetworkScoringService:
    """Get singleton scoring service instance"""
    global _scoring_service
    if _scoring_service is None:
        _scoring_service = NeuralNetworkScoringService()
        _scoring_service.load_model()
    return _scoring_service


def predict_credit_score(features: Dict) -> Dict:
    """
    Convenience function to predict credit score.
    Returns dict with score, risk_band, and confidence.
    """
    service = get_scoring_service()
    score, risk_band, confidence = service.predict_score(features)
    
    return {
        "score": score,
        "risk_band": risk_band,
        "confidence": round(confidence, 3),
        "model_info": service.get_model_info()
    }


if __name__ == "__main__":
    # Test the service
    service = NeuralNetworkScoringService()
    
    if service.load_model():
        print("✅ Model loaded successfully")
        print(f"Model info: {service.get_model_info()}")
        
        # Test prediction with dummy data
        test_features = {
            'age': 35, 'gender': 'male', 'monthly_income': 50000,
            'dti': 0.3, 'loan_amount': 500000
        }
        
        score, risk_band, prob = service.predict_score(test_features)
        print(f"Test prediction: Score={score}, Risk={risk_band}, Prob={prob:.3f}")
    else:
        print("❌ Failed to load model")
