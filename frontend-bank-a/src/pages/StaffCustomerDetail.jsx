// StaffCustomerDetail.jsx
// Detailed view of a single borrower for bank staff.
// Shows profile section, loan info, behavioural and UPI aggregates in cards.
// Includes latest score + history snippet (reuses ScoreGauge + ChartPlaceholder).
// Optionally allows editing of non-sensitive fields (via /staff/customers/{id} PATCH).
// Provides a button to re-score this customer using current local model.

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

const StaffCustomerDetail = () => {
  const { customerId } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomer();
  }, [customerId]);

  const fetchCustomer = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/staff/customers/${customerId}`);
      const data = await response.json();
      setCustomer(data.customer);
    } catch (error) {
      console.error('Failed to fetch customer:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskBand = (defaultFlag) => {
    return defaultFlag === 0 ? 'Low' : 'High';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="card p-8 text-center">
            <p className="text-gray-500">Loading customer details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="card p-8 text-center">
            <p className="text-red-600">Customer not found</p>
            <button onClick={() => navigate('/staff/customers')} className="btn btn-secondary mt-4">
              Back to Customer List
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Customer Details</h1>
          <button onClick={() => navigate('/staff/customers')} className="btn btn-secondary">
            ← Back to List
          </button>
        </div>
        
        <div className="grid gap-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Risk Assessment</h2>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Customer ID: {customer.customer_id}</p>
              <p className={`text-lg font-semibold ${
                getRiskBand(customer.default_flag) === 'Low' ? 'text-green-600' : 'text-red-600'
              }`}>
                Risk Band: {getRiskBand(customer.default_flag)}
              </p>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Personal Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Age</p>
                <p className="font-medium">{customer.age}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Gender</p>
                <p className="font-medium">{customer.gender}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Region</p>
                <p className="font-medium">{customer.region}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Education</p>
                <p className="font-medium">{customer.education}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Marital Status</p>
                <p className="font-medium">{customer.marital_status}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Dependents</p>
                <p className="font-medium">{customer.dependents}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Home Ownership</p>
                <p className="font-medium">{customer.home_ownership}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Job Type</p>
                <p className="font-medium">{customer.job_type}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Financial Metrics</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Monthly Income</p>
                <p className="font-medium">₹{customer.monthly_income?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Annual Income</p>
                <p className="font-medium">₹{customer.annual_income?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">DTI Ratio</p>
                <p className="font-medium">{customer.dti?.toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total DTI</p>
                <p className="font-medium">{customer.total_dti?.toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Savings Balance</p>
                <p className="font-medium">₹{customer.savings_balance?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Checking Balance</p>
                <p className="font-medium">₹{customer.checking_balance?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Net Worth</p>
                <p className="font-medium">₹{customer.net_worth?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">CC Utilization</p>
                <p className="font-medium">{customer.CC_utilization?.toFixed(2)}%</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Loan Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Loan Amount</p>
                <p className="font-medium">₹{customer.loan_amount?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Loan Duration</p>
                <p className="font-medium">{customer.loan_duration_months} months</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Loan Purpose</p>
                <p className="font-medium">{customer.loan_purpose}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Interest Rate</p>
                <p className="font-medium">{customer.interest_rate?.toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Monthly Payment</p>
                <p className="font-medium">₹{customer.monthly_loan_payment?.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Credit History</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Enquiries</p>
                <p className="font-medium">{customer.tot_enq}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Enquiries (Last 3 months)</p>
                <p className="font-medium">{customer.enq_L3m}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">30 DPD Count</p>
                <p className="font-medium">{customer.num_30dpd}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">60 DPD Count</p>
                <p className="font-medium">{customer.num_60dpd}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Max Delinquency</p>
                <p className="font-medium">{customer.max_delinquency_level}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Utility Bill Score</p>
                <p className="font-medium">{customer.utility_bill_score}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">UPI Activity</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Avg Transaction Count</p>
                <p className="font-medium">{customer.upi_txn_count_avg?.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Avg Monthly Spend</p>
                <p className="font-medium">₹{customer.upi_total_spend_month_avg?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Merchant Diversity</p>
                <p className="font-medium">{customer.upi_merchant_diversity?.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Failed Transaction Rate</p>
                <p className="font-medium">{customer.upi_failed_txn_rate?.toFixed(2)}%</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StaffCustomerDetail;
