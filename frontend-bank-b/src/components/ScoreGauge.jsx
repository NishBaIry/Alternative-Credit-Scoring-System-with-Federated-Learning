// ScoreGauge.jsx
// Visual component to display the Alternative Credit Score (300-900).
// Color gradient: 300-550 (Red), 551-700 (Yellow/Amber), 701-900 (Green).
// Renders a radial gauge with the score prominently displayed.
// Used in StaffCustomerDetail to show risk implicitly through color.

import React from 'react';

const ScoreGauge = ({ score, minScore = 300, maxScore = 900 }) => {
  // Handle invalid or missing scores
  const displayScore = score == null || isNaN(score) ? 'NA' : Math.round(score);
  const numericScore = score == null || isNaN(score) ? minScore : score;

  // Calculate percentage for gauge (0-100)
  const percentage = ((numericScore - minScore) / (maxScore - minScore)) * 100;
  const clampedPercentage = Math.max(0, Math.min(100, percentage));

  // Determine color based on score ranges
  const getColor = () => {
    if (numericScore >= 701) return '#10b981'; // Green (Tailwind green-500)
    if (numericScore >= 551) return '#f59e0b'; // Amber (Tailwind amber-500)
    return '#ef4444'; // Red (Tailwind red-500)
  };

  const color = getColor();

  // Calculate stroke dasharray for the progress arc
  const circumference = 2 * Math.PI * 80; // r=80
  const strokeDashoffset = circumference - (clampedPercentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-4">
      <h3 className="text-lg font-semibold text-gray-700">Alternative Credit Score</h3>
      <div className="relative w-56 h-56">
        <svg className="w-full h-full transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="112"
            cy="112"
            r="80"
            stroke="#e5e7eb"
            strokeWidth="16"
            fill="none"
          />
          {/* Progress circle */}
          <circle
            cx="112"
            cy="112"
            r="80"
            stroke={color}
            strokeWidth="16"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.5s ease-in-out' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-5xl font-bold"
            style={{ color }}
          >
            {displayScore}
          </span>
          {displayScore !== 'NA' && (
            <span className="text-sm text-gray-500 mt-1">
              {minScore}–{maxScore}
            </span>
          )}
        </div>
      </div>
      {/* Risk level indicator (subtle) */}
      {displayScore !== 'NA' && (
        <div className="flex gap-2 items-center">
          <div className="h-3 w-16 bg-red-500 rounded-l" />
          <div className="h-3 w-16 bg-amber-500" />
          <div className="h-3 w-16 bg-green-500 rounded-r" />
        </div>
      )}
    </div>
  );
};

export default ScoreGauge;
