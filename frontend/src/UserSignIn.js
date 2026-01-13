import React, { useState } from "react";
import axios from "axios";
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from "jwt-decode";
import './home.css';

export default function UserSignIn({ goToSignUp, goBack, onSignInSuccess, goToHome }) {
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showOtpVerification, setShowOtpVerification] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [resetSuccess, setResetSuccess] = useState('');

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('/api/users/login', form);
      
      // Store token
      sessionStorage.setItem('_userToken', response.data.token);
      sessionStorage.setItem('_user', JSON.stringify(response.data.user));
      
      // Call success callback
      if (onSignInSuccess) {
        onSignInSuccess(response.data.user);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Sign in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const decoded = jwtDecode(credentialResponse.credential);
      const response = await axios.post('/api/users/google-login', {
        google_id: decoded.sub,
        email: decoded.email,
        name: decoded.name
      });
      
      // Store token
      sessionStorage.setItem('_userToken', response.data.token);
      sessionStorage.setItem('_user', JSON.stringify(response.data.user));
      
      // Call success callback
      if (onSignInSuccess) {
        onSignInSuccess(response.data.user);
      }
      
      // Redirect to home page
      if (goToHome) {
        goToHome();
      }
    } catch (err) {
      setError('Google sign-in failed. Please try again.');
    }
  };

  const handleGoogleError = () => {
    setError('Google sign-in failed. Please try again.');
  };

  const handleForgotPassword = async () => {
    if (!forgotEmail) {
      setError('Please enter your email');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('/api/users/forgot-password', { email: forgotEmail });
      setResetSuccess('OTP sent to your email!');
      setShowOtpVerification(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    if (!otp) {
      setError('Please enter OTP');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      await axios.post('/api/users/verify-otp', { email: forgotEmail, otp });
      setResetSuccess('OTP verified! Enter your new password.');
      setShowResetPassword(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async () => {
    if (!newPassword || newPassword.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      await axios.post('/api/users/reset-password', { 
        email: forgotEmail, 
        otp, 
        new_password: newPassword 
      });
      setResetSuccess('Password reset successfully! You can now sign in.');
      setTimeout(() => {
        setShowForgotPassword(false);
        setShowOtpVerification(false);
        setShowResetPassword(false);
        setForgotEmail('');
        setOtp('');
        setNewPassword('');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to reset password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (showForgotPassword) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          <h2>Reset Password</h2>
          
          {!showOtpVerification && !showResetPassword && (
            <>
              <input 
                type="email" 
                placeholder="Enter your email" 
                value={forgotEmail} 
                onChange={(e) => setForgotEmail(e.target.value)} 
                required 
              />
              <button onClick={handleForgotPassword} disabled={loading}>
                {loading ? 'Sending...' : 'Send OTP'}
              </button>
            </>
          )}
          
          {showOtpVerification && !showResetPassword && (
            <>
              <input 
                type="text" 
                placeholder="Enter OTP" 
                value={otp} 
                onChange={(e) => setOtp(e.target.value)} 
                maxLength="6"
                className="otp-input"
                required 
              />
              <button onClick={handleVerifyOtp} disabled={loading}>
                {loading ? 'Verifying...' : 'Verify OTP'}
              </button>
            </>
          )}
          
          {showResetPassword && (
            <>
              <input 
                type="password" 
                placeholder="Enter new password" 
                value={newPassword} 
                onChange={(e) => setNewPassword(e.target.value)} 
                minLength="6"
                required 
              />
              <button onClick={handleResetPassword} disabled={loading}>
                {loading ? 'Resetting...' : 'Reset Password'}
              </button>
            </>
          )}
          
          {error && <div className="auth-error">{error}</div>}
          {resetSuccess && <div className="auth-success">{resetSuccess}</div>}
          
          <div className="auth-links">
            <span onClick={() => {
              setShowForgotPassword(false);
              setShowOtpVerification(false);
              setShowResetPassword(false);
            }}>Back to Sign In</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>Sign In</h2>
        <form onSubmit={handleSubmit}>
          <input 
            name="email" 
            type="email" 
            placeholder="Email" 
            value={form.email} 
            onChange={handleChange} 
            required 
          />
          <input 
            name="password" 
            type="password" 
            placeholder="Password" 
            value={form.password} 
            onChange={handleChange} 
            required 
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        
        {error && <div className="auth-error">{error}</div>}
        
        <div className="auth-divider">or</div>
        
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          text="signin_with"
          shape="rectangular"
          theme="filled_blue"
          size="large"
          width="100%"
        />
        
        <div className="auth-links">
          <span onClick={goToSignUp}>Create an account</span>
          <span onClick={goBack}>Back</span>
          <span className="forgot-link" onClick={() => setShowForgotPassword(true)}>
            Forgot password?
          </span>
        </div>
      </div>
    </div>
  );
}
