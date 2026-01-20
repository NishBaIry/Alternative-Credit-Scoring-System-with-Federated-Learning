"""
Generate Unified Credit Scoring Dataset (CIBIL Only)

This script creates a unified dataset from the CIBIL dataset with:
- 1.5x income boost (multiply by 1.5)
- Realistic UPI spending patterns based on default likelihood
- Credit score column included
- 5 decimal precision for all numeric values
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

# ============================================================================
# CONFIGURATION
# ============================================================================

CIBIL_FILE = "data/credit_scoring_dataset.csv"
OUTPUT_FILE = "unified_credit_scoring_dataset.csv"
DECIMAL_PRECISION = 5

# ============================================================================
# LOAD AND PREPARE CIBIL DATA
# ============================================================================

print("Loading CIBIL dataset...")
df_cibil = pd.read_csv(CIBIL_FILE)
print(f"Loaded {len(df_cibil)} records from CIBIL dataset")

# Parse malformed decimal values (e.g., "35.441.791.880.765.800" → 0.3544)
def parse_malformed_decimal(val):
    """Convert malformed decimals like '35.441.791.880.765.800' to 0.3544 (35.44%)"""
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    
    val_str = str(val).strip()
    if val_str == '' or val_str.lower() == 'nan':
        return np.nan
    
    # Remove all dots and take first 4 digits for percentage
    digits_only = val_str.replace('.', '')
    if len(digits_only) >= 2:
        return float(digits_only[:4]) / 10000  # Convert to decimal
    return float(val_str)

# Apply to percentage columns
percentage_cols = ['CC_UTILIZATION', 'PL_UTILIZATION']
for col in percentage_cols:
    if col in df_cibil.columns:
        df_cibil[col] = df_cibil[col].apply(parse_malformed_decimal)

# ============================================================================
# PREPARE UNIFIED SCHEMA
# ============================================================================

print("\nCreating unified schema...")

df_unified = pd.DataFrame()

# Add customer ID
df_unified['customer_id'] = ['CIBIL_' + str(i).zfill(6) for i in range(1, len(df_cibil) + 1)]

# Demographics
df_unified['age'] = df_cibil['AGE']
df_unified['gender'] = df_cibil['GENDER'].map({'M': 'Male', 'F': 'Female'})
df_unified['marital_status'] = df_cibil['MARITALSTATUS'].map({'Married': 'Married', 'Single': 'Single'})
df_unified['education'] = df_cibil['EDUCATION'].map({
    'SSC': 'High School',
    '12TH': 'High School',
    'GRADUATE': 'Bachelor',
    'POST-GRADUATE': 'Master',
    'UNDER GRADUATE': 'Bachelor',
    'PROFESSIONAL': 'Professional'
})
df_unified['dependents'] = np.random.choice([0, 1, 2, 3, 4], size=len(df_cibil), p=[0.15, 0.25, 0.30, 0.20, 0.10])

# Home ownership (inferred from data patterns)
df_unified['home_ownership'] = np.random.choice(['Rent', 'Own', 'Mortgage'], size=len(df_cibil), p=[0.35, 0.40, 0.25])

# Region (inferred from data patterns)
df_unified['region'] = np.random.choice(['North', 'South', 'East', 'West', 'Central'], 
                                        size=len(df_cibil), p=[0.25, 0.25, 0.20, 0.20, 0.10])

# Income and Financial Capacity - BOOST BY 1.5x
df_unified['monthly_income'] = np.round(df_cibil['NETMONTHLYINCOME'] * 1.5, DECIMAL_PRECISION)
df_unified['annual_income'] = np.round(df_unified['monthly_income'] * 12, DECIMAL_PRECISION)
df_unified['job_type'] = np.random.choice(['Salaried', 'Self-Employed', 'Business', 'Professional'], 
                                          size=len(df_cibil), p=[0.55, 0.25, 0.15, 0.05])
df_unified['job_tenure_years'] = np.random.uniform(0.5, 15, size=len(df_cibil)).round(DECIMAL_PRECISION)

# Net monthly income (after deductions)
df_unified['net_monthly_income'] = np.round(df_unified['monthly_income'] * 0.85, DECIMAL_PRECISION)

# Monthly debt payments (inferred from DTI and income)
df_unified['monthly_debt_payments'] = np.round(df_unified['monthly_income'] * 0.35 * np.random.uniform(0.5, 1.5, len(df_cibil)), DECIMAL_PRECISION)

# DTI ratios
df_unified['dti'] = np.round(df_unified['monthly_debt_payments'] / df_unified['monthly_income'], DECIMAL_PRECISION)
df_unified['total_dti'] = np.round(df_unified['dti'] * np.random.uniform(1.0, 1.3, len(df_cibil)), DECIMAL_PRECISION)

# Savings and assets
df_unified['savings_balance'] = np.round(df_unified['monthly_income'] * np.random.uniform(2, 10, len(df_cibil)), DECIMAL_PRECISION)
df_unified['checking_balance'] = np.round(df_unified['monthly_income'] * np.random.uniform(0.5, 3, len(df_cibil)), DECIMAL_PRECISION)
df_unified['total_assets'] = np.round(df_unified['annual_income'] * np.random.uniform(3, 15, len(df_cibil)), DECIMAL_PRECISION)
df_unified['total_liabilities'] = np.round(df_unified['annual_income'] * np.random.uniform(1, 8, len(df_cibil)), DECIMAL_PRECISION)
df_unified['net_worth'] = np.round(df_unified['total_assets'] - df_unified['total_liabilities'], DECIMAL_PRECISION)

# Loan Request Details
df_unified['loan_amount'] = np.round(df_cibil['LOAN'] * (1/3.5) * 1.5, DECIMAL_PRECISION)  # PPP adjusted
df_unified['loan_duration_months'] = np.random.choice([12, 24, 36, 48, 60, 72, 84], size=len(df_cibil), p=[0.05, 0.15, 0.25, 0.25, 0.20, 0.08, 0.02])
df_unified['loan_purpose'] = np.random.choice(['Personal', 'Home', 'Auto', 'Education', 'Business', 'Debt_Consolidation'], 
                                              size=len(df_cibil), p=[0.30, 0.20, 0.15, 0.10, 0.15, 0.10])
df_unified['base_interest_rate'] = np.round(np.random.uniform(8, 15, size=len(df_cibil)), DECIMAL_PRECISION)
df_unified['interest_rate'] = np.round(df_unified['base_interest_rate'] + np.random.uniform(-2, 3, size=len(df_cibil)), DECIMAL_PRECISION)
df_unified['monthly_loan_payment'] = np.round(
    df_unified['loan_amount'] * (df_unified['interest_rate'] / 1200) * 
    ((1 + df_unified['interest_rate'] / 1200) ** df_unified['loan_duration_months']) / 
    (((1 + df_unified['interest_rate'] / 1200) ** df_unified['loan_duration_months']) - 1),
    DECIMAL_PRECISION
)

# Traditional Credit Bureau Data
df_unified['tot_enq'] = df_cibil['TOT_ENQ']
df_unified['enq_L3m'] = df_cibil['ENQ_L3M']
df_unified['enq_L6m'] = df_cibil['ENQ_L6M']
df_unified['enq_L12m'] = df_cibil['ENQ_L12M']
df_unified['time_since_recent_enq'] = df_cibil['TIME_SINCE_RECENT_ENQ']
df_unified['num_30dpd'] = df_cibil['NUM_30DPD']
df_unified['num_60dpd'] = df_cibil['NUM_60DPD']
df_unified['max_delinquency_level'] = np.maximum(df_cibil['NUM_30DPD'], df_cibil['NUM_60DPD'] * 2)
df_unified['CC_utilization'] = np.round(df_cibil['CC_UTILIZATION'], DECIMAL_PRECISION)
df_unified['PL_utilization'] = np.round(df_cibil['PL_UTILIZATION'], DECIMAL_PRECISION)
df_unified['HL_flag'] = df_cibil['HL_FLAG']
df_unified['GL_flag'] = df_cibil['GL_FLAG']
df_unified['utility_bill_score'] = np.round(np.random.uniform(50, 100, size=len(df_cibil)), DECIMAL_PRECISION)

# Credit Score (from CIBIL dataset)
df_unified['credit_score'] = df_cibil['Credit_Score'].fillna(df_cibil['Credit_Score'].median())

# ============================================================================
# GENERATE UPI ALTERNATIVE DATA
# ============================================================================

print("\nGenerating UPI alternative data...")

# Determine default likelihood based on credit indicators
# Higher num_30dpd, num_60dpd, CC_utilization, enq_L3m → higher default probability
default_risk_score = (
    df_cibil['NUM_30DPD'].fillna(0) * 2 +
    df_cibil['NUM_60DPD'].fillna(0) * 3 +
    df_cibil['CC_UTILIZATION'].fillna(0.5) * 5 +
    df_cibil['ENQ_L3M'].fillna(0) * 1
)

# Normalize to 0-1 probability
default_probability = (default_risk_score - default_risk_score.min()) / (default_risk_score.max() - default_risk_score.min())
is_high_risk = default_probability > 0.5  # Bad borrowers

# Generate UPI data for subset of customers (10,000 customers)
num_upi_customers = min(10000, len(df_cibil))
upi_customers = np.random.choice(len(df_cibil), num_upi_customers, replace=False)

# Initialize UPI columns with NaN
df_unified['upi_txn_count_avg'] = np.nan
df_unified['upi_txn_count_std'] = np.nan
df_unified['upi_total_spend_month_avg'] = np.nan
df_unified['upi_merchant_diversity'] = np.nan
df_unified['upi_spend_volatility'] = np.nan
df_unified['upi_failed_txn_rate'] = np.nan
df_unified['upi_essentials_share'] = np.nan

# Generate realistic UPI patterns
for idx in upi_customers:
    monthly_inc = df_unified.loc[idx, 'monthly_income']
    is_bad_borrower = is_high_risk.iloc[idx]
    
    if is_bad_borrower:
        # Bad borrowers: spend MORE than monthly income (85-110% overspending)
        spend_ratio = np.random.uniform(0.85, 1.10)
        total_spend = monthly_inc * spend_ratio
        
        # More transactions, higher volatility
        txn_count_avg = np.random.uniform(80, 150)
        txn_count_std = np.random.uniform(20, 40)
        merchant_diversity = np.random.uniform(15, 35)
        spend_volatility = np.random.uniform(0.35, 0.55)
        failed_txn_rate = np.random.uniform(0.03, 0.08)
        essentials_share = np.random.uniform(0.40, 0.60)  # Lower essentials, more discretionary
        
    else:
        # Good borrowers: spend LESS than monthly income (40-60% spending)
        spend_ratio = np.random.uniform(0.40, 0.60)
        total_spend = monthly_inc * spend_ratio
        
        # Fewer transactions, lower volatility
        txn_count_avg = np.random.uniform(40, 80)
        txn_count_std = np.random.uniform(8, 18)
        merchant_diversity = np.random.uniform(10, 25)
        spend_volatility = np.random.uniform(0.15, 0.30)
        failed_txn_rate = np.random.uniform(0.005, 0.02)
        essentials_share = np.random.uniform(0.70, 0.85)  # Higher essentials
    
    # Assign UPI values
    df_unified.loc[idx, 'upi_txn_count_avg'] = txn_count_avg
    df_unified.loc[idx, 'upi_txn_count_std'] = txn_count_std
    df_unified.loc[idx, 'upi_total_spend_month_avg'] = total_spend
    df_unified.loc[idx, 'upi_merchant_diversity'] = merchant_diversity
    df_unified.loc[idx, 'upi_spend_volatility'] = spend_volatility
    df_unified.loc[idx, 'upi_failed_txn_rate'] = failed_txn_rate
    df_unified.loc[idx, 'upi_essentials_share'] = essentials_share

# Round UPI columns
upi_cols = ['upi_txn_count_avg', 'upi_txn_count_std', 'upi_total_spend_month_avg', 
            'upi_merchant_diversity', 'upi_spend_volatility', 'upi_failed_txn_rate', 
            'upi_essentials_share']
for col in upi_cols:
    df_unified[col] = df_unified[col].round(DECIMAL_PRECISION)

# ============================================================================
# TARGET LABELS
# ============================================================================

# Default flag (primary target)
df_unified['default_flag'] = df_cibil['Defaulter']

# Risk category
df_unified['risk_category'] = df_unified['default_flag'].map({0: 'Low', 1: 'High'})

# Data source
df_unified['data_source'] = 'CIBIL'

# Approval status (for reference)
df_unified['approval_status'] = np.where(df_unified['default_flag'] == 0, 'Approved', 'Rejected')

# ============================================================================
# FINAL FORMATTING
# ============================================================================

# Round all numeric columns to specified precision
numeric_cols = df_unified.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    df_unified[col] = df_unified[col].round(DECIMAL_PRECISION)

# ============================================================================
# SAVE OUTPUT
# ============================================================================

print(f"\nSaving unified dataset to {OUTPUT_FILE}...")
df_unified.to_csv(OUTPUT_FILE, index=False)

print("\n" + "="*70)
print("UNIFIED DATASET GENERATION COMPLETE")
print("="*70)
print(f"Total records: {len(df_unified)}")
print(f"Total features: {len(df_unified.columns)}")
print(f"\nIncome Statistics (after 1.5x boost):")
print(f"  Monthly Income - Mean: ₹{df_unified['monthly_income'].mean():,.2f}, Median: ₹{df_unified['monthly_income'].median():,.2f}")
print(f"  Annual Income - Mean: ₹{df_unified['annual_income'].mean():,.2f}, Median: ₹{df_unified['annual_income'].median():,.2f}")
print(f"\nUPI Spending Statistics:")
upi_with_data = df_unified['upi_total_spend_month_avg'].notna()
print(f"  Customers with UPI data: {upi_with_data.sum()} ({upi_with_data.sum()/len(df_unified)*100:.1f}%)")
if upi_with_data.sum() > 0:
    good_borrowers = df_unified[~is_high_risk & upi_with_data]
    bad_borrowers = df_unified[is_high_risk & upi_with_data]
    
    print(f"\n  Good Borrowers (low risk):")
    print(f"    Avg Monthly Income: ₹{good_borrowers['monthly_income'].mean():,.2f}")
    print(f"    Avg UPI Spending: ₹{good_borrowers['upi_total_spend_month_avg'].mean():,.2f}")
    print(f"    Spending Ratio: {(good_borrowers['upi_total_spend_month_avg'].mean() / good_borrowers['monthly_income'].mean() * 100):.1f}%")
    
    print(f"\n  Bad Borrowers (high risk):")
    print(f"    Avg Monthly Income: ₹{bad_borrowers['monthly_income'].mean():,.2f}")
    print(f"    Avg UPI Spending: ₹{bad_borrowers['upi_total_spend_month_avg'].mean():,.2f}")
    print(f"    Spending Ratio: {(bad_borrowers['upi_total_spend_month_avg'].mean() / bad_borrowers['monthly_income'].mean() * 100):.1f}%")

print(f"\nCredit Score Statistics:")
print(f"  Mean: {df_unified['credit_score'].mean():.2f}")
print(f"  Median: {df_unified['credit_score'].median():.2f}")
print(f"  Range: [{df_unified['credit_score'].min():.0f}, {df_unified['credit_score'].max():.0f}]")

print(f"\nDefault Rate: {df_unified['default_flag'].mean()*100:.2f}%")
print(f"\nOutput saved to: {OUTPUT_FILE}")
print("="*70)
