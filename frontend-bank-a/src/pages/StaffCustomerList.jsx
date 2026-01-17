// StaffCustomerList.jsx
// Table view of customers for this bank only, using CustomerTable component.
// Columns: customer_id, alias, age, region, latest score, risk band.
// Supports basic search/filter by id or risk band (front-end only is fine).
// Row click routes to StaffCustomerDetail with that customer's id.
// Calls /staff/customers to fetch paginated data from backend.

import React from 'react';
import { useNavigate } from 'react-router-dom';

const StaffCustomerList = () => {
  const navigate = useNavigate();

  const customers = [
    { id: 'C001', name: 'John Doe', score: 742, riskBand: 'Low', age: 28, region: 'Mumbai' },
    { id: 'C002', name: 'Jane Smith', score: 620, riskBand: 'Medium', age: 35, region: 'Delhi' },
    { id: 'C003', name: 'Mike Johnson', score: 810, riskBand: 'Low', age: 42, region: 'Bangalore' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Customer List</h1>
        
        <div className="card">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Customer ID</th>
                  <th className="text-left py-3 px-4">Name</th>
                  <th className="text-left py-3 px-4">Score</th>
                  <th className="text-left py-3 px-4">Risk Band</th>
                  <th className="text-left py-3 px-4">Age</th>
                  <th className="text-left py-3 px-4">Region</th>
                  <th className="text-left py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((customer) => (
                  <tr key={customer.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">{customer.id}</td>
                    <td className="py-3 px-4">{customer.name}</td>
                    <td className="py-3 px-4 font-semibold">{customer.score}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-sm ${
                        customer.riskBand === 'Low' ? 'bg-green-100 text-green-800' :
                        customer.riskBand === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {customer.riskBand}
                      </span>
                    </td>
                    <td className="py-3 px-4">{customer.age}</td>
                    <td className="py-3 px-4">{customer.region}</td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => navigate(`/staff/customers/${customer.id}`)}
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
      </div>
    </div>
  );
};

export default StaffCustomerList;
