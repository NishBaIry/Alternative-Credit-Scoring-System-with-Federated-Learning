// useAuth.js
// Custom hook wrapping AuthContext for easier access in components.
// Exposes currentUser, role, bankId, token, login(), logout() helpers.
// Central place for handling auth state and redirects.
// Keeps auth logic out of page components.

import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored auth token
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
    
    setLoading(false);
  }, []);

  const login = async (credentials, userType) => {
    // TODO: Implement actual API call
    const mockUser = {
      id: credentials.username || credentials.customerId,
      type: userType,
      bankId: credentials.bankId,
    };
    
    localStorage.setItem('authToken', 'mock-token');
    localStorage.setItem('userData', JSON.stringify(mockUser));
    setUser(mockUser);
    
    return mockUser;
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    setUser(null);
  };

  return {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    logout,
  };
};
