"""
Neural Network Scoring Service - Uses trained model for credit scoring
Loads model.h5, scaler.pkl, and encoders.pkl from models directory
Provides credit score predictions using proper feature pipeline
Alternative Credit Score: 300 + 600 * (1 - p_default)
"""

import os
import numpy as np
import pandas as pd
import pickle
import tensorflow as tf
from tensorflow import keras
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging
from datetime import datetime

# Suppress TensorFlow warnings and disable XLA JIT
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices=false'
os.environ['XLA_FLAGS'] = '--xla_gpu_cuda_data_dir=/usr/local/cuda'
tf.get_logger().setLevel('ERROR')
# Disable XLA JIT compilation to avoid libdevice issues
tf.config.optimizer.set_jit(False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model paths - use the trained model as base
MODEL_PATH = 'models/global_model.h5'  # Base model for scoring (updated from model.h5)
WEIGHTS_PATH = 'models/global_model.weights.h5'
SCALER_PATH = 'models/scaler.pkl'
ENCODERS_PATH = 'models/encoders.pkl'

# Feature specification (46 features - same as training)
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

# Categorical columns that need encoding (only these 3 were encoded during training)
CATEGORICAL_COLS = ['gender', 'marital_status', 'education']


class NeuralNetworkScoringService:
    """Neural Network-based credit scoring using trained model with proper preprocessing"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = None
        self.model_loaded_at = None
        
    def load_model(self, force_reload: bool = False) -> bool:
        """Load the model, scaler, and encoders"""
        try:
            if not force_reload and self.model is not None:
                return True
            
            # Check if all required files exist
            if not os.path.exists(MODEL_PATH):
                logger.error(f"Model file not found: {MODEL_PATH}")
                return False
            
            if not os.path.exists(SCALER_PATH):
                logger.error(f"Scaler file not found: {SCALER_PATH}")
                return False
            
            if not os.path.exists(ENCODERS_PATH):
                logger.error(f"Encoders file not found: {ENCODERS_PATH}")
                return False
            
            # Load the model - enable GPU
            logger.info(f"Loading model from: {MODEL_PATH}")
            os.environ['XLA_FLAGS'] = '--xla_gpu_cuda_data_dir=' + os.environ.get('CONDA_PREFIX', '')
            self.model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            
            # Compile for inference
            self.model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Load scaler
            logger.info(f"Loading scaler from: {SCALER_PATH}")
            with open(SCALER_PATH, 'rb') as f:
                self.scaler = pickle.load(f)
            
            # Load encoders
            logger.info(f"Loading encoders from: {ENCODERS_PATH}")
            with open(ENCODERS_PATH, 'rb') as f:
                self.encoders = pickle.load(f)
            
            self.model_loaded_at = datetime.now().isoformat()
            
            logger.info(f"✅ Model, scaler, and encoders loaded successfully")
            logger.info(f"   Model expects {len(FEATURE_COLS)} features")
            logger.info(f"   Categorical encoders: {list(self.encoders.keys())}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model components: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def preprocess_features(self, features: Dict) -> np.ndarray:
        """Preprocess features using saved scaler and encoders"""
        try:
            # Create DataFrame with single row
            df = pd.DataFrame([features])
            
            # Ensure all feature columns exist (fill missing with default values)
            for col in FEATURE_COLS:
                if col not in df.columns:
                    # Column doesn't exist - set to 0
                    df[col] = 0
                elif df[col].isnull().any():
                    # Column exists but has NaN values
                    if col in CATEGORICAL_COLS:
                        # For categorical columns that were encoded, use most common value
                        df[col].fillna('Unknown', inplace=True)
                    else:
                        # For numeric columns, use 0
                        df[col].fillna(0, inplace=True)
            
            # Select only feature columns in correct order
            X = df[FEATURE_COLS].copy()
            
            # Apply label encoders ONLY to the 3 categorical columns that were encoded in training
            for col in CATEGORICAL_COLS:
                if col in self.encoders:
                    encoder = self.encoders[col]
                    try:
                        # Transform known values
                        X[col] = encoder.transform(X[col].astype(str))
                    except ValueError as e:
                        # Handle unknown categories - use first class (usually most common)
                        logger.warning(f"Unknown category '{X[col].values[0]}' in {col}, mapping to 0")
                        X[col] = 0
                else:
                    # This shouldn't happen if encoders are loaded correctly
                    logger.error(f"Missing encoder for {col}! This should not happen.")
                    X[col] = 0
            
            # Convert to numpy array
            X_array = X.values.astype(float)
            
            # Apply scaler
            X_scaled = self.scaler.transform(X_array)
            
            # Handle any NaN/Inf values
            X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)
            
            return X_scaled
            
        except Exception as e:
            logger.error(f"Error preprocessing features: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def predict_score(self, features: Dict) -> Tuple[int, str, float]:
        """
        Predict credit score from features.
        Returns (alt_score, risk_band, p_default)
        """
        try:
            # Load model if not loaded
            if self.model is None:
                if not self.load_model():
                    raise Exception("Failed to load model")
            
            # Preprocess features
            X = self.preprocess_features(features)
            
            # Make prediction - get default probability (force CPU execution)
            with tf.device('/CPU:0'):
                p_default = float(self.model.predict(X, verbose=0)[0][0])
            
            # Convert to Alternative Credit Score: 300 + 600 * (1 - p_default)
            alt_score = int(round(300 + 600 * (1 - p_default)))
            
            # Clamp to valid range
            alt_score = max(300, min(900, alt_score))
            
            # Determine risk band based on score
            if alt_score >= 750:
                risk_band = "Low"
        except Exception as e:
            logger.error(f"Error predicting score: {e}")
            import traceback
            traceback.print_exc()
            # Return conservative fallback values (high default probability = low score)
            return 400, "High", 0.83  # 300 + 600 * (1 - 0.83) = ~402nd, p_default
            
        except Exception as e:
            logger.error(f"Error predicting score: {e}")
            import traceback
            traceback.print_exc()
            # Return default safe values
            return 600, "Medium", 0.5
    
    def get_model_info(self) -> Dict:
        """Get information about the currently loaded model"""
        return {
            "model_path": MODEL_PATH,
            "model_loaded_at": self.model_loaded_at,
            "model_exists": self.model is not None,
            "scaler_loaded": self.scaler is not None,
            "encoders_loaded": self.encoders is not None,
            "num_features": len(FEATURE_COLS),
            "categorical_features": CATEGORICAL_COLS,
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
    Returns dict with alt_score, risk_band, and p_default.
    """
    service = get_scoring_service()
    alt_score, risk_band, p_default = service.predict_score(features)
    
    return {
        "credit_score": alt_score,
        "alt_score": alt_score,
        "risk_band": risk_band,
        "default_probability": round(p_default, 4),
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
            'age': 35, 'gender': 'Male', 'monthly_income': 50000,
            'dti': 0.3, 'loan_amount': 500000, 'marital_status': 'Married',
            'education': 'Graduate', 'home_ownership': 'Owned'
        }
        
        alt_score, risk_band, p_default = service.predict_score(test_features)
        print(f"Test prediction: Score={alt_score}, Risk={risk_band}, P(default)={p_default:.4f}")
    else:
        print("❌ Failed to load model")
