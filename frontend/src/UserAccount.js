import React, { useState } from "react";
import axios from "axios";
import "./home.css";

export default function UserAccount({ user, onLogout, goToOrderHistory, goToMenu, goToHome }) {
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [passwordForm, setPasswordForm] = useState({ otp: '', newPassword: '' });
  const [profileForm, setProfileForm] = useState({ name: user.name, phone: user.phone || '' });
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
        setError('');
        setSuccess('');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleEditProfile = async () => {
    if (!profileForm.name.trim()) {
      setError('Name is required');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const token = sessionStorage.getItem('_userToken');
      await axios.put('/api/users/profile', {
        name: profileForm.name,
        phone: profileForm.phone
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update user data in sessionStorage
      const updatedUser = { ...user, name: profileForm.name, phone: profileForm.phone };
      sessionStorage.setItem('_user', JSON.stringify(updatedUser));
      
      setSuccess('Profile updated successfully!');
      setTimeout(() => {
        setShowEditProfile(false);
        setError('');
        setSuccess('');
        window.location.reload(); // Refresh to show updated data
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="account-container">
      {/* Global Success/Error Popup */}
      {(error || success) && (
        <div className={`popup-notification ${success ? 'success' : 'error'}`}>
          {success || error}
        </div>
      )}
      
      <button 
        className="back-btn" 
        onClick={goToHome}
        style={{
          marginBottom: '1.5rem',
          padding: '0.75rem 1.5rem',
          background: '#7a0000',
          color: '#f5c542',
          border: 'none',
          borderRadius: '8px',
          fontSize: '1rem',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}
        onMouseOver={(e) => {
          e.target.style.background = '#5c0000';
          e.target.style.transform = 'translateX(-4px)';
        }}
        onMouseOut={(e) => {
          e.target.style.background = '#7a0000';
          e.target.style.transform = 'translateX(0)';
        }}
      >
        ← Back to Home
      </button>
      
      <div className="account-header">
        <h2>My Account</h2>
        <button className="logout-btn" onClick={onLogout}>
          Logout
        </button>
      </div>

      <div className="account-grid">
        <div className="account-card">
          <h3>Profile Information</h3>
          {!showEditProfile ? (
            <>
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
              <button 
                className="account-btn secondary" 
                onClick={() => setShowEditProfile(true)}
                style={{ marginTop: '1rem' }}
              >
                Edit Profile
              </button>
            </>
          ) : (
            <>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', color: '#7a0000', fontWeight: 600, marginBottom: '0.5rem' }}>
                    Name:
                  </label>
                  <input
                    type="text"
                    value={profileForm.name}
                    onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                    style={{ 
                      width: '100%',
                      padding: '0.875rem',
                      borderRadius: '8px',
                      border: '1px solid #e6d3a3',
                      fontSize: '1rem'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#7a0000', fontWeight: 600, marginBottom: '0.5rem' }}>
                    Phone:
                  </label>
                  <input
                    type="tel"
                    value={profileForm.phone}
                    onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                    style={{ 
                      width: '100%',
                      padding: '0.875rem',
                      borderRadius: '8px',
                      border: '1px solid #e6d3a3',
                      fontSize: '1rem'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#6b7280', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                    Email: {user.email} (cannot be changed)
                  </label>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button 
                  className="account-btn" 
                  onClick={handleEditProfile}
                  disabled={loading}
                  style={{ flex: 1 }}
                >
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
                <button 
                  className="account-btn secondary" 
                  onClick={() => {
                    setShowEditProfile(false);
                    setProfileForm({ name: user.name, phone: user.phone || '' });
                    setError('');
                    setSuccess('');
                  }}
                  disabled={loading}
                  style={{ flex: 1 }}
                >
                  Cancel
                </button>
              </div>
            </>
          )}
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
        </div>
      )}
    </div>
  );
}
