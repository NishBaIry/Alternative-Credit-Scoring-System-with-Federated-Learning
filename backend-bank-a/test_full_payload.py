#!/usr/bin/env python3
"""Test with exact frontend payload"""

import sys
sys.path.insert(0, '.')

from app.services.nn_scoring_service import get_scoring_service

# Exact data from frontend with all defaults
application_data = {
    "customer_id": "00035001",
    "name": "Test User",
    "age": 35,
    "gender": "M",
    "marital_status": "Married",
    "monthly_income": 50000,
    "annual_income": 600000,
    "loan_amount": 500000,
    "loan_duration_months": 12,
    "loan_purpose": "Personal",
    "dti": 0.30,  # 30% converted to 0.30
    "tot_enq": 2,
    "education": "GRADUATE",
    "dependents": 0,
    "home_ownership": "Rented",
    "region": "Urban",
    "job_type": "Salaried",
    "job_tenure_years": 3,
    "net_monthly_income": 50000,
    "monthly_debt_payments": 15000,
    "total_dti": 0.30,
    "savings_balance": 10000,
    "checking_balance": 5000,
    "total_assets": 15000,
    "total_liabilities": 500000,
    "net_worth": -485000,
    "base_interest_rate": 8.5,
    "interest_rate": 10.0,
    "monthly_loan_payment": 500,
    "enq_L3m": 2,
    "enq_L6m": 2,
    "enq_L12m": 2,
    "time_since_recent_enq": 30,
    "num_30dpd": 0,
    "num_60dpd": 0,
    "max_delinquency_level": 0,
    "CC_utilization": 0.3,
    "PL_utilization": 0.2,
    "HL_flag": 0,
    "GL_flag": 0,
    "utility_bill_score": 700,
    "upi_txn_count_avg": 20,
    "upi_txn_count_std": 5,
    "upi_total_spend_month_avg": 30000,
    "upi_merchant_diversity": 10,
    "upi_spend_volatility": 0.2,
    "upi_failed_txn_rate": 0.02,
    "upi_essentials_share": 0.4
}

print("Testing with complete payload...")
print()

try:
    scoring_service = get_scoring_service()
    alt_score, risk_band, p_default = scoring_service.predict_score(application_data)

    print(f"✅ Score: {alt_score}")
    print(f"   Risk Band: {risk_band}")
    print(f"   Default Probability: {p_default:.4f}")
    print(f"   Recommendation: {'Approve' if alt_score >= 650 else 'Review' if alt_score >= 500 else 'Decline'}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
