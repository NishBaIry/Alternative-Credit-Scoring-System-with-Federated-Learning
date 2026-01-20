// StaffCustomerDetail.jsx
// Detailed view of a single customer for bank staff.
// Shows Alternative Credit Score gauge (300-900) with color-coded risk.
// Sections: Personal Information, Financial Metrics, Credit History, UPI Activity.
// All missing values display as "NA" instead of 0 or blank.

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ScoreGauge from '../components/ScoreGauge';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

const StaffCustomerDetail = () => {
  const { customerId } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomer();
  }, [customerId]);

  const fetchCustomer = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/staff/customers/${customerId}`);
      const data = await response.json();
      setCustomer(data.customer);
    } catch (error) {
      console.error('Failed to fetch customer:', error);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to display values or "NA" for missing data
  const formatValue = (value, formatter = null) => {
    if (value === null || value === undefined || value === '' || (typeof value === 'number' && isNaN(value))) {
      return 'NA';
    }
    return formatter ? formatter(value) : value;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto">
          <div className="card p-8 text-center">
            <p className="text-gray-500">Loading customer details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto">
          <div className="card p-8 text-center">
            <p className="text-red-600">Customer not found</p>
            <button onClick={() => navigate('/staff/customers')} className="btn btn-secondary mt-4">
              Back to Customer List
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Customer Details</h1>
            <p className="text-sm text-gray-600 mt-1 font-mono">ID: {customer.customer_id}</p>
          </div>
          <button
            onClick={() => navigate('/staff/customers')}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            ← Back to List
          </button>
        </div>

        <div className="space-y-6">
          {/* Alternative Credit Score Gauge */}
          <div className="card p-8">
            <ScoreGauge score={customer.alt_score || customer.credit_score} />
          </div>

          {/* Personal Information */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Personal Information</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <InfoItem label="Age" value={formatValue(customer.age)} />
              <InfoItem label="Gender" value={formatValue(customer.gender)} />
              <InfoItem label="Marital Status" value={formatValue(customer.marital_status)} />
              <InfoItem label="Education" value={formatValue(customer.education)} />
              <InfoItem label="Region" value={formatValue(customer.region)} />
              <InfoItem label="Home Ownership" value={formatValue(customer.home_ownership)} />
              <InfoItem label="Dependents" value={formatValue(customer.dependents)} />
            </div>
          </div>

          {/* Financial Metrics */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Financial Metrics</h2>
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
          </div>

          {/* Credit History */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Credit History</h2>
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
          </div>

          {/* UPI Activity */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">UPI Activity</h2>
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
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper component for displaying labeled information
const InfoItem = ({ label, value }) => (
  <div>
    <p className="text-sm text-gray-600 mb-1">{label}</p>
    <p className="font-medium text-gray-900">{value}</p>
  </div>
);

export default StaffCustomerDetail;
