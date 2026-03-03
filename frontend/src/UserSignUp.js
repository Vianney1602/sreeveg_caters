import React, { useState } from "react";
import axios from "axios";
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from "jwt-decode";
import './home.css';

export default function UserSignUp({ goToSignIn, goBack, onSignUpSuccess, goToHome }) {
  const [form, setForm] = useState({ name: '', email: '', password: '', phone: '' });
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState(0); // 0: Details, 1: OTP
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSendOtp = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const res = await axios.post('/api/users/send-registration-otp', { email: form.email });
      setStep(1);
      setSuccess(res.data?.message || 'Verification code sent to your email!');
    } catch (err) {
      const msg = err.response?.data?.error || 'Failed to send verification code.';
      setError(msg);
      // If we already reached step 1, stay there so user can resend
      if (step === 0) setStep(0);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await axios.post('/api/users/register', { ...form, otp });
      setSuccess('Account created successfully! Redirecting...');

      // Auto login if possible or go to sign in
      setTimeout(() => {
        goToSignIn();
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please check your OTP.');
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
      if (onSignUpSuccess) {
        onSignUpSuccess(response.data.user);
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

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>{step === 0 ? "Create Your Account" : "Verify Your Email"}</h2>

        {step === 0 ? (
          <form onSubmit={handleSendOtp}>
            <input
              name="name"
              type="text"
              placeholder="Full Name"
              value={form.name}
              onChange={handleChange}
              required
            />
            <input
              name="email"
              type="email"
              placeholder="Email"
              value={form.email}
              onChange={handleChange}
              required
            />
            <input
              name="phone"
              type="tel"
              placeholder="Phone Number (Optional)"
              value={form.phone}
              onChange={handleChange}
            />
            <input
              name="password"
              type="password"
              placeholder="Password"
              value={form.password}
              onChange={handleChange}
              required
              minLength="6"
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Sending Code...' : 'Send Verification Code'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSubmit}>
            <p className="auth-instruction">Enter the 6-digit code sent to <strong>{form.email}</strong></p>
            <input
              type="text"
              placeholder="6-digit OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
              required
              maxLength="6"
              className="otp-input"
              style={{ textAlign: 'center', fontSize: '24px', letterSpacing: '8px' }}
            />
            <button type="submit" disabled={loading || otp.length !== 6}>
              {loading ? 'Verifying...' : 'Verify & Create Account'}
            </button>
            <div className="auth-links">
              <span onClick={() => { if (!loading) handleSendOtp(); }} style={{ cursor: loading ? 'not-allowed' : 'pointer' }}>
                {loading ? 'Sending...' : 'Resend OTP'}
              </span>
              <span onClick={() => setStep(0)}>Change Email / Edit Details</span>
            </div>
          </form>
        )}

        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}

        {step === 0 && (
          <>
            <div className="auth-divider">or</div>

            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              text="signup_with"
              shape="rectangular"
              theme="filled_blue"
              size="large"
              width="100%"
            />
          </>
        )}

        <div className="auth-links">
          <span onClick={goToSignIn}>Already have an account? Sign In</span>
          <span onClick={goBack}>Back</span>
        </div>
      </div>
    </div>
  );
}
