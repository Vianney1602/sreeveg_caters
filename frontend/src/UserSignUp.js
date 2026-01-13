import React, { useState } from "react";
import axios from "axios";
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from "jwt-decode";
import './home.css';

export default function UserSignUp({ goToSignIn, goBack, onSignUpSuccess, goToHome }) {
  const [form, setForm] = useState({ name: '', email: '', password: '', phone: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const response = await axios.post('/api/users/register', form);
      setSuccess('Account created successfully! You can now sign in.');
      setTimeout(() => {
        goToSignIn();
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
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
        <h2>Create Your Account</h2>
        <form onSubmit={handleSubmit}>
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
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>
        
        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}
        
        <div className="auth-divider">or</div>
        
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          text="signup_with"
          shape="rectangular"
          theme="filled_blue"
          size="large"
          width="400"
        />
        
        <div className="auth-links">
          <span onClick={goToSignIn}>Already have an account? Sign In</span>
          <span onClick={goBack}>Back</span>
        </div>
      </div>
    </div>
  );
}
