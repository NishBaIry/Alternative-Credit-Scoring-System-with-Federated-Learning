// StaffCustomerList.jsx
// Table view of customers for this bank only, using CustomerTable component.
// Columns: customer_id, alias, age, region, latest score, risk band.
// Supports basic search/filter by id or risk band (front-end only is fine).
// Row click routes to StaffCustomerDetail with that customer's id.
// Calls /staff/customers to fetch paginated data from backend.

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

const StaffCustomerList = () => {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(100);

  useEffect(() => {
    fetchCustomers();
  }, [page]);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/api/staff/customers?skip=${page * limit}&limit=${limit}`
      );
      const data = await response.json();
      setCustomers(data.customers || []);
      setTotal(data.total || 0);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
      setCustomers([]);
    } finally {
      setLoading(false);
    }
  };

  const getRiskBand = (defaultFlag) => {
    // 0 = no default (Low risk), 1 = default (High risk)
    return defaultFlag === 0 ? 'Low' : 'High';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Customer List</h1>
          <div className="text-sm text-gray-600">
            Total: {total} customers
          </div>
        </div>
        
        {loading ? (
          <div className="card p-8 text-center">
            <div className="text-gray-500">Loading customers...</div>
          </div>
        ) : (
          <>
            <div className="card">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4">Customer ID</th>
                      <th className="text-left py-3 px-4">Age</th>
                      <th className="text-left py-3 px-4">Region</th>
                      <th className="text-left py-3 px-4">Monthly Income</th>
                      <th className="text-left py-3 px-4">DTI</th>
                      <th className="text-left py-3 px-4">Risk Band</th>
                      <th className="text-left py-3 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {customers.map((customer) => (
                      <tr key={customer.customer_id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4 font-mono text-sm">{customer.customer_id}</td>
                        <td className="py-3 px-4">{customer.age}</td>
                        <td className="py-3 px-4">{customer.region}</td>
                        <td className="py-3 px-4">₹{customer.monthly_income?.toLocaleString()}</td>
                        <td className="py-3 px-4">{customer.dti?.toFixed(2)}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded text-sm ${
                            getRiskBand(customer.default_flag) === 'Low' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {getRiskBand(customer.default_flag)}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <button
                            onClick={() => navigate(`/staff/customers/${customer.customer_id}`)}
                            className="text-primary-600 hover:underline"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="mt-4 flex justify-between items-center">
              <button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                className="btn btn-secondary disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {page + 1} of {Math.ceil(total / limit)}
              </span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={(page + 1) * limit >= total}
                className="btn btn-secondary disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default StaffCustomerList;
