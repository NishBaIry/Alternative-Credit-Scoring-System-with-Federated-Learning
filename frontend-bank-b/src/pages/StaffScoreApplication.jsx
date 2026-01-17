// StaffScoreApplication.jsx
// Form to score a NEW loan application (e.g., from offline KYC).
// Staff enters key fields (income, loan amount, DTI proxies, UPI summary if known).
// On submit, calls /staff/applications/score and displays score + decision band.
// Optionally offers "Save as new customer" to push into dataset via backend.
// Helps demonstrate real-world use: instant scoring using the alternative model.

import React, { useState } from 'react';

const StaffScoreApplication = () => {
  const [formData, setFormData] = useState({
    customerId: '',
    age: '',
    monthlyIncome: '',
    loanAmount: '',
    dti: '',
  });

  const [result, setResult] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Call API to score application
    setResult({
      score: 742,
      riskBand: 'Approve',
      topDrivers: [
        'High bill on-time rate',
        'Strong UPI essentials share',
        'Low DTI ratio',
      ],
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Score New Application</h1>
        
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
                <label className="block text-sm font-medium mb-2">Monthly Income</label>
                <input
                  type="number"
                  value={formData.monthlyIncome}
                  onChange={(e) => setFormData({ ...formData, monthlyIncome: e.target.value })}
                  className="input-field"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Loan Amount</label>
                <input
                  type="number"
                  value={formData.loanAmount}
                  onChange={(e) => setFormData({ ...formData, loanAmount: e.target.value })}
                  className="input-field"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">DTI Ratio (%)</label>
                <input
                  type="number"
                  value={formData.dti}
                  onChange={(e) => setFormData({ ...formData, dti: e.target.value })}
                  className="input-field"
                  required
                />
              </div>
            </div>
            
            <button type="submit" className="btn-primary">
              Score Application
            </button>
          </form>
        </div>

        {result && (
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Scoring Result</h2>
            <div className="space-y-4">
              <div className="text-center">
                <p className="text-5xl font-bold text-primary-600">{result.score}</p>
                <p className="text-lg mt-2">
                  Risk Band: <span className="font-semibold text-green-600">{result.riskBand}</span>
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Top Drivers:</h3>
                <ul className="space-y-1">
                  {result.topDrivers.map((driver, index) => (
                    <li key={index} className="text-gray-700">• {driver}</li>
                  ))}
                </ul>
              </div>
              
              <button className="btn-secondary">
                Save to Dataset
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StaffScoreApplication;
