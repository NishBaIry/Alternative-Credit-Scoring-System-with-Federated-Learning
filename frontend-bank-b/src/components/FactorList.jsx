// FactorList.jsx
// Component to display score factors with positive/negative/neutral indicators.
// Used in ClientScoreDetails and StaffCustomerDetail.
// Shows visual icons and descriptions for each factor.

import React from 'react';

const FactorList = ({ factors }) => {
  const getIcon = (impact) => {
    if (impact === 'positive') return '✓';
    if (impact === 'negative') return '✗';
    return '⚠';
  };

  const getColor = (impact) => {
    if (impact === 'positive') return 'text-green-600';
    if (impact === 'negative') return 'text-red-600';
    return 'text-yellow-600';
  };

  return (
    <div className="space-y-3">
      {factors.map((factor, index) => (
        <div key={index} className="flex items-start">
          <span className={`${getColor(factor.impact)} mr-3 text-xl`}>
            {getIcon(factor.impact)}
          </span>
          <div className="flex-1">
            <p className="font-medium">{factor.title}</p>
            {factor.description && (
              <p className="text-sm text-gray-600">{factor.description}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default FactorList;
