import React, { useState } from 'react';
import './login.css';
import logo from '../assets/logo.png';

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      if (response.ok) {
        if (onLogin) onLogin(data);
      } else {
        setError(data.message || 'Invalid Credentials');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('An error occurred during login');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <div className="login-brand">
            <img src={logo} alt="HealthCare Logo" className="login-logo" />
            <span className="brand-text">CardioMonitor</span>
          </div>
          <h3>Welcome Back</h3>
          <p>Please sign in to continue</p>
        </div>
        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label htmlFor="email">Email address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="login-options">
            <a href="/forgot-password" className="forgot-link">Forgot password?</a>
          </div>
          {error && <div style={{ color: 'red', marginTop: '10px' }}>{error}</div>}
          <button type="submit">Sign In</button>
        </form>
      </div>
    </div>
  );
}
