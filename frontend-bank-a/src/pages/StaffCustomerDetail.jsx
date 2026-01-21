import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  User, 
  DollarSign, 
  CreditCard, 
  Smartphone,
  Loader2,
  AlertCircle
} from 'lucide-react';

const API_URL = 'http://localhost:8002';

// ScoreGauge Component (unchanged)
const ScoreGauge = ({ score, minScore = 300, maxScore = 900 }) => {
  const displayScore = score == null || isNaN(score) ? 'NA' : Math.round(score);
  const numericScore = score == null || isNaN(score) ? minScore : score;

  const percentage = ((numericScore - minScore) / (maxScore - minScore)) * 100;
  const clampedPercentage = Math.max(0, Math.min(100, percentage));

  const getColor = () => {
    if (numericScore >= 701) return '#10b981';
    if (numericScore >= 551) return '#f59e0b';
    return '#ef4444';
  };

  const color = getColor();

  const circumference = 2 * Math.PI * 80;
  const strokeDashoffset = circumference - (clampedPercentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-4">
      <h3 className="text-lg font-semibold text-gray-700">Alternative Credit Score</h3>
      <div className="relative w-56 h-56">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="112"
            cy="112"
            r="80"
            stroke="#e5e7eb"
            strokeWidth="16"
            fill="none"
          />
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

const StaffCustomerDetail = () => {
  const customerId = '00000001'; // Placeholder
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomer();
  }, [customerId]);

  const fetchCustomer = async () => {
    setLoading(true);
    try {
      // Simulating API call with sample data
      await new Promise(resolve => setTimeout(resolve, 1000));
      setCustomer({
        customer_id: '00000001',
        name: 'Rajesh Kumar',
        alt_score: 745,
        age: 32,
        gender: 'Male',
        marital_status: 'Married',
        education: 'Graduate',
        region: 'Urban',
        home_ownership: 'Owned',
        dependents: 2,
        monthly_income: 75000,
        annual_income: 900000,
        dti: 35.5,
        total_dti: 42.3,
        monthly_debt_payments: 26625,
        net_worth: 1500000,
        tot_enq: 5,
        enq_L3m: 1,
        enq_L6m: 2,
        enq_L12m: 4,
        num_30dpd: 0,
        num_60dpd: 0,
        max_delinquency_level: 0,
        utility_bill_score: 85,
        upi_txn_count_avg: 45.5,
        upi_total_spend_month_avg: 32000,
        upi_merchant_diversity: 0.75,
        upi_spend_volatility: 0.32,
        upi_failed_txn_rate: 2.5,
        upi_essentials_share: 62.3
      });
    } catch (error) {
      console.error('Failed to fetch customer:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatValue = (value, formatter = null) => {
    if (value === null || value === undefined || value === '' || (typeof value === 'number' && isNaN(value))) {
      return 'NA';
    }
    return formatter ? formatter(value) : value;
  };

  const handleBackClick = () => {
    console.log('Navigate back to customer list');
    // Replace with: navigate('/staff/customers')
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-2xl p-12 border border-gray-200 shadow-sm text-center"
          >
            <Loader2 className="w-12 h-12 text-purple-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600 font-medium">Loading customer details...</p>
          </motion.div>
        </div>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-2xl p-12 border border-gray-200 shadow-sm text-center"
          >
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <p className="text-red-600 text-lg font-semibold mb-4">Customer not found</p>
            <button
              onClick={handleBackClick}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-300 hover:scale-105"
            >
              Back to Customer List
            </button>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex justify-between items-center mb-8"
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Customer Details</h1>
            <p className="text-sm text-gray-500 mt-1 font-mono">ID: {customer.customer_id}</p>
          </div>
          <button
            onClick={handleBackClick}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors font-medium text-gray-700"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to List</span>
          </button>
        </motion.div>

        <div className="space-y-6">
          {/* Alternative Credit Score Gauge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm"
          >
            <ScoreGauge score={customer.alt_score || customer.credit_score} />
          </motion.div>

          {/* Personal Information */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm"
          >
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
              <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                <User className="w-5 h-5 text-purple-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Personal Information</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <InfoItem label="Age" value={formatValue(customer.age)} />
              <InfoItem label="Gender" value={formatValue(customer.gender)} />
              <InfoItem label="Marital Status" value={formatValue(customer.marital_status)} />
              <InfoItem label="Education" value={formatValue(customer.education)} />
              <InfoItem label="Region" value={formatValue(customer.region)} />
              <InfoItem label="Home Ownership" value={formatValue(customer.home_ownership)} />
              <InfoItem label="Dependents" value={formatValue(customer.dependents)} />
            </div>
          </motion.div>

          {/* Financial Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm"
          >
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
              <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-green-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Financial Metrics</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <InfoItem
                label="Monthly Income"
                value={formatValue(customer.monthly_income, (v) => `₹${v.toLocaleString()}`)}
              />
              <InfoItem
                label="Annual Income"
                value={formatValue(customer.annual_income, (v) => `₹${v.toLocaleString()}`)}
              />
              <InfoItem
                label="DTI"
                value={formatValue(customer.dti, (v) => `${v.toFixed(2)}%`)}
              />
              <InfoItem
                label="Total DTI"
                value={formatValue(customer.total_dti, (v) => `${v.toFixed(2)}%`)}
              />
              <InfoItem
                label="Monthly Debt Payments"
                value={formatValue(customer.monthly_debt_payments, (v) => `₹${v.toLocaleString()}`)}
              />
              <InfoItem
                label="Net Worth"
                value={formatValue(customer.net_worth, (v) => `₹${v.toLocaleString()}`)}
              />
            </div>
          </motion.div>

          {/* Credit History */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm"
          >
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <CreditCard className="w-5 h-5 text-blue-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Credit History</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <InfoItem label="Total Enquiries" value={formatValue(customer.tot_enq)} />
              <InfoItem label="Enquiries (Last 3 months)" value={formatValue(customer.enq_L3m)} />
              <InfoItem label="Enquiries (Last 6 months)" value={formatValue(customer.enq_L6m)} />
              <InfoItem label="Enquiries (Last 12 months)" value={formatValue(customer.enq_L12m)} />
              <InfoItem label="30 DPD Count" value={formatValue(customer.num_30dpd)} />
              <InfoItem label="60 DPD Count" value={formatValue(customer.num_60dpd)} />
              <InfoItem label="Max Delinquency Level" value={formatValue(customer.max_delinquency_level)} />
              <InfoItem label="Utility Bill Score" value={formatValue(customer.utility_bill_score)} />
            </div>
          </motion.div>

          {/* UPI Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm"
          >
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
              <div className="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center">
                <Smartphone className="w-5 h-5 text-orange-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">UPI Activity</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <InfoItem
                label="Avg Transaction Count"
                value={formatValue(customer.upi_txn_count_avg, (v) => v.toFixed(2))}
              />
              <InfoItem
                label="Avg Monthly Spend"
                value={formatValue(customer.upi_total_spend_month_avg, (v) => `₹${v.toLocaleString()}`)}
              />
              <InfoItem
                label="Merchant Diversity"
                value={formatValue(customer.upi_merchant_diversity, (v) => v.toFixed(2))}
              />
              <InfoItem
                label="Spend Volatility"
                value={formatValue(customer.upi_spend_volatility, (v) => v.toFixed(2))}
              />
              <InfoItem
                label="Failed Transaction Rate"
                value={formatValue(customer.upi_failed_txn_rate, (v) => `${v.toFixed(2)}%`)}
              />
              <InfoItem
                label="Essentials Share"
                value={formatValue(customer.upi_essentials_share, (v) => `${v.toFixed(2)}%`)}
              />
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

// Helper component for displaying labeled information
const InfoItem = ({ label, value }) => (
  <div>
    <p className="text-sm text-gray-500 mb-1 font-medium">{label}</p>
    <p className="font-semibold text-gray-900">{value}</p>
  </div>
);

export default StaffCustomerDetail;