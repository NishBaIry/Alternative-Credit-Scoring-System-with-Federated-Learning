// Navbar.jsx
// Top navigation bar used across public and authenticated pages.
// Shows project name + quick links based on auth role (client vs staff).
// Reads state from AuthContext to render appropriate menu items.
// Keep styling consistent with Tailwind, minimal logic in this file.
// Should also include a Logout button when user is authenticated.

import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = ({ userType = null }) => {
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="flex items-center">
            <span className="text-2xl font-bold text-primary-600">CashFlow</span>
          </Link>
          
          <div className="flex items-center space-x-4">
            {!userType && (
              <Link to="/auth" className="btn-primary">
                Login
              </Link>
            )}
            
            {userType === 'client' && (
              <>
                <Link to="/client/dashboard" className="text-gray-700 hover:text-primary-600">
                  Dashboard
                </Link>
                <Link to="/client/profile" className="text-gray-700 hover:text-primary-600">
                  Profile
                </Link>
                <button className="text-gray-700 hover:text-primary-600">
                  Logout
                </button>
              </>
            )}
            
            {userType === 'staff' && (
              <>
                <Link to="/staff/dashboard" className="text-gray-700 hover:text-primary-600">
                  Dashboard
                </Link>
                <Link to="/staff/customers" className="text-gray-700 hover:text-primary-600">
                  Customers
                </Link>
                <button className="text-gray-700 hover:text-primary-600">
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
