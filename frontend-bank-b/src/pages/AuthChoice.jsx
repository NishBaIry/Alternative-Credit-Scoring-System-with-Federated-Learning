// AuthChoice.jsx
// Simple page that asks whether the user is a Client or Bank Staff.
// Two big cards/buttons that route to Client flow (bank select) or StaffLogin.
// Used only after LandingPage to keep navigation clear.
// No backend calls here; purely front-end routing state.
// Keep the UI minimal but obvious for judges.

import React from 'react';
import { useNavigate } from 'react-router-dom';

const AuthChoice = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <h2 className="text-3xl font-bold text-center">Choose Login Type</h2>
        <div className="space-y-4">
          <button 
            onClick={() => navigate('/client/bank-select')}
            className="btn-primary w-full"
          >
            Client Login
          </button>
          <button 
            onClick={() => navigate('/staff/login')}
            className="btn-secondary w-full"
          >
            Bank Staff Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthChoice;
