"""
Model Accuracy Evaluation Script
Evaluates a trained model's performance on validation dataset
"""

import os
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report
)
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.fl')

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

def load_and_preprocess_data(dataset_path):
    """Load and preprocess dataset"""
    print(f"\n{'='*80}")
    print("LOADING DATASET")
    print(f"{'='*80}")
    
    print(f"\nDataset: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"✓ Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    # Remove authentication columns
    remove_cols = ['customer_id', 'password']
    df = df.drop(columns=[col for col in remove_cols if col in df.columns])
    
    # Separate target
    if TARGET_COL not in df.columns:
        raise ValueError(f"{TARGET_COL} not found in dataset!")
    
    y = df[TARGET_COL].astype(int).values
    
    # Select features
    available_features = [col for col in FEATURE_COLS if col in df.columns]
    X = df[available_features].copy()
    
    print(f"✓ Features: {X.shape[1]}")
    print(f"✓ Default rate: {y.mean():.2%}")
    
    # Identify categorical and numerical columns
    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
    numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    
    print(f"✓ Numerical: {len(numerical_cols)}, Categorical: {len(categorical_cols)}")
    
    # Handle missing values
    print("\nPreprocessing...")
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
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)
    
    print("✓ Preprocessing complete")
    
    return X_scaled, y

def evaluate_model(model_path, X, y):
    """Evaluate model and print metrics"""
    print(f"\n{'='*80}")
    print("MODEL EVALUATION")
    print(f"{'='*80}")
    
    print(f"\nLoading model: {model_path}")
    model = tf.keras.models.load_model(model_path, compile=False)
    print(f"✓ Model loaded: {len(model.get_weights())} weight layers")
    
    # Make predictions
    print("\nMaking predictions...")
    y_pred_proba = model.predict(X, verbose=0)
    y_pred = (y_pred_proba > 0.5).astype(int).flatten()
    
    # Calculate metrics
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, zero_division=0)
    recall = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    auc = roc_auc_score(y, y_pred_proba)
    
    print(f"\n📊 Performance Metrics:")
    print(f"  • Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  • Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"  • Recall:    {recall:.4f} ({recall*100:.2f}%)")
    print(f"  • F1 Score:  {f1:.4f}")
    print(f"  • ROC-AUC:   {auc:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y, y_pred)
    print(f"\n📈 Confusion Matrix:")
    print(f"                Predicted")
    print(f"              No Default  Default")
    print(f"  Actual  No  {cm[0][0]:8d}  {cm[0][1]:7d}")
    print(f"         Yes  {cm[1][0]:8d}  {cm[1][1]:7d}")
    
    # Additional stats
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    
    print(f"\n📉 Additional Metrics:")
    print(f"  • True Positives:  {tp:,}")
    print(f"  • True Negatives:  {tn:,}")
    print(f"  • False Positives: {fp:,}")
    print(f"  • False Negatives: {fn:,}")
    print(f"  • Specificity:     {specificity:.4f}")
    print(f"  • NPV:             {npv:.4f}")
    
    # Classification report
    print(f"\n📋 Classification Report:")
    print(classification_report(y, y_pred, target_names=['No Default', 'Default'], digits=4))
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc': auc,
        'confusion_matrix': cm.tolist()
    }

def evaluate_weights(base_model_path, weights_path, X, y):
    """Evaluate model with custom weights loaded"""
    print(f"\n{'='*80}")
    print("MODEL EVALUATION WITH CUSTOM WEIGHTS")
    print(f"{'='*80}")
    
    print(f"\nLoading base model: {base_model_path}")
    model = tf.keras.models.load_model(base_model_path, compile=False)
    print(f"✓ Base model loaded")
    
    print(f"\nLoading weights: {weights_path}")
    if weights_path.endswith('.npz'):
        data = np.load(weights_path, allow_pickle=True)
        weights = []
        for i in range(len(data.files)):
            key = f'arr_{i}'
            if key in data:
                weights.append(data[key])
        if not weights:
            weights = [data[key] for key in sorted(data.files)]
        
        model.set_weights(weights)
        print(f"✓ Custom weights loaded: {len(weights)} layers")
    else:
        print("❌ Only .npz weights supported")
        return None
    
    # Make predictions
    print("\nMaking predictions...")
    y_pred_proba = model.predict(X, verbose=0)
    y_pred = (y_pred_proba > 0.5).astype(int).flatten()
    
    # Calculate metrics
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, zero_division=0)
    recall = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    auc = roc_auc_score(y, y_pred_proba)
    
    print(f"\n📊 Performance Metrics:")
    print(f"  • Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  • Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"  • Recall:    {recall:.4f} ({recall*100:.2f}%)")
    print(f"  • F1 Score:  {f1:.4f}")
    print(f"  • ROC-AUC:   {auc:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y, y_pred)
    print(f"\n📈 Confusion Matrix:")
    print(f"                Predicted")
    print(f"              No Default  Default")
    print(f"  Actual  No  {cm[0][0]:8d}  {cm[0][1]:7d}")
    print(f"         Yes  {cm[1][0]:8d}  {cm[1][1]:7d}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc': auc,
        'confusion_matrix': cm.tolist()
    }

def compare_models(model1_path, model2_path, X, y):
    """Compare two models side by side"""
    print(f"\n{'='*80}")
    print("MODEL COMPARISON")
    print(f"{'='*80}")
    
    # Evaluate both models
    print("\n[1/2] Evaluating Model 1...")
    metrics1 = evaluate_model(model1_path, X, y)
    
    print(f"\n{'='*80}")
    print("\n[2/2] Evaluating Model 2...")
    metrics2 = evaluate_model(model2_path, X, y)
    
    # Compare
    print(f"\n{'='*80}")
    print("COMPARISON SUMMARY")
    print(f"{'='*80}")
    
    print(f"\nModel 1: {model1_path}")
    print(f"Model 2: {model2_path}")
    print(f"\n{'Metric':<12} {'Model 1':>10} {'Model 2':>10} {'Difference':>12} {'Winner':>10}")
    print("-" * 58)
    
    metrics = ['accuracy', 'precision', 'recall', 'f1', 'auc']
    for metric in metrics:
        v1 = metrics1[metric]
        v2 = metrics2[metric]
        diff = v2 - v1
        winner = "Model 2 ✓" if v2 > v1 else ("Model 1 ✓" if v1 > v2 else "Tie")
        print(f"{metric.capitalize():<12} {v1:>10.4f} {v2:>10.4f} {diff:>+12.4f} {winner:>10}")
    
    print()

def main():
    parser = argparse.ArgumentParser(description='Evaluate model accuracy on validation dataset')
    parser.add_argument('--model', type=str, required=True, help='Path to model file (.h5)')
    parser.add_argument('--dataset', type=str, required=True, help='Path to validation dataset (.csv)')
    parser.add_argument('--compare', type=str, default=None, help='Optional: Path to second model for comparison (.h5)')
    parser.add_argument('--weights', type=str, default=None, help='Optional: Load custom weights (.npz) into base model')
    
    args = parser.parse_args()
    
    # Check if files exist
    if not os.path.exists(args.model):
        print(f"❌ Error: Model not found: {args.model}")
        sys.exit(1)
    
    if not os.path.exists(args.dataset):
        print(f"❌ Error: Dataset not found: {args.dataset}")
        sys.exit(1)
    
    if args.compare and not os.path.exists(args.compare):
        print(f"❌ Error: Comparison model not found: {args.compare}")
        sys.exit(1)
    
    if args.weights and not os.path.exists(args.weights):
        print(f"❌ Error: Weights file not found: {args.weights}")
        sys.exit(1)
    
    # Load and preprocess data
    X, y = load_and_preprocess_data(args.dataset)
    
    # Evaluate with custom weights, compare, or single model
    if args.weights:
        evaluate_weights(args.model, args.weights, X, y)
    elif args.compare:
        compare_models(args.model, args.compare, X, y)
    else:
        evaluate_model(args.model, X, y)
    
    print(f"\n{'='*80}")
    print("✅ EVALUATION COMPLETE")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
