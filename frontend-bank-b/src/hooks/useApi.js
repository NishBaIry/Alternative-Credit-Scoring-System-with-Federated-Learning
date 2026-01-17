// useApi.js
// Custom hook for making API calls with loading and error states.
// Provides convenient methods: get, post, put, delete.
// Automatically handles loading states and error messages.
// Used throughout the app for data fetching.

import { useState, useCallback } from 'react';
import { apiClient } from '../lib/apiClient';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const request = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient(endpoint, options);
      setLoading(false);
      return response;
    } catch (err) {
      setError(err.message || 'An error occurred');
      setLoading(false);
      throw err;
    }
  }, []);

  const get = useCallback((endpoint) => {
    return request(endpoint, { method: 'GET' });
  }, [request]);

  const post = useCallback((endpoint, data) => {
    return request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }, [request]);

  const put = useCallback((endpoint, data) => {
    return request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }, [request]);

  const del = useCallback((endpoint) => {
    return request(endpoint, { method: 'DELETE' });
  }, [request]);

  return {
    loading,
    error,
    request,
    get,
    post,
    put,
    delete: del,
  };
};
