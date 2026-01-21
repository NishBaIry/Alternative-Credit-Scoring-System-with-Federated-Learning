// constants.js
// Application-wide constants for banks, roles, score ranges, etc.
// Single source of truth for configuration values.
// All config loaded from environment variables (.env file)

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Bank Configuration
export const BANK_ID = import.meta.env.VITE_BANK_ID || 'bank_b';
export const BANK_NAME = import.meta.env.VITE_BANK_NAME || 'Bank A';
export const APP_TYPE = import.meta.env.VITE_APP_TYPE || 'staff';
export const APP_TITLE = import.meta.env.VITE_APP_TITLE || 'CashFlow - Bank A Staff Portal';

// Score Configuration
export const SCORE_RANGES = {
  MIN: parseInt(import.meta.env.VITE_SCORE_MIN) || 300,
  MAX: parseInt(import.meta.env.VITE_SCORE_MAX) || 900,
  GOOD_THRESHOLD: parseInt(import.meta.env.VITE_SCORE_GOOD_THRESHOLD) || 700,
  FAIR_THRESHOLD: parseInt(import.meta.env.VITE_SCORE_FAIR_THRESHOLD) || 600,
};

// Bank definitions
export const BANKS = {
  BANK_A: {
    id: 'bank_a',
    name: 'Bank A',
    description: 'Your trusted banking partner',
  },
  BANK_B: {
    id: 'bank_b',
    name: 'Bank B',
    description: 'Banking made simple',
  },
};

// Risk bands based on score
export const RISK_BANDS = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
};

// User types
export const USER_TYPES = {
  CLIENT: 'client',
  STAFF: 'staff',
};

// Staff roles
export const ROLES = {
  RISK_ANALYST: 'risk_analyst',
  ADMIN: 'admin',
};

// Helper function to get risk band from score
export const getRiskBand = (score) => {
  if (score >= SCORE_RANGES.GOOD_THRESHOLD) return RISK_BANDS.LOW;
  if (score >= SCORE_RANGES.FAIR_THRESHOLD) return RISK_BANDS.MEDIUM;
  return RISK_BANDS.HIGH;
};

// Helper function to get score color
export const getScoreColor = (score) => {
  if (score >= SCORE_RANGES.GOOD_THRESHOLD) return '#10b981'; // green
  if (score >= SCORE_RANGES.FAIR_THRESHOLD) return '#f59e0b'; // amber
  return '#ef4444'; // red
};
