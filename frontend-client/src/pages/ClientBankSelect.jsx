// ClientBankSelect.jsx
// Lets the client choose between Bank A and Bank B (or more in future).
// Clicking a bank stores selected bank in global AuthContext or localStorage.
// After selection, user is routed to ClientLogin for that bank.
// This simulates multi-tenant FL setup in the UI.

import React from 'react';
import { useNavigate } from 'react-router-dom';

const ClientBankSelect = () => {
  const navigate = useNavigate();

  const banks = [
    { 
      id: 'bank_a', 
      name: 'Bank A',
      description: 'Your trusted banking partner',
      color: 'bg-blue-500'
    },
    { 
      id: 'bank_b', 
      name: 'Bank B',
      description: 'Banking made simple',
      color: 'bg-green-500'
    },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Select Your Bank</h2>
          <p className="text-gray-600 mt-2">Choose the bank where you have an account</p>
        </div>
        
        <div className="grid md:grid-cols-2 gap-6">
          {banks.map((bank) => (
            <button
              key={bank.id}
              onClick={() => navigate(`/client/login?bank=${bank.id}`)}
              className="card hover:shadow-xl transition-all cursor-pointer text-left p-8 border-2 border-transparent hover:border-primary"
            >
              <div className={`w-16 h-16 ${bank.color} rounded-lg mb-4 flex items-center justify-center`}>
                <span className="text-white text-2xl font-bold">
                  {bank.name.charAt(bank.name.length - 1)}
                </span>
              </div>
              <h3 className="text-2xl font-semibold mb-2">{bank.name}</h3>
              <p className="text-gray-600">{bank.description}</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ClientBankSelect;
