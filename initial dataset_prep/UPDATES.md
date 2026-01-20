Searched codebase for "alternative credit score calculation formula 300-900 neural network default probability", 13 results

# Complete Dataset & Alternative Credit Scoring System - Summary

## 📊 **Dataset Evolution**

### **1. Original Data Source**
- **CIBIL Dataset**: 51,336 customers from Indian credit bureau
- **Source**: `data/processed.csv` → credit_scoring_dataset.csv

### **2. Income Adjustment (1.5x Boost)**
```python
monthly_income = CIBIL_monthly_income × 1.5
annual_income = monthly_income × 12
```
- **Reason**: Purchasing Power Parity (PPP) adjustment for realistic Indian income levels
- **Result**: Median monthly income ~₹34,500 (from ~₹23,000)

### **3. UPI Alternative Data Generation**
**Good Borrowers (Low Default Risk):**
- UPI spending: **40-60%** of monthly income (conservative)
- Transaction count: 40-80 per month
- Failed transaction rate: 0.5-2%
- Essentials spending share: 70-85%

**Bad Borrowers (High Default Risk):**
- UPI spending: **85-110%** of monthly income (overspending)
- Transaction count: 80-150 per month
- Failed transaction rate: 3-8%
- Essentials spending share: 40-60%

### **4. Dataset Structure**
**Total**: 51,336 customers × 52 features

**Feature Categories:**
- **Demographics**: Age, gender, marital status, education, dependents, home ownership, region
- **Financial**: Monthly/annual income, job type, tenure, DTI, assets, liabilities
- **Loan Details**: Amount, duration, purpose, interest rate, monthly payment
- **Traditional Credit**: Enquiries, delinquencies (30/60 DPD), utilization rates, loan flags
- **UPI Alt-Data**: Transaction counts, spending patterns, merchant diversity, volatility, failure rates
- **Target Labels**: `default_flag` (primary), `credit_score` (benchmark)

---

## 🤖 **Neural Network Training**

### **Model Architecture**
```python
Input Layer (46 features)
    ↓
Dense(256) + BatchNorm + Dropout(0.3)
    ↓
Dense(128) + BatchNorm + Dropout(0.25)
    ↓
Dense(64) + BatchNorm + Dropout(0.2)
    ↓
Dense(32) + BatchNorm + Dropout(0.15)
    ↓
Dense(1, activation='sigmoid')  → P(default)
```

### **Training Configuration**
- **Primary Label**: `default_flag` (0=good borrower, 1=defaulter)
- **Loss Function**: Binary Cross-Entropy
- **Optimizer**: Adam
- **Validation Split**: 80% train, 20% validation
- **Data**: 51,336 samples
- **Features Used**: 46 columns (excluding customer_id, data_source, target labels)

### **Model Performance**
```
Accuracy:   77.92%
Precision:  96.51% (high confidence in default predictions)
Recall:     77.93%
F1-Score:   86.23%
ROC-AUC:    86.75%

Confusion Matrix:
  True Negatives:     904 ✓ (correctly predicted good)
  False Positives:    257 ✗ (wrongly flagged as default)
  False Negatives:  2,010 ✗ (missed defaults)
  True Positives:   7,097 ✓ (correctly caught defaults)
```

---

## 🎯 **Alternative Credit Score Calculation**

### **Formula**
```python
P(default) = Neural_Network_Output  # from sigmoid (0 to 1)

alt_score = 300 + 600 × (1 - P(default))

# Clipped to [300, 900] range
```

### **Score Interpretation**
| P(default) | Alt Score | Interpretation |
|------------|-----------|----------------|
| 0.00 (0%) | 900 | Excellent - No default risk |
| 0.17 (17%) | 800 | Very Good |
| 0.33 (33%) | 700 | Good |
| 0.50 (50%) | 600 | Fair |
| 0.67 (67%) | 500 | Poor |
| 0.83 (83%) | 400 | Very Poor |
| 1.00 (100%) | 300 | Critical - Certain default |

### **Score Distribution (Validation Set)**
```
Mean:   504.3
Median: 483.0
Range:  [300, 900]
```

### **Default Rate by Score Band**
```
Score Band   Default Rate   Count
800-900      34.3%          571
700-799      68.7%        1,081
600-699      84.8%        1,274
500-599      91.9%        2,005
400-499      96.6%        1,539
300-399      99.0%        3,798
```

**✓ Monotonic Relationship**: Higher scores → Lower default rates (validates model logic)

---

## 📈 **Benchmark Comparison (vs CIBIL Score)**

```
Pearson Correlation:  0.5666
Spearman Correlation: 0.5712
```

**Interpretation**: Moderate positive correlation shows the alternative score captures **similar but complementary** risk patterns to traditional CIBIL scores.

---

## 🏦 **Federated Learning Datasets**

### **Bank A Dataset**
- **Total**: 35,000 customers
- **Real Data**: 15,400 (44%) from original CIBIL dataset
- **Synthetic Data**: 19,600 (56%) generated with proper distributions
- **Default Rate**: 88.73%
- **Avg Income**: ₹39,278
- **Database**: bank_a.db (14 MB)

### **Bank B Dataset**
- **Total**: 35,000 customers
- **Real Data**: 12,834 (37%) from original CIBIL dataset (non-overlapping with Bank A)
- **Synthetic Data**: 22,166 (63%) generated with proper distributions
- **Default Rate**: 89.43%
- **Avg Income**: ₹40,725
- **Database**: bank_b.db (13 MB)

### **Data Quality Checks**
✅ No customer overlap between banks  
✅ Default rates within ±1% of original  
✅ Income distributions maintained  
✅ UPI spending patterns correlated with default risk  
✅ 5 decimal precision for all numeric values  

---

## 🗄️ **SQLite Database Schema**

### **Table**: `customers`
```sql
customer_id TEXT PRIMARY KEY      -- '00000001' to '00035000'
password TEXT NOT NULL            -- SHA256 hash of customer_id
age INTEGER
gender TEXT
monthly_income REAL
dti REAL
... [48 feature columns total]
default_flag INTEGER              -- Target label (0/1)
credit_score REAL                 -- Alternative score (300-900)
```

### **Indexes**
- `PRIMARY KEY` on `customer_id`
- `INDEX` on `default_flag` (analytics)
- `INDEX` on `monthly_income` (filtering)
- `INDEX` on `dti` (risk queries)
- `INDEX` on `credit_score` (score lookups)

### **Authentication**
```python
# User logs in with account number (e.g., '00000001') as username & password
password_hash = hashlib.sha256('00000001'.encode()).hexdigest()

# Backend verifies
SELECT * FROM customers 
WHERE customer_id = '00000001' 
AND password = '{password_hash}'
```

---

## 📁 **File Structure**

```
/home/nishanth/Desktop/main-el/
├── data/
│   ├── credit_scoring_dataset.csv       (51,336 rows - original unified)
│   ├── bank_a_fl_dataset.csv            (35,000 rows - Bank A clean CSV)
│   ├── bank_b_fl_dataset.csv            (35,000 rows - Bank B clean CSV)
│   ├── bank_a.db                        (14 MB - SQLite database)
│   └── bank_b.db                        (13 MB - SQLite database)
├── outputs/
│   ├── model.h5                         (Full Keras model)
│   ├── model.weights.h5                 (Model weights only)
│   ├── scaler.pkl                       (StandardScaler for features)
│   ├── encoders.pkl                     (LabelEncoders for categoricals)
│   └── metrics_nn.txt                   (Performance metrics)
├── generate_unified_dataset_cibil_only.py
├── train_neural_network_v2.py
├── generate_fl_datasets.py
├── cleanup_fl_datasets.py
└── setup_bank_databases.py
```

---

## 🔬 **Key Innovations**

1. **UPI Behavior as Credit Signal**: Spending patterns (relative to income) strongly predict default risk
2. **Income Adjustment**: PPP-adjusted to reflect real Indian purchasing power
3. **Alternative Score**: Derived from neural network P(default) prediction, not traditional credit history
4. **Federated Learning Ready**: Separate bank databases with no customer overlap
5. **Synthetic Data Quality**: Generated using statistical distributions + risk correlations to maintain realism

---

## 🎓 **How Alternative Score Works**

**Step 1**: Train neural network on `default_flag` (0 or 1)  
**Step 2**: Model outputs `P(default)` probability (0.0 to 1.0)  
**Step 3**: Transform to credit score: `300 + 600 × (1 - P(default))`

**Example**:
- P(default) = 0.10 → alt_score = 300 + 600×0.90 = **840** (Excellent)
- P(default) = 0.50 → alt_score = 300 + 600×0.50 = **600** (Fair)
- P(default) = 0.90 → alt_score = 300 + 600×0.10 = **360** (Very Poor)

This system enables **credit scoring without traditional credit history**, using behavioral data (UPI patterns, income stability, financial capacity) instead! 🚀