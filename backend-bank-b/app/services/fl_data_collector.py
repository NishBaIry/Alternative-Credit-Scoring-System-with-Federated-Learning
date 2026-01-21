"""
FL Data Collector Service
Appends newly scored applications to fl_dataset.csv for next FL training round
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Paths
CUSTOMERS_CSV = 'data/customers.csv'
FL_DATASET_CSV = 'data/fl_dataset.csv'

def append_to_fl_dataset(application_data: dict):
    """
    Append a newly scored application to fl_dataset.csv
    
    Args:
        application_data: Dict containing all features and default_flag
    
    Returns:
        bool: Success status
    """
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Convert to DataFrame with single row
        new_row = pd.DataFrame([application_data])
        
        # Check if fl_dataset.csv exists
        if os.path.exists(FL_DATASET_CSV):
            # Read existing dataset
            existing_df = pd.read_csv(FL_DATASET_CSV)
            
            # Ensure columns match
            if set(new_row.columns) != set(existing_df.columns):
                logger.warning("Column mismatch - ensuring column order matches")
                new_row = new_row[existing_df.columns]
            
            # Append new row
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            
        else:
            # Create new fl_dataset.csv with header
            logger.info("Creating new fl_dataset.csv file")
            
            # Get column order from customers.csv if it exists
            if os.path.exists(CUSTOMERS_CSV):
                customers_df = pd.read_csv(CUSTOMERS_CSV, nrows=1)
                new_row = new_row[customers_df.columns]
            
            updated_df = new_row
        
        # Save to fl_dataset.csv
        updated_df.to_csv(FL_DATASET_CSV, index=False)
        
        logger.info(f"✅ Appended new application to fl_dataset.csv (total: {len(updated_df)} rows)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to append to fl_dataset.csv: {e}")
        return False


def get_fl_dataset_stats():
    """Get statistics about the FL dataset"""
    try:
        if not os.path.exists(FL_DATASET_CSV):
            return {
                'exists': False,
                'count': 0,
                'message': 'No new data collected yet'
            }
        
        df = pd.read_csv(FL_DATASET_CSV)
        
        return {
            'exists': True,
            'count': len(df),
            'default_rate': df['default_flag'].mean() if 'default_flag' in df.columns else None,
            'file_size_mb': os.path.getsize(FL_DATASET_CSV) / (1024 * 1024)
        }
    
    except Exception as e:
        logger.error(f"Error getting FL dataset stats: {e}")
        return {'exists': False, 'count': 0, 'error': str(e)}


def merge_fl_dataset_to_customers():
    """
    Merge fl_dataset.csv into customers.csv after successful FL round
    Then clear fl_dataset.csv
    
    This should be called after FL aggregation completes
    """
    try:
        if not os.path.exists(FL_DATASET_CSV):
            logger.info("No fl_dataset.csv to merge")
            return True
        
        fl_df = pd.read_csv(FL_DATASET_CSV)
        
        if len(fl_df) == 0:
            logger.info("fl_dataset.csv is empty, nothing to merge")
            return True
        
        # Merge into customers.csv
        if os.path.exists(CUSTOMERS_CSV):
            customers_df = pd.read_csv(CUSTOMERS_CSV)
            merged_df = pd.concat([customers_df, fl_df], ignore_index=True)
        else:
            merged_df = fl_df
        
        # Save merged data
        merged_df.to_csv(CUSTOMERS_CSV, index=False)
        logger.info(f"✅ Merged {len(fl_df)} rows from fl_dataset.csv into customers.csv")
        
        # Clear fl_dataset.csv (keep header)
        header_df = fl_df.iloc[:0]  # Empty DataFrame with same columns
        header_df.to_csv(FL_DATASET_CSV, index=False)
        logger.info("✅ Cleared fl_dataset.csv")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to merge datasets: {e}")
        return False
