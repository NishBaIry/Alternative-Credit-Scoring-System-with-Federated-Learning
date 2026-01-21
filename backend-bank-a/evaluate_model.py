"""
Model Accuracy Evaluation Script
Evaluates a trained model's performance on validation dataset
Generates comparison graphs and detailed improvement analysis
"""

import os
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report, roc_curve
)
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
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

def compare_models_with_visualization(model1_path, model2_path, X, y, model1_name="Old Model", model2_name="New Model"):
    """Compare two models side by side with detailed visualizations"""
    print(f"\n{'='*80}")
    print("MODEL COMPARISON WITH VISUALIZATION")
    print(f"{'='*80}")
    
    # Load models
    print(f"\nLoading {model1_name}...")
    model1 = tf.keras.models.load_model(model1_path, compile=False)
    print(f"✓ {model1_name} loaded")
    
    print(f"\nLoading {model2_name}...")
    model2 = tf.keras.models.load_model(model2_path, compile=False)
    print(f"✓ {model2_name} loaded")
    
    # Make predictions
    print("\nMaking predictions...")
    y_pred_proba1 = model1.predict(X, verbose=0)
    y_pred1 = (y_pred_proba1 > 0.5).astype(int).flatten()
    
    y_pred_proba2 = model2.predict(X, verbose=0)
    y_pred2 = (y_pred_proba2 > 0.5).astype(int).flatten()
    
    # Calculate metrics for both models
    metrics1 = {
        'accuracy': accuracy_score(y, y_pred1),
        'precision': precision_score(y, y_pred1, zero_division=0),
        'recall': recall_score(y, y_pred1, zero_division=0),
        'f1': f1_score(y, y_pred1, zero_division=0),
        'auc': roc_auc_score(y, y_pred_proba1)
    }
    
    metrics2 = {
        'accuracy': accuracy_score(y, y_pred2),
        'precision': precision_score(y, y_pred2, zero_division=0),
        'recall': recall_score(y, y_pred2, zero_division=0),
        'f1': f1_score(y, y_pred2, zero_division=0),
        'auc': roc_auc_score(y, y_pred_proba2)
    }
    
    cm1 = confusion_matrix(y, y_pred1)
    cm2 = confusion_matrix(y, y_pred2)
    
    # Print comparison
    print(f"\n{'='*80}")
    print("COMPARISON SUMMARY")
    print(f"{'='*80}")
    
    print(f"\n{model1_name}: {model1_path}")
    print(f"{model2_name}: {model2_path}")
    print(f"\n{'Metric':<12} {model1_name[:10]:>10} {model2_name[:10]:>10} {'Difference':>12} {'Improvement':>12}")
    print("-" * 60)
    
    for metric in ['accuracy', 'precision', 'recall', 'f1', 'auc']:
        v1 = metrics1[metric]
        v2 = metrics2[metric]
        diff = v2 - v1
        improvement = (diff / v1 * 100) if v1 > 0 else 0
        symbol = "↑" if diff > 0 else ("↓" if diff < 0 else "→")
        print(f"{metric.capitalize():<12} {v1:>10.4f} {v2:>10.4f} {diff:>+12.4f} {symbol} {improvement:>+10.2f}%")
    
    # Generate visualizations
    print(f"\n{'='*80}")
    print("GENERATING VISUALIZATIONS")
    print(f"{'='*80}")
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (16, 12)
    
    # Create comprehensive comparison plot
    fig = plt.figure(figsize=(18, 12))
    
    # 1. Metrics Comparison Bar Chart
    ax1 = plt.subplot(2, 3, 1)
    metrics_names = list(metrics1.keys())
    x = np.arange(len(metrics_names))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, [metrics1[m] for m in metrics_names], width, 
                    label=model1_name, color='#3498db', alpha=0.8)
    bars2 = ax1.bar(x + width/2, [metrics2[m] for m in metrics_names], width, 
                    label=model2_name, color='#2ecc71', alpha=0.8)
    
    ax1.set_xlabel('Metrics', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax1.set_title('Performance Metrics Comparison', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([m.capitalize() for m in metrics_names], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 1.1])
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=8)
    
    # 2. Improvement Percentage Chart
    ax2 = plt.subplot(2, 3, 2)
    improvements = [(metrics2[m] - metrics1[m]) / metrics1[m] * 100 if metrics1[m] > 0 else 0 
                    for m in metrics_names]
    colors = ['#2ecc71' if x > 0 else '#e74c3c' for x in improvements]
    bars = ax2.barh(metrics_names, improvements, color=colors, alpha=0.8)
    ax2.set_xlabel('Improvement (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Relative Improvement', fontsize=14, fontweight='bold')
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, improvements)):
        ax2.text(val, i, f' {val:+.2f}%', va='center', fontsize=10, fontweight='bold')
    
    # 3. Confusion Matrix - Old Model
    ax3 = plt.subplot(2, 3, 3)
    sns.heatmap(cm1, annot=True, fmt='d', cmap='Blues', ax=ax3, 
                xticklabels=['No Default', 'Default'],
                yticklabels=['No Default', 'Default'])
    ax3.set_title(f'{model1_name} - Confusion Matrix', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Actual', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Predicted', fontsize=12, fontweight='bold')
    
    # 4. Confusion Matrix - New Model
    ax4 = plt.subplot(2, 3, 4)
    sns.heatmap(cm2, annot=True, fmt='d', cmap='Greens', ax=ax4,
                xticklabels=['No Default', 'Default'],
                yticklabels=['No Default', 'Default'])
    ax4.set_title(f'{model2_name} - Confusion Matrix', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Actual', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Predicted', fontsize=12, fontweight='bold')
    
    # 5. ROC Curve Comparison
    ax5 = plt.subplot(2, 3, 5)
    fpr1, tpr1, _ = roc_curve(y, y_pred_proba1)
    fpr2, tpr2, _ = roc_curve(y, y_pred_proba2)
    
    ax5.plot(fpr1, tpr1, label=f'{model1_name} (AUC={metrics1["auc"]:.4f})', 
            color='#3498db', linewidth=2)
    ax5.plot(fpr2, tpr2, label=f'{model2_name} (AUC={metrics2["auc"]:.4f})', 
            color='#2ecc71', linewidth=2)
    ax5.plot([0, 1], [0, 1], 'k--', label='Random', alpha=0.3)
    ax5.set_xlabel('False Positive Rate', fontsize=12, fontweight='bold')
    ax5.set_ylabel('True Positive Rate', fontsize=12, fontweight='bold')
    ax5.set_title('ROC Curve Comparison', fontsize=14, fontweight='bold')
    ax5.legend(loc='lower right')
    ax5.grid(True, alpha=0.3)
    
    # 6. Prediction Distribution
    ax6 = plt.subplot(2, 3, 6)
    ax6.hist(y_pred_proba1[y==0], bins=50, alpha=0.5, label=f'{model1_name} (No Default)', 
            color='#3498db', density=True)
    ax6.hist(y_pred_proba1[y==1], bins=50, alpha=0.5, label=f'{model1_name} (Default)', 
            color='#e74c3c', density=True)
    ax6.hist(y_pred_proba2[y==0], bins=50, alpha=0.5, label=f'{model2_name} (No Default)', 
            color='#1abc9c', density=True, linestyle='--')
    ax6.hist(y_pred_proba2[y==1], bins=50, alpha=0.5, label=f'{model2_name} (Default)', 
            color='#e67e22', density=True, linestyle='--')
    ax6.set_xlabel('Prediction Probability', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Density', fontsize=12, fontweight='bold')
    ax6.set_title('Prediction Distribution', fontsize=14, fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f'model_comparison_{timestamp}.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualization saved: {output_path}")
    
    # Display
    plt.show()
    
    # Print detailed improvement analysis
    print(f"\n{'='*80}")
    print("DETAILED IMPROVEMENT ANALYSIS")
    print(f"{'='*80}")
    
    print(f"\n📊 Overall Performance:")
    acc_improvement = (metrics2['accuracy'] - metrics1['accuracy']) / metrics1['accuracy'] * 100
    print(f"  • Accuracy improved by {acc_improvement:+.2f}%")
    print(f"  • From {metrics1['accuracy']*100:.2f}% → {metrics2['accuracy']*100:.2f}%")
    
    print(f"\n🎯 Classification Quality:")
    prec_improvement = (metrics2['precision'] - metrics1['precision']) / metrics1['precision'] * 100
    rec_improvement = (metrics2['recall'] - metrics1['recall']) / metrics1['recall'] * 100
    print(f"  • Precision improved by {prec_improvement:+.2f}%")
    print(f"  • Recall improved by {rec_improvement:+.2f}%")
    print(f"  • F1-Score improved by {((metrics2['f1'] - metrics1['f1']) / metrics1['f1'] * 100):+.2f}%")
    
    print(f"\n📈 Confusion Matrix Changes:")
    tn1, fp1, fn1, tp1 = cm1.ravel()
    tn2, fp2, fn2, tp2 = cm2.ravel()
    print(f"  • True Positives: {tp1:,} → {tp2:,} ({tp2-tp1:+,})")
    print(f"  • True Negatives: {tn1:,} → {tn2:,} ({tn2-tn1:+,})")
    print(f"  • False Positives: {fp1:,} → {fp2:,} ({fp2-fp1:+,})")
    print(f"  • False Negatives: {fn1:,} → {fn2:,} ({fn2-fn1:+,})")
    
    print(f"\n💡 Key Insights:")
    if metrics2['accuracy'] > metrics1['accuracy']:
        print(f"  ✅ The new model shows improvement across metrics")
    else:
        print(f"  ⚠️  The new model shows degradation - consider reverting")
    
    if abs(acc_improvement) < 1:
        print(f"  ℹ️  Improvement is marginal (<1%) - model is converging")
    elif acc_improvement > 5:
        print(f"  🚀 Significant improvement (>5%) - excellent progress!")
    
    return metrics1, metrics2

def compare_models(model1_path, model2_path, X, y):
    """Wrapper for backward compatibility"""
    return compare_models_with_visualization(model1_path, model2_path, X, y)

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
