// ClientProfile.jsx
// Read-only panel of key model inputs: age, region, employment, loan info, UPI summaries.
// Calls /client/me/profile; only allows editing of non-financial fields if backend permits.
// Use disabled inputs to signal that income/UPI/delinquencies are system-sourced.
// Add a small note about how data is sourced from bank systems, not manually entered.
// Good place to re-emphasize privacy and data usage policies.

import React, { useState } from 'react';

const ClientProfile = () => {
  const [profile, setProfile] = useState({
    customerId: 'C12345',
    name: 'John Doe',
    email: 'john@example.com',
    phone: '+91-9876543210',
    age: 28,
    employmentType: 'Salaried',
    monthlyIncome: 50000,
  });

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">My Profile</h1>
        
        <div className="card">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Customer ID</label>
              <input
                type="text"
                value={profile.customerId}
                disabled
                className="input-field bg-gray-100"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Name</label>
              <input
                type="text"
                value={profile.name}
                disabled
                className="input-field bg-gray-100"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={profile.email}
                className="input-field"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Phone</label>
              <input
                type="tel"
                value={profile.phone}
                className="input-field"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Age</label>
              <input
                type="number"
                value={profile.age}
                disabled
                className="input-field bg-gray-100"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Employment Type</label>
              <input
                type="text"
                value={profile.employmentType}
                disabled
                className="input-field bg-gray-100"
              />
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> Financial figures and credit data are sourced from bank systems and cannot be edited manually.
            </p>
          </div>
          
          <button className="btn-primary mt-6">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClientProfile;
