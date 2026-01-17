// BankCard.jsx
// Reusable card component for displaying bank options.
// Used in ClientBankSelect to show available banks.
// Accepts bank object with id, name, description.

import React from 'react';

const BankCard = ({ bank, onSelect }) => {
  return (
    <div
      onClick={() => onSelect(bank.id)}
      className="card hover:shadow-lg transition-shadow cursor-pointer"
    >
      <div className="flex items-center space-x-4">
        <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
          <span className="text-2xl font-bold text-primary-600">{bank.name.charAt(0)}</span>
        </div>
        <div>
          <h3 className="text-xl font-semibold">{bank.name}</h3>
          <p className="text-gray-600">{bank.description || 'Click to login'}</p>
        </div>
      </div>
    </div>
  );
};

export default BankCard;
