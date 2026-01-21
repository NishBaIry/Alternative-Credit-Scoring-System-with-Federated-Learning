# new_applications_service.py
# Service for managing new loan applications in new_applications.db
# Functions:
# - save_application(data): saves new application to new_applications.db
# - get_application_count(): returns count of pending applications
# - merge_applications_to_bank(bank_id): merges new_applications into bank_a.db
# - clear_applications(): deletes new_applications.db after merge

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import logging
import os

from app.config import settings

logger = logging.getLogger(__name__)

class NewApplicationsService:
    """Service for managing new loan applications."""

    def __init__(self, data_path: str = None):
        self.data_path = Path(data_path or settings.DATA_DIR)
        self.db_path = Path(settings.NEW_APPLICATIONS_DB)

    def _ensure_database_exists(self):
        """Create new_applications.db if it doesn't exist."""
        if not self.db_path.exists():
            logger.info(f"Creating new_applications.db at {self.db_path}")
            conn = sqlite3.connect(str(self.db_path))

            # Create customers table with same schema as bank databases
            conn.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    password TEXT DEFAULT 'default_password',
                    age INTEGER,
                    gender TEXT,
                    marital_status TEXT,
                    education TEXT,
                    dependents INTEGER,
                    home_ownership TEXT,
                    region TEXT,
                    monthly_income REAL,
                    annual_income REAL,
                    job_type TEXT,
                    job_tenure_years REAL,
                    net_monthly_income REAL,
                    monthly_debt_payments REAL,
                    dti REAL,
                    total_dti REAL,
                    savings_balance REAL,
                    checking_balance REAL,
                    total_assets REAL,
                    total_liabilities REAL,
                    net_worth REAL,
                    loan_amount REAL,
                    loan_duration_months INTEGER,
                    loan_purpose TEXT,
                    base_interest_rate REAL,
                    interest_rate REAL,
                    monthly_loan_payment REAL,
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
                    utility_bill_score INTEGER,
                    upi_txn_count_avg REAL,
                    upi_txn_count_std REAL,
                    upi_total_spend_month_avg REAL,
                    upi_merchant_diversity REAL,
                    upi_spend_volatility REAL,
                    upi_failed_txn_rate REAL,
                    upi_essentials_share REAL,
                    default_flag INTEGER DEFAULT 0,
                    credit_score REAL,
                    alt_score REAL,
                    name TEXT DEFAULT NULL,
                    loan_status TEXT DEFAULT 'pending',
                    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approval_date TIMESTAMP DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
            logger.info("new_applications.db created successfully")

    def save_application(self, application_data: Dict) -> bool:
        """
        Save a new loan application to new_applications.db.
        Returns True if successful.
        """
        try:
            self._ensure_database_exists()

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Prepare data - ensure all required fields are present
            data = {
                'customer_id': application_data['customer_id'],
                'password': 'default_password',
                'age': application_data.get('age'),
                'gender': application_data.get('gender'),
                'marital_status': application_data.get('marital_status'),
                'education': application_data.get('education'),
                'dependents': application_data.get('dependents'),
                'home_ownership': application_data.get('home_ownership'),
                'region': application_data.get('region'),
                'monthly_income': application_data.get('monthly_income'),
                'annual_income': application_data.get('annual_income'),
                'job_type': application_data.get('job_type'),
                'job_tenure_years': application_data.get('job_tenure_years'),
                'net_monthly_income': application_data.get('net_monthly_income'),
                'monthly_debt_payments': application_data.get('monthly_debt_payments'),
                'dti': application_data.get('dti'),
                'total_dti': application_data.get('total_dti'),
                'savings_balance': application_data.get('savings_balance'),
                'checking_balance': application_data.get('checking_balance'),
                'total_assets': application_data.get('total_assets'),
                'total_liabilities': application_data.get('total_liabilities'),
                'net_worth': application_data.get('net_worth'),
                'loan_amount': application_data.get('loan_amount'),
                'loan_duration_months': application_data.get('loan_duration_months'),
                'loan_purpose': application_data.get('loan_purpose'),
                'base_interest_rate': application_data.get('base_interest_rate'),
                'interest_rate': application_data.get('interest_rate'),
                'monthly_loan_payment': application_data.get('monthly_loan_payment'),
                'tot_enq': application_data.get('tot_enq'),
                'enq_L3m': application_data.get('enq_L3m'),
                'enq_L6m': application_data.get('enq_L6m'),
                'enq_L12m': application_data.get('enq_L12m'),
                'time_since_recent_enq': application_data.get('time_since_recent_enq'),
                'num_30dpd': application_data.get('num_30dpd'),
                'num_60dpd': application_data.get('num_60dpd'),
                'max_delinquency_level': application_data.get('max_delinquency_level'),
                'CC_utilization': application_data.get('CC_utilization'),
                'PL_utilization': application_data.get('PL_utilization'),
                'HL_flag': application_data.get('HL_flag'),
                'GL_flag': application_data.get('GL_flag'),
                'utility_bill_score': application_data.get('utility_bill_score'),
                'upi_txn_count_avg': application_data.get('upi_txn_count_avg'),
                'upi_txn_count_std': application_data.get('upi_txn_count_std'),
                'upi_total_spend_month_avg': application_data.get('upi_total_spend_month_avg'),
                'upi_merchant_diversity': application_data.get('upi_merchant_diversity'),
                'upi_spend_volatility': application_data.get('upi_spend_volatility'),
                'upi_failed_txn_rate': application_data.get('upi_failed_txn_rate'),
                'upi_essentials_share': application_data.get('upi_essentials_share'),
                'default_flag': 0,  # Unknown for new applications
                'credit_score': application_data.get('credit_score'),
                'alt_score': application_data.get('alt_score'),
                'name': application_data.get('name'),
                'loan_status': 'pending',
                'application_date': application_data.get('application_date', 'CURRENT_TIMESTAMP')
            }

            # Build INSERT query
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT OR REPLACE INTO customers ({columns}) VALUES ({placeholders})"

            cursor.execute(query, list(data.values()))
            conn.commit()
            conn.close()

            logger.info(f"Application {data['customer_id']} saved to new_applications.db")
            return True

        except Exception as e:
            logger.error(f"Error saving application: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_application_count(self) -> int:
        """Get the count of pending applications in new_applications.db."""
        if not self.db_path.exists():
            return 0

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting application count: {e}")
            return 0

    def merge_applications_to_bank(self, bank_id: str = "bank_a") -> int:
        """
        Merge all applications from new_applications.db into bank database.
        For existing customers, updates their record. For new customers, inserts.
        Returns the number of applications merged.
        """
        if not self.db_path.exists():
            logger.info("No new_applications.db found, nothing to merge")
            return 0

        try:
            bank_db_path = self.data_path / f"{bank_id}.db"

            if not bank_db_path.exists():
                logger.error(f"Bank database {bank_db_path} not found")
                return 0

            # Read all applications
            new_apps_conn = sqlite3.connect(str(self.db_path))
            df_new = pd.read_sql_query("SELECT * FROM customers", new_apps_conn)
            new_apps_conn.close()

            if len(df_new) == 0:
                logger.info("No applications to merge")
                return 0

            # Connect to bank database
            bank_conn = sqlite3.connect(str(bank_db_path))
            cursor = bank_conn.cursor()

            # Check which customers already exist
            existing_ids = pd.read_sql_query(
                "SELECT customer_id FROM customers",
                bank_conn
            )['customer_id'].tolist()

            new_customers = df_new[~df_new['customer_id'].isin(existing_ids)]
            existing_customers = df_new[df_new['customer_id'].isin(existing_ids)]

            # Insert new customers
            if len(new_customers) > 0:
                new_customers.to_sql('customers', bank_conn, if_exists='append', index=False)
                logger.info(f"Inserted {len(new_customers)} new customers")

            # Update existing customers - add new loan to existing debts
            for _, row in existing_customers.iterrows():
                # Get current monthly_debt_payments from bank
                cursor.execute(
                    "SELECT monthly_debt_payments FROM customers WHERE customer_id = ?",
                    (row['customer_id'],)
                )
                result = cursor.fetchone()
                current_debt = result[0] if result and result[0] else 0

                # Add new monthly loan payment to existing debt
                new_monthly_loan_payment = row['loan_amount'] / row['loan_duration_months']
                updated_debt = current_debt + new_monthly_loan_payment

                cursor.execute("""
                    UPDATE customers SET
                        loan_amount = loan_amount + ?,
                        loan_duration_months = ?,
                        loan_purpose = ?,
                        monthly_loan_payment = ?,
                        alt_score = ?,
                        credit_score = ?,
                        loan_status = ?,
                        application_date = ?,
                        approval_date = ?,
                        monthly_debt_payments = ?,
                        tot_enq = ?
                    WHERE customer_id = ?
                """, (
                    row['loan_amount'],  # Add to existing loan amount
                    row['loan_duration_months'],
                    row['loan_purpose'],
                    new_monthly_loan_payment,
                    row['alt_score'],
                    row['credit_score'],
                    row['loan_status'],
                    row['application_date'],
                    row.get('approval_date'),
                    updated_debt,  # Current debt + new monthly payment
                    row['tot_enq'],
                    row['customer_id']
                ))

            if len(existing_customers) > 0:
                logger.info(f"Updated {len(existing_customers)} existing customers")

            bank_conn.commit()
            bank_conn.close()

            logger.info(f"Merged {len(df_new)} applications from new_applications.db to {bank_id}.db")
            return len(df_new)

        except Exception as e:
            logger.error(f"Error merging applications: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def approve_application(self, customer_id: str) -> bool:
        """
        Approve a pending application by updating loan_status to 'approved'.
        Sets approval_date to current timestamp.
        """
        if not self.db_path.exists():
            logger.error("new_applications.db not found")
            return False

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE customers
                SET loan_status = 'approved', approval_date = CURRENT_TIMESTAMP
                WHERE customer_id = ?
            """, (customer_id,))

            conn.commit()
            affected = cursor.rowcount
            conn.close()

            if affected > 0:
                logger.info(f"Application {customer_id} approved")
                return True
            else:
                logger.warning(f"Application {customer_id} not found")
                return False

        except Exception as e:
            logger.error(f"Error approving application: {e}")
            return False

    def reject_application(self, customer_id: str) -> bool:
        """
        Reject a pending application by updating loan_status to 'rejected'.
        """
        if not self.db_path.exists():
            logger.error("new_applications.db not found")
            return False

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE customers
                SET loan_status = 'rejected'
                WHERE customer_id = ?
            """, (customer_id,))

            conn.commit()
            affected = cursor.rowcount
            conn.close()

            if affected > 0:
                logger.info(f"Application {customer_id} rejected")
                return True
            else:
                logger.warning(f"Application {customer_id} not found")
                return False

        except Exception as e:
            logger.error(f"Error rejecting application: {e}")
            return False

    def clear_applications(self) -> bool:
        """Delete new_applications.db after merging."""
        try:
            if self.db_path.exists():
                os.remove(self.db_path)
                logger.info("new_applications.db deleted successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting new_applications.db: {e}")
            return False


# Global instance
_new_applications_service = None


def get_new_applications_service() -> NewApplicationsService:
    """Get singleton instance of NewApplicationsService."""
    global _new_applications_service
    if _new_applications_service is None:
        _new_applications_service = NewApplicationsService()
    return _new_applications_service
