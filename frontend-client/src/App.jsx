import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import PrivacyBanner from './components/PrivacyBanner';

// Pages - Client Portal Only
import LandingPage from './pages/LandingPage';
import ClientBankSelect from './pages/ClientBankSelect';
import ClientLogin from './pages/ClientLogin';
import ClientDashboard from './pages/ClientDashboard';
import ClientScoreDetails from './pages/ClientScoreDetails';
import ClientProfile from './pages/ClientProfile';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="flex flex-col min-h-screen">
          <Navbar />
          
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              
              {/* Client Routes - Direct to bank selection */}
              <Route path="/client/bank-select" element={<ClientBankSelect />} />
              <Route path="/client/login" element={<ClientLogin />} />
              <Route path="/client/dashboard" element={<ClientDashboard />} />
              <Route path="/client/score-details" element={<ClientScoreDetails />} />
              <Route path="/client/profile" element={<ClientProfile />} />
            </Routes>
          </main>
          
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
