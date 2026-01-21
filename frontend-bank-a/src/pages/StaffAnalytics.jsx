import React from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  PieChart, 
  Activity,
  Users,
  Briefcase,
  UserCheck
} from 'lucide-react';

const StaffAnalytics = () => {
  const featureData = [
    { name: 'time_since_recent_enq', value: 0.21, color: 'bg-blue-500' },
    { name: 'age', value: 0.19, color: 'bg-purple-500' },
    { name: 'GL_flag', value: 0.15, color: 'bg-green-500' },
    { name: 'enq_L3m', value: 0.12, color: 'bg-orange-500' },
    { name: 'enq_L6m', value: 0.12, color: 'bg-pink-500' },
    { name: 'job_tenure_years', value: 0.11, color: 'bg-cyan-500' },
    { name: 'enq_L12m', value: 0.10, color: 'bg-blue-600' },
    { name: 'HL_flag', value: 0.10, color: 'bg-purple-600' },
    { name: 'upi_failed_txn_rate', value: 0.08, color: 'bg-green-600' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold mb-8 text-gray-900"
        >
          Analytics & Monitoring
        </motion.h1>
        
        <div className="grid gap-6">
          {/* Top Metrics Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.5 }}
              className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
            >
              <p className="text-sm text-gray-600 mb-2">Total Customers</p>
              <p className="text-4xl font-bold text-gray-900">35,000</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15, duration: 0.5 }}
              className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
            >
              <p className="text-sm text-gray-600 mb-2">Average Score</p>
              <p className="text-4xl font-bold text-blue-600">556</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
            >
              <p className="text-sm text-gray-600 mb-2">Default Rate</p>
              <p className="text-4xl font-bold text-red-600">92.2%</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25, duration: 0.5 }}
              className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
            >
              <p className="text-sm text-gray-600 mb-2">Model AUC</p>
              <p className="text-4xl font-bold text-green-600">0.950</p>
            </motion.div>
          </div>

          {/* Feature Importance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="bg-white rounded-xl shadow-sm p-8 border border-gray-200"
          >
            <div className="flex items-center gap-3 mb-8">
              <TrendingUp className="w-6 h-6 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900">Feature Importance</h2>
            </div>
            <div className="space-y-5">
              {featureData.map((feature, index) => (
                <div key={index}>
                  <div className="flex justify-between mb-2">
                    <span className="text-gray-900 font-medium">{feature.name}</span>
                    <span className="font-bold text-gray-900">{feature.value.toFixed(2)}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2.5">
                    <div 
                      className={`${feature.color} h-2.5 rounded-full transition-all duration-700`}
                      style={{ width: `${feature.value * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Approval Rates */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
                <Users className="w-5 h-5 text-green-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Approval Rates by Segment</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-6 bg-gray-50 rounded-xl border border-gray-200 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Briefcase className="w-6 h-6 text-green-600" />
                </div>
                <p className="text-sm text-gray-600 mb-2 font-medium">Salaried</p>
                <p className="text-4xl font-bold text-green-600">78%</p>
              </div>
              <div className="text-center p-6 bg-gray-50 rounded-xl border border-gray-200 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <UserCheck className="w-6 h-6 text-yellow-600" />
                </div>
                <p className="text-sm text-gray-600 mb-2 font-medium">Self-Employed</p>
                <p className="text-4xl font-bold text-yellow-600">65%</p>
              </div>
              <div className="text-center p-6 bg-gray-50 rounded-xl border border-gray-200 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Activity className="w-6 h-6 text-orange-600" />
                </div>
                <p className="text-sm text-gray-600 mb-2 font-medium">Gig Worker</p>
                <p className="text-4xl font-bold text-orange-600">58%</p>
              </div>
            </div>
          </motion.div>

          {/* Model Performance Trends */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Model Performance Trends</h2>
            </div>
            <div className="h-64 flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border border-gray-200">
              <div className="text-center">
                <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 font-medium">[Chart Placeholder - Model AUC over time]</p>
              </div>
            </div>
          </motion.div>

          {/* Distribution Plot */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center">
                <PieChart className="w-5 h-5 text-orange-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Distribution: DTI Ratio (Good vs Bad)</h2>
            </div>
            <div className="h-64 flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border border-gray-200">
              <div className="text-center">
                <PieChart className="w-16 h-16 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 font-medium">[Chart Placeholder - Distribution plot]</p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default StaffAnalytics;