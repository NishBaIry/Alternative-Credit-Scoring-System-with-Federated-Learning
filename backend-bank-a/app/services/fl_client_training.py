"""
Federated Learning Client Training Script for Bank
Loads base model, fine-tunes on bank's local SQLite data, uploads weights to FL server
Updated to match train_neural_network_v2.py pipeline
"""

import os
import sys
import requests
import numpy as np
import pandas as pd
import sqlite3
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import json
from datetime import datetime
import pickle
from dotenv import load_dotenv

# Set XLA flags for GPU
os.environ['XLA_FLAGS'] = '--xla_gpu_cuda_data_dir=' + os.environ.get('CONDA_PREFIX', '')

# Load environment variables
load_dotenv()

# Import centralized config
from app.config import settings

# Configuration from centralized settings
FL_SERVER_URL = settings.FL_SERVER_URL
BANK_ID = settings.BANK_ID
BANK_NAME = settings.BANK_NAME
DATABASE_PATH = settings.get_bank_db_path()
BASE_MODEL_PATH = settings.GLOBAL_MODEL_PATH
CLIENT_MODEL_PATH = settings.get_client_model_path()
WEIGHTS_UPLOAD_PATH = settings.get_weights_upload_path()

# Training hyperparameters from config
EPOCHS = settings.FL_EPOCHS
BATCH_SIZE = settings.FL_BATCH_SIZE
LEARNING_RATE = float(os.getenv('FL_LEARNING_RATE', 0.001))
VALIDATION_SPLIT = settings.FL_VALIDATION_SPLIT

# Feature specification (46 features - same as train_neural_network_v2.py)
FEATURE_COLS = [
    # Demographics
    'age', 'gender', 'marital_status', 'education', 'dependents', 'home_ownership', 'region',
    
    # Income & Capacity
    'monthly_income', 'annual_income', 'job_type', 'job_tenure_years', 'net_monthly_income',
    'monthly_debt_payments', 'dti', 'total_dti',
    'savings_balance', 'checking_balance', 'total_assets', 'total_liabilities', 'net_worth',
    
    # Loan Request
    'loan_amount', 'loan_duration_months', 'loan_purpose',
    'base_interest_rate', 'interest_rate', 'monthly_loan_payment',
    
    # Traditional Credit Behavior
    'tot_enq', 'enq_L3m', 'enq_L6m', 'enq_L12m', 'time_since_recent_enq',
    'num_30dpd', 'num_60dpd', 'max_delinquency_level',
    'CC_utilization', 'PL_utilization', 'HL_flag', 'GL_flag',
    'utility_bill_score',
    
    # UPI Alternative Data
    'upi_txn_count_avg', 'upi_txn_count_std', 'upi_total_spend_month_avg',
    'upi_merchant_diversity', 'upi_spend_volatility', 'upi_failed_txn_rate', 'upi_essentials_share',
]

TARGET_COL = "default_flag"

# Categorical columns that need encoding (only these 3)
CATEGORICAL_COLS = ['gender', 'marital_status', 'education']

# Set random seeds
np.random.seed(42)
tf.random.set_seed(42)

class BankFLClient:
    """Federated Learning Client for Bank"""
    
    def __init__(self, bank_id, bank_name, database_path, server_url):
        self.bank_id = bank_id
        self.bank_name = bank_name
        self.database_path = database_path
        self.server_url = server_url
        self.model = None
        self.base_weights = None
        self.scaler = None
        self.encoders = {}
        
    def load_data(self):
        """Load and preprocess bank's local dataset from SQLite database"""
        print("=" * 80)
        print(f"FEDERATED LEARNING CLIENT - {self.bank_name}")
        print("=" * 80)
        
        print(f"\n[1/6] Loading training data from SQLite...")
        
        # Check if database exists
        if not os.path.exists(self.database_path):
            raise FileNotFoundError(f"Database not found: {self.database_path}")
        
        # Connect to SQLite and load data
        conn = sqlite3.connect(self.database_path)
        df = pd.read_sql_query("SELECT * FROM customers", conn)
        conn.close()
        
        print(f"  ✓ Loaded {len(df):,} rows from {self.database_path}")
        
        # Remove non-feature columns
        remove_cols = ['customer_id', 'password', 'created_at', 'updated_at', 'credit_score']
        df = df.drop(columns=[col for col in remove_cols if col in df.columns])
        
        # Separate target
        if TARGET_COL not in df.columns:
            raise ValueError(f"Target column '{TARGET_COL}' not found in database")
        
        y = df[TARGET_COL].astype(int).values
        
        # Select features (ensure all expected features exist)
        for col in FEATURE_COLS:
            if col not in df.columns:
                df[col] = 0  # Fill missing columns with 0
        
        X = df[FEATURE_COLS].copy()
        
        print(f"  ✓ Features: {X.shape[1]}")
        print(f"  ✓ Samples: {X.shape[0]:,}")
        print(f"  ✓ Default rate: {y.mean():.2%}")
        
        # Handle missing values
        print("\n[2/6] Preprocessing data...")
        for col in FEATURE_COLS:
            if X[col].isnull().any():
                if col in CATEGORICAL_COLS:
                    X[col].fillna('Unknown', inplace=True)
                else:
                    X[col].fillna(0, inplace=True)
        
        # Encode categorical variables (only the 3 that were encoded in training)
        print(f"  ✓ Encoding {len(CATEGORICAL_COLS)} categorical features...")
        for col in CATEGORICAL_COLS:
            if col in X.columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.encoders[col] = le
        
        # Scale features
        print("  ✓ Scaling features...")
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)
        
        print(f"  ✓ Preprocessed shape: {X_scaled.shape}")
        
        return X_scaled, y
    
    def download_global_model(self):
        """Download global model from FL server"""
        print(f"\n[3/6] Downloading global model from server...")
        
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
                # Use local model if download fails
                if os.path.exists(BASE_MODEL_PATH):
                    print(f"  ✓ Using local model: {BASE_MODEL_PATH}")
                    return BASE_MODEL_PATH
                return None
        
        except Exception as e:
            print(f"  ⚠️  Download failed: {e}")
            # Use local model if download fails
            if os.path.exists(BASE_MODEL_PATH):
                print(f"  ✓ Using local model: {BASE_MODEL_PATH}")
                return BASE_MODEL_PATH
            return None
    
    def load_model(self, model_path):
        """Load base model"""
        print(f"\n[4/6] Loading base model...")
        
        try:
            # Load model (will use GPU if available)
            self.model = tf.keras.models.load_model(model_path, compile=False)
            self.base_weights = self.model.get_weights()
            print(f"  ✓ Model loaded: {len(self.base_weights)} layers")
            
            # Compile model
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
                loss='binary_crossentropy',
                metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
            )
            print(f"  ✓ Model compiled with Adam optimizer (lr={LEARNING_RATE})")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to load model: {e}")
            return False
    
    def train(self, X_train, y_train):
        """Train model on local data"""
        print(f"\n[5/6] Training on local data...")
        print(f"  • Epochs: {EPOCHS}")
        print(f"  • Batch size: {BATCH_SIZE}")
        print(f"  • Validation split: {VALIDATION_SPLIT}")
        
        # Check GPU availability
        gpus = tf.config.list_physical_devices('GPU')
        print(f"  • GPUs available: {len(gpus)}")
        if gpus:
            print(f"    └─ {gpus[0].name}")
        
        try:
            # Train (will use GPU if available)
            history = self.model.fit(
                X_train, y_train,
                epochs=EPOCHS,
                batch_size=BATCH_SIZE,
                validation_split=VALIDATION_SPLIT,
                verbose=1
            )
            
            # Get final metrics
            final_loss = history.history['loss'][-1]
            final_acc = history.history['accuracy'][-1]
            final_auc = history.history['auc'][-1]
            
            val_loss = history.history['val_loss'][-1]
            val_acc = history.history['val_accuracy'][-1]
            val_auc = history.history['val_auc'][-1]
            
            print(f"\n  ✓ Training completed!")
            print(f"    Train - Loss: {final_loss:.4f}, Acc: {final_acc:.4f}, AUC: {final_auc:.4f}")
            print(f"    Val   - Loss: {val_loss:.4f}, Acc: {val_acc:.4f}, AUC: {val_auc:.4f}")
            
            return history
            
        except Exception as e:
            print(f"  ❌ Training failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
    """Main FL training workflow"""
    print("\n" + "=" * 80)
    print("FEDERATED LEARNING CLIENT - LOCAL TRAINING")
    print("=" * 80)
    
    # Initialize client
    client = BankFLClient(
        bank_id=BANK_ID,
        bank_name=BANK_NAME,
        database_path=DATABASE_PATH,
        server_url=FL_SERVER_URL
    )
    
    try:
        # Step 1: Load data from SQLite
        X_train, y_train = client.load_data()
        
        # Step 2: Download or use local global model
        model_path = client.download_global_model()
        if model_path is None:
            print("\n❌ Failed to get base model")
            return
        
        # Step 3: Load model
        if not client.load_model(model_path):
            print("\n❌ Failed to load model")
            return
        
        # Step 4: Train on local data
        history = client.train(X_train, y_train)
        if history is None:
            print("\n❌ Training failed")
            return
        
        # Step 5: Save weights
        weights_path = client.save_weights()
        
        # Step 6: Upload weights to server
        success = client.upload_weights_to_server(weights_path, num_samples=len(X_train))
        
        if success:
            print("\n" + "=" * 80)
            print("✅ FL TRAINING COMPLETED SUCCESSFULLY")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("⚠️  Training completed but upload failed")
            print("=" * 80)
    
    except Exception as e:
        print(f"\n❌ FL Training Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_fl_training()
