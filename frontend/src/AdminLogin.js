import React, { useState } from 'react';
import authService from './services/authService';
import './admin.css';

export default function AdminLogin({ goBack, onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('Username and password are required');
      return;
    }
    
    setLoading(true);
    const result = await authService.login(username, password);
    
    if (result.success) {
      setUsername('');
      setPassword('');
      onLoginSuccess();
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="admin-login-container">
      <button className="back-link" onClick={goBack}>← Back to Home</button>

      <div className="login-card">
        <div className="login-icon">👨‍💼</div>
        <h1>Admin Portal</h1>
        <p className="login-subtitle">
          Sign in to manage your catering business
        </p>

        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label>
              <span className="icon">👤</span>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
            />
          </div>

          <div className="form-group">
            <label>
              <span className="icon">🔒</span>
              Password
            </label>
            <div className="password-input-container">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
              <button
                type="button"
                className="show-password-btn"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="sign-in-btn" 
            disabled={loading}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}