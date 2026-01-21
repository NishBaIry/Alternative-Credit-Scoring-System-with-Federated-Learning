// StaffScoreApplication.jsx (renamed to Apply Loan)
// Loan application form with two modes: Existing Customer or New Customer
// Existing: Search by customer ID and pre-fill data
// New: Auto-generate customer ID, ask for name and other details
// Scores application and saves to new_applications.db

import { useState, useEffect } from 'react';
import ScoreGauge from '../components/ScoreGauge';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

const StaffScoreApplication = () => {
  const [customerType, setCustomerType] = useState('new'); // 'new' or 'existing'
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
  const [approvalAction, setApprovalAction] = useState(null); // 'approved' or 'rejected'
  const [processingApproval, setProcessingApproval] = useState(false);

  // Fetch next customer ID for new customers
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

        // Pre-fill form with existing customer data
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
      // Prepare application data
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
        // Add defaults for other required fields
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
        <h1 className="text-3xl font-bold mb-8">Apply for Loan</h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Customer Type Selection */}
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">Customer Type</h2>
          <div className="flex gap-4">
            <button
              onClick={() => {
                setCustomerType('new');
                setSearchCustomerId('');
                setCustomerFound(null);
                setResult(null);
              }}
              className={`flex-1 py-3 px-6 rounded-lg font-medium transition-colors ${
                customerType === 'new'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              New Customer
            </button>
            <button
              onClick={() => {
                setCustomerType('existing');
                setResult(null);
              }}
              className={`flex-1 py-3 px-6 rounded-lg font-medium transition-colors ${
                customerType === 'existing'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Existing Customer
            </button>
          </div>
        </div>

        {/* Existing Customer Search */}
        {customerType === 'existing' && !customerFound && (
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-4">Search Existing Customer</h2>
            <div className="flex gap-4">
              <input
                type="text"
                value={searchCustomerId}
                onChange={(e) => setSearchCustomerId(e.target.value)}
                placeholder="Enter Customer ID (e.g., 00000001)"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyDown={(e) => e.key === 'Enter' && handleSearchCustomer()}
              />
              <button
                onClick={handleSearchCustomer}
                disabled={searchingCustomer}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
              >
                {searchingCustomer ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>
        )}

        {/* Customer Found Banner */}
        {customerType === 'existing' && customerFound && (
          <div className="card mb-6 bg-green-50 border-green-200">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold text-green-800">Customer Found</h3>
                <p className="text-green-700">
                  {customerFound.name || 'NA'} ({customerFound.customer_id})
                </p>
              </div>
              <button
                onClick={() => {
                  setSearchCustomerId('');
                  setCustomerFound(null);
                }}
                className="text-green-600 hover:text-green-800 underline"
              >
                Search Different Customer
              </button>
            </div>
          </div>
        )}

        {/* Application Form */}
        {(customerType === 'new' || customerFound) && (
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-4">Loan Application Details</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Customer Info */}
              <div>
                <h3 className="text-lg font-medium mb-3 text-gray-700">Customer Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {customerType === 'new' && (
                    <div>
                      <label className="block text-sm font-medium mb-2">Customer ID *</label>
                      <input
                        type="text"
                        value={formData.customerId}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
                        disabled
                      />
                      <p className="text-xs text-gray-500 mt-1">Auto-generated 8-digit ID</p>
                    </div>
                  )}

                  {customerType === 'existing' && (
                    <div>
                      <label className="block text-sm font-medium mb-2">Customer ID</label>
                      <input
                        type="text"
                        value={formData.customerId}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
                        disabled
                      />
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium mb-2">Name *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                      placeholder="Enter full name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Age *</label>
                    <input
                      type="number"
                      value={formData.age}
                      onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                      min="18"
                      max="100"
                      placeholder="e.g., 35"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Gender *</label>
                    <select
                      value={formData.gender}
                      onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    >
                      <option value="M">Male</option>
                      <option value="F">Female</option>
                      <option value="O">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Marital Status *</label>
                    <select
                      value={formData.maritalStatus}
                      onChange={(e) => setFormData({ ...formData, maritalStatus: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                <h3 className="text-lg font-medium mb-3 text-gray-700">Financial Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Monthly Income (₹) *</label>
                    <input
                      type="number"
                      value={formData.monthlyIncome}
                      onChange={(e) => setFormData({ ...formData, monthlyIncome: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                      min="0"
                      placeholder="e.g., 50000"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">DTI Ratio (%) *</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.dti}
                      onChange={(e) => setFormData({ ...formData, dti: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                <h3 className="text-lg font-medium mb-3 text-gray-700">Loan Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Loan Amount (₹) *</label>
                    <input
                      type="number"
                      value={formData.loanAmount}
                      onChange={(e) => setFormData({ ...formData, loanAmount: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                      min="0"
                      placeholder="e.g., 200000"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Loan Duration (months) *</label>
                    <select
                      value={formData.loanDuration}
                      onChange={(e) => setFormData({ ...formData, loanDuration: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                    <label className="block text-sm font-medium mb-2">Loan Purpose *</label>
                    <select
                      value={formData.loanPurpose}
                      onChange={(e) => setFormData({ ...formData, loanPurpose: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                    <label className="block text-sm font-medium mb-2">Total Credit Enquiries (past 12 months) *</label>
                    <input
                      type="number"
                      value={formData.totalEnquiries}
                      onChange={(e) => setFormData({ ...formData, totalEnquiries: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                      min="0"
                      placeholder="e.g., 2"
                    />
                    <p className="text-xs text-gray-500 mt-1">Number of credit applications</p>
                  </div>
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-400"
                  disabled={loading}
                >
                  {loading ? 'Processing Application...' : 'Submit Application'}
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                >
                  Reset
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="card">
            <h2 className="text-xl font-semibold mb-6">Application Result</h2>
            <div className="space-y-6">
              <div className="flex justify-center">
                <ScoreGauge score={result.score} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Credit Score</p>
                  <p className="text-3xl font-bold text-primary-600">
                    {Math.round(result.score)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Range: 300-900</p>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Default Probability</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {(result.probability * 100).toFixed(2)}%
                  </p>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Recommendation</p>
                  <p className={`text-2xl font-bold ${
                    result.recommendation === 'Approve' ? 'text-green-600' :
                    result.recommendation === 'Review' ? 'text-amber-600' : 'text-red-600'
                  }`}>
                    {result.recommendation}
                  </p>
                </div>
              </div>

              {result.saved && !approvalAction && (
                <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                  <p className="text-sm text-blue-800 mb-3">
                    ✓ Application saved. Customer ID: <strong>{formData.customerId}</strong>
                    {customerType === 'new' && ' (New customer)'}
                  </p>
                  <div className="flex gap-4 justify-center">
                    <button
                      onClick={handleApprove}
                      disabled={processingApproval}
                      className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                      {processingApproval ? 'Processing...' : '✓ Approve Loan'}
                    </button>
                    <button
                      onClick={handleReject}
                      disabled={processingApproval}
                      className="px-8 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                      {processingApproval ? 'Processing...' : '✗ Reject Loan'}
                    </button>
                  </div>
                </div>
              )}

              {approvalAction === 'approved' && (
                <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                  <p className="text-lg text-green-800 font-semibold mb-2">
                    ✓ Loan Approved
                  </p>
                  <p className="text-sm text-green-700">
                    Customer ID: <strong>{formData.customerId}</strong> has been approved for a loan of ₹{formData.loanAmount}.
                  </p>
                  <p className="text-xs text-green-600 mt-2">
                    This application will be merged into the bank database when FL training starts.
                  </p>
                </div>
              )}

              {approvalAction === 'rejected' && (
                <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                  <p className="text-lg text-red-800 font-semibold mb-2">
                    ✗ Loan Rejected
                  </p>
                  <p className="text-sm text-red-700">
                    Customer ID: <strong>{formData.customerId}</strong> loan application has been rejected.
                  </p>
                  <p className="text-xs text-red-600 mt-2">
                    The rejection status will be recorded in the system.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StaffScoreApplication;
