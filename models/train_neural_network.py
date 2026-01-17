"""
Neural Network Training for Credit Scoring with .h5 Weights
Suitable for Federated Learning frameworks
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix
)
import os
import pickle

# ============================================================================
# CONFIGURATION
# ============================================================================

PROCESSED_DATA_PATH = "data/processed.csv"
MODEL_PATH = "outputs/model.h5"
WEIGHTS_PATH = "outputs/model.weights.h5"
SCALER_PATH = "outputs/scaler.pkl"
ENCODERS_PATH = "outputs/encoders.pkl"
METRICS_PATH = "outputs/metrics_nn.txt"

# Explicit feature list - all borrower and behavior columns
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

# Columns to ignore (not model inputs)
IGNORE_COLS = [
    "customer_id",
    "data_source",
    "credit_score_original",
    "good_borrower"
]

# Ensure output directory exists
os.makedirs("outputs", exist_ok=True)

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

print("=" * 80)
print("CREDIT SCORING NEURAL NETWORK - TRAINING & EVALUATION")
print("=" * 80)

print("\n[1/6] Loading processed data...")
df = pd.read_csv(PROCESSED_DATA_PATH)
print(f"  ✓ Data shape: {df.shape}")
print(f"  ✓ Samples: {df.shape[0]:,}")

# ============================================================================
# STEP 2: PREPARE FEATURES AND TARGET
# ============================================================================

print("\n[2/6] Preparing features and target...")

# Separate target
y = df[TARGET_COL].astype(int).values

# Select only the specified features
available_features = [col for col in FEATURE_COLS if col in df.columns]
missing_features = [col for col in FEATURE_COLS if col not in df.columns]

if missing_features:
    print(f"  ⚠️  Missing features (will be skipped): {missing_features}")

X = df[available_features].copy()

# Identify categorical and numerical columns
categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()

print(f"  ✓ Total features: {X.shape[1]} (specified: {len(FEATURE_COLS)})")
print(f"  ✓ Numerical features: {len(numerical_cols)}")
print(f"  ✓ Categorical features: {len(categorical_cols)}")
print(f"  ✓ Using explicit feature list from LightGBM specification")

# ============================================================================
# STEP 3: ENCODE CATEGORICAL FEATURES
# ============================================================================

print("\n[3/6] Encoding categorical features and handling missing values...")

# Handle missing values BEFORE encoding
print(f"  • Handling missing values...")

# Fill NaN in numerical columns with median
for col in numerical_cols:
    if X[col].isnull().any():
        median_val = X[col].median()
        X[col].fillna(median_val, inplace=True)

# Fill NaN in categorical columns with mode or 'Unknown'
for col in categorical_cols:
    if X[col].isnull().any():
        mode_val = X[col].mode()
        if len(mode_val) > 0:
            X[col].fillna(mode_val[0], inplace=True)
        else:
            X[col].fillna('Unknown', inplace=True)

# Replace inf values with large finite numbers
X.replace([np.inf, -np.inf], [1e10, -1e10], inplace=True)

print(f"  ✓ Missing values handled")

# Encode categorical features
encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))
    encoders[col] = le

print(f"  ✓ Encoded {len(categorical_cols)} categorical columns")

# Convert to numpy array
X = X.values.astype(np.float32)

# Final check for NaN/inf
if np.isnan(X).any() or np.isinf(X).any():
    print(f"  ⚠️  WARNING: Still have NaN or inf values after cleaning!")
    print(f"     NaN count: {np.isnan(X).sum()}")
    print(f"     Inf count: {np.isinf(X).sum()}")
else:
    print(f"  ✓ All values are finite and valid")

# ============================================================================
# STEP 4: TRAIN/VALIDATION SPLIT
# ============================================================================

print("\n[4/6] Splitting and scaling data...")

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

# Handle any NaN created by scaling (e.g., columns with zero variance)
X_train_scaled = np.nan_to_num(X_train_scaled, nan=0.0, posinf=0.0, neginf=0.0)
X_val_scaled = np.nan_to_num(X_val_scaled, nan=0.0, posinf=0.0, neginf=0.0)

print(f"  ✓ Train set: {X_train.shape[0]:,} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
print(f"  ✓ Validation set: {X_val.shape[0]:,} samples ({X_val.shape[0]/len(X)*100:.1f}%)")
print(f"  ✓ All scaled values are finite: {not (np.isnan(X_train_scaled).any() or np.isnan(X_val_scaled).any())}")

# Class distribution
num_negative = (y_train == 0).sum()
num_positive = (y_train == 1).sum()
class_weight = {0: 1.0, 1: num_negative / num_positive}

print(f"\n  Class distribution in training set:")
print(f"    - Class 0 (Good): {num_negative:,} ({num_negative/len(y_train)*100:.1f}%)")
print(f"    - Class 1 (Default): {num_positive:,} ({num_positive/len(y_train)*100:.1f}%)")
print(f"    - Class weight for class 1: {class_weight[1]:.2f}")

# ============================================================================
# STEP 5: BUILD NEURAL NETWORK MODEL
# ============================================================================

print("\n[5/6] Building neural network architecture...")

# Enhanced architecture for 88%+ accuracy - wider and less regularization
model = models.Sequential([
    layers.Input(shape=(X_train_scaled.shape[1],)),
    
    # First block - very wide to capture all patterns
    layers.Dense(512, activation='relu', kernel_regularizer=keras.regularizers.l2(0.0001), name='dense_1'),
    layers.BatchNormalization(),
    layers.Dropout(0.2),  # Reduced dropout
    
    # Second block
    layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.0001), name='dense_2'),
    layers.BatchNormalization(),
    layers.Dropout(0.2),
    
    # Third block
    layers.Dense(128, activation='relu', kernel_regularizer=keras.regularizers.l2(0.0001), name='dense_3'),
    layers.BatchNormalization(),
    layers.Dropout(0.15),
    
    # Fourth block
    layers.Dense(64, activation='relu', name='dense_4'),
    layers.BatchNormalization(),
    layers.Dropout(0.1),
    
    # Fifth block
    layers.Dense(32, activation='relu', name='dense_5'),
    layers.Dropout(0.1),
    
    # Output
    layers.Dense(1, activation='sigmoid', name='output')
])

# Compile with slightly higher learning rate for faster convergence
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),  # Back to higher LR
    loss='binary_crossentropy',
    metrics=[
        'accuracy',
        keras.metrics.Precision(name='precision'),
        keras.metrics.Recall(name='recall'),
        keras.metrics.AUC(name='auc')
    ]
)

print(f"  ✓ Model architecture:")
model.summary()

# ============================================================================
# STEP 6: TRAIN MODEL
# ============================================================================

print("\n[6/6] Training neural network...")

# Optimized callbacks for 88%+ accuracy
early_stopping = keras.callbacks.EarlyStopping(
    monitor='val_accuracy',  # Monitor accuracy instead of loss
    patience=30,  # More patience
    mode='max',  # Maximize accuracy
    restore_best_weights=True,
    verbose=1
)

reduce_lr = keras.callbacks.ReduceLROnPlateau(
    monitor='val_accuracy',
    factor=0.5,
    patience=10,
    mode='max',
    min_lr=0.000001,
    verbose=1
)

# Train model with optimized settings
history = model.fit(
    X_train_scaled, y_train,
    validation_data=(X_val_scaled, y_val),
    epochs=250,  # More epochs
    batch_size=256,  # Smaller batch for better gradients
    class_weight=class_weight,
    callbacks=[early_stopping, reduce_lr],
    verbose=1
)

print(f"\n  ✓ Training complete!")
print(f"  ✓ Total epochs trained: {len(history.history['loss'])}")

# ============================================================================
# SAVE MODEL AND WEIGHTS
# ============================================================================

print("\nSaving model and weights...")

# Save full model
model.save(MODEL_PATH)
print(f"  ✓ Full model saved to: {MODEL_PATH}")

# Save weights only (for FL)
model.save_weights(WEIGHTS_PATH)
print(f"  ✓ Model weights saved to: {WEIGHTS_PATH}")

# Save scaler
with open(SCALER_PATH, 'wb') as f:
    pickle.dump(scaler, f)
print(f"  ✓ Scaler saved to: {SCALER_PATH}")

# Save encoders
with open(ENCODERS_PATH, 'wb') as f:
    pickle.dump(encoders, f)
print(f"  ✓ Encoders saved to: {ENCODERS_PATH}")

# ============================================================================
# EVALUATE MODEL
# ============================================================================

print("\nEvaluating model performance...")

# Generate predictions
y_pred_proba = model.predict(X_val_scaled, verbose=0).flatten()
y_pred = (y_pred_proba >= 0.5).astype(int)

# Compute metrics
accuracy = accuracy_score(y_val, y_pred)
precision = precision_score(y_val, y_pred, zero_division=0)
recall = recall_score(y_val, y_pred, zero_division=0)
f1 = f1_score(y_val, y_pred, zero_division=0)
roc_auc = roc_auc_score(y_val, y_pred_proba)

# Confusion matrix
cm = confusion_matrix(y_val, y_pred)
tn, fp, fn, tp = cm.ravel()

# Get final training and validation losses
final_train_loss = history.history['loss'][-1]
final_val_loss = history.history['val_loss'][-1]

# ============================================================================
# DISPLAY RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("MODEL EVALUATION RESULTS")
print("=" * 80)

print("\n📊 PERFORMANCE METRICS:")
print(f"  • Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  • Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"  • Recall:    {recall:.4f} ({recall*100:.2f}%)")
print(f"  • F1-Score:  {f1:.4f}")
print(f"  • ROC-AUC:   {roc_auc:.4f}")

print("\n🎯 CONFUSION MATRIX:")
print(f"  True Negatives (TN):  {tn:>6,}  (Correctly predicted as Good)")
print(f"  False Positives (FP): {fp:>6,}  (Wrongly predicted as Default)")
print(f"  False Negatives (FN): {fn:>6,}  (Wrongly predicted as Good)")
print(f"  True Positives (TP):  {tp:>6,}  (Correctly predicted as Default)")

print("\n📈 LOSS METRICS:")
print(f"  • Training Loss:   {final_train_loss:.4f}")
print(f"  • Validation Loss: {final_val_loss:.4f}")

print("\n" + "=" * 80)

# ============================================================================
# SAVE METRICS
# ============================================================================

with open(METRICS_PATH, "w") as f:
    f.write("=" * 80 + "\n")
    f.write("NEURAL NETWORK MODEL EVALUATION RESULTS\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("PERFORMANCE METRICS:\n")
    f.write(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)\n")
    f.write(f"  Precision: {precision:.4f} ({precision*100:.2f}%)\n")
    f.write(f"  Recall:    {recall:.4f} ({recall*100:.2f}%)\n")
    f.write(f"  F1-Score:  {f1:.4f}\n")
    f.write(f"  ROC-AUC:   {roc_auc:.4f}\n\n")
    
    f.write("CONFUSION MATRIX:\n")
    f.write(f"  True Negatives (TN):  {tn:>6,}\n")
    f.write(f"  False Positives (FP): {fp:>6,}\n")
    f.write(f"  False Negatives (FN): {fn:>6,}\n")
    f.write(f"  True Positives (TP):  {tp:>6,}\n\n")
    
    f.write("LOSS METRICS:\n")
    f.write(f"  Training Loss:   {final_train_loss:.4f}\n")
    f.write(f"  Validation Loss: {final_val_loss:.4f}\n\n")
    
    f.write("=" * 80 + "\n")

print(f"✅ Detailed metrics saved to: {METRICS_PATH}")

# ============================================================================
# FEDERATED LEARNING INFO
# ============================================================================

print("\n" + "=" * 80)
print("FEDERATED LEARNING - MODEL FILES")
print("=" * 80)
print(f"\n📁 Full Model: {MODEL_PATH}")
print(f"   Format: Keras/TensorFlow SavedModel")
print(f"   Size: {os.path.getsize(MODEL_PATH) / 1024:.2f} KB")
print(f"   Use: Complete model for inference")

print(f"\n⚖️  Weights Only: {WEIGHTS_PATH}")
print(f"   Format: HDF5 (.h5)")
print(f"   Size: {os.path.getsize(WEIGHTS_PATH) / 1024:.2f} KB")
print(f"   Use: For Federated Learning - share/aggregate weights")

print(f"\n📊 Scaler: {SCALER_PATH}")
print(f"   Use: Standardize input features before prediction")

print(f"\n🔤 Encoders: {ENCODERS_PATH}")
print(f"   Use: Encode categorical features before prediction")

print("\n💡 Federated Learning Usage:")
print("   1. Each client loads: model.load_weights('outputs/model_weights.h5')")
print("   2. Client trains on local data")
print("   3. Client sends updated weights back to server")
print("   4. Server aggregates weights from all clients (FedAvg)")
print("   5. Server distributes aggregated weights to all clients")

print("\n🔧 To load weights in FL client:")
print("   ```python")
print("   model = build_model()  # Same architecture as above")
print("   model.load_weights('outputs/model_weights.h5')")
print("   ```")

print("=" * 80)
print("\n✅ Training complete! Model ready for Federated Learning!")
