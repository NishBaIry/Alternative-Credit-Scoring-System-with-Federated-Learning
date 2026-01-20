// StaffCustomerList.jsx
// Neutral directory of customers - no risk labels at this level.
// Displays: customer_id, name, and a "View" action button.
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
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    if (!searchQuery) {
      fetchCustomers();
    }
  }, [page]);

  useEffect(() => {
    if (searchQuery) {
      handleSearch();
    } else {
      fetchCustomers();
    }
  }, [searchQuery]);

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

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchCustomers();
      return;
    }

    setSearching(true);
    try {
      const response = await fetch(`${API_URL}/api/staff/customers/${searchQuery.trim()}`);
      if (response.ok) {
        const data = await response.json();
        setCustomers([data.customer]);
        setTotal(1);
      } else {
        setCustomers([]);
        setTotal(0);
      }
    } catch (error) {
      console.error('Failed to search customer:', error);
      setCustomers([]);
      setTotal(0);
    } finally {
      setSearching(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setPage(0);
    fetchCustomers();
  };


  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Manage Accounts</h1>
          <div className="text-sm text-gray-600">
            Total: {total} customers
          </div>
        </div>

        {/* Search Bar */}
        <div className="card mb-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by Customer ID (e.g., 00000001)"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              {searchQuery && (
                <button
                  onClick={handleClearSearch}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label="Clear search"
                >
                  ✕
                </button>
              )}
            </div>
            <button
              onClick={handleSearch}
              disabled={searching || !searchQuery.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </div>
          {searchQuery && customers.length === 0 && !loading && (
            <div className="mt-3 text-sm text-red-600">
              No customer found with ID "{searchQuery}"
            </div>
          )}
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
                      <th className="text-left py-3 px-4">Name</th>
                      <th className="text-left py-3 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {customers.map((customer) => (
                      <tr key={customer.customer_id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4 font-mono text-sm">{customer.customer_id}</td>
                        <td className="py-3 px-4">{customer.name || 'NA'}</td>
                        <td className="py-3 px-4">
                          <button
                            onClick={() => navigate(`/staff/customers/${customer.customer_id}`)}
                            className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
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
            
            {!searchQuery && (
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
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default StaffCustomerList;
