# db.py
# Database connection and session management using SQLite.
# Each bank has its own SQLite database (bank_a.db, bank_b.db).
# Provides connection pooling and thread-safe database access.
# Functions: get_db_connection(), load_customer_data(bank_id), get_customer(bank_id, customer_id).
# All operations use SQLite as the authoritative data store.

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manager for database operations using SQLite."""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.connections = {}
    
    def get_db_path(self, bank_id: str) -> Path:
        """Get the database path for a specific bank."""
        db_file = f"{bank_id}.db"
        return self.data_path / db_file
    
    @contextmanager
    def get_connection(self, bank_id: str):
        """Get a database connection for a specific bank (context manager)."""
        db_path = self.get_db_path(bank_id)
        
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        try:
            yield conn
        finally:
            conn.close()
    
    def load_customers(self, bank_id: str) -> pd.DataFrame:
        """Load all customer data for a specific bank as DataFrame."""
        with self.get_connection(bank_id) as conn:
            df = pd.read_sql_query("SELECT * FROM customers", conn)
            return df
    
    def get_customer(self, bank_id: str, customer_id: str) -> Optional[Dict]:
        """Get a specific customer by ID."""
        with self.get_connection(bank_id) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def update_customer(self, bank_id: str, customer_id: str, updates: Dict) -> bool:
        """Update specific fields for a customer."""
        if not updates:
            return False
        
        # Build UPDATE query
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [customer_id]
        
        query = f"UPDATE customers SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE customer_id = ?"
        
        try:
            with self.get_connection(bank_id) as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating customer {customer_id}: {e}")
            return False
    
    def authenticate_customer(self, bank_id: str, customer_id: str, password_hash: str) -> Optional[Dict]:
        """Authenticate a customer by checking password hash."""
        with self.get_connection(bank_id) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM customers WHERE customer_id = ? AND password = ?",
                (customer_id, password_hash)
            )
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_customers_paginated(
        self, 
        bank_id: str, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict] = None
    ) -> tuple[List[Dict], int]:
        """Get paginated list of customers with optional filters."""
        query = "SELECT * FROM customers"
        count_query = "SELECT COUNT(*) as total FROM customers"
        params = []
        
        if filters:
            where_clauses = []
            if 'min_score' in filters:
                where_clauses.append("credit_score >= ?")
                params.append(filters['min_score'])
            if 'max_score' in filters:
                where_clauses.append("credit_score <= ?")
                params.append(filters['max_score'])
            if 'default_flag' in filters:
                where_clauses.append("default_flag = ?")
                params.append(filters['default_flag'])
            
            if where_clauses:
                where_clause = " WHERE " + " AND ".join(where_clauses)
                query += where_clause
                count_query += where_clause
        
        query += f" LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        with self.get_connection(bank_id) as conn:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute(count_query, params[:-2] if filters else [])
            total = cursor.fetchone()[0]
            
            # Get paginated results
            cursor.execute(query, params)
            rows = cursor.fetchall()
            customers = [dict(row) for row in rows]
            
            return customers, total

# Global database manager instance
db_manager = DatabaseManager()
