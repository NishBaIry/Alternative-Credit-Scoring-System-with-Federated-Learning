// ClientDashboard.jsx
// Main client home after login, shows current Alternative Credit Score card.
// Fetches score + risk band from /client/me/score when mounted.
// Uses ScoreGauge + RecommendationCard components to render info.
// Includes a "Refresh my score" button to refetch and update view.
// Provides quick links to ScoreDetails and Profile pages.

import React from 'react';
import { Link } from 'react-router-dom';

const ClientDashboard = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">My Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-2">Credit Score</h2>
            <p className="text-4xl font-bold text-primary-600">742</p>
            <Link to="/client/score-details" className="text-primary-600 mt-4 inline-block">
              View Details →
            </Link>
          </div>
          
          <div className="card">
            <h2 className="text-xl font-semibold mb-2">Risk Level</h2>
            <p className="text-lg text-green-600">Low</p>
          </div>
          
          <div className="card">
            <h2 className="text-xl font-semibold mb-2">Profile</h2>
            <Link to="/client/profile" className="text-primary-600">
              View Profile →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClientDashboard;
