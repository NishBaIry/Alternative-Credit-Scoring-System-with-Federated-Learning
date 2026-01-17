// ClientBankSelect.jsx
// Lets the client choose between Bank A and Bank B (or more in future).
// Clicking a bank stores selected bank in global AuthContext or localStorage.
// After selection, user is routed to ClientLogin for that bank.
// Use BankCard component to display bank name + description.
// This simulates multi-tenant FL setup in the UI.

import React from 'react';
import { useNavigate } from 'react-router-dom';

const ClientBankSelect = () => {
  const navigate = useNavigate();

  const banks = [
    { id: 'bank_a', name: 'Bank A' },
    { id: 'bank_b', name: 'Bank B' },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <h2 className="text-3xl font-bold text-center">Select Your Bank</h2>
        <div className="grid gap-4">
          {banks.map((bank) => (
            <button
              key={bank.id}
              onClick={() => navigate(`/client/login?bank=${bank.id}`)}
              className="card hover:shadow-lg transition-shadow cursor-pointer"
            >
              <h3 className="text-xl font-semibold">{bank.name}</h3>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ClientBankSelect;
