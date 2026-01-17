// ClientLogin.jsx
// Login form for borrowers: customer_id + password (hashed on backend).
// Uses selected bank from context to call the appropriate /client/login API.
// On success, saves auth token + bank id via useAuth() and redirects to ClientDashboard.
// Shows basic error messages (invalid credentials, network issues).
// Keep layout clean; use PrivacyBanner component to remind about data locality.

import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const ClientLogin = () => {
  const [customerId, setCustomerId] = useState('');
  const [password, setPassword] = useState('');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const bankId = searchParams.get('bank');

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement authentication logic
    navigate('/client/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="card max-w-md w-full">
        <h2 className="text-2xl font-bold mb-6">Client Login - {bankId?.toUpperCase()}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Customer ID</label>
            <input
              type="text"
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              className="input-field"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              required
            />
          </div>
          <button type="submit" className="btn-primary w-full">
            Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default ClientLogin;
