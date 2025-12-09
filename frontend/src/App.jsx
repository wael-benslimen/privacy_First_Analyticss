import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Login from './components/Login';
import Settings from './components/Settings';
import Analysis from './components/Analysis';
import PrivacyPolicy from './components/PrivacyPolicy';
import FullAuditLog from './components/FullAuditLog';
import { auth } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('analysis');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    const verifyToken = async () => {
      if (token) {
        try {
          const response = await auth.me();
          setUser(response.data);
        } catch (error) {
          console.error('Token verification failed:', error);
          setToken(null);
          setUser(null);
          localStorage.removeItem('token');
        }
      }
    };

    verifyToken();
  }, [token]);

  const handleLogin = (data) => {
    setToken(data.access);
    setUser(data.user);
    localStorage.setItem('token', data.access);
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'analysis':
        return <Analysis />;
      case 'policy':
        return <PrivacyPolicy />;
      case 'audit':
        return <FullAuditLog />;
      case 'settings':
        return <Settings />;
      default:
        return <Analysis />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} onLogout={handleLogout} />
      <Header user={user} />

      <main className="ml-64 min-h-[calc(100vh-80px)]">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
