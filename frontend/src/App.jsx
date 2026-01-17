import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import PrivacyBanner from './components/PrivacyBanner';

// Pages
import LandingPage from './pages/LandingPage';
import AuthChoice from './pages/AuthChoice';
import ClientBankSelect from './pages/ClientBankSelect';
import ClientLogin from './pages/ClientLogin';
import ClientDashboard from './pages/ClientDashboard';
import ClientScoreDetails from './pages/ClientScoreDetails';
import ClientProfile from './pages/ClientProfile';
import StaffLogin from './pages/StaffLogin';
import StaffDashboard from './pages/StaffDashboard';
import StaffCustomerList from './pages/StaffCustomerList';
import StaffCustomerDetail from './pages/StaffCustomerDetail';
import StaffScoreApplication from './pages/StaffScoreApplication';
import StaffModelTraining from './pages/StaffModelTraining';
import StaffAnalytics from './pages/StaffAnalytics';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="flex flex-col min-h-screen">
          <Navbar />
          
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/auth" element={<AuthChoice />} />
              
              {/* Client Routes */}
              <Route path="/client/bank-select" element={<ClientBankSelect />} />
              <Route path="/client/login" element={<ClientLogin />} />
              <Route path="/client/dashboard" element={<ClientDashboard />} />
              <Route path="/client/score-details" element={<ClientScoreDetails />} />
              <Route path="/client/profile" element={<ClientProfile />} />
              
              {/* Staff Routes */}
              <Route path="/staff/login" element={<StaffLogin />} />
              <Route path="/staff/dashboard" element={<StaffDashboard />} />
              <Route path="/staff/customers" element={<StaffCustomerList />} />
              <Route path="/staff/customers/:customerId" element={<StaffCustomerDetail />} />
              <Route path="/staff/score-application" element={<StaffScoreApplication />} />
              <Route path="/staff/model-training" element={<StaffModelTraining />} />
              <Route path="/staff/analytics" element={<StaffAnalytics />} />
            </Routes>
          </main>
          
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
