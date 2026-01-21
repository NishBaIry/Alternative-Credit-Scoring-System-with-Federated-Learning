#!/usr/bin/env python3
"""
Test script to verify validation dataset works with the model
"""

import os
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Set XLA flags for GPU/CUDA before loading TensorFlow (fix libdevice issue)
if 'XLA_FLAGS' not in os.environ and 'CONDA_PREFIX' in os.environ:
    os.environ['XLA_FLAGS'] = f'--xla_gpu_cuda_data_dir={os.environ["CONDA_PREFIX"]}'

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

# Feature specification (46 features - same as training)
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

def test_validation():
    print("=" * 70)
    print("VALIDATION DATASET TEST")
    print("=" * 70)
    print()
    
    # Paths
    validation_path = "validation_data/bank_a_validation_dataset.csv"
    model_path = "models/global_model.h5"
    
    # Check files exist
    if not os.path.exists(validation_path):
        print(f"❌ Validation dataset not found: {validation_path}")
        return False
        
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return False
    
    print(f"✅ Found validation dataset: {validation_path}")
    print(f"✅ Found model: {model_path}")
    print()
    
    # Load dataset
    print("📂 Loading validation dataset...")
    df = pd.read_csv(validation_path)
    print(f"  • Total rows: {len(df)}")
    print(f"  • Total columns: {len(df.columns)}")
    print(f"  • Columns: {list(df.columns)[:10]}... (showing first 10)")
    print()
    
    # Check for target column
    if 'default_flag' not in df.columns:
        print("❌ 'default_flag' column not found in dataset")
        return False
    
    # Remove non-feature columns
    columns_to_drop = ['customer_id', 'password']
    existing_drops = [col for col in columns_to_drop if col in df.columns]
    if existing_drops:
        print(f"🗑️  Dropping columns: {existing_drops}")
        df = df.drop(columns=existing_drops)
    
    # Split features and target
    X = df.drop(columns=['default_flag'])
    y = df['default_flag'].values
    
    print(f"✅ Features shape before selection: {X.shape}")
    print(f"✅ Target distribution: {np.bincount(y)}")
    print()
    
    # Check if all required features exist
    missing_features = [col for col in FEATURE_COLS if col not in X.columns]
    if missing_features:
        print(f"❌ Missing features in dataset: {missing_features}")
        return False
    
    # Select only the required features
    print(f"🔧 Selecting {len(FEATURE_COLS)} required features...")
    X = X[FEATURE_COLS]
    print(f"✅ Features shape after selection: {X.shape}")
    print()
    
    # Identify categorical and numerical columns
    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
    numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    
    print(f"📊 Feature types:")
    print(f"  • Numerical: {len(numerical_cols)}")
    print(f"  • Categorical: {len(categorical_cols)} {categorical_cols}")
    print()
    
    # Handle missing values
    print("🔧 Handling missing values...")
    for col in numerical_cols:
        if X[col].isnull().any():
            median_val = X[col].median()
            X[col].fillna(median_val, inplace=True)
    
    for col in categorical_cols:
        if X[col].isnull().any():
            mode_val = X[col].mode()
            if len(mode_val) > 0:
                X[col].fillna(mode_val[0], inplace=True)
            else:
                X[col].fillna('Unknown', inplace=True)
    
    # Encode categorical variables
    print(f"🔧 Encoding {len(categorical_cols)} categorical features...")
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    
    # Scale features
    print("🔧 Scaling features...")
    X = X.replace([np.inf, -np.inf], [1e10, -1e10])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)
    
    print(f"✅ Final feature shape: {X_scaled.shape}")
    print()
    
    # Load model
    print("📦 Loading model...")
    model = tf.keras.models.load_model(model_path, compile=False)
    print(f"✅ Model loaded")
    print(f"  • Input shape: {model.input_shape}")
    print(f"  • Output shape: {model.output_shape}")
    print()
    
    # Check shape compatibility
    expected_features = model.input_shape[1]
    actual_features = X_scaled.shape[1]
    
    if expected_features != actual_features:
        print(f"❌ SHAPE MISMATCH:")
        print(f"  • Model expects: {expected_features} features")
        print(f"  • Dataset has: {actual_features} features")
        return False
    
    print(f"✅ Shape compatibility check passed: {actual_features} features")
    print()
    
    # Make predictions
    print("🔮 Making predictions...")
    y_pred_proba = model.predict(X_scaled, verbose=0)
    y_pred = (y_pred_proba > 0.5).astype(int).flatten()
    
    # Calculate metrics
    print("📊 Calculating metrics...")
    metrics = {
        'accuracy': float(accuracy_score(y, y_pred)),
        'precision': float(precision_score(y, y_pred)),
        'recall': float(recall_score(y, y_pred)),
        'f1': float(f1_score(y, y_pred)),
        'auc': float(roc_auc_score(y, y_pred_proba))
    }
    
    print()
    print("=" * 70)
    print("✅ TEST SUCCESSFUL")
    print("=" * 70)
    print()
    print("Model Metrics:")
    for metric, value in metrics.items():
        print(f"  • {metric.upper()}: {value:.4f}")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = test_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ TEST FAILED")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
