import React from 'react';
import './LoadingAnimation.css';

export default function LoadingAnimation() {
  return (
    <div className="loading-overlay">
      <div className="loading-container">
        {/* Chef Hat Animation */}
        <div className="chef-hat-container">
          <div className="chef-hat">
            <div className="hat-top"></div>
            <div className="hat-band"></div>
          </div>
        </div>

        {/* Spinning Plate with Fork & Spoon */}
        <div className="plate-container">
          <div className="plate">
            <div className="plate-inner"></div>
          </div>
          
          {/* Utensils rotating around plate */}
          <div className="utensil fork-utensil">🍴</div>
          <div className="utensil spoon-utensil">🥄</div>
          <div className="utensil knife-utensil">🔪</div>
        </div>

        {/* Loading Text */}
        <div className="loading-text-container">
          <h2 className="loading-title">Hotel Shanmuga Bhavaan</h2>
          <p className="loading-subtitle">Preparing your meal...</p>
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="food-animation">
          <span className="food-item">🍽️</span>
          <span className="food-item">🍜</span>
          <span className="food-item">🥘</span>
          <span className="food-item">🍛</span>
        </div>
      </div>
    </div>
  );
}
