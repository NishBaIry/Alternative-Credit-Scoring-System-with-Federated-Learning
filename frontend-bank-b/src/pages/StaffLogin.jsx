// StaffLogin.jsx
// Login screen for Bank B staff (risk/data team).
// Form: username + password, calls /staff/login with hardcoded bank_b.
// On success, store role (Admin / Analyst) in AuthContext.
// Redirect to StaffDashboard after login.
// Bank ID is hardcoded from environment variables - no selection needed.

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BANK_ID, BANK_NAME } from '@/lib/constants';

const StaffLogin = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement authentication logic with BANK_ID
    console.log('Logging in to', BANK_ID);
    navigate('/staff/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="card max-w-md w-full">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold">{BANK_NAME} Staff Login</h2>
          <p className="text-gray-500 text-sm mt-2">Risk Analysts & Administrators</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input-field"
              placeholder="admin@bankb.com"
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
            Login to {BANK_NAME}
          </button>
        </form>
      </div>
    </div>
  );
};

export default StaffLogin;
