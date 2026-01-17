import React from 'react';

const CustomerTable = ({ customers, onRowClick }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b bg-gray-50">
            <th className="text-left py-3 px-4 font-semibold">ID</th>
            <th className="text-left py-3 px-4 font-semibold">Name</th>
            <th className="text-left py-3 px-4 font-semibold">Score</th>
            <th className="text-left py-3 px-4 font-semibold">Risk Band</th>
            <th className="text-left py-3 px-4 font-semibold">Age</th>
            <th className="text-left py-3 px-4 font-semibold">Region</th>
            <th className="text-left py-3 px-4 font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody>
          {customers.map((customer) => (
            <tr
              key={customer.id}
              className="border-b hover:bg-gray-50 cursor-pointer"
              onClick={() => onRowClick && onRowClick(customer)}
            >
              <td className="py-3 px-4">{customer.id}</td>
              <td className="py-3 px-4">{customer.name}</td>
              <td className="py-3 px-4 font-semibold">{customer.score}</td>
              <td className="py-3 px-4">
                <span
                  className={`px-2 py-1 rounded text-sm ${
                    customer.riskBand === 'Low'
                      ? 'bg-green-100 text-green-800'
                      : customer.riskBand === 'Medium'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {customer.riskBand}
                </span>
              </td>
              <td className="py-3 px-4">{customer.age}</td>
              <td className="py-3 px-4">{customer.region}</td>
              <td className="py-3 px-4">
                <button className="text-primary-600 hover:underline">View</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CustomerTable;
