// constants.js
// Application-wide constants for banks, roles, score ranges, etc.
// Single source of truth for configuration values.
// Makes it easy to adjust thresholds and options across the app.

// Application constants

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

export const RISK_BANDS = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
};

export const SCORE_RANGES = {
  MIN: 300,
  MAX: 900,
  GOOD_THRESHOLD: 700,
  FAIR_THRESHOLD: 600,
};

export const USER_TYPES = {
  CLIENT: 'client',
  STAFF: 'staff',
};

export const ROLES = {
  RISK_ANALYST: 'risk_analyst',
  ADMIN: 'admin',
};
