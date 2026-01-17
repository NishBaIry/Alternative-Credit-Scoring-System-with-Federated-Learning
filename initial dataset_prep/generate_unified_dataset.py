"""
Generate Unified Indian Credit Dataset with Rescaled GitHub Data and Synthetic UPI Transactions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

print("=" * 80)
print("UNIFIED INDIAN CREDIT DATASET GENERATOR")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD AND EXPLORE DATASETS
# ============================================================================
print("\n[STEP 1] Loading datasets...")

# Load CIBIL dataset
cibil_df = pd.read_csv('External_Cibil_Dataset.csv')
print(f"  ✓ Loaded CIBIL dataset: {cibil_df.shape[0]:,} rows, {cibil_df.shape[1]} columns")

# Load GitHub alt-loan dataset
github_df = pd.read_csv('Loan new datset.csv')
print(f"  ✓ Loaded GitHub alt-loan dataset: {github_df.shape[0]:,} rows, {github_df.shape[1]} columns")

# ============================================================================
# STEP 2: RESCALE GITHUB MONETARY FIELDS TO INDIAN PPP LEVELS
# ============================================================================
print("\n[STEP 2] Rescaling GitHub monetary fields to Indian PPP levels...")

# Income scale factor: 1/3.5 ≈ 0.28 (PPP adjustment)
INCOME_SCALE = 1 / 3.5

# Create a copy for processing
github_scaled = github_df.copy()

# Convert monetary columns to numeric first (handle any string values)
monetary_cols = ['AnnualIncome', 'MonthlyDebtPayments', 'SavingsAccountBalance', 
                 'CheckingAccountBalance', 'TotalAssets', 'TotalLiabilities', 
                 'NetWorth', 'MonthlyLoanPayment']

for col in monetary_cols:
    if col in github_scaled.columns:
        github_scaled[col] = pd.to_numeric(github_scaled[col], errors='coerce')

# Rescale monetary fields
github_scaled['AnnualIncome_Scaled'] = github_scaled['AnnualIncome'] * INCOME_SCALE
github_scaled['MonthlyIncome_Scaled'] = github_scaled['AnnualIncome_Scaled'] / 12
github_scaled['MonthlyDebtPayments_Scaled'] = github_scaled['MonthlyDebtPayments'] * INCOME_SCALE
github_scaled['SavingsAccountBalance_Scaled'] = github_scaled['SavingsAccountBalance'] * INCOME_SCALE
github_scaled['CheckingAccountBalance_Scaled'] = github_scaled['CheckingAccountBalance'] * INCOME_SCALE
github_scaled['TotalAssets_Scaled'] = github_scaled['TotalAssets'] * INCOME_SCALE
github_scaled['TotalLiabilities_Scaled'] = github_scaled['TotalLiabilities'] * INCOME_SCALE
github_scaled['NetWorth_Scaled'] = github_scaled['NetWorth'] * INCOME_SCALE
github_scaled['MonthlyLoanPayment_Scaled'] = github_scaled['MonthlyLoanPayment'] * INCOME_SCALE

print(f"  ✓ Applied income_scale = {INCOME_SCALE:.3f} to monetary fields")
print(f"    Example: AnnualIncome ${github_df['AnnualIncome'].median():,.0f} → ₹{github_scaled['AnnualIncome_Scaled'].median():,.0f}")

# ============================================================================
# STEP 3: STANDARDIZE AND MAP COLUMNS TO UNIFIED SCHEMA
# ============================================================================
print("\n[STEP 3] Mapping to unified schema...")

# --- CIBIL Dataset Mapping ---
cibil_unified = pd.DataFrame()

# Generate customer_id
cibil_unified['customer_id'] = 'CIBIL_' + cibil_df['PROSPECTID'].astype(str)
cibil_unified['data_source'] = 'CIBIL'

# Demographics
cibil_unified['age'] = cibil_df['AGE']
cibil_unified['gender'] = cibil_df['GENDER']
cibil_unified['marital_status'] = cibil_df['MARITALSTATUS'].map({'Married': 'Married', 'Single': 'Single'})
cibil_unified['education'] = cibil_df['EDUCATION']
cibil_unified['dependents'] = np.nan  # Not in CIBIL
cibil_unified['home_ownership'] = np.nan  # Not in CIBIL
cibil_unified['region'] = np.nan  # Not in CIBIL

# Income & capacity
cibil_unified['monthly_income'] = cibil_df['NETMONTHLYINCOME']
cibil_unified['annual_income'] = cibil_df['NETMONTHLYINCOME'] * 12
cibil_unified['job_type'] = np.nan  # Not explicitly in CIBIL
cibil_unified['job_tenure_years'] = cibil_df['Time_With_Curr_Empr'] / 12  # Convert months to years
cibil_unified['net_monthly_income'] = cibil_df['NETMONTHLYINCOME']
cibil_unified['monthly_debt_payments'] = np.nan  # Not in CIBIL
cibil_unified['dti'] = np.nan  # Will compute later
cibil_unified['total_dti'] = np.nan  
cibil_unified['savings_balance'] = np.nan
cibil_unified['checking_balance'] = np.nan
cibil_unified['total_assets'] = np.nan
cibil_unified['total_liabilities'] = np.nan
cibil_unified['net_worth'] = np.nan

# Loan request (CIBIL doesn't have loan request, these would be from loan application)
cibil_unified['loan_amount'] = np.nan
cibil_unified['loan_duration_months'] = np.nan
cibil_unified['loan_purpose'] = np.nan
cibil_unified['base_interest_rate'] = np.nan
cibil_unified['interest_rate'] = np.nan
cibil_unified['monthly_loan_payment'] = np.nan

# Behavioural credit (semi-traditional)
cibil_unified['tot_enq'] = cibil_df['tot_enq']
cibil_unified['enq_L3m'] = cibil_df['enq_L3m']
cibil_unified['enq_L6m'] = cibil_df['enq_L6m']
cibil_unified['enq_L12m'] = cibil_df['enq_L12m']
cibil_unified['time_since_recent_enq'] = cibil_df['time_since_recent_enq']
cibil_unified['num_30dpd'] = cibil_df['num_times_30p_dpd']
cibil_unified['num_60dpd'] = cibil_df['num_times_60p_dpd']
cibil_unified['max_delinquency_level'] = cibil_df['max_delinquency_level']
cibil_unified['CC_utilization'] = cibil_df['CC_utilization']
cibil_unified['PL_utilization'] = cibil_df['PL_utilization']
cibil_unified['HL_flag'] = cibil_df['HL_Flag']
cibil_unified['GL_flag'] = cibil_df['GL_Flag']
cibil_unified['utility_bill_score'] = np.nan  # Not in CIBIL

# Labels (map Approved_Flag to default_flag: P1=approved=0, P2/P3/P4=rejected/default=1)
cibil_unified['default_flag'] = cibil_df['Approved_Flag'].map({'P1': 0, 'P2': 1, 'P3': 1, 'P4': 1})

# Keep credit score for evaluation only
cibil_unified['credit_score_original'] = cibil_df['Credit_Score']

print(f"  ✓ Mapped CIBIL dataset: {len(cibil_unified)} records")

# --- GitHub Dataset Mapping ---
github_unified = pd.DataFrame()

# Generate customer_id
github_unified['customer_id'] = 'GITHUB_' + (github_df.index + 1).astype(str)
github_unified['data_source'] = 'GITHUB'

# Demographics
github_unified['age'] = github_df['Age']
github_unified['gender'] = np.random.choice(['M', 'F'], size=len(github_df), p=[0.52, 0.48])  # Simulate gender
github_unified['marital_status'] = github_df['MaritalStatus']
github_unified['education'] = github_df['EducationLevel'].map({
    'High School': 'SSC',
    'Associate': '12TH',
    'Bachelor': 'GRADUATE',
    'Master': 'GRADUATE',
    'Doctorate': 'GRADUATE'
})
github_unified['dependents'] = github_df['NumberOfDependents']
github_unified['home_ownership'] = github_df['HomeOwnershipStatus']
github_unified['region'] = np.nan  # Not in GitHub

# Income & capacity (using RESCALED values)
github_unified['monthly_income'] = github_scaled['MonthlyIncome_Scaled']
github_unified['annual_income'] = github_scaled['AnnualIncome_Scaled']
github_unified['job_type'] = github_df['EmploymentStatus']
github_unified['job_tenure_years'] = github_df['JobTenure']
github_unified['net_monthly_income'] = github_scaled['MonthlyIncome_Scaled']
github_unified['monthly_debt_payments'] = github_scaled['MonthlyDebtPayments_Scaled']
github_unified['dti'] = github_df['DebtToIncomeRatio']
github_unified['total_dti'] = github_df['TotalDebtToIncomeRatio']
github_unified['savings_balance'] = github_scaled['SavingsAccountBalance_Scaled']
github_unified['checking_balance'] = github_scaled['CheckingAccountBalance_Scaled']
github_unified['total_assets'] = github_scaled['TotalAssets_Scaled']
github_unified['total_liabilities'] = github_scaled['TotalLiabilities_Scaled']
github_unified['net_worth'] = github_scaled['NetWorth_Scaled']

# Loan request
github_unified['loan_amount'] = github_df['LoanAmount'] * INCOME_SCALE  # Also scale loan amounts
github_unified['loan_duration_months'] = github_df['LoanDuration']
github_unified['loan_purpose'] = github_df['LoanPurpose']
github_unified['base_interest_rate'] = github_df['BaseInterestRate']
github_unified['interest_rate'] = github_df['InterestRate']
github_unified['monthly_loan_payment'] = github_scaled['MonthlyLoanPayment_Scaled']

# Behavioural credit (semi-traditional)
github_unified['tot_enq'] = github_df['NumberOfCreditInquiries']
github_unified['enq_L3m'] = np.where(github_df['NumberOfCreditInquiries'] > 0, 
                                      np.random.randint(0, github_df['NumberOfCreditInquiries'] + 1), 0)
github_unified['enq_L6m'] = np.where(github_df['NumberOfCreditInquiries'] > 0,
                                      np.random.randint(github_unified['enq_L3m'], github_df['NumberOfCreditInquiries'] + 1), 0)
github_unified['enq_L12m'] = github_df['NumberOfCreditInquiries']
github_unified['time_since_recent_enq'] = np.random.randint(0, 365, len(github_df))
github_unified['num_30dpd'] = github_df['PreviousLoanDefaults']
github_unified['num_60dpd'] = (github_df['PreviousLoanDefaults'] * 0.5).astype(int)
github_unified['max_delinquency_level'] = github_df['PreviousLoanDefaults'] * 30
github_unified['CC_utilization'] = github_df['CreditCardUtilizationRate']
github_unified['PL_utilization'] = np.random.uniform(0, 1, len(github_df))
github_unified['HL_flag'] = (github_df['HomeOwnershipStatus'] == 'Mortgage').astype(int)
github_unified['GL_flag'] = np.random.randint(0, 2, len(github_df))
github_unified['utility_bill_score'] = github_df['UtilityBillsPaymentHistory']

# Labels (map LoanApproved to default_flag: 1=approved=no default=0, 0=rejected=potential default=1)
github_unified['default_flag'] = (1 - github_df['LoanApproved']).astype(int)

# Keep credit score for evaluation only
github_unified['credit_score_original'] = github_df['CreditScore']

print(f"  ✓ Mapped GitHub dataset: {len(github_unified)} records")

# Combine datasets
unified_df = pd.concat([cibil_unified, github_unified], ignore_index=True)
print(f"\n  ✓ Combined unified dataset: {len(unified_df):,} total records")

# Fill missing DTI for CIBIL records (estimate from data)
for idx in unified_df[unified_df['data_source'] == 'CIBIL'].index:
    if pd.notna(unified_df.loc[idx, 'net_monthly_income']) and unified_df.loc[idx, 'net_monthly_income'] > 0:
        # Estimate monthly debt based on utilization
        estimated_debt = np.random.uniform(0.2, 0.5) * unified_df.loc[idx, 'net_monthly_income']
        unified_df.loc[idx, 'monthly_debt_payments'] = estimated_debt
        unified_df.loc[idx, 'dti'] = estimated_debt / unified_df.loc[idx, 'net_monthly_income']

# Replace -99999 and invalid values
unified_df.replace(-99999, np.nan, inplace=True)

# Convert numeric columns to proper types
numeric_cols = ['CC_utilization', 'PL_utilization', 'dti', 'total_dti', 
                'num_30dpd', 'num_60dpd', 'enq_L6m', 'default_flag',
                'age', 'monthly_income', 'annual_income', 'net_monthly_income',
                'monthly_debt_payments', 'loan_amount', 'tot_enq', 'enq_L3m', 
                'enq_L12m', 'utility_bill_score']

for col in numeric_cols:
    if col in unified_df.columns:
        unified_df[col] = pd.to_numeric(unified_df[col], errors='coerce')

unified_df.loc[unified_df['CC_utilization'] < 0, 'CC_utilization'] = np.nan
unified_df.loc[unified_df['PL_utilization'] < 0, 'PL_utilization'] = np.nan

# ============================================================================
# STEP 4: DEFINE REPAYMENT GROUPS FOR UPI GENERATION
# ============================================================================
print("\n[STEP 4] Defining repayment groups...")

# Compute good_borrower flag
unified_df['good_borrower'] = 0

conditions = (
    (unified_df['default_flag'] == 0) &
    (unified_df['dti'].fillna(1) < 0.45) &
    (unified_df['num_30dpd'].fillna(0) == 0) &
    (unified_df['enq_L6m'].fillna(100) <= 3)
)

unified_df.loc[conditions, 'good_borrower'] = 1

good_count = (unified_df['good_borrower'] == 1).sum()
bad_count = (unified_df['good_borrower'] == 0).sum()

print(f"  ✓ Good borrowers: {good_count:,} ({good_count/len(unified_df)*100:.1f}%)")
print(f"  ✓ Bad/risky borrowers: {bad_count:,} ({bad_count/len(unified_df)*100:.1f}%)")

# ============================================================================
# STEP 5: GENERATE SYNTHETIC UPI TRANSACTIONS
# ============================================================================
print("\n[STEP 5] Generating synthetic UPI transactions...")
print("  (This may take a few minutes...)")

# UPI transaction generation parameters
MERCHANT_CATEGORIES = {
    'essentials': ['Grocery', 'Food & Dining', 'Fuel', 'Utilities', 'Rent'],
    'discretionary': ['Shopping', 'Entertainment', 'Travel', 'Other']
}

STATES = ['Maharashtra', 'Karnataka', 'Delhi', 'Tamil Nadu', 'Gujarat', 'West Bengal', 
          'Telangana', 'Uttar Pradesh', 'Rajasthan', 'Kerala']

BANKS = ['SBI', 'HDFC', 'ICICI', 'Axis', 'Kotak', 'PNB', 'BOB', 'Paytm Payments Bank', 
         'IDFC First', 'Yes Bank']

DEVICE_OS = ['Android', 'iOS']
NETWORK_TYPE = ['4G', '5G', 'WiFi']

upi_transactions = []
transaction_id = 1

# Generate UPI for a sample (to keep dataset manageable, we'll generate for first 10k customers)
sample_size = min(10000, len(unified_df))
sample_df = unified_df.iloc[:sample_size].copy()

print(f"  Generating UPI transactions for {sample_size:,} customers...")

for idx, row in sample_df.iterrows():
    customer_id = row['customer_id']
    good_borrower = row['good_borrower']
    monthly_income = row['monthly_income'] if pd.notna(row['monthly_income']) else 25000
    
    # Determine transaction count based on borrower quality
    if good_borrower == 1:
        # Good borrower: 40-60 transactions per month
        txn_count = np.random.poisson(50)
        txn_count = max(30, min(80, txn_count))  # Clamp between 30-80
        
        # Category mix: 70-80% essentials
        essentials_pct = np.random.uniform(0.70, 0.80)
        
        # Amount distribution: log-normal with median 500-1500
        median_amount = np.random.uniform(500, 1500)
        amount_scale = median_amount / np.exp(0)  # Adjust for log-normal
        
        # Low failure rate
        failed_rate = 0.02
        
    else:
        # Bad borrower: 10-25 transactions or highly variable
        if np.random.random() < 0.3:
            txn_count = np.random.poisson(15)
        else:
            txn_count = np.random.poisson(40)
        txn_count = max(5, min(100, txn_count))
        
        # Category mix: 40-50% discretionary
        essentials_pct = np.random.uniform(0.40, 0.60)
        
        # Higher spend volatility
        median_amount = np.random.uniform(300, 2000)
        amount_scale = median_amount * np.random.uniform(1.0, 2.5)
        
        # Higher failure rate
        failed_rate = np.random.uniform(0.05, 0.10)
    
    # Generate transactions for this customer
    for _ in range(txn_count):
        # Determine category
        if np.random.random() < essentials_pct:
            category = np.random.choice(MERCHANT_CATEGORIES['essentials'])
        else:
            category = np.random.choice(MERCHANT_CATEGORIES['discretionary'])
        
        # Transaction amount (scaled by income)
        base_amount = np.random.lognormal(mean=0, sigma=1) * amount_scale
        income_factor = monthly_income / 25000  # Normalize to 25k baseline
        amount = base_amount * np.sqrt(income_factor)  # Sqrt to reduce extreme scaling
        amount = max(50, min(50000, amount))  # Clamp between 50-50000
        
        # Transaction status
        if np.random.random() < failed_rate:
            status = 'FAILED'
            failed_flag = 1
        else:
            status = 'SUCCESS'
            failed_flag = 0
        
        # Day of month and day of week
        if good_borrower == 1:
            # More regular pattern
            day_of_month = np.random.choice(range(1, 32), p=None)
            day_of_week = np.random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 
                                           'Saturday', 'Sunday'], p=[0.18, 0.18, 0.18, 0.18, 0.15, 0.08, 0.05])
        else:
            # More irregular
            day_of_month = np.random.randint(1, 32)
            day_of_week = np.random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 
                                           'Saturday', 'Sunday'])
        
        # Other attributes
        upi_txn_type = np.random.choice(['P2M', 'P2P'], p=[0.7, 0.3])
        
        upi_transactions.append({
            'transaction_id': f'TXN{transaction_id:010d}',
            'customer_id': customer_id,
            'upi_txn_type': upi_txn_type,
            'merchant_category': category,
            'amount_inr': round(amount, 2),
            'status': status,
            'payer_age_band': f"{(row['age'] // 10) * 10}-{(row['age'] // 10) * 10 + 9}" if pd.notna(row['age']) else '30-39',
            'merchant_age_band': np.random.choice(['20-29', '30-39', '40-49', '50-59']),
            'state': np.random.choice(STATES),
            'payer_bank': np.random.choice(BANKS),
            'payee_bank': np.random.choice(BANKS),
            'device_os': np.random.choice(DEVICE_OS, p=[0.75, 0.25]),
            'network_type': np.random.choice(NETWORK_TYPE, p=[0.6, 0.15, 0.25]),
            'failed_flag': failed_flag,
            'txn_dayofmonth': day_of_month,
            'day_of_week': day_of_week
        })
        
        transaction_id += 1
    
    # Progress indicator
    if (idx + 1) % 1000 == 0:
        print(f"    Processed {idx + 1:,} customers, generated {len(upi_transactions):,} transactions")

upi_df = pd.DataFrame(upi_transactions)
print(f"\n  ✓ Generated {len(upi_df):,} UPI transactions")

# ============================================================================
# STEP 6: AGGREGATE UPI FEATURES TO BORROWER LEVEL
# ============================================================================
print("\n[STEP 6] Aggregating UPI features to borrower level...")

# Aggregate by customer
upi_agg = upi_df.groupby('customer_id').agg({
    'transaction_id': 'count',
    'amount_inr': ['mean', 'std', 'sum'],
    'failed_flag': 'sum',
    'merchant_category': lambda x: x.nunique()
}).reset_index()

upi_agg.columns = ['customer_id', 'upi_txn_count', 'upi_amount_mean', 'upi_amount_std', 
                   'upi_total_spend', 'upi_failed_count', 'upi_merchant_diversity']

# Calculate additional features
upi_agg['upi_txn_count_avg'] = upi_agg['upi_txn_count']  # Per month
upi_agg['upi_txn_count_std'] = upi_agg['upi_txn_count'] * 0.2  # Simulate std across months
upi_agg['upi_total_spend_month_avg'] = upi_agg['upi_total_spend']
upi_agg['upi_merchant_diversity'] = upi_agg['upi_merchant_diversity'] / upi_agg['upi_txn_count']
upi_agg['upi_spend_volatility'] = upi_agg['upi_amount_std'] / (upi_agg['upi_amount_mean'] + 1)
upi_agg['upi_failed_txn_rate'] = upi_agg['upi_failed_count'] / upi_agg['upi_txn_count']

# Calculate essentials share
essentials_list = MERCHANT_CATEGORIES['essentials']
upi_essentials = upi_df[upi_df['merchant_category'].isin(essentials_list)].groupby('customer_id')['amount_inr'].sum().reset_index()
upi_essentials.columns = ['customer_id', 'essentials_spend']

upi_agg = upi_agg.merge(upi_essentials, on='customer_id', how='left')
upi_agg['essentials_spend'] = upi_agg['essentials_spend'].fillna(0)
upi_agg['upi_essentials_share'] = upi_agg['essentials_spend'] / (upi_agg['upi_total_spend'] + 1)

# Select final UPI features
upi_features = upi_agg[['customer_id', 'upi_txn_count_avg', 'upi_txn_count_std', 
                         'upi_total_spend_month_avg', 'upi_merchant_diversity',
                         'upi_spend_volatility', 'upi_failed_txn_rate', 'upi_essentials_share']]

# Merge back to unified dataset
unified_final = unified_df.merge(upi_features, on='customer_id', how='left')

# Fill NaN for customers without UPI data
upi_cols = ['upi_txn_count_avg', 'upi_txn_count_std', 'upi_total_spend_month_avg',
            'upi_merchant_diversity', 'upi_spend_volatility', 'upi_failed_txn_rate', 'upi_essentials_share']
unified_final[upi_cols] = unified_final[upi_cols].fillna(0)

print(f"  ✓ Aggregated UPI features for {len(upi_features):,} customers")
print(f"  ✓ Final unified dataset shape: {unified_final.shape}")

# ============================================================================
# STEP 7: SAVE FINAL DATASETS
# ============================================================================
print("\n[STEP 7] Saving final unified dataset...")

# Save single unified dataset with all features
output_file = 'unified_credit_scoring_dataset.csv'
unified_final.to_csv(output_file, index=False)
print(f"  ✓ Saved unified dataset: {output_file}")
print(f"  ✓ Shape: {unified_final.shape[0]:,} customers × {unified_final.shape[1]} features")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n" + "=" * 80)
print("DATASET GENERATION COMPLETE")
print("=" * 80)

print(f"\n📊 UNIFIED DATASET SUMMARY:")
print(f"  • Total customers: {len(unified_final):,}")
print(f"  • CIBIL records: {(unified_final['data_source'] == 'CIBIL').sum():,}")
print(f"  • GitHub records: {(unified_final['data_source'] == 'GITHUB').sum():,}")
print(f"  • Good borrowers: {(unified_final['good_borrower'] == 1).sum():,}")
print(f"  • Bad/risky borrowers: {(unified_final['good_borrower'] == 0).sum():,}")
print(f"  • Default rate: {unified_final['default_flag'].mean()*100:.1f}%")

print(f"\n💰 INCOME STATISTICS (Rescaled to Indian PPP):")
print(f"  • Median annual income: ₹{unified_final['annual_income'].median():,.0f}")
print(f"  • Median monthly income: ₹{unified_final['monthly_income'].median():,.0f}")
print(f"  • Median DTI: {unified_final['dti'].median():.2%}")

print(f"\n📱 UPI ALTERNATIVE DATA COVERAGE:")
print(f"  • Customers with UPI features: {unified_final['upi_txn_count_avg'].notna().sum():,} ({unified_final['upi_txn_count_avg'].notna().sum()/len(unified_final)*100:.1f}%)")
print(f"  • Customers without UPI (thin-file): {unified_final['upi_txn_count_avg'].isna().sum():,} ({unified_final['upi_txn_count_avg'].isna().sum()/len(unified_final)*100:.1f}%)")
print(f"  • Avg UPI transactions/month: {unified_final['upi_txn_count_avg'].mean():.1f}")
print(f"  • Avg essentials share: {unified_final['upi_essentials_share'].mean()*100:.1f}%")
print(f"  • Avg failure rate: {unified_final['upi_failed_txn_rate'].mean()*100:.1f}%")

print(f"\n📋 FEATURE CATEGORIES:")
print(f"  • Demographics: age, gender, marital_status, education, dependents, home_ownership, region")
print(f"  • Income & Capacity: monthly_income, annual_income, job_type, job_tenure_years, dti, savings_balance, etc.")
print(f"  • Loan Request: loan_amount, loan_duration_months, loan_purpose, interest_rate, monthly_loan_payment")
print(f"  • Traditional Credit: tot_enq, enq_L6m, num_30dpd, CC_utilization, HL_flag, GL_flag, utility_bill_score")
print(f"  • UPI Alt-Data: upi_txn_count_avg, upi_merchant_diversity, upi_failed_txn_rate, upi_essentials_share")
print(f"  • Target Labels: default_flag, good_borrower")

print(f"\n✅ Ready for credit scoring model training!")
print(f"  • File: {output_file}")
print(f"  • Use cases:")
print(f"    - Traditional scoring: Use CIBIL/behavioral credit features")
print(f"    - Alternative scoring: Use UPI features for thin-file customers")
print(f"    - Hybrid scoring: Combine both traditional + UPI features")
