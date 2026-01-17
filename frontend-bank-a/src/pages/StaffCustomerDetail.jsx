// StaffCustomerDetail.jsx
// Detailed view of a single borrower for bank staff.
// Shows profile section, loan info, behavioural and UPI aggregates in cards.
// Includes latest score + history snippet (reuses ScoreGauge + ChartPlaceholder).
// Optionally allows editing of non-sensitive fields (via /staff/customers/{id} PATCH).
// Provides a button to re-score this customer using current local model.

import React from 'react';
import { useParams } from 'react-router-dom';

const StaffCustomerDetail = () => {
  const { customerId } = useParams();

  // Mock data
  const customer = {
    id: customerId,
    name: 'John Doe',
    score: 742,
    riskBand: 'Low',
    age: 28,
    region: 'Mumbai',
    income: 50000,
    dti: 35,
    loanAmount: 200000,
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Customer Details - {customerId}</h1>
        
        <div className="grid gap-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Credit Score</h2>
            <div className="text-center">
              <p className="text-5xl font-bold text-primary-600">{customer.score}</p>
              <p className="text-lg mt-2">Risk Band: <span className="font-semibold text-green-600">{customer.riskBand}</span></p>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Personal Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Name</p>
                <p className="font-medium">{customer.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Age</p>
                <p className="font-medium">{customer.age}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Region</p>
                <p className="font-medium">{customer.region}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Monthly Income</p>
                <p className="font-medium">₹{customer.income.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Financial Metrics</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">DTI Ratio</p>
                <p className="font-medium">{customer.dti}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Loan Amount</p>
                <p className="font-medium">₹{customer.loanAmount.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Top Score Factors</h2>
            <ul className="space-y-2">
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>High bill on-time rate</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Consistent UPI transaction patterns</span>
              </li>
              <li className="flex items-start">
                <span className="text-yellow-600 mr-2">⚠</span>
                <span>Moderate DTI ratio</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StaffCustomerDetail;
