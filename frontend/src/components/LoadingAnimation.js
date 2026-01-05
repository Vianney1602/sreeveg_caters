import React from 'react';
import './LoadingAnimation.css';

export default function LoadingAnimation() {
  return (
    <div className="loading-overlay">
      <div className="loading-container">
        {/* Elegant Spinner */}
        <div className="spinner-wrapper">
          <div className="spinner"></div>
        </div>

        {/* Loading Text */}
        <div className="loading-text-container">
          <h2 className="loading-title">Hotel Shanmuga Bhavaan</h2>
          <p className="loading-subtitle">Loading delicious menu...</p>
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
  );
}
