import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  UserPlus, 
  Users, 
  Search, 
  FileText, 
  DollarSign, 
  CreditCard,
  CheckCircle,
  XCircle,
  Loader2,
  AlertCircle
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8002';

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

const StaffScoreApplication = () => {
  const [customerType, setCustomerType] = useState('new');
  const [searchCustomerId, setSearchCustomerId] = useState('');
  const [searchingCustomer, setSearchingCustomer] = useState(false);
  const [customerFound, setCustomerFound] = useState(null);

  const [formData, setFormData] = useState({
    customerId: '',
    name: '',
    age: '',
    gender: 'M',
    maritalStatus: 'Single',
    monthlyIncome: '',
    loanAmount: '',
    loanDuration: '36',
    loanPurpose: 'Personal',
    dti: '',
    totalEnquiries: '0',
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [approvalAction, setApprovalAction] = useState(null);
  const [processingApproval, setProcessingApproval] = useState(false);

  useEffect(() => {
    if (customerType === 'new') {
      fetchNextCustomerId();
    }
  }, [customerType]);

  const fetchNextCustomerId = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/staff/applications/next-customer-id`);
      if (response.ok) {
        const data = await response.json();
        setFormData(prev => ({ ...prev, customerId: data.customer_id }));
      }
    } catch (err) {
      console.error('Failed to fetch next customer ID:', err);
    }
  };

  const handleSearchCustomer = async () => {
    if (!searchCustomerId.trim()) {
      setError('Please enter a customer ID');
      return;
    }

    setSearchingCustomer(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/staff/customers/${searchCustomerId}`);
      if (response.ok) {
        const data = await response.json();
        const customer = data.customer;

        setCustomerFound(customer);

        setFormData({
          customerId: customer.customer_id,
          name: customer.name || 'NA',
          age: customer.age?.toString() || '',
          gender: customer.gender || 'M',
          maritalStatus: customer.marital_status || 'Single',
          monthlyIncome: customer.monthly_income?.toString() || '',
          loanAmount: '',
          loanDuration: '36',
          loanPurpose: 'Personal',
          dti: customer.dti ? (customer.dti * 100).toFixed(2) : '',
          totalEnquiries: customer.tot_enq?.toString() || '0',
        });
      } else {
        setError('Customer not found');
        setCustomerFound(null);
      }
    } catch (err) {
      setError('Failed to search customer: ' + err.message);
      setCustomerFound(null);
    } finally {
      setSearchingCustomer(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const applicationData = {
        customer_id: formData.customerId,
        name: formData.name,
        age: parseInt(formData.age),
        gender: formData.gender,
        marital_status: formData.maritalStatus,
        monthly_income: parseFloat(formData.monthlyIncome),
        annual_income: parseFloat(formData.monthlyIncome) * 12,
        loan_amount: parseFloat(formData.loanAmount),
        loan_duration_months: parseInt(formData.loanDuration),
        loan_purpose: formData.loanPurpose,
        dti: parseFloat(formData.dti) / 100,
        tot_enq: parseInt(formData.totalEnquiries),
        education: 'GRADUATE',
        dependents: 0,
        home_ownership: 'Rented',
        region: 'Urban',
        job_type: 'Salaried',
        job_tenure_years: 3,
        net_monthly_income: parseFloat(formData.monthlyIncome),
        monthly_debt_payments: parseFloat(formData.monthlyIncome) * (parseFloat(formData.dti) / 100),
        total_dti: parseFloat(formData.dti) / 100,
        savings_balance: 10000,
        checking_balance: 5000,
        total_assets: 15000,
        total_liabilities: parseFloat(formData.loanAmount),
        net_worth: 15000 - parseFloat(formData.loanAmount),
        base_interest_rate: 8.5,
        interest_rate: 10.0,
        monthly_loan_payment: (parseFloat(formData.loanAmount) * 0.01) / parseInt(formData.loanDuration),
        enq_L3m: Math.min(parseInt(formData.totalEnquiries), 2),
        enq_L6m: Math.min(parseInt(formData.totalEnquiries), 3),
        enq_L12m: parseInt(formData.totalEnquiries),
        time_since_recent_enq: 30,
        num_30dpd: 0,
        num_60dpd: 0,
        max_delinquency_level: 0,
        CC_utilization: 0.3,
        PL_utilization: 0.2,
        HL_flag: 0,
        GL_flag: 0,
        utility_bill_score: 700,
        upi_txn_count_avg: 20,
        upi_txn_count_std: 5,
        upi_total_spend_month_avg: parseFloat(formData.monthlyIncome) * 0.6,
        upi_merchant_diversity: 10,
        upi_spend_volatility: 0.2,
        upi_failed_txn_rate: 0.02,
        upi_essentials_share: 0.4
      };

      const response = await fetch(`${API_BASE_URL}/api/staff/applications/score`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(applicationData),
      });

      if (!response.ok) {
        throw new Error(`Scoring failed: ${response.statusText}`);
      }

      const data = await response.json();

      setResult({
        score: data.alt_score || data.credit_score || 0,
        riskBand: data.risk_band || 'Unknown',
        probability: data.default_probability || 0,
        recommendation: data.recommendation || '',
        saved: data.saved || false
      });
    } catch (err) {
      setError(err.message);
      console.error('Scoring error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!formData.customerId) return;

    setProcessingApproval(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/staff/applications/approve/${formData.customerId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Approval failed: ${response.statusText}`);
      }

      const data = await response.json();
      setApprovalAction('approved');
    } catch (err) {
      setError(err.message);
      console.error('Approval error:', err);
    } finally {
      setProcessingApproval(false);
    }
  };

  const handleReject = async () => {
    if (!formData.customerId) return;

    setProcessingApproval(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/staff/applications/reject/${formData.customerId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Rejection failed: ${response.statusText}`);
      }

      const data = await response.json();
      setApprovalAction('rejected');
    } catch (err) {
      setError(err.message);
      console.error('Rejection error:', err);
    } finally {
      setProcessingApproval(false);
    }
  };

  const handleReset = () => {
    setCustomerType('new');
    setSearchCustomerId('');
    setCustomerFound(null);
    setResult(null);
    setError(null);
    setApprovalAction(null);
    setFormData({
      customerId: '',
      name: '',
      age: '',
      gender: 'M',
      maritalStatus: 'Single',
      monthlyIncome: '',
      loanAmount: '',
      loanDuration: '36',
      loanPurpose: 'Personal',
      dti: '',
      totalEnquiries: '0',
    });
    if (customerType === 'new') {
      fetchNextCustomerId();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold mb-8 text-gray-900"
        >
          Apply for Loan
        </motion.h1>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4 flex items-center gap-2"
          >
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </motion.div>
        )}

        {/* Customer Type Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.5 }}
          className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm mb-6"
        >
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Customer Type</h2>
          <div className="flex gap-4">
            <button
              onClick={() => {
                setCustomerType('new');
                setSearchCustomerId('');
                setCustomerFound(null);
                setResult(null);
              }}
              className={`flex-1 py-3 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${
                customerType === 'new'
                  ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <UserPlus className="w-5 h-5" />
              <span>New Customer</span>
            </button>
            <button
              onClick={() => {
                setCustomerType('existing');
                setResult(null);
              }}
              className={`flex-1 py-3 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${
                customerType === 'existing'
                  ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Users className="w-5 h-5" />
              <span>Existing Customer</span>
            </button>
          </div>
        </motion.div>

        {/* Existing Customer Search */}
        {customerType === 'existing' && !customerFound && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm mb-6"
          >
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Search Existing Customer</h2>
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Search className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchCustomerId}
                  onChange={(e) => setSearchCustomerId(e.target.value)}
                  placeholder="Enter Customer ID (e.g., 00000001)"
                  className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                  onKeyDown={(e) => e.key === 'Enter' && handleSearchCustomer()}
                />
              </div>
              <button
                onClick={handleSearchCustomer}
                disabled={searchingCustomer}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {searchingCustomer ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    <span>Search</span>
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}

        {/* Customer Found Banner */}
        {customerType === 'existing' && customerFound && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="bg-green-50 border border-green-200 rounded-2xl p-6 mb-6"
          >
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-green-800">Customer Found</h3>
                  <p className="text-green-700">
                    {customerFound.name || 'NA'} ({customerFound.customer_id})
                  </p>
                </div>
              </div>
              <button
                onClick={() => {
                  setSearchCustomerId('');
                  setCustomerFound(null);
                }}
                className="text-green-600 hover:text-green-800 font-medium transition-colors"
              >
                Search Different Customer
              </button>
            </div>
          </motion.div>
        )}

        {/* Application Form */}
        {(customerType === 'new' || customerFound) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm mb-6"
          >
            <h2 className="text-xl font-semibold mb-6 text-gray-900">Loan Application Details</h2>
            <div className="space-y-8">
              {/* Customer Info */}
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Users className="w-4 h-4 text-purple-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800">Customer Information</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {customerType === 'new' && (
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Customer ID *</label>
                      <input
                        type="text"
                        value={formData.customerId}
                        className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 font-mono"
                        disabled
                      />
                      <p className="text-xs text-gray-500 mt-1">Auto-generated 8-digit ID</p>
                    </div>
                  )}

                  {customerType === 'existing' && (
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Customer ID</label>
                      <input
                        type="text"
                        value={formData.customerId}
                        className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 font-mono"
                        disabled
                      />
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Name *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                      placeholder="Enter full name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Age *</label>
                    <input
                      type="number"
                      value={formData.age}
                      onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                      min="18"
                      max="100"
                      placeholder="e.g., 35"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Gender *</label>
                    <select
                      value={formData.gender}
                      onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                    >
                      <option value="M">Male</option>
                      <option value="F">Female</option>
                      <option value="O">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Marital Status *</label>
                    <select
                      value={formData.maritalStatus}
                      onChange={(e) => setFormData({ ...formData, maritalStatus: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                    >
                      <option value="Single">Single</option>
                      <option value="Married">Married</option>
                      <option value="Divorced">Divorced</option>
                      <option value="Widowed">Widowed</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Financial Information */}
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                    <DollarSign className="w-4 h-4 text-green-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800">Financial Information</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Monthly Income (₹) *</label>
                    <input
                      type="number"
                      value={formData.monthlyIncome}
                      onChange={(e) => setFormData({ ...formData, monthlyIncome: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                      min="0"
                      placeholder="e.g., 50000"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">DTI Ratio (%) *</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.dti}
                      onChange={(e) => setFormData({ ...formData, dti: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                      min="0"
                      max="100"
                      placeholder="e.g., 35"
                    />
                    <p className="text-xs text-gray-500 mt-1">Debt-to-Income ratio</p>
                  </div>
                </div>
              </div>

              {/* Loan Details */}
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <CreditCard className="w-4 h-4 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800">Loan Details</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Loan Amount (₹) *</label>
                    <input
                      type="number"
                      value={formData.loanAmount}
                      onChange={(e) => setFormData({ ...formData, loanAmount: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                      min="0"
                      placeholder="e.g., 200000"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Loan Duration (months) *</label>
                    <select
                      value={formData.loanDuration}
                      onChange={(e) => setFormData({ ...formData, loanDuration: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                    >
                      <option value="12">12 months</option>
                      <option value="24">24 months</option>
                      <option value="36">36 months</option>
                      <option value="48">48 months</option>
                      <option value="60">60 months</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Loan Purpose *</label>
                    <select
                      value={formData.loanPurpose}
                      onChange={(e) => setFormData({ ...formData, loanPurpose: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                    >
                      <option value="Personal">Personal</option>
                      <option value="Home">Home</option>
                      <option value="Auto">Auto</option>
                      <option value="Education">Education</option>
                      <option value="Business">Business</option>
                      <option value="Medical">Medical</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Total Credit Enquiries (past 12 months) *</label>
                    <input
                      type="number"
                      value={formData.totalEnquiries}
                      onChange={(e) => setFormData({ ...formData, totalEnquiries: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                      required
                      min="0"
                      placeholder="e.g., 2"
                    />
                    <p className="text-xs text-gray-500 mt-1">Number of credit applications</p>
                  </div>
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  onClick={handleSubmit}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 rounded-xl hover:shadow-lg transition-all duration-300 hover:scale-105 font-semibold disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Processing Application...</span>
                    </>
                  ) : (
                    <>
                      <FileText className="w-5 h-5" />
                      <span>Submit Application</span>
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-8 py-4 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors font-semibold"
                >
                  Reset
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Results */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm"
          >
            <h2 className="text-xl font-semibold mb-6 text-gray-900">Application Result</h2>
            <div className="space-y-6">
              <div className="flex justify-center">
                <ScoreGauge score={result.score} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-6 bg-gray-50 rounded-xl border border-gray-200">
                  <p className="text-sm text-gray-600 mb-2 font-medium">Credit Score</p>
                  <p className="text-4xl font-bold text-purple-600">
                    {Math.round(result.score)}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">Range: 300-900</p>
                </div>

                <div className="p-6 bg-gray-50 rounded-xl border border-gray-200">
                  <p className="text-sm text-gray-600 mb-2 font-medium">Default Probability</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {(result.probability * 100).toFixed(2)}%
                  </p>
                </div>

                <div className="p-6 bg-gray-50 rounded-xl border border-gray-200">
                  <p className="text-sm text-gray-600 mb-2 font-medium">Recommendation</p>
                  <p className={`text-3xl font-bold ${
                    result.recommendation === 'Approve' ? 'text-green-600' :
                    result.recommendation === 'Review' ? 'text-amber-600' : 'text-red-600'
                  }`}>
                    {result.recommendation}
                  </p>
                </div>
              </div>

              {result.saved && !approvalAction && (
                <div className="bg-blue-50 border border-blue-200 p-6 rounded-xl">
                  <div className="flex items-start gap-3 mb-4">
                    <CheckCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm text-blue-800 font-medium">
                        Application saved. Customer ID: <strong>{formData.customerId}</strong>
                        {customerType === 'new' && ' (New customer)'}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 justify-center">
                    <button
                      onClick={handleApprove}
                      disabled={processingApproval}
                      className="inline-flex items-center gap-2 px-8 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 hover:shadow-lg transition-all duration-300 hover:scale-105 font-semibold disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                    >
                      {processingApproval ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          <span>Processing...</span>
                        </>
                      ) : (
                        <>
                          <CheckCircle className="w-5 h-5" />
                          <span>Approve Loan</span>
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleReject}
                      disabled={processingApproval}
                      className="inline-flex items-center gap-2 px-8 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 hover:shadow-lg transition-all duration-300 hover:scale-105 font-semibold disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                    >
                      {processingApproval ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          <span>Processing...</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-5 h-5" />
                          <span>Reject Loan</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}

              {approvalAction === 'approved' && (
                <div className="bg-green-50 border border-green-200 p-6 rounded-xl">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-lg text-green-800 font-semibold mb-2">
                        Loan Approved
                      </p>
                      <p className="text-sm text-green-700 mb-2">
                        Customer ID: <strong>{formData.customerId}</strong> has been approved for a loan of ₹{formData.loanAmount}.
                      </p>
                      <p className="text-xs text-green-600">
                        This application will be merged into the bank database when FL training starts.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {approvalAction === 'rejected' && (
                <div className="bg-red-50 border border-red-200 p-6 rounded-xl">
                  <div className="flex items-start gap-3">
                    <XCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-lg text-red-800 font-semibold mb-2">
                        Loan Rejected
                      </p>
                      <p className="text-sm text-red-700 mb-2">
                        Customer ID: <strong>{formData.customerId}</strong> loan application has been rejected.
                      </p>
                      <p className="text-xs text-red-600">
                        The rejection status will be recorded in the system.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default StaffScoreApplication;