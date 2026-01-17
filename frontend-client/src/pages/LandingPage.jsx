// LandingPage.jsx
// Public landing screen explaining the alternative credit score product.
// Shows key benefits: privacy-preserving FL, inclusion for thin-file borrowers.
// Client portal - direct to bank selection after landing page
// Tailwind-based responsive layout for hackathon demo.

import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto text-center px-6">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Alternative Credit Scoring Platform
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Privacy-preserving credit scoring using alternative data and federated learning
        </p>
        <p className="text-lg text-gray-500 mb-12">
          Access credit even without traditional credit history. We use UPI transactions, 
          utility bills, and behavioral data to calculate your score.
        </p>
        <Link 
          to="/client/bank-select"
          className="btn-primary text-lg px-8 py-3 inline-block"
        >
          Check Your Credit Score
        </Link>
      </div>
    </div>
  );
};

export default LandingPage;
