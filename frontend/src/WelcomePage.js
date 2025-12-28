import "./welcome.css";

export default function WelcomePage({ goUser, goAdmin }) {
  const bgUrl = process.env.PUBLIC_URL + "/images/meals_veg.png";
  return (
    <div className="welcome-container" style={{ backgroundImage: `url(${bgUrl})` }}>
        <div className="overlay">
      <h1>Welcome to Shree Veg Caterers</h1>

      <div className="welcome-buttons">
        <button className="user-btn" onClick={goUser}>
          Continue as User
        </button>

        <button className="admin-btn" onClick={goAdmin}>
          Login as Admin
        </button>
      </div>
      </div>
    </div>
  );
}
