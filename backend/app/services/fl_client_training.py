"""
Federated Learning Client Training Script for Bank A
Loads base model, fine-tunes on bank's local data, uploads weights to FL server
"""

import os
import sys
import requests
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import json
from datetime import datetime
import pickle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
FL_SERVER_URL = os.getenv('FL_SERVER_URL', 'http://localhost:5000')
BANK_ID = os.getenv('BANK_ID', 'bank_a')
BANK_NAME = os.getenv('BANK_NAME', 'Bank A')
LOCAL_DATASET_PATH = os.getenv('LOCAL_DATASET_PATH', 'data/fl_dataset.csv')
BASE_MODEL_PATH = os.getenv('BASE_MODEL_PATH', 'models/global_model.h5')
WEIGHTS_UPLOAD_PATH = os.getenv('WEIGHTS_UPLOAD_PATH', 'models/client_weights.npz')

# Training hyperparameters
EPOCHS = int(os.getenv('FL_EPOCHS', 10))
BATCH_SIZE = int(os.getenv('FL_BATCH_SIZE', 256))
LEARNING_RATE = float(os.getenv('FL_LEARNING_RATE', 0.001))
VALIDATION_SPLIT = float(os.getenv('FL_VALIDATION_SPLIT', 0.2))

# Feature specification
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

TARGET_COL = "default_flag"

# Set random seeds
np.random.seed(42)
tf.random.set_seed(42)

class BankFLClient:
    """Federated Learning Client for Bank"""
    
    def __init__(self, bank_id, bank_name, dataset_path, server_url):
        self.bank_id = bank_id
        self.bank_name = bank_name
        self.dataset_path = dataset_path
        self.server_url = server_url
        self.model = None
        self.base_weights = None
        self.scaler = None
        self.encoders = {}
        
    def load_data(self):
        """Load and preprocess bank's local dataset"""
        print("=" * 80)
        print(f"FEDERATED LEARNING CLIENT - {self.bank_name}")
        print("=" * 80)
        
        print(f"\n[1/6] Loading local dataset: {self.dataset_path}")
        df = pd.read_csv(self.dataset_path)
        print(f"  ✓ Data shape: {df.shape}")
        
        # Remove authentication columns
        remove_cols = ['customer_id', 'password']
        df = df.drop(columns=[col for col in remove_cols if col in df.columns])
        
        # Separate target
        y = df[TARGET_COL].astype(int).values
        
        # Select features
        available_features = [col for col in FEATURE_COLS if col in df.columns]
        X = df[available_features].copy()
        
        # Identify categorical and numerical columns
        categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
        numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        
        print(f"  ✓ Features: {X.shape[1]}")
        print(f"  ✓ Numerical: {len(numerical_cols)}, Categorical: {len(categorical_cols)}")
        print(f"  ✓ Default rate: {y.mean():.2%}")
        
        # Handle missing values
        print("\n[2/6] Handling missing values...")
        for col in numerical_cols:
            if X[col].isnull().any():
                median_val = X[col].median()
                X[col].fillna(median_val, inplace=True)
        
        for col in categorical_cols:
            if X[col].isnull().any():
                mode_val = X[col].mode()
                if len(mode_val) > 0:
                    X[col].fillna(mode_val[0], inplace=True)
        
        # Encode categorical variables
        print("\n[3/6] Encoding categorical variables...")
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.encoders[col] = le
        
        # Scale features
        print("\n[4/6] Scaling features...")
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)
        
        print(f"  ✓ Scaled shape: {X_scaled.shape}")
        
        return X_scaled, y
    
    def download_global_model(self):
        """Download global model from FL server"""
        print(f"\n[5/6] Downloading global model from server...")
        
        try:
            response = requests.get(
                f"{self.server_url}/api/download_global_model",
                params={'client_id': self.bank_id, 'format': 'bytes'},
                timeout=60
            )
            
            if response.status_code == 200:
                # Save model temporarily
                temp_model_path = BASE_MODEL_PATH
                os.makedirs(os.path.dirname(temp_model_path), exist_ok=True)
                
                with open(temp_model_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"  ✓ Downloaded model ({len(response.content) / (1024*1024):.2f} MB)")
                return temp_model_path
            else:
                print(f"  ⚠️  Server returned status {response.status_code}")
                return None
        
        except Exception as e:
            print(f"  ⚠️  Download failed: {e}")
            return None
    
    def load_model(self, model_path):
        """Load base model"""
        print(f"\n[6/6] Loading base model...")
        
        try:
            self.model = tf.keras.models.load_model(model_path, compile=False)
            self.base_weights = self.model.get_weights()
            print(f"  ✓ Model loaded: {len(self.base_weights)} layers")
            
            # Compile model
            self.model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
                loss='binary_crossentropy',
                metrics=['accuracy', 
                        keras.metrics.Precision(name='precision'),
                        keras.metrics.Recall(name='recall')]
            )
            
            return True
        
        except Exception as e:
            print(f"  ❌ Failed to load model: {e}")
            return False
    
    def train_local_model(self, X_train, y_train):
        """Fine-tune model on local bank data"""
        print("\n" + "=" * 80)
        print("STARTING LOCAL TRAINING")
        print("=" * 80)
        
        print(f"\nTraining Configuration:")
        print(f"  • Epochs: {EPOCHS}")
        print(f"  • Batch Size: {BATCH_SIZE}")
        print(f"  • Learning Rate: {LEARNING_RATE}")
        print(f"  • Validation Split: {VALIDATION_SPLIT}")
        print(f"  • Training Samples: {len(X_train)}")
        
        # Early stopping
        early_stop = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        )
        
        # Train
        print("\nTraining Progress:")
        history = self.model.fit(
            X_train, y_train,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            validation_split=VALIDATION_SPLIT,
            callbacks=[early_stop],
            verbose=1
        )
        
        print("\n✅ Training completed!")
        
        # Evaluate
        print("\nFinal Metrics:")
        results = self.model.evaluate(X_train, y_train, verbose=0)
        print(f"  • Loss: {results[0]:.4f}")
        print(f"  • Accuracy: {results[1]:.4f}")
        print(f"  • Precision: {results[2]:.4f}")
        print(f"  • Recall: {results[3]:.4f}")
        
        return history
    
    def save_weights(self):
        """Save trained weights to file"""
        print(f"\nSaving weights to: {WEIGHTS_UPLOAD_PATH}")
        
        os.makedirs(os.path.dirname(WEIGHTS_UPLOAD_PATH), exist_ok=True)
        
        # Get trained weights
        trained_weights = self.model.get_weights()
        
        # Save as .npz
        np.savez_compressed(WEIGHTS_UPLOAD_PATH, *trained_weights)
        
        file_size_mb = os.path.getsize(WEIGHTS_UPLOAD_PATH) / (1024 * 1024)
        print(f"  ✓ Weights saved ({file_size_mb:.2f} MB)")
        
        return WEIGHTS_UPLOAD_PATH
    
    def upload_weights_to_server(self, weights_path, num_samples):
        """Upload trained weights to FL server"""
        print("\n" + "=" * 80)
        print("UPLOADING WEIGHTS TO FL SERVER")
        print("=" * 80)
        
        try:
            # Prepare metadata
            metadata = {
                'client_id': self.bank_id,
                'client_name': self.bank_name,
                'upload_type': 'full_weights',
                'num_samples': num_samples,
                'timestamp': datetime.now().isoformat(),
                'epochs': EPOCHS,
                'batch_size': BATCH_SIZE,
                'learning_rate': LEARNING_RATE
            }
            
            # Open weights file
            with open(weights_path, 'rb') as f:
                files = {'weights': (os.path.basename(weights_path), f, 'application/octet-stream')}
                data = {'metadata': json.dumps(metadata)}
                
                print(f"\nUploading to: {self.server_url}/api/upload_weights")
                print(f"Bank: {self.bank_name} ({self.bank_id})")
                print(f"Samples: {num_samples}")
                
                response = requests.post(
                    f"{self.server_url}/api/upload_weights",
                    files=files,
                    data=data,
                    timeout=120
                )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Upload successful!")
                print(f"  • Upload ID: {result.get('upload_id')}")
                print(f"  • Pending banks: {result.get('pending_clients')}/{result.get('threshold')}")
                
                if result.get('new_model_available'):
                    print(f"  • New global model available (Round {result.get('round')})")
                
                return True
            else:
                print(f"\n❌ Upload failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        
        except Exception as e:
            print(f"\n❌ Upload error: {e}")
            import traceback
            traceback.print_exc()
            return False

def run_fl_training():
    """Main function to run FL training for bank"""
    
    # Initialize client
    client = BankFLClient(
        bank_id=BANK_ID,
        bank_name=BANK_NAME,
        dataset_path=LOCAL_DATASET_PATH,
        server_url=FL_SERVER_URL
    )
    
    # Load and preprocess data
    X_train, y_train = client.load_data()
    
    # Download global model from server
    model_path = client.download_global_model()
    
    # If download failed, try to use local base model
    if model_path is None:
        if os.path.exists(BASE_MODEL_PATH):
            print(f"  ℹ️  Using local base model: {BASE_MODEL_PATH}")
            model_path = BASE_MODEL_PATH
        else:
            print(f"  ❌ No model available. Exiting.")
            return False
    
    # Load model
    if not client.load_model(model_path):
        return False
    
    # Train on local data
    client.train_local_model(X_train, y_train)
    
    # Save trained weights
    weights_path = client.save_weights()
    
    # Upload to server
    success = client.upload_weights_to_server(weights_path, num_samples=len(X_train))
    
    if success:
        print("\n" + "=" * 80)
        print("✅ FEDERATED LEARNING ROUND COMPLETE")
        print("=" * 80)
    
    return success

if __name__ == "__main__":
    run_fl_training()
