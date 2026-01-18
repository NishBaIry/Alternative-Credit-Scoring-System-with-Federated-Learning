// StaffDashboard.jsx
// Overview page for bank staff after login.
// Shows high-level metrics: number of customers, FL status, model info.
// Provides navigation cards to CustomerList, ScoreApplication, and ModelTraining.
// This is the entry point to the "bank console" experience.

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const StaffDashboard = () => {
  const [metrics, setMetrics] = useState({
    totalCustomers: '...',
    applicationsToday: '...',
    currentRound: '...',
    modelStatus: 'Loading...'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardMetrics();
  }, []);

  const fetchDashboardMetrics = async () => {
    try {
      // Fetch FL status
      const flResponse = await fetch(`${API_BASE_URL}/api/fl/fl-status`);
      const flData = await flResponse.ok ? await flResponse.json() : null;

      // Fetch local model info
      const modelResponse = await fetch(`${API_BASE_URL}/api/fl/local-model-info`);
      const modelData = await modelResponse.ok ? await modelResponse.json() : null;

      setMetrics({
        totalCustomers: 'N/A', // Would need customer count API
        applicationsToday: 'N/A', // Would need applications API
        currentRound: flData?.current_round ?? 0,
        modelStatus: modelData?.active_model ? 
          `Active (${modelData.active_model.size_mb.toFixed(1)} MB)` : 
          'No Model'
      });
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard metrics:', error);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Bank Staff Dashboard</h1>
          <button 
            onClick={fetchDashboardMetrics}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Refresh
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <h3 className="text-sm font-medium text-gray-600">Total Customers</h3>
            <p className="text-3xl font-bold mt-2">{metrics.totalCustomers}</p>
          </div>
          
          <div className="card">
            <h3 className="text-sm font-medium text-gray-600">Applications Today</h3>
            <p className="text-3xl font-bold mt-2">{metrics.applicationsToday}</p>
          </div>
          
          <div className="card">
            <h3 className="text-sm font-medium text-gray-600">Active Model</h3>
            <p className="text-lg font-bold mt-2">{metrics.modelStatus}</p>
          </div>
          
          <div className="card">
            <h3 className="text-sm font-medium text-gray-600">FL Round</h3>
            <p className="text-3xl font-bold mt-2">{metrics.currentRound}</p>
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
