// StaffAnalytics.jsx
// Monitoring and explainability page for risk team.
// Charts for feature importance, distribution of key features by label, approval rates.
// Data from /staff/model/analytics (backend precomputes summaries).
// Use ChartPlaceholder components now; can hook real charts later.
// Optional fairness view: approval by gender/region/income type if time permits.

import React from 'react';

const StaffAnalytics = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Analytics & Monitoring</h1>
        
        <div className="grid gap-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Feature Importance</h2>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-1">
                  <span>DTI Ratio</span>
                  <span className="font-semibold">0.25</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-600 h-2 rounded-full" style={{ width: '25%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span>UPI Transaction Rate</span>
                  <span className="font-semibold">0.20</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-600 h-2 rounded-full" style={{ width: '20%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span>Bill On-Time Rate</span>
                  <span className="font-semibold">0.18</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-600 h-2 rounded-full" style={{ width: '18%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span>Monthly Income</span>
                  <span className="font-semibold">0.15</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-600 h-2 rounded-full" style={{ width: '15%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Approval Rates by Segment</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded">
                <p className="text-sm text-gray-600">Salaried</p>
                <p className="text-3xl font-bold text-green-600">78%</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded">
                <p className="text-sm text-gray-600">Self-Employed</p>
                <p className="text-3xl font-bold text-yellow-600">65%</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded">
                <p className="text-sm text-gray-600">Gig Worker</p>
                <p className="text-3xl font-bold text-orange-600">58%</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Model Performance Trends</h2>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
              <p className="text-gray-500">[Chart Placeholder - Model AUC over time]</p>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Distribution: DTI Ratio (Good vs Bad)</h2>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
              <p className="text-gray-500">[Chart Placeholder - Distribution plot]</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StaffAnalytics;
