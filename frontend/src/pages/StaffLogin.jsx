// StaffLogin.jsx
// Login screen for bank staff (risk/data team).
// Form: username + password, calls /staff/login for the selected bank.
// On success, store role (Admin / Analyst) in AuthContext.
// Redirect to StaffDashboard after login.
// Layout can be similar to ClientLogin but with different copy and color accent.

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const StaffLogin = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [bankId, setBankId] = useState('bank_a');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement authentication logic
    navigate('/staff/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="card max-w-md w-full">
        <h2 className="text-2xl font-bold mb-6">Bank Staff Login</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Bank</label>
            <select
              value={bankId}
              onChange={(e) => setBankId(e.target.value)}
              className="input-field"
            >
              <option value="bank_a">Bank A</option>
              <option value="bank_b">Bank B</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
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

export default StaffLogin;
