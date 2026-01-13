import React, { useState } from "react";
import axios from "axios";
import "./home.css";

export default function UserAccount({ user, onLogout, goToOrderHistory, goToMenu }) {
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [passwordForm, setPasswordForm] = useState({ otp: '', newPassword: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [otpSent, setOtpSent] = useState(false);

  const handleSendOTP = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const response = await axios.post('/api/users/forgot-password', { 
        email: user.email 
      });
      setSuccess('OTP sent to your email!');
      setOtpSent(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (!passwordForm.otp || !passwordForm.newPassword) {
      setError('Please enter OTP and new password');
      return;
    }
    
    if (passwordForm.newPassword.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const token = sessionStorage.getItem('_userToken');
      await axios.post('/api/users/change-password', {
        otp: passwordForm.otp,
        new_password: passwordForm.newPassword
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSuccess('Password changed successfully!');
      setTimeout(() => {
        setShowChangePassword(false);
        setOtpSent(false);
        setPasswordForm({ otp: '', newPassword: '' });
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="account-container">
      <div className="account-header">
        <h2>My Account</h2>
        <button className="logout-btn" onClick={onLogout}>
          Logout
        </button>
      </div>

      <div className="account-grid">
        <div className="account-card">
          <h3>Profile Information</h3>
          <div className="account-info">
            <div className="account-info-item">
              <span className="account-info-label">Name:</span>
              <span className="account-info-value">{user.name}</span>
            </div>
            <div className="account-info-item">
              <span className="account-info-label">Email:</span>
              <span className="account-info-value">{user.email}</span>
            </div>
            {user.phone && (
              <div className="account-info-item">
                <span className="account-info-label">Phone:</span>
                <span className="account-info-value">{user.phone}</span>
              </div>
            )}
          </div>
        </div>

        <div className="account-card">
          <h3>Quick Actions</h3>
          <div className="account-actions">
            <button className="account-btn" onClick={goToOrderHistory}>
              View Order History
            </button>
            <button className="account-btn" onClick={goToMenu}>
              Start New Order
            </button>
            <button 
              className="account-btn secondary" 
              onClick={() => setShowChangePassword(!showChangePassword)}
            >
              {showChangePassword ? 'Cancel' : 'Change Password'}
            </button>
          </div>
        </div>
      </div>

      {showChangePassword && (
        <div className="account-card" style={{ marginTop: '1.5rem', maxWidth: '600px' }}>
          <h3>Change Password</h3>
          
          {!otpSent ? (
            <>
              <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
                We'll send an OTP to {user.email} to verify your identity.
              </p>
              <button 
                className="account-btn" 
                onClick={handleSendOTP} 
                disabled={loading}
                style={{ maxWidth: '200px' }}
              >
                {loading ? 'Sending...' : 'Send OTP'}
              </button>
            </>
          ) : (
            <>
              <input
                type="text"
                placeholder="Enter OTP"
                value={passwordForm.otp}
                onChange={(e) => setPasswordForm({ ...passwordForm, otp: e.target.value })}
                maxLength="6"
                className="otp-input"
                style={{ 
                  width: '100%',
                  padding: '0.875rem',
                  marginBottom: '1rem',
                  borderRadius: '8px',
                  border: '1px solid #e6d3a3',
                  fontSize: '1rem'
                }}
              />
              <input
                type="password"
                placeholder="Enter new password"
                value={passwordForm.newPassword}
                onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                minLength="6"
                style={{ 
                  width: '100%',
                  padding: '0.875rem',
                  marginBottom: '1rem',
                  borderRadius: '8px',
                  border: '1px solid #e6d3a3',
                  fontSize: '1rem'
                }}
              />
              <button 
                className="account-btn" 
                onClick={handleChangePassword} 
                disabled={loading}
                style={{ maxWidth: '200px' }}
              >
                {loading ? 'Changing...' : 'Change Password'}
              </button>
            </>
          )}
          
          {error && <div className="auth-error" style={{ marginTop: '1rem' }}>{error}</div>}
          {success && <div className="auth-success" style={{ marginTop: '1rem' }}>{success}</div>}
        </div>
      )}
    </div>
  );
}
