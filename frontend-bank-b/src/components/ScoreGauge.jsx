// ScoreGauge.jsx
// Visual component to display the Alternative Credit Score (e.g., 300-900).
// Accepts props: score, riskBand, maybe size.
// Renders a simple gauge or radial progress using Tailwind/HTML.
// Used in ClientDashboard and StaffCustomerDetail.

import React from 'react';

const ScoreGauge = ({ score, maxScore = 900 }) => {
  const percentage = (score / maxScore) * 100;
  
  const getColor = () => {
    if (score >= 700) return 'text-green-600';
    if (score >= 600) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-48">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="96"
            cy="96"
            r="80"
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            className="text-gray-200"
          />
          <circle
            cx="96"
            cy="96"
            r="80"
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            strokeDasharray={`${percentage * 5.024} 502.4`}
            className={getColor()}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-bold ${getColor()}`}>{score}</span>
          <span className="text-sm text-gray-600">/ {maxScore}</span>
        </div>
      </div>
    </div>
  );
};

export default ScoreGauge;
