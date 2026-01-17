// LandingPage.jsx
// Public landing screen explaining the alternative credit score product.
// Shows key benefits: privacy-preserving FL, inclusion for thin-file borrowers.
// Contains CTAs to "Continue as Client" or "Continue as Bank Staff".
// Very light logic; just routing to AuthChoice or StaffLogin.
// Tailwind-based responsive layout for hackathon demo.

import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="min-h-screen">
      <h1 className="text-4xl font-bold">Alternative Credit Scoring Platform</h1>
      <p className="text-lg text-gray-600 mt-4">Privacy-preserving credit scoring using alternative data</p>
    </div>
  );
};

export default LandingPage;
