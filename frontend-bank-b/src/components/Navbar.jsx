// Navbar.jsx
// Top navigation bar used across public and authenticated pages.
// Shows project name + quick links based on auth role (client vs staff).
// Reads state from AuthContext to render appropriate menu items.
// Keep styling consistent with Tailwind, minimal logic in this file.
// Should also include a Logout button when user is authenticated.

import { Link, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuthContext();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/staff/login');
  };

  const handleLogoClick = (e) => {
    e.preventDefault();
    if (isAuthenticated && user?.type === 'staff') {
      navigate('/staff/dashboard');
    } else if (isAuthenticated && user?.type === 'client') {
      navigate('/client/dashboard');
    } else {
      navigate('/staff/login');
    }
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <a href="#" onClick={handleLogoClick} className="flex items-center">
            <span className="text-2xl font-bold text-primary-600">CashFlow</span>
          </a>

          <div className="flex items-center space-x-4">
            {!isAuthenticated && (
              <Link to="/staff/login" className="btn-primary">
                Login
              </Link>
            )}

            {isAuthenticated && user?.type === 'client' && (
              <>
                <Link to="/client/dashboard" className="text-gray-700 hover:text-primary-600">
                  Dashboard
                </Link>
                <Link to="/client/profile" className="text-gray-700 hover:text-primary-600">
                  Profile
                </Link>
                <button onClick={handleLogout} className="text-gray-700 hover:text-primary-600">
                  Logout
                </button>
              </>
            )}

            {isAuthenticated && user?.type === 'staff' && (
              <>
                <Link to="/staff/dashboard" className="text-gray-700 hover:text-primary-600">
                  Dashboard
                </Link>
                <Link to="/staff/customers" className="text-gray-700 hover:text-primary-600">
                  Manage Accounts
                </Link>
                <button onClick={handleLogout} className="text-gray-700 hover:text-primary-600">
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
