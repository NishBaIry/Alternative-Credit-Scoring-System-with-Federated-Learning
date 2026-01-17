// ClientScoreDetails.jsx
// Detailed view explaining why the client's score looks the way it does.
// Calls /client/me/score-details to get top factors + feature contributions.
// Uses FactorList component to show positive/negative drivers (DTI, bills, UPI, etc.).
// Optionally shows a small history chart via ChartPlaceholder.
// Keep copy educational and friendly (AI for social good vibe).

import React from 'react';

const ClientScoreDetails = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Score Details</h1>
        
        <div className="card mb-6">
          <h2 className="text-2xl font-semibold mb-4">Alternative Credit Score</h2>
          <div className="text-center">
            <p className="text-6xl font-bold text-primary-600">742</p>
            <p className="text-gray-600 mt-2">Out of 900</p>
          </div>
        </div>

        <div className="card mb-6">
          <h3 className="text-xl font-semibold mb-4">Why is my score like this?</h3>
          <ul className="space-y-3">
            <li className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              <span>High bill on-time rate is improving your score</span>
            </li>
            <li className="flex items-start">
              <span className="text-red-600 mr-2">⚠</span>
              <span>High expense-to-income ratio is reducing your score</span>
            </li>
          </ul>
        </div>

        <div className="card">
          <h3 className="text-xl font-semibold mb-4">How can I improve?</h3>
          <ul className="space-y-3 text-gray-700">
            <li>• Try to keep DTI below 40%</li>
            <li>• Increase UPI essentials share (Grocery/Fuel)</li>
            <li>• Maintain on-time utility payments</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ClientScoreDetails;
