// apiClient.js
// Thin wrapper around fetch/axios for API calls to backend.
// Automatically attaches auth token and selected bank id to requests.
// Provides helpers like get('/client/me/score') and post('/staff/model/train').
// API URL is loaded from centralized constants.

import { API_BASE_URL } from './constants';

export const apiClient = async (endpoint, options = {}) => {
  const token = localStorage.getItem('authToken');
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export default apiClient;
