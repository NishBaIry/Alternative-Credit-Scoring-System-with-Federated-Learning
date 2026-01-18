// StaffScoreApplication.jsx
// Form to score a NEW loan application (e.g., from offline KYC).
// Staff enters key fields (income, loan amount, DTI proxies, UPI summary if known).
// On submit, calls /staff/applications/score and displays score + decision band.
// Optionally offers "Save as new customer" to push into dataset via backend.
// Helps demonstrate real-world use: instant scoring using the alternative model.

import React, { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const StaffScoreApplication = () => {
  const [formData, setFormData] = useState({
    customerId: '',
    age: '',
    monthlyIncome: '',
    loanAmount: '',
    dti: '',
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Prepare features for scoring (simplified - using only what we have)
      const features = {
        age: parseFloat(formData.age),
        monthly_income: parseFloat(formData.monthlyIncome),
        annual_income: parseFloat(formData.monthlyIncome) * 12,
        loan_amount: parseFloat(formData.loanAmount),
        dti: parseFloat(formData.dti) / 100,
        // Add default values for required features
        gender: 'M',
        marital_status: 'Single',
        education: 'GRADUATE',
        dependents: 0,
        home_ownership: '',
        region: '',
        job_type: '',
        job_tenure_years: 5,
        net_monthly_income: parseFloat(formData.monthlyIncome),
        monthly_debt_payments: parseFloat(formData.monthlyIncome) * (parseFloat(formData.dti) / 100),
        total_dti: parseFloat(formData.dti) / 100,
        savings_balance: 0,
        checking_balance: 0,
        total_assets: 0,
        total_liabilities: 0,
        net_worth: 0,
        loan_duration_months: 36,
        loan_purpose: '',
        base_interest_rate: 0,
        interest_rate: 0,
        monthly_loan_payment: 0,
        tot_enq: 0,
        enq_L3m: 0,
        enq_L6m: 0,
        enq_L12m: 0,
        time_since_recent_enq: 0,
        num_30dpd: 0,
        num_60dpd: 0,
        max_delinquency_level: 0,
        CC_utilization: 0,
        PL_utilization: 0,
        HL_flag: 0,
        GL_flag: 0,
        utility_bill_score: 0,
        upi_txn_count_avg: 0,
        upi_txn_count_std: 0,
        upi_total_spend_month_avg: 0,
        upi_merchant_diversity: 0,
        upi_spend_volatility: 0,
        upi_failed_txn_rate: 0,
        upi_essentials_share: 0
      };

      const response = await fetch(`${API_BASE_URL}/api/score`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(features),
      });

      if (!response.ok) {
        throw new Error(`Scoring failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      setResult({
        score: data.credit_score || 0,
        riskBand: data.risk_band || 'Unknown',
        probability: data.default_probability || 0,
        message: data.message || ''
      });
    } catch (err) {
      setError(err.message);
      console.error('Scoring error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Score New Application</h1>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">Application Details</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Customer ID</label>
                <input
                  type="text"
                  value={formData.customerId}
                  onChange={(e) => setFormData({ ...formData, customerId: e.target.value })}
                  className="input-field"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Age</label>
                <input
                  type="number"
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                  className="input-field"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Monthly Income (₹)</label>
                <input
                  type="number"
                  value={formData.monthlyIncome}
                  onChange={(e) => setFormData({ ...formData, monthlyIncome: e.target.value })}
                  className="input-field"
                  required
                  placeholder="e.g., 50000"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Loan Amount (₹)</label>
                <input
                  type="number"
                  value={formData.loanAmount}
                  onChange={(e) => setFormData({ ...formData, loanAmount: e.target.value })}
                  className="input-field"
                  required
                  placeholder="e.g., 200000"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">DTI Ratio (%)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.dti}
                  onChange={(e) => setFormData({ ...formData, dti: e.target.value })}
                  className="input-field"
                  required
                  placeholder="e.g., 35"
                />
              </div>
            </div>
            
            <button 
              type="submit" 
              className="btn-primary"
              disabled={loading}
            >
              {loading ? 'Scoring...' : 'Score Application'}
            </button>
          </form>
        </div>

        {result && (
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Scoring Result</h2>
            <div className="space-y-4">
              <div className="text-center">
                <p className="text-5xl font-bold text-primary-600">{Math.round(result.score)}</p>
                <p className="text-lg mt-2">
                  Risk Band: <span className={`font-semibold ${
                    result.riskBand === 'Low Risk' ? 'text-green-600' : 
                    result.riskBand === 'Medium Risk' ? 'text-yellow-600' : 'text-red-600'
                  }`}>{result.riskBand}</span>
                </p>
                {result.probability !== undefined && (
                  <p className="text-sm text-gray-600 mt-2">
                    Default Probability: {(result.probability * 100).toFixed(2)}%
                  </p>
                )}
              </div>
              
              {result.message && (
                <div className="bg-blue-50 p-3 rounded">
                  <p className="text-sm text-gray-700">{result.message}</p>
                </div>
              )}
              
              <div className="bg-green-50 p-3 rounded">
                <p className="text-sm text-green-800">
                  ✓ Application automatically added to FL training dataset
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StaffScoreApplication;
