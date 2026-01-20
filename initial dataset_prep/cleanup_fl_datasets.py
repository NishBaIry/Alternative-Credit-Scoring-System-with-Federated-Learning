"""
Clean up FL datasets for Bank A and Bank B
- Replace customer_id with 5-digit sequential numbers
- Add hashed password column (SHA256 of customer_id)
- Remove unnecessary columns
"""

import pandas as pd
import hashlib

# Configuration
BANK_A_INPUT = "data/bank_a_fl_dataset.csv"
BANK_B_INPUT = "data/bank_b_fl_dataset.csv"
BANK_A_OUTPUT = "data/bank_a_fl_dataset.csv"
BANK_B_OUTPUT = "data/bank_b_fl_dataset.csv"

# Columns to remove (not needed for prediction)
COLUMNS_TO_REMOVE = [
    'data_source',           # Only for tracking, not for prediction
    'credit_score_original', # Legacy score, we're building new one
    'good_borrower'          # Derived from default_flag, redundant
]

def hash_password(account_number):
    """Generate SHA256 hash of account number for password"""
    return hashlib.sha256(str(account_number).encode()).hexdigest()

def process_dataset(input_file, output_file, bank_name):
    """Process a dataset with new IDs and passwords"""
    print(f"\n{'='*80}")
    print(f"Processing {bank_name} Dataset")
    print(f"{'='*80}")
    
    # Load dataset
    print(f"\n[1/4] Loading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"  ✓ Loaded {len(df):,} rows, {df.shape[1]} columns")
    
    # Generate new customer IDs (8-digit sequential)
    print(f"\n[2/4] Generating new customer IDs...")
    new_ids = [f"{i:08d}" for i in range(1, len(df) + 1)]
    df['customer_id'] = new_ids
    print(f"  ✓ Generated IDs from 00000001 to {len(df):08d}")
    
    # Generate hashed passwords
    print(f"\n[3/4] Generating hashed passwords (SHA256)...")
    df['password'] = df['customer_id'].apply(hash_password)
    print(f"  ✓ Generated {len(df):,} hashed passwords")
    print(f"  Example: ID=00001, Password Hash={df.iloc[0]['password'][:32]}...")
    
    # Remove unnecessary columns
    print(f"\n[4/4] Removing unnecessary columns...")
    cols_to_remove = [col for col in COLUMNS_TO_REMOVE if col in df.columns]
    if cols_to_remove:
        df = df.drop(columns=cols_to_remove)
        print(f"  ✓ Removed columns: {', '.join(cols_to_remove)}")
    else:
        print(f"  ✓ No columns to remove")
    
    # Reorder columns: customer_id, password, then features, then default_flag at end
    feature_cols = [col for col in df.columns if col not in ['customer_id', 'password', 'default_flag']]
    new_column_order = ['customer_id', 'password'] + feature_cols + ['default_flag']
    df = df[new_column_order]
    
    # Ensure customer_id is stored as string (preserve leading zeros)
    df['customer_id'] = df['customer_id'].astype(str)
    
    # Save cleaned dataset with proper float formatting (5 decimal places)
    print(f"\n  Saving with decimal precision (5 decimal places)...")
    df.to_csv(output_file, index=False, float_format='%.5f')
    print(f"  ✓ Saved cleaned dataset to: {output_file}")
    print(f"  ✓ Final shape: {len(df):,} rows, {df.shape[1]} columns")
    
    # Show statistics
    print(f"\n  📊 Dataset Statistics:")
    print(f"    - Customer IDs: 00000001 to {len(df):08d}")
    print(f"    - Features: {len(feature_cols)} columns")
    print(f"    - Default rate: {df['default_flag'].mean():.2%}")
    print(f"    - Password column: SHA256 hashed")
    
    return df

# ============================================================================
# MAIN EXECUTION
# ============================================================================

print("="*80)
print("CLEANING UP FEDERATED LEARNING DATASETS")
print("="*80)

# Process Bank A
df_bank_a = process_dataset(BANK_A_INPUT, BANK_A_OUTPUT, "BANK A")

# Process Bank B
df_bank_b = process_dataset(BANK_B_INPUT, BANK_B_OUTPUT, "BANK B")

# Summary
print("\n" + "="*80)
print("✅ CLEANUP COMPLETE!")
print("="*80)

print(f"\n📁 Output Files:")
print(f"  • Bank A: {BANK_A_OUTPUT}")
print(f"    - {len(df_bank_a):,} customers (IDs: 00000001-{len(df_bank_a):08d})")
print(f"    - {df_bank_a.shape[1]} columns (including password)")
print(f"    - Default rate: {df_bank_a['default_flag'].mean():.2%}")

print(f"\n  • Bank B: {BANK_B_OUTPUT}")
print(f"    - {len(df_bank_b):,} customers (IDs: 00000001-{len(df_bank_b):08d})")
print(f"    - {df_bank_b.shape[1]} columns (including password)")
print(f"    - Default rate: {df_bank_b['default_flag'].mean():.2%}")

print(f"\n💡 Authentication Flow:")
print(f"  1. User enters account number (e.g., '00000001') and password ('00000001')")
print(f"  2. Frontend hashes password: sha256('00000001')")
print(f"  3. Frontend sends: account_number + hashed_password to backend")
print(f"  4. Backend looks up account_number in CSV")
print(f"  5. Backend compares received hash with stored hash")
print(f"  6. If match → authenticated ✓")

print(f"\n🔐 Security Note:")
print(f"  • Passwords are stored as SHA256 hashes in CSV")
print(f"  • Never store plaintext passwords")
print(f"  • Account number = password (for simplicity)")
print(f"  • Example: Account 00000001 → Password 00000001")
print(f"  • Production: Use stronger authentication (bcrypt, JWT, etc.)")

print(f"\n📊 Removed Columns:")
print(f"  • data_source: Tracking only, not for prediction")
print(f"  • credit_score_original: Legacy score, not needed")
print(f"  • good_borrower: Derived from default_flag (redundant)")

print("\n" + "="*80)
