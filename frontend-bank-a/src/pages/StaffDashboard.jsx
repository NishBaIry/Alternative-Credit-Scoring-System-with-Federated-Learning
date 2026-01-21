import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  FileText, 
  Activity, 
  Layers, 
  RefreshCw,
  Shield,
  TrendingUp,
  Brain,
  BarChart3
} from 'lucide-react';

import { API_BASE_URL } from '../lib/constants';

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
        totalCustomers: 'N/A',
        applicationsToday: 'N/A',
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

  const metricCards = [
    {
      title: 'Total Customers',
      value: metrics.totalCustomers,
      icon: Users,
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      title: 'Applications Today',
      value: metrics.applicationsToday,
      icon: FileText,
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      title: 'Active Model',
      value: metrics.modelStatus,
      icon: Brain,
      gradient: 'from-green-500 to-emerald-500',
      isText: true
    },
    {
      title: 'FL Round',
      value: metrics.currentRound,
      icon: Layers,
      gradient: 'from-orange-500 to-red-500'
    }
  ];

  const navigationCards = [
    {
      title: 'Manage Accounts',
      description: 'View and manage customer accounts',
      icon: Users,
      href: '/staff/customers',
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      title: 'Apply for a Loan',
      description: 'Process new loan applications',
      icon: FileText,
      href: '/staff/score-application',
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      title: 'Model Training',
      description: 'Train and update models',
      icon: Brain,
      href: '/staff/model-training',
      gradient: 'from-green-500 to-emerald-500'
    },
    {
      title: 'Analytics',
      description: 'View performance metrics',
      icon: BarChart3,
      href: '/staff/analytics',
      gradient: 'from-orange-500 to-red-500'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Bank Staff Dashboard</h1>
                <p className="text-sm text-gray-500">Welcome back to CashFlow</p>
              </div>
            </div>
            <button 
              onClick={fetchDashboardMetrics}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all duration-300 hover:scale-105"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span className="font-medium">Refresh</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metricCards.map((metric, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              className="relative group"
            >
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-lg transition-all duration-300">
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-12 h-12 bg-gradient-to-br ${metric.gradient} rounded-xl flex items-center justify-center shadow-lg`}>
                    <metric.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className={`w-2 h-2 rounded-full bg-gradient-to-br ${metric.gradient} animate-pulse`}></div>
                </div>
                <h3 className="text-sm font-semibold text-gray-600 mb-2">{metric.title}</h3>
                <p className={`${metric.isText ? 'text-xl' : 'text-3xl'} font-bold bg-gradient-to-br ${metric.gradient} bg-clip-text text-transparent`}>
                  {metric.value}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {navigationCards.map((card, index) => (
            <motion.a
              key={index}
              href={card.href}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + index * 0.1, duration: 0.5 }}
              className="group relative bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-xl transition-all duration-300 hover:scale-[1.02] cursor-pointer overflow-hidden"
            >
              {/* Gradient overlay on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
              
              <div className="relative">
                <div className={`w-14 h-14 bg-gradient-to-br ${card.gradient} rounded-xl flex items-center justify-center shadow-lg mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <card.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:bg-gradient-to-r group-hover:from-purple-600 group-hover:to-blue-600 group-hover:bg-clip-text group-hover:text-transparent transition-all duration-300">
                  {card.title}
                </h3>
                <p className="text-gray-600 group-hover:text-gray-700 transition-colors">
                  {card.description}
                </p>
              </div>

              {/* Arrow indicator */}
              <div className="absolute bottom-4 right-4 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:translate-x-1">
                <TrendingUp className="w-4 h-4 text-gray-600" />
              </div>
            </motion.a>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StaffDashboard;