// StaffDashboard.jsx
// Overview page for bank staff after login.
// Shows high-level metrics: number of customers, default rate, last training time.
// Uses MetricCard components and maybe a ChartPlaceholder for trends.
// Provides navigation cards to CustomerList, ScoreApplication, and ModelTraining.
// This is the entry point to the "bank console" experience.

import React from 'react';
import { Link } from 'react-router-dom';

const StaffDashboard = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Bank Staff Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <h3 className="text-sm font-medium text-gray-600">Total Customers</h3>
            <p className="text-3xl font-bold mt-2">1,234</p>
          </div>
          
          <div className="card">
            <h3 className="text-sm font-medium text-gray-600">Applications Today</h3>
            <p className="text-3xl font-bold mt-2">23</p>
          </div>
          
          <div className="card">
            <h3 className="text-sm font-medium text-gray-600">Model Accuracy</h3>
            <p className="text-3xl font-bold mt-2">94.2%</p>
          </div>
          
          <div className="card">
            <h3 className="text-sm font-medium text-gray-600">FL Round</h3>
            <p className="text-3xl font-bold mt-2">12</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link to="/staff/customers" className="card hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-semibold mb-2">Customer Management</h3>
            <p className="text-gray-600">View and manage customer data</p>
          </Link>
          
          <Link to="/staff/score-application" className="card hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-semibold mb-2">Score Application</h3>
            <p className="text-gray-600">Score new loan applications</p>
          </Link>
          
          <Link to="/staff/model-training" className="card hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-semibold mb-2">Model Training</h3>
            <p className="text-gray-600">Train and update models</p>
          </Link>
          
          <Link to="/staff/analytics" className="card hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-semibold mb-2">Analytics</h3>
            <p className="text-gray-600">View performance metrics</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default StaffDashboard;
