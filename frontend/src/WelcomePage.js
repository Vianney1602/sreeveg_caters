import "./welcome.css";

export default function WelcomePage({ goUser, goAdmin, onGetStarted }) {
  const bgUrl = process.env.PUBLIC_URL + "/images/meals_veg.png";
  return (
    <div className="welcome-container" style={{ backgroundImage: `url(${bgUrl})` }}>
        <div className="overlay">
      <h1>Welcome to Hotel Shanmuga Bhavaan</h1>

      <div className="welcome-buttons">
        <button className="get-started-btn" onClick={onGetStarted}>
          Get Started
        </button>
      </div>
      </div>
    </div>
  );
}
