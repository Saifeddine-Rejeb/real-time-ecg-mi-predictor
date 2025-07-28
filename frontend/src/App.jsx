import React, { useState, useEffect } from 'react';
import './App.css';
import './components/sidebar.css';
import Sidebar from './components/sidebar';
import AppRoutes from './../routes/Routes';
import Login from './pages/Login';
import { useLocation, useNavigate } from 'react-router-dom';
import TopBar from './components/TopBar';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (data) => {
    if (data && data.token) {
      setIsAuthenticated(true);
      localStorage.setItem('token', data.token);
      localStorage.setItem('role', data.role);
      localStorage.setItem('user_id', data.user_id);
      if (data.email) {
        localStorage.setItem('email', data.email);
      }
    } else {
      setIsAuthenticated(false);
    }
  };

  const logout = async () => {
    const email = localStorage.getItem('email');
    if (email) {
      try {
        await fetch('http://localhost:5000/api/auth/logout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
      } catch (e) {
        console.error('Logout error:', e);
      }
    }
    setIsAuthenticated(false);
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('role');
    localStorage.removeItem('email');
    navigate('/', { replace: true });
  };

  useEffect(() => {
    if (location.pathname === '/logout') {
      logout();
    }
  }, [location.pathname]);

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app-main-layout">
      <Sidebar />
      <div className="app-content-area">
        <TopBar
          user="User Name"
          email={localStorage.getItem('email') || 'user@example.com'}
          onLogout={logout}
        />
        <div className="app-centered-content">
          <AppRoutes />
        </div>
      </div>
    </div>
  );
}

export default App;
