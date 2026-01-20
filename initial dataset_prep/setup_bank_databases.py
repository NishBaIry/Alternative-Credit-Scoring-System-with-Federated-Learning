"""
Initialize SQLite Databases for Bank A and Bank B

This script:
1. Checks if bank_a.db and bank_b.db exist
2. On first run, reads CSV files and creates customers table
3. Bulk-inserts all rows from CSV into SQLite
4. From then on, all operations use SQLite as authoritative store

Usage:
    python setup_bank_databases.py
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

BANK_A_CSV = "data/bank_a_fl_dataset.csv"
BANK_B_CSV = "data/bank_b_fl_dataset.csv"
BANK_A_DB = "data/bank_a.db"
BANK_B_DB = "data/bank_b.db"

# ============================================================================
# DATABASE SETUP FUNCTIONS
# ============================================================================

def create_customers_table(conn):
    """Create customers table with all required columns"""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        -- Identifier & Authentication
        customer_id TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        
        -- Demographics
        age INTEGER,
        gender TEXT,
        marital_status TEXT,
        education TEXT,
        dependents INTEGER,
        home_ownership TEXT,
        region TEXT,
        
        -- Income & Financial Capacity
        monthly_income REAL,
        annual_income REAL,
        job_type TEXT,
        job_tenure_years REAL,
        net_monthly_income REAL,
        monthly_debt_payments REAL,
        dti REAL,
        total_dti REAL,
        
        -- Assets & Liabilities
        savings_balance REAL,
        checking_balance REAL,
        total_assets REAL,
        total_liabilities REAL,
        net_worth REAL,
        
        -- Loan Request
        loan_amount REAL,
        loan_duration_months INTEGER,
        loan_purpose TEXT,
        base_interest_rate REAL,
        interest_rate REAL,
        monthly_loan_payment REAL,
        
        -- Traditional Credit Bureau Data
        tot_enq INTEGER,
        enq_L3m INTEGER,
        enq_L6m INTEGER,
        enq_L12m INTEGER,
        time_since_recent_enq INTEGER,
        num_30dpd INTEGER,
        num_60dpd INTEGER,
        max_delinquency_level INTEGER,
        CC_utilization REAL,
        PL_utilization REAL,
        HL_flag INTEGER,
        GL_flag INTEGER,
        utility_bill_score REAL,
        
        -- Labels & Targets (removed: credit_score_original, good_borrower)
        default_flag INTEGER,
        credit_score REAL,
        
        -- UPI Alternative Data
        upi_txn_count_avg REAL,
        upi_txn_count_std REAL,
        upi_total_spend_month_avg REAL,
        upi_txn_amt_avg REAL,
        upi_merchant_diversity REAL,
        upi_spend_volatility REAL,
        upi_failed_txn_rate REAL,
        upi_essentials_share REAL,
        
        -- Metadata
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create indexes for common queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_default_flag ON customers(default_flag)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_credit_score ON customers(credit_score)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_monthly_income ON customers(monthly_income)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dti ON customers(dti)")
    
    conn.commit()
    print("  ✓ Created customers table with indexes")

def bulk_insert_from_csv(conn, csv_path, bank_name):
    """Bulk insert all rows from CSV into SQLite database"""
    print(f"\n  Loading data from {csv_path}...")
    # Ensure customer_id is read as string to preserve leading zeros
    df = pd.read_csv(csv_path, dtype={'customer_id': str})
    print(f"  ✓ Loaded {len(df):,} rows from CSV")
    
    # Insert into database
    print(f"  Inserting rows into SQLite database...")
    df.to_sql('customers', conn, if_exists='append', index=False)
    
    # Verify insertion
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers")
    count = cursor.fetchone()[0]
    print(f"  ✓ Inserted {count:,} rows into {bank_name} database")
    
    return count

def initialize_bank_database(db_path, csv_path, bank_name):
    """Initialize or connect to bank database"""
    is_new_db = not os.path.exists(db_path)
    
    if is_new_db:
        print(f"\n{'='*70}")
        print(f"INITIALIZING {bank_name} DATABASE (First Run)")
        print(f"{'='*70}")
    else:
        print(f"\n{'='*70}")
        print(f"{bank_name} DATABASE EXISTS - Skipping CSV Import")
        print(f"{'='*70}")
    
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(db_path)
    
    if is_new_db:
        # First run: Create table and import from CSV
        create_customers_table(conn)
        row_count = bulk_insert_from_csv(conn, csv_path, bank_name)
        
        # Get statistics
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(monthly_income), AVG(credit_score), AVG(default_flag) FROM customers")
        avg_income, avg_score, default_rate = cursor.fetchone()
        
        print(f"\n  Database Statistics:")
        print(f"    • Total customers: {row_count:,}")
        print(f"    • Avg monthly income: ₹{avg_income:,.2f}")
        print(f"    • Avg credit score: {avg_score:.2f}")
        print(f"    • Default rate: {default_rate*100:.2f}%")
        print(f"\n  ✓ {bank_name} database initialized successfully!")
        print(f"  ✓ Database location: {db_path}")
        print(f"  ✓ All future operations will use SQLite (not CSV)")
    else:
        # Database exists: Just verify and show stats
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM customers")
        row_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(monthly_income), AVG(credit_score), AVG(default_flag) FROM customers")
        avg_income, avg_score, default_rate = cursor.fetchone()
        
        print(f"\n  Database Statistics:")
        print(f"    • Total customers: {row_count:,}")
        print(f"    • Avg monthly income: ₹{avg_income:,.2f}")
        print(f"    • Avg credit score: {avg_score:.2f}")
        print(f"    • Default rate: {default_rate*100:.2f}%")
        print(f"\n  ✓ Connected to existing {bank_name} database")
        print(f"  ✓ Using SQLite as authoritative store")
    
    conn.close()
    return is_new_db

# ============================================================================
# HELPER FUNCTIONS FOR DATABASE OPERATIONS
# ============================================================================

def get_bank_connection(bank='A'):
    """Get database connection for specified bank"""
    db_path = BANK_A_DB if bank == 'A' else BANK_B_DB
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not initialized. Run setup_bank_databases.py first.")
    return sqlite3.connect(db_path)

def query_customers(bank='A', limit=None, filters=None):
    """
    Query customers from bank database
    
    Args:
        bank: 'A' or 'B'
        limit: Number of rows to return (None = all)
        filters: Dict of column:value filters
    
    Returns:
        pandas DataFrame
    """
    conn = get_bank_connection(bank)
    
    query = "SELECT * FROM customers"
    params = []
    
    if filters:
        where_clauses = []
        for col, val in filters.items():
            where_clauses.append(f"{col} = ?")
            params.append(val)
        query += " WHERE " + " AND ".join(where_clauses)
    
    if limit:
        query += f" LIMIT {limit}"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

def get_customer_by_id(customer_id, bank='A'):
    """Get single customer by ID"""
    conn = get_bank_connection(bank)
    df = pd.read_sql_query(
        "SELECT * FROM customers WHERE customer_id = ?", 
        conn, 
        params=[customer_id]
    )
    conn.close()
    
    return df.iloc[0] if len(df) > 0 else None

def update_customer(customer_id, updates, bank='A'):
    """
    Update customer record
    
    Args:
        customer_id: Customer ID to update
        updates: Dict of column:new_value
        bank: 'A' or 'B'
    
    Returns:
        Number of rows updated
    """
    conn = get_bank_connection(bank)
    cursor = conn.cursor()
    
    set_clauses = []
    params = []
    for col, val in updates.items():
        set_clauses.append(f"{col} = ?")
        params.append(val)
    
    params.append(customer_id)
    
    query = f"UPDATE customers SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE customer_id = ?"
    cursor.execute(query, params)
    
    rows_updated = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_updated

def insert_customer(customer_data, bank='A'):
    """
    Insert new customer record
    
    Args:
        customer_data: Dict of column:value
        bank: 'A' or 'B'
    
    Returns:
        Customer ID of inserted record
    """
    conn = get_bank_connection(bank)
    df = pd.DataFrame([customer_data])
    df.to_sql('customers', conn, if_exists='append', index=False)
    conn.close()
    
    return customer_data.get('customer_id')

def get_database_stats(bank='A'):
    """Get comprehensive database statistics"""
    conn = get_bank_connection(bank)
    cursor = conn.cursor()
    
    stats = {}
    
    # Total customers
    cursor.execute("SELECT COUNT(*) FROM customers")
    stats['total_customers'] = cursor.fetchone()[0]
    
    # Default statistics
    cursor.execute("SELECT COUNT(*), AVG(default_flag) FROM customers")
    count, default_rate = cursor.fetchone()
    stats['default_rate'] = default_rate
    
    # Income statistics
    cursor.execute("SELECT AVG(monthly_income), MIN(monthly_income), MAX(monthly_income) FROM customers")
    avg, min_val, max_val = cursor.fetchone()
    stats['avg_monthly_income'] = avg
    stats['min_monthly_income'] = min_val
    stats['max_monthly_income'] = max_val
    
    # Credit score statistics
    cursor.execute("SELECT AVG(credit_score), MIN(credit_score), MAX(credit_score) FROM customers WHERE credit_score IS NOT NULL")
    avg, min_val, max_val = cursor.fetchone()
    stats['avg_credit_score'] = avg
    stats['min_credit_score'] = min_val
    stats['max_credit_score'] = max_val
    
    # Data source breakdown
    cursor.execute("SELECT data_source, COUNT(*) FROM customers GROUP BY data_source")
    stats['data_sources'] = dict(cursor.fetchall())
    
    # UPI data coverage
    cursor.execute("SELECT COUNT(*) FROM customers WHERE upi_txn_count_avg IS NOT NULL AND upi_txn_count_avg > 0")
    stats['upi_customers'] = cursor.fetchone()[0]
    
    conn.close()
    return stats

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("BANK DATABASE INITIALIZATION")
    print("="*70)
    
    # Check if CSV files exist
    if not os.path.exists(BANK_A_CSV):
        print(f"\n❌ Error: {BANK_A_CSV} not found!")
        print("   Please run generate_fl_datasets.py first.")
        exit(1)
    
    if not os.path.exists(BANK_B_CSV):
        print(f"\n❌ Error: {BANK_B_CSV} not found!")
        print("   Please run generate_fl_datasets.py first.")
        exit(1)
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Initialize Bank A database
    bank_a_new = initialize_bank_database(BANK_A_DB, BANK_A_CSV, "BANK A")
    
    # Initialize Bank B database
    bank_b_new = initialize_bank_database(BANK_B_DB, BANK_B_CSV, "BANK B")
    
    # Final summary
    print("\n" + "="*70)
    print("SETUP COMPLETE")
    print("="*70)
    
    if bank_a_new or bank_b_new:
        print("\n✅ Database(s) initialized from CSV files")
        print("\n📁 Database Files Created:")
        if bank_a_new:
            print(f"  • {BANK_A_DB}")
        if bank_b_new:
            print(f"  • {BANK_B_DB}")
        
        print("\n💡 Important:")
        print("  • All future operations will use SQLite databases")
        print("  • CSV files are no longer needed for reads/writes")
        print("  • SQLite is now the authoritative data store")
    else:
        print("\n✅ Both databases already exist - using existing data")
    
    print("\n📊 Usage Examples:")
    print("""
    # Query customers from Bank A
    from setup_bank_databases import query_customers
    df = query_customers(bank='A', limit=100)
    
    # Get specific customer
    from setup_bank_databases import get_customer_by_id
    customer = get_customer_by_id('CIBIL_000001', bank='A')
    
    # Update customer
    from setup_bank_databases import update_customer
    update_customer('CIBIL_000001', {'monthly_income': 50000}, bank='A')
    
    # Get statistics
    from setup_bank_databases import get_database_stats
    stats = get_database_stats(bank='A')
    """)
    
    print("\n" + "="*70)
