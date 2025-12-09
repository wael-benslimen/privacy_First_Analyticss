import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Login from './components/Login';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      // Optional: Verify token validity here
    }
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

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} onLogout={handleLogout} />
      <Header user={user} />

      <main className="ml-64 min-h-[calc(100vh-80px)]">
        {activeTab === 'dashboard' ? (
          <Dashboard token={token} />
        ) : (
          <div className="flex items-center justify-center h-[calc(100vh-80px)] text-slate-400">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-slate-600 mb-2">Work in Progress</h2>
              <p>The {activeTab} module is currently under development.</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
