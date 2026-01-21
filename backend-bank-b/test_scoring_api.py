#!/usr/bin/env python3
"""Test script to reproduce scoring issue"""

import sys
sys.path.insert(0, '.')

from app.services.nn_scoring_service import get_scoring_service

# Exact data from frontend
application_data = {
    "customer_id": "00035001",
    "name": "Test User",
    "age": 35,
    "gender": "M",
    "marital_status": "Married",
    "education": "GRADUATE",
    "monthly_income": 50000,
    "loan_amount": 500000,
    "loan_duration_months": 12,
    "loan_purpose": "Personal",
    "dti": 30
}

print("Testing scoring service with application data...")
print(f"Input: {application_data}")
print()

try:
    scoring_service = get_scoring_service()
    alt_score, risk_band, p_default = scoring_service.predict_score(application_data)

    print(f"✅ SUCCESS:")
    print(f"  Score: {alt_score}")
    print(f"  Risk Band: {risk_band}")
    print(f"  Default Probability: {p_default:.4f}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
