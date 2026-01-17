// routes.js
// Centralized route definitions for the application.
// Makes it easy to update routes without searching through components.
// Groups routes by user type (client, staff) for organization.

// Client routes
export const ROUTES = {
  HOME: '/',
  AUTH_CHOICE: '/auth',
  
  // Client routes
  CLIENT: {
    BANK_SELECT: '/client/bank-select',
    LOGIN: '/client/login',
    DASHBOARD: '/client/dashboard',
    SCORE_DETAILS: '/client/score-details',
    PROFILE: '/client/profile',
  },
  
  // Staff routes
  STAFF: {
    LOGIN: '/staff/login',
    DASHBOARD: '/staff/dashboard',
    CUSTOMERS: '/staff/customers',
    CUSTOMER_DETAIL: '/staff/customers/:customerId',
    SCORE_APPLICATION: '/staff/score-application',
    MODEL_TRAINING: '/staff/model-training',
    ANALYTICS: '/staff/analytics',
  },
};

export default ROUTES;
