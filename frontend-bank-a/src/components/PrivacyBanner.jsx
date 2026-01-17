// PrivacyBanner.jsx
// Informational banner explaining privacy-preserving federated learning.
// Displays message about data never leaving the bank.
// Used in login pages and dashboards to emphasize privacy benefits.

import React from 'react';

const PrivacyBanner = () => {
  return (
    <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <span className="text-2xl">🔒</span>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-blue-800">Your Privacy is Protected</h3>
          <p className="text-sm text-blue-700 mt-1">
            Your data never leaves your bank. Only anonymized model updates are shared through 
            federated learning, ensuring your financial information remains private and secure.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PrivacyBanner;
